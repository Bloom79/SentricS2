"""
Audit logging utilities
Simplifies audit logging across the application
"""

from typing import Optional, Dict, Any
from fastapi import Request
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def log_audit_event(
    db: Session,
    request: Request,
    action: str,
    resource_type: str = None,
    resource_id: Any = None,
    resource_name: str = None,
    description: str = None,
    old_values: Dict = None,
    new_values: Dict = None,
    changes: Dict = None,
    metadata: Dict = None,
    severity: str = "INFO"
):
    """
    Simplified audit logging function

    Args:
        db: Database session
        request: FastAPI request object
        action: Action being performed (use AuditActionEnum values)
        resource_type: Type of resource (e.g., "plant", "asset")
        resource_id: ID of affected resource
        resource_name: Name of resource
        description: Human-readable description
        old_values: Previous values (for updates)
        new_values: New values (for updates)
        changes: Specific changed fields
        metadata: Additional context
        severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
    """
    try:
        from app.models.audit_log import AuditLog, AuditActionEnum, AuditSeverityEnum

        # Extract user info from request state
        user_id = None
        user_email = None
        user_role = None
        tenant_id = None

        if hasattr(request.state, "user"):
            user = request.state.user
            user_id = getattr(user, "sub", None) or getattr(user, "id", None)
            user_email = getattr(user, "email", None)
            user_role = getattr(user, "role", None)

        if hasattr(request.state, "tenant_id"):
            tenant_id = request.state.tenant_id

        # Extract request metadata
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        request_id = request.headers.get("x-request-id")

        # Convert action string to enum if needed
        if isinstance(action, str):
            try:
                action = AuditActionEnum[action]
            except KeyError:
                action = AuditActionEnum.CREATED  # Default fallback

        # Convert severity string to enum
        try:
            severity_enum = AuditSeverityEnum[severity]
        except KeyError:
            severity_enum = AuditSeverityEnum.INFO

        # Create audit log entry
        AuditLog.log_action(
            db=db,
            action=action,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            metadata=metadata,
            severity=severity_enum,
            tenant_id=tenant_id
        )

    except Exception as e:
        # Don't fail the request if audit logging fails
        # But log the error for investigation
        logger.error(f"Failed to create audit log: {e}", exc_info=True)


def calculate_changes(old_data: Dict, new_data: Dict) -> Dict:
    """
    Calculate what changed between old and new data

    Args:
        old_data: Previous state
        new_data: New state

    Returns:
        Dictionary of changed fields with old and new values
    """
    if not old_data or not new_data:
        return {}

    changes = {}
    all_keys = set(old_data.keys()) | set(new_data.keys())

    for key in all_keys:
        old_val = old_data.get(key)
        new_val = new_data.get(key)

        if old_val != new_val:
            changes[key] = {
                "old": old_val,
                "new": new_val
            }

    return changes
