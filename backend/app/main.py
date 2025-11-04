"""
SentricS2 - Main FastAPI application
Enterprise Asset Management for Italian Renewable Energy
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from app.core.config import settings
from app.core.database import init_db
from app.core.middleware import setup_middleware
from app.core.security_middleware import SecurityHeadersMiddleware
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"] if settings.RATE_LIMIT_ENABLED else [],
    storage_uri=str(settings.REDIS_URL) if not settings.DISABLE_REDIS else "memory://",
    enabled=settings.RATE_LIMIT_ENABLED,
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Asset Management for Italian Renewable Energy",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,  # Disable docs in production
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    logger.info(f"Rate limiting enabled: {settings.RATE_LIMIT_PER_MINUTE}/minute")

# Setup middleware
setup_middleware(app)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Trusted hosts (protect against Host header attacks)
if settings.ALLOWED_HOSTS != "*":
    allowed_hosts = [h.strip() for h in settings.ALLOWED_HOSTS.split(",")]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    logger.info(f"Trusted hosts: {allowed_hosts}")

# CORS Configuration for GCP
cors_origins = []
if settings.BACKEND_CORS_ORIGINS:
    cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
elif settings.CORS_ORIGINS:
    cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]

# Add development origins
if settings.ENVIRONMENT == "development":
    cors_origins.extend([
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ])

# Add production origins
if settings.FRONTEND_URL and settings.FRONTEND_URL not in cors_origins:
    cors_origins.append(settings.FRONTEND_URL)

# Add GCP-specific origins
if settings.GCP_PROJECT_ID:
    cors_origins.extend([
        f"https://{settings.GCP_PROJECT_ID}.web.app",
        f"https://{settings.GCP_PROJECT_ID}.firebaseapp.com",
        f"https://{settings.GCP_SERVICE_NAME}-{settings.GCP_PROJECT_ID}.a.run.app" if settings.GCP_SERVICE_NAME else "",
    ])

# Remove empty strings and duplicates
cors_origins = list(set(filter(None, cors_origins)))

if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "X-Content-Range"],
        max_age=600,
    )
    logger.info(f"CORS enabled for origins: {cors_origins}")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

