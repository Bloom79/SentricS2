"""
Base models and mixins for multi-tenant support
Consolidated from Kronos EAM
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, event, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session

from app.core.database import Base


class TenantMixin:
    """Mixin to add tenant support to models"""

    @declared_attr
    def tenant_id(cls):
        return Column(String(50), nullable=False, index=True)


class TimestampMixin:
    """Mixin to add timestamp fields"""

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class SoftDeleteMixin:
    """Mixin to add soft delete support"""

    @declared_attr
    def deleted_at(cls):
        return Column(DateTime(timezone=True), nullable=True)

    @declared_attr
    def deleted_by(cls):
        return Column(Integer, nullable=True)

    def soft_delete(self, user_id: Optional[int] = None):
        """Soft delete the record"""
        self.deleted_at = datetime.utcnow()
        self.deleted_by = user_id


class AuditMixin(TimestampMixin):
    """Mixin to add audit fields"""

    @declared_attr
    def created_by(cls):
        return Column(Integer, nullable=True)

    @declared_attr
    def updated_by(cls):
        return Column(Integer, nullable=True)


class BaseModel(Base, TenantMixin, AuditMixin, SoftDeleteMixin):
    """Base model with all common fields"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def create(cls, db: Session, **kwargs):
        """Create new instance"""
        instance = cls(**kwargs)
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance

    def update(self, db: Session, **kwargs):
        """Update instance"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.commit()
        db.refresh(self)
        return self

    def delete(self, db: Session, soft: bool = True, user_id: Optional[int] = None):
        """Delete instance (soft or hard)"""
        if soft and hasattr(self, "soft_delete"):
            self.soft_delete(user_id)
            db.commit()
        else:
            db.delete(self)
            db.commit()


# Event listeners for automatic tenant assignment
@event.listens_for(Session, "before_flush")
def receive_before_flush(session, flush_context, instances):
    """
    Automatically set tenant_id on new instances if not set
    """
    for instance in session.new:
        if isinstance(instance, BaseModel) and not instance.tenant_id:
            # Get tenant from session context if available
            tenant_id = getattr(session, "tenant_id", None)
            if tenant_id:
                instance.tenant_id = tenant_id
