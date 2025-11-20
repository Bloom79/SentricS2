"""
Audit Log Model
Tracks all significant actions in the system for security and compliance
"""

from sqlalchemy import Column, String, Integer, JSON, DateTime, Enum
from datetime import datetime
import enum

from app.models.base import BaseModel


class AuditActionEnum(str, enum.Enum):
    """Audit action types"""
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    PASSWORD_RESET = "PASSWORD_RESET"

    # User Management
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    USER_SUSPENDED = "USER_SUSPENDED"
    USER_ACTIVATED = "USER_ACTIVATED"

    # Data Operations
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    VIEWED = "VIEWED"
    EXPORTED = "EXPORTED"
    IMPORTED = "IMPORTED"

    # CER Operations
    CER_CREATED = "CER_CREATED"
    CER_UPDATED = "CER_UPDATED"
    CER_MEMBER_ADDED = "CER_MEMBER_ADDED"
    CER_MEMBER_REMOVED = "CER_MEMBER_REMOVED"

    # Compliance
    COMPLIANCE_SUBMITTED = "COMPLIANCE_SUBMITTED"
    COMPLIANCE_APPROVED = "COMPLIANCE_APPROVED"
    COMPLIANCE_REJECTED = "COMPLIANCE_REJECTED"

    # Workflows
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_CANCELLED = "WORKFLOW_CANCELLED"

    # System
    SETTINGS_CHANGED = "SETTINGS_CHANGED"
    API_KEY_CREATED = "API_KEY_CREATED"
    API_KEY_REVOKED = "API_KEY_REVOKED"


class AuditSeverityEnum(str, enum.Enum):
    """Severity levels for audit events"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditLog(BaseModel):
    """
    Audit log for tracking system actions
    Provides complete audit trail for compliance and security
    """
    __tablename__ = "audit_logs"

    # Action details
    action = Column(Enum(AuditActionEnum), nullable=False, index=True)
    severity = Column(Enum(AuditSeverityEnum), nullable=False, default=AuditSeverityEnum.INFO)

    # Actor (who performed the action)
    user_id = Column(Integer, index=True)
    user_email = Column(String(255))
    user_role = Column(String(50))

    # Target (what was affected)
    resource_type = Column(String(50), index=True)  # e.g., "plant", "asset", "cer"
    resource_id = Column(String(100), index=True)  # ID of the affected resource
    resource_name = Column(String(255))  # Human-readable name

    # Context
    description = Column(String(500))
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(String(500))
    request_id = Column(String(100), index=True)  # For request tracing

    # Changes (for data modifications)
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    changes = Column(JSON)  # Specific fields that changed

    # Additional metadata
    metadata = Column(JSON)  # Flexible field for additional context

    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_email} on {self.resource_type}:{self.resource_id}>"

    @classmethod
    def log_action(
        cls,
        db,
        action: AuditActionEnum,
        user_id: int = None,
        user_email: str = None,
        user_role: str = None,
        resource_type: str = None,
        resource_id: str = None,
        resource_name: str = None,
        description: str = None,
        ip_address: str = None,
        user_agent: str = None,
        request_id: str = None,
        old_values: dict = None,
        new_values: dict = None,
        changes: dict = None,
        metadata: dict = None,
        severity: AuditSeverityEnum = AuditSeverityEnum.INFO,
        tenant_id: str = None
    ):
        """
        Create an audit log entry

        Args:
            db: Database session
            action: The action being logged
            user_id: ID of user performing action
            user_email: Email of user
            user_role: Role of user
            resource_type: Type of resource affected
            resource_id: ID of resource
            resource_name: Name of resource
            description: Human-readable description
            ip_address: IP address of request
            user_agent: User agent string
            request_id: Request tracking ID
            old_values: Previous state of data
            new_values: New state of data
            changes: Specific changed fields
            metadata: Additional context
            severity: Severity level
            tenant_id: Tenant ID for multi-tenant support
        """
        log_entry = cls(
            action=action,
            severity=severity,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            resource_name=resource_name,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            metadata=metadata,
            tenant_id=tenant_id
        )

        db.add(log_entry)
        db.commit()

        return log_entry
