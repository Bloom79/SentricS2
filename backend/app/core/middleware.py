"""
Middleware configuration
Consolidated from Kronos EAM
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging
import time

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Centralized error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=True)
            return Response(
                content='{"detail": "Internal server error"}',
                status_code=500,
                media_type="application/json"
            )


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Add tenant context to requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract tenant from header or token
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        return response


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Track request metrics"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        
        return response


def setup_middleware(app):
    """Setup all middleware"""
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(TenantContextMiddleware)
    app.add_middleware(RequestTrackingMiddleware)

