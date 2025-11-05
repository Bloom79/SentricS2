"""
Tenant models
Consolidated from Kronos EAM
"""

from sqlalchemy import Column, String, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base
from app.models.base import TimestampMixin


class TenantStatusEnum(str, enum.Enum):
    """Tenant status"""

    ACTIVE = "Active"
    SUSPENDED = "Suspended"
    EXPIRED = "Expired"


class Tenant(Base, TimestampMixin):
    """Tenant model"""

    __tablename__ = "tenants"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    status = Column(Enum(TenantStatusEnum), nullable=False, default=TenantStatusEnum.ACTIVE)

    # Subscription
    plan = Column(String(50), default="free")  # free, professional, enterprise
    plan_expiry = Column(DateTime)

    # Settings
    settings = Column(JSON, default=dict)

    # Relationships
    users = relationship(
        "User",
        back_populates="tenant",
        foreign_keys="[User.tenant_id]",
        primaryjoin="Tenant.id == foreign(User.tenant_id)",
    )
    plants = relationship(
        "Plant",
        back_populates="tenant",
        foreign_keys="[Plant.tenant_id]",
        primaryjoin="Tenant.id == foreign(Plant.tenant_id)",
    )

    def __repr__(self):
        return f"<Tenant {self.id}: {self.name}>"
