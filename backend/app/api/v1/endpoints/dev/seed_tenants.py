"""
Seed tenants and users for development testing
Split from monolithic dev.py for better maintainability
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.tenant import Tenant, TenantStatusEnum
from app.core.security import get_password_hash


def seed_tenant_and_user(db: Session) -> dict:
    """
    Create or get demo tenant and test user

    Returns:
        dict: Results with tenant and user info
    """
    results = {"tenant": None, "user": None}

    # 1. Create or get tenant
    tenant = db.query(Tenant).filter(Tenant.id == "demo").first()
    if not tenant:
        tenant = Tenant(
            id="demo",
            name="Demo Tenant",
            status=TenantStatusEnum.ACTIVE,
            plan="professional",
            plan_expiry=datetime.utcnow() + timedelta(days=365),
        )
        db.add(tenant)
        db.commit()
        results["tenant"] = {"id": tenant.id, "name": tenant.name}

    # 2. Create or get user
    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(
            tenant_id="demo",
            name="Test User",
            email="test@example.com",
            password_hash=get_password_hash("test123"),
            role=UserRoleEnum.ADMIN,
            status=UserStatusEnum.ACTIVE,
            email_verified=True,
        )
        db.add(user)
        db.commit()
        results["user"] = {"email": user.email, "name": user.name}

    # Always return the user for other seed functions
    if not user:
        user = db.query(User).filter(User.email == "test@example.com").first()

    return results, user
