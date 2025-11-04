#!/usr/bin/env python3
"""
Seed test data for development
Creates tenants, users, sites, plants, and assets
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
from app.core.security import get_password_hash
from datetime import datetime, timedelta
from decimal import Decimal

def seed_test_data():
    """Create comprehensive test data"""
    db: Session = next(get_db())
    
    try:
        # 1. Create or get tenant
        tenant = db.query(Tenant).filter(Tenant.id == "demo").first()
        if not tenant:
            tenant = Tenant(
                id="demo",
                name="Demo Tenant",
                status=TenantStatusEnum.ACTIVE,
                plan="professional",
                plan_expiry=datetime.utcnow() + timedelta(days=365)
            )
            db.add(tenant)
            db.commit()
            print("✅ Created tenant: demo")
        else:
            print("ℹ️  Tenant 'demo' already exists")
        
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
                email_verified=True
            )
            db.add(user)
            db.commit()
            print("✅ Created user: test@example.com / test123")
        else:
            print("ℹ️  User 'test@example.com' already exists")
            user.password_hash = get_password_hash("test123")
            db.commit()
        
        # 3. Create Sites
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
                Site.tenant_id == "demo",
                Site.code == site_data["code"]
            ).first()
            
            if not existing_site:
                site = Site(
                    tenant_id="demo",
                    **site_data
                )
                db.add(site)
                db.flush()
                created_sites.append(site)
                print(f"✅ Created site: {site.name} ({site.code})")
            else:
                created_sites.append(existing_site)
                print(f"ℹ️  Site '{site_data['code']}' already exists")
        
        db.commit()
        
        # 4. Create Plants
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
                "gse_integration": True,
                "tags": ["solar", "renewable", "north"],
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
                "gse_integration": True,
                "tags": ["solar", "renewable"],
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
                "tags": ["wind", "renewable"],
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
                "gse_integration": True,
                "tags": ["solar", "south"],
            },
            {
                "name": "Hydro Plant Delta",
                "code": "PLT-005",
                "power": "5.0 MW",
                "power_kw": 5000.0,
                "status": PlantStatusEnum.IN_OPERATION,
                "type": PlantTypeEnum.HYDROELECTRIC,
                "site_id": created_sites[1].id if len(created_sites) > 1 else None,
                "location": "Central River Station",
                "address": "Via Acqua 20",
                "municipality": "Rome",
                "province": "RM",
                "region": "Lazio",
                "latitude": 41.9100,
                "longitude": 12.5000,
                "tags": ["hydro", "renewable"],
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
                "tags": ["solar", "pending"],
            }
        ]
        
        created_plants = []
        for plant_data in plants_data:
            existing_plant = db.query(Plant).filter(
                Plant.tenant_id == "demo",
                Plant.code == plant_data["code"]
            ).first()
            
            if not existing_plant:
                plant = Plant(
                    tenant_id="demo",
                    created_by=user.id,
                    **plant_data
                )
                db.add(plant)
                db.flush()
                created_plants.append(plant)
                print(f"✅ Created plant: {plant.name} ({plant.code})")
            else:
                created_plants.append(existing_plant)
                print(f"ℹ️  Plant '{plant_data['code']}' already exists")
        
        db.commit()
        
        # 5. Create Asset Types
        asset_types_data = [
            {"name": "Solar Panel", "normalized_name": "solar_panel", "description": "Photovoltaic solar panel"},
            {"name": "Inverter", "normalized_name": "inverter", "description": "DC to AC power inverter"},
            {"name": "Battery", "normalized_name": "battery", "description": "Energy storage battery"},
            {"name": "Transformer", "normalized_name": "transformer", "description": "Power transformer"},
        ]
        
        created_asset_types = {}
        for at_data in asset_types_data:
            existing_at = db.query(AssetType).filter(
                AssetType.tenant_id == "demo",
                AssetType.normalized_name == at_data["normalized_name"]
            ).first()
            
            if not existing_at:
                asset_type = AssetType(
                    tenant_id="demo",
                    **at_data
                )
                db.add(asset_type)
                db.flush()
                created_asset_types[at_data["normalized_name"]] = asset_type
                print(f"✅ Created asset type: {asset_type.name}")
            else:
                created_asset_types[at_data["normalized_name"]] = existing_at
        
        db.commit()
        
        # 6. Create Assets
        if created_plants and created_asset_types:
            assets_data = []
            
            # Add solar panels for photovoltaic plants
            for plant in created_plants:
                if plant.type == PlantTypeEnum.PHOTOVOLTAIC:
                    # Add some solar panels
                    for i in range(1, 4):
                        assets_data.append({
                            "name": f"Panel Array {i}",
                            "plant_id": plant.id,
                            "asset_type_id": created_asset_types["solar_panel"].id,
                            "component_type": ComponentType.PANEL,
                            "status": AssetStatus.OPERATIONAL,
                            "manufacturer": "SunPower",
                            "model": "SPR-400",
                            "specifications": {"power_w": 400, "voltage_v": 40, "current_a": 10},
                        })
                    
                    # Add inverters
                    for i in range(1, 3):
                        assets_data.append({
                            "name": f"Inverter {i}",
                            "plant_id": plant.id,
                            "asset_type_id": created_asset_types["inverter"].id,
                            "component_type": ComponentType.INVERTER,
                            "status": AssetStatus.OPERATIONAL,
                            "manufacturer": "SMA",
                            "model": "Sunny Boy 5000",
                            "specifications": {"power_kw": 5.0, "efficiency": 98.5},
                        })
                
                elif plant.type == PlantTypeEnum.WIND:
                    # Add wind turbine components
                    assets_data.append({
                        "name": "Wind Turbine 1",
                        "plant_id": plant.id,
                        "asset_type_id": created_asset_types["transformer"].id,
                        "component_type": ComponentType.TRANSFORMER,
                        "status": AssetStatus.OPERATIONAL,
                        "manufacturer": "Vestas",
                        "model": "V150-3.0",
                        "specifications": {"power_mw": 3.0, "rotor_diameter_m": 150},
                    })
            
            for asset_data in assets_data:
                asset = Asset(
                    tenant_id="demo",
                    created_by=user.id,
                    **asset_data
                )
                db.add(asset)
            
            db.commit()
            print(f"✅ Created {len(assets_data)} assets")
        
        # 7. Create Storage Units for sites
        if created_sites:
            from app.models.site import StorageUnit
            storage_units_data = [
                {
                    "site_id": created_sites[0].id,
                    "name": "BESS Alpha",
                    "code": "BESS-001",
                    "capacity_kwh": 500.0,
                    "rated_power_kw": 250.0,
                    "chemistry_type": "Li-ion",
                    "efficiency": 95.0,
                    "status": "operational",
                    "manufacturer": "Tesla",
                    "model": "Megapack",
                },
                {
                    "site_id": created_sites[1].id,
                    "name": "BESS Beta",
                    "code": "BESS-002",
                    "capacity_kwh": 300.0,
                    "rated_power_kw": 150.0,
                    "chemistry_type": "Li-ion",
                    "efficiency": 93.0,
                    "status": "operational",
                    "manufacturer": "BYD",
                    "model": "Battery Box",
                }
            ]
            
            for su_data in storage_units_data:
                existing_su = db.query(StorageUnit).filter(
                    StorageUnit.tenant_id == "demo",
                    StorageUnit.code == su_data["code"]
                ).first()
                
                if not existing_su:
                    storage_unit = StorageUnit(
                        tenant_id="demo",
                        **su_data
                    )
                    db.add(storage_unit)
                    print(f"✅ Created storage unit: {storage_unit.name}")
            
            db.commit()
        
        # 8. Create Consumers for sites
        if created_sites:
            from app.models.site import Consumer
            consumers_data = [
                {
                    "site_id": created_sites[0].id,
                    "name": "Industrial Consumer A",
                    "code": "CONS-001",
                    "consumer_type": "industrial",
                    "average_consumption_kw": 150.0,
                    "peak_consumption_kw": 250.0,
                    "status": "active",
                    "pod_id": "IT001E12345678",
                },
                {
                    "site_id": created_sites[0].id,
                    "name": "Commercial Consumer B",
                    "code": "CONS-002",
                    "consumer_type": "commercial",
                    "average_consumption_kw": 50.0,
                    "peak_consumption_kw": 100.0,
                    "status": "active",
                    "pod_id": "IT001E12345679",
                },
                {
                    "site_id": created_sites[1].id,
                    "name": "Residential Consumer C",
                    "code": "CONS-003",
                    "consumer_type": "residential",
                    "average_consumption_kw": 5.0,
                    "peak_consumption_kw": 10.0,
                    "status": "active",
                    "pod_id": "IT001E12345680",
                }
            ]
            
            for cons_data in consumers_data:
                existing_cons = db.query(Consumer).filter(
                    Consumer.tenant_id == "demo",
                    Consumer.code == cons_data["code"]
                ).first()
                
                if not existing_cons:
                    consumer = Consumer(
                        tenant_id="demo",
                        **cons_data
                    )
                    db.add(consumer)
                    print(f"✅ Created consumer: {consumer.name}")
            
            db.commit()
        
        print("\n" + "="*60)
        print("🎉 Test data seeding completed!")
        print("="*60)
        print(f"✅ Tenant: demo")
        print(f"✅ User: test@example.com / test123")
        print(f"✅ Sites: {len(created_sites)}")
        print(f"✅ Plants: {len(created_plants)}")
        print(f"✅ Asset Types: {len(created_asset_types)}")
        print(f"✅ Assets: {len(assets_data) if 'assets_data' in locals() else 0}")
        print("\n💡 To seed CER data, run: python scripts/seed_cer_data.py")
        print("💡 To seed workflows, run: python scripts/seed_workflows.py")
        print("\nYou can now log in and see the data in the UI!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data()

