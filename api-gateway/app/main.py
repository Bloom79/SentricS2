"""
SentricS2 API Gateway - Insanely Great Edition
Thin layer connecting the new UI to existing backend services
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import cer, trading, bess

app = FastAPI(
    title="SentricS2 API Gateway",
    description="Thin API layer for the Insanely Great UI",
    version="2.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cer.router, prefix="/api/v2/cer", tags=["CER Billing"])
app.include_router(trading.router, prefix="/api/v2/trading", tags=["15-Min Trading"])
app.include_router(bess.router, prefix="/api/v2/bess", tags=["BESS Monitoring"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "SentricS2 API Gateway - Insanely Great Edition",
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "cer": "operational",
            "trading": "operational",
            "bess": "operational",
        },
    }
