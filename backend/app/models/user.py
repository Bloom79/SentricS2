"""
User models with multi-tenant support
Consolidated from Kronos EAM
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel
from app.core.security import get_password_hash


class UserRoleEnum(str, enum.Enum):
    """User roles"""
    ADMIN = "Admin"
    ASSET_MANAGER = "Asset Manager"
    PLANT_OWNER = "Plant Owner"
    OPERATOR = "Operator"
    VIEWER = "Viewer"


class UserStatusEnum(str, enum.Enum):
    """User status"""
    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    INVITED = "Invited"


class User(BaseModel):
    """User model with multi-tenant support"""
    __tablename__ = "users"
    
    # Basic info
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Role and permissions
    role = Column(Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.VIEWER)
    permissions = Column(JSON, default=list)
    
    # Status
    status = Column(Enum(UserStatusEnum), nullable=False, default=UserStatusEnum.INVITED)
    email_verified = Column(Boolean, default=False)
    
    # Access control
    last_access = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    
    # Multi-factor authentication
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(100))
    
    # Profile
    phone = Column(String(50))
    avatar_url = Column(String(500))
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="Europe/Rome")
    
    # Plant access (JSON array of plant IDs)
    authorized_plants = Column(JSON, default=list)
    
    # Preferences
    preferences = Column(JSON, default=dict)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users", foreign_keys="[User.tenant_id]", primaryjoin="User.tenant_id == Tenant.id", lazy='select')
    cer_members = relationship("CERMember", back_populates="user")
    cer_participation_requests = relationship("CERParticipationRequest", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    @property
    def password(self):
        raise AttributeError("Password is not readable")
    
    @password.setter
    def password(self, password: str):
        """Set password with validation"""
        from app.core.password_validator import validate_password_strength

        # Validate password strength
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            raise ValueError(f"Password does not meet security requirements: {'; '.join(errors)}")

        self.password_hash = get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Verify password"""
        from app.core.security import verify_password
        return verify_password(password, self.password_hash)

    @property
    def is_active(self) -> bool:
        """Check if user is active"""
        return self.status == UserStatusEnum.ACTIVE

