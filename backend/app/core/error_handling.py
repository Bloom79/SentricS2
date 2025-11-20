"""
Error handling utilities
Sanitizes error messages to prevent information leakage
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class SafeHTTPException(HTTPException):
    """
    HTTP Exception that logs full error details but returns sanitized message to client
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        internal_detail: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        """
        Args:
            status_code: HTTP status code
            detail: Safe message to return to client
            internal_detail: Full error details for server logs only
            headers: Optional response headers
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)

        # Log internal details if provided
        if internal_detail:
            if status_code >= 500:
                logger.error(f"Internal error: {internal_detail}", exc_info=True)
            elif status_code >= 400:
                logger.warning(f"Client error: {internal_detail}")


def sanitize_error_message(error: Exception, default_message: str = "An error occurred") -> str:
    """
    Sanitize error message to remove sensitive information

    Args:
        error: The exception
        default_message: Default safe message

    Returns:
        Sanitized error message safe for client
    """
    # For development, we might want more details
    from app.core.config import settings

    if settings.DEBUG and settings.ENVIRONMENT == "development":
        return str(error)

    # In production, return generic messages
    error_type = type(error).__name__

    if isinstance(error, IntegrityError):
        if "duplicate key" in str(error).lower():
            return "A record with this information already exists"
        elif "foreign key" in str(error).lower():
            return "Cannot perform this action due to related records"
        elif "not null" in str(error).lower():
            return "Required field is missing"
        else:
            return "Database constraint violation"

    elif isinstance(error, ValueError):
        # ValueError often contains safe messages we set ourselves
        return str(error)

    elif isinstance(error, SQLAlchemyError):
        return "Database operation failed"

    elif isinstance(error, HTTPException):
        # HTTPException detail is usually safe
        return error.detail

    else:
        # Generic error for unknown types
        return default_message


def handle_database_error(error: Exception, operation: str = "database operation") -> HTTPException:
    """
    Handle database errors with appropriate sanitization

    Args:
        error: The database error
        operation: Description of operation that failed

    Returns:
        Sanitized HTTPException
    """
    # Log full error details
    logger.error(f"Database error during {operation}: {error}", exc_info=True)

    # Determine appropriate response
    if isinstance(error, IntegrityError):
        error_str = str(error).lower()

        if "duplicate key" in error_str or "unique constraint" in error_str:
            return SafeHTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A record with this information already exists",
                internal_detail=str(error)
            )
        elif "foreign key" in error_str:
            return SafeHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot perform this action due to related records",
                internal_detail=str(error)
            )
        elif "not null" in error_str:
            return SafeHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Required field is missing",
                internal_detail=str(error)
            )
        else:
            return SafeHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid data provided",
                internal_detail=str(error)
            )

    else:
        # Generic database error
        return SafeHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete {operation}",
            internal_detail=str(error)
        )


def safe_error_response(
    error: Exception,
    operation: str = "operation",
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
) -> HTTPException:
    """
    Create a safe error response from any exception

    Args:
        error: The exception
        operation: Description of what failed
        status_code: HTTP status code to return

    Returns:
        Sanitized HTTPException
    """
    # Log full error
    logger.error(f"Error during {operation}: {error}", exc_info=True)

    # Get sanitized message
    safe_message = sanitize_error_message(error, f"Failed to complete {operation}")

    return SafeHTTPException(
        status_code=status_code,
        detail=safe_message,
        internal_detail=str(error)
    )


# Common error responses
class CommonErrors:
    """Pre-defined common error responses"""

    @staticmethod
    def not_found(resource: str = "Resource") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )

    @staticmethod
    def unauthorized() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    @staticmethod
    def forbidden(message: str = "Insufficient permissions") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )

    @staticmethod
    def bad_request(message: str = "Invalid request") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    @staticmethod
    def conflict(message: str = "Resource already exists") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message
        )

    @staticmethod
    def internal_error(message: str = "Internal server error") -> HTTPException:
        return SafeHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
