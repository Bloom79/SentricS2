"""
Rate limiting middleware for API endpoints
Protects against brute force and DDoS attacks
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting.
    Uses user ID if authenticated, otherwise IP address.
    """
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user") and request.state.user:
        user_id = getattr(request.state.user, "id", None)
        if user_id:
            return f"user:{user_id}"

    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["100/minute"],  # Default: 100 requests per minute
    storage_uri="memory://",  # Use in-memory storage (can be changed to Redis)
    strategy="fixed-window",
    headers_enabled=True,
)


# Rate limit presets for different endpoint types
RATE_LIMITS = {
    "auth": "5/minute",  # Strict limit for login/registration
    "api": "60/minute",  # Standard API endpoints
    "read": "100/minute",  # Read operations
    "write": "30/minute",  # Write operations
    "heavy": "10/minute",  # Resource-intensive operations
}


def get_rate_limit(limit_type: str = "api") -> str:
    """Get rate limit string for a specific type"""
    return RATE_LIMITS.get(limit_type, RATE_LIMITS["api"])
