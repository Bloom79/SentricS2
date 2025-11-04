#!/usr/bin/env python3
"""
Seed data with authenticated user connection
Creates seed data that is properly linked to the authenticated user
This ensures data belongs to the correct tenant and user
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.tenant import Tenant, TenantStatusEnum
from app.models.site import Site, SiteTypeEnum, SiteStatusEnum
from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.asset import Asset, AssetType, AssetStatus, ComponentType
from app.models.workflow import Workflow, WorkflowPhase, WorkflowStatusEnum, WorkflowTypeEnum
from app.models.workflow_template import WorkflowTemplate, WorkflowTemplatePhase
from app.core.security import get_password_hash
from datetime import datetime, timedelta
from decimal import Decimal
import argparse

def get_or_create_tenant(db: Session, tenant_id: str = "demo", tenant_name: str = "Demo Tenant"):
    """Get or create tenant"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        tenant = Tenant(
            id=tenant_id,
            name=tenant_name,
            status=TenantStatusEnum.ACTIVE,
            plan="professional",
            plan_expiry=datetime.utcnow() + timedelta(days=365)
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        print(f"✅ Created tenant: {tenant_id}")
    return tenant

def get_or_create_user(db: Session, tenant_id: str, email: str, name: str, 
                       password: str = None, role: UserRoleEnum = UserRoleEnum.ADMIN):
    """Get or create user, linking to tenant"""
    user = db.query(User).filter(
        User.email == email,
        User.tenant_id == tenant_id
    ).first()
    
    if not user:
        # Use provided password or generate a secure one
        if not password:
            password = "ChangeMe123!"  # Must be changed after first login
        
        user = User(
            tenant_id=tenant_id,
            name=name,
            email=email,
            password_hash=get_password_hash(password),
            role=role,
            status=UserStatusEnum.ACTIVE,
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created user: {email} (password: {password})")
        print(f"   ⚠️  IMPORTANT: Change password after first login!")
    else:
        # Update password if provided
        if password:
            user.password_hash = get_password_hash(password)
            db.commit()
            print(f"✅ Updated password for user: {email}")
        else:
            print(f"ℹ️  User '{email}' already exists")
    
    return user

def seed_data_for_user(db: Session, tenant_id: str, user_id: int):
    """Seed all data linked to the authenticated user"""
    print(f"\n📦 Seeding data for tenant '{tenant_id}', user ID: {user_id}")
    
    # Get or create sites
    sites_data = [
        {
            "name": "Solar Park North",
            "code": "SPN-001",
            "site_type": SiteTypeEnum.INDUSTRIAL,
            "status": "active",
            "location": "Northern Italy",
            "city": "Milan",
            "province": "MI",
            "region": "Lombardy",
            "country": "Italy",
            "latitude": 45.4642,
            "longitude": 9.1900,
            "capacity": 5000.0,
            "efficiency": 85.5,
        },
        {
            "name": "Wind Farm Central",
            "code": "WFC-001",
            "site_type": SiteTypeEnum.INDUSTRIAL,
            "status": "active",
            "location": "Central Italy",
            "city": "Rome",
            "province": "RM",
            "region": "Lazio",
            "country": "Italy",
            "latitude": 41.9028,
            "longitude": 12.4964,
            "capacity": 3000.0,
            "efficiency": 78.2,
        },
        {
            "name": "Solar Complex South",
            "code": "SCS-001",
            "site_type": SiteTypeEnum.COMMERCIAL,
            "status": "active",
            "location": "Southern Italy",
            "city": "Naples",
            "province": "NA",
            "region": "Campania",
            "country": "Italy",
            "latitude": 40.8518,
            "longitude": 14.2681,
            "capacity": 2500.0,
            "efficiency": 82.0,
        }
    ]
    
    created_sites = []
    for site_data in sites_data:
        existing_site = db.query(Site).filter(
            Site.tenant_id == tenant_id,
            Site.code == site_data["code"]
        ).first()
        
        if not existing_site:
            site = Site(
                tenant_id=tenant_id,
                created_by=user_id,
                **site_data
            )
            db.add(site)
            db.flush()
            created_sites.append(site)
            print(f"  ✅ Created site: {site.name}")
        else:
            created_sites.append(existing_site)
    
    db.commit()
    
    # Get or create plants
    plants_data = [
        {
            "name": "Solar Array Alpha",
            "code": "PLT-001",
            "power": "2.5 MW",
            "power_kw": 2500.0,
            "status": PlantStatusEnum.IN_OPERATION,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "site_id": created_sites[0].id if created_sites else None,
            "location": "Solar Park North - Zone A",
            "address": "Via Solare 1",
            "municipality": "Milan",
            "province": "MI",
            "region": "Lombardy",
            "latitude": 45.4642,
            "longitude": 9.1900,
        },
        {
            "name": "Solar Array Beta",
            "code": "PLT-002",
            "power": "1.8 MW",
            "power_kw": 1800.0,
            "status": PlantStatusEnum.IN_OPERATION,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "site_id": created_sites[0].id if created_sites else None,
            "location": "Solar Park North - Zone B",
            "address": "Via Solare 2",
            "municipality": "Milan",
            "province": "MI",
            "region": "Lombardy",
            "latitude": 45.4650,
            "longitude": 9.1910,
        },
        {
            "name": "Wind Turbine Cluster 1",
            "code": "PLT-003",
            "power": "3.0 MW",
            "power_kw": 3000.0,
            "status": PlantStatusEnum.IN_OPERATION,
            "type": PlantTypeEnum.WIND,
            "site_id": created_sites[1].id if len(created_sites) > 1 else None,
            "location": "Wind Farm Central - Sector 1",
            "address": "Via Vento 10",
            "municipality": "Rome",
            "province": "RM",
            "region": "Lazio",
            "latitude": 41.9028,
            "longitude": 12.4964,
        },
        {
            "name": "Solar Farm Gamma",
            "code": "PLT-004",
            "power": "1.2 MW",
            "power_kw": 1200.0,
            "status": PlantStatusEnum.IN_OPERATION,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "site_id": created_sites[2].id if len(created_sites) > 2 else None,
            "location": "Solar Complex South - Block 1",
            "address": "Via Sole 5",
            "municipality": "Naples",
            "province": "NA",
            "region": "Campania",
            "latitude": 40.8518,
            "longitude": 14.2681,
        },
        {
            "name": "Hydro Plant Delta",
            "code": "PLT-005",
            "power": "5.0 MW",
            "power_kw": 5000.0,
            "status": PlantStatusEnum.IN_OPERATION,
            "type": PlantTypeEnum.HYDROELECTRIC,
            "site_id": created_sites[0].id if created_sites else None,
            "location": "Central River Station",
            "address": "Via Acqua 20",
            "municipality": "Milan",
            "province": "MI",
            "region": "Lombardy",
            "latitude": 45.4700,
            "longitude": 9.2000,
        },
        {
            "name": "Solar Array Epsilon",
            "code": "PLT-006",
            "power": "0.8 MW",
            "power_kw": 800.0,
            "status": PlantStatusEnum.IN_AUTHORIZATION,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "site_id": created_sites[2].id if len(created_sites) > 2 else None,
            "location": "Solar Complex South - Block 2",
            "address": "Via Sole 6",
            "municipality": "Naples",
            "province": "NA",
            "region": "Campania",
            "latitude": 40.8520,
            "longitude": 14.2685,
        }
    ]
    
    created_plants = []
    for plant_data in plants_data:
        existing_plant = db.query(Plant).filter(
            Plant.tenant_id == tenant_id,
            Plant.code == plant_data["code"]
        ).first()
        
        if not existing_plant:
            plant = Plant(
                tenant_id=tenant_id,
                created_by=user_id,
                **plant_data
            )
            db.add(plant)
            db.flush()
            created_plants.append(plant)
            print(f"  ✅ Created plant: {plant.name} ({plant.code})")
        else:
            created_plants.append(existing_plant)
    
    db.commit()
    
    print(f"\n✅ Seeded {len(created_sites)} sites and {len(created_plants)} plants")
    return created_plants

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Seed data for authenticated user')
    parser.add_argument('--tenant-id', type=str, default='demo', help='Tenant ID')
    parser.add_argument('--tenant-name', type=str, default='Demo Tenant', help='Tenant name')
    parser.add_argument('--user-email', type=str, required=True, help='User email (will be created if not exists)')
    parser.add_argument('--user-name', type=str, required=True, help='User name')
    parser.add_argument('--user-password', type=str, help='User password (if not provided, will use ChangeMe123!)')
    parser.add_argument('--user-role', type=str, default='Admin', choices=['Admin', 'Asset Manager', 'Plant Owner', 'Operator', 'Viewer'])
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Kronos EAM - Seed Data for Authenticated User")
    print("=" * 60)
    print()
    print(f"Tenant ID: {args.tenant_id}")
    print(f"User Email: {args.user_email}")
    print(f"User Name: {args.user_name}")
    print()
    
    db: Session = next(get_db())
    
    try:
        # 1. Get or create tenant
        tenant = get_or_create_tenant(db, args.tenant_id, args.tenant_name)
        
        # 2. Get or create user (this is the authenticated user)
        user = get_or_create_user(
            db=db,
            tenant_id=args.tenant_id,
            email=args.user_email,
            name=args.user_name,
            password=args.user_password,
            role=UserRoleEnum[args.user_role.upper().replace(' ', '_')]
        )
        
        # 3. Seed data linked to this user
        plants = seed_data_for_user(db, args.tenant_id, user.id)
        
        print()
        print("=" * 60)
        print("✅ Seed data complete!")
        print("=" * 60)
        print()
        print(f"Tenant: {tenant.name} ({tenant.id})")
        print(f"User: {user.name} ({user.email})")
        print(f"Plants created: {len(plants)}")
        print()
        print("⚠️  IMPORTANT:")
        if not args.user_password:
            print(f"  - User password: ChangeMe123!")
        print("  - Change password after first login")
        print("  - All data is linked to this user and tenant")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()

