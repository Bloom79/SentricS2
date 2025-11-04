#!/usr/bin/env python3
"""
Create test user for development
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_db
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.tenant import Tenant, TenantStatusEnum
from app.core.security import get_password_hash
from datetime import datetime, timedelta

def create_test_user():
    """Create test tenant and user"""
    db = next(get_db())
    
    try:
        # Check if tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == "demo").first()
        if not tenant:
            tenant = Tenant(
                id="demo",
                name="Demo Tenant",
                status=TenantStatusEnum.ACTIVE,
                plan="free",
                plan_expiry=datetime.utcnow() + timedelta(days=365)
            )
            db.add(tenant)
            db.commit()
            print("✅ Created tenant: demo")
        else:
            print("ℹ️  Tenant 'demo' already exists")
        
        # Check if user exists
        user = db.query(User).filter(User.email == "test@example.com").first()
        if not user:
            user = User(
                tenant_id="demo",
                name="Test User",
                email="test@example.com",
                password_hash=get_password_hash("test123"),
                role=UserRoleEnum.ADMIN,
                status=UserStatusEnum.ACTIVE,
                email_verified=True
            )
            db.add(user)
            db.commit()
            print("✅ Created user: test@example.com / test123")
        else:
            print("ℹ️  User 'test@example.com' already exists")
            # Update password in case it changed
            user.password_hash = get_password_hash("test123")
            db.commit()
            print("✅ Updated password")
        
        print("\n🎉 Test user ready!")
        print("   Email: test@example.com")
        print("   Password: test123")
        print("   Tenant: demo")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()


