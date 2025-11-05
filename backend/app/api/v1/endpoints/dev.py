"""
Development endpoints for seeding test data
ONLY ENABLE IN DEVELOPMENT MODE
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.tenant import Tenant, TenantStatusEnum
from app.models.site import Site, SiteTypeEnum
from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.asset import Asset, AssetType, AssetStatus, ComponentType
from app.models.site import StorageUnit, Consumer
from app.models.cer import CER, CERMember, CERLegalType, CERStatus, CERType
from app.core.geography import create_point, create_polygon
from app.core.security import get_password_hash
from datetime import datetime, timedelta
from sqlalchemy import text
import json

router = APIRouter()


@router.post("/seed", tags=["development"])
async def seed_test_data(db: Session = Depends(get_db)):
    """
    Seed test data for development
    Creates: tenant, user, sites, plants, assets, storage units, consumers
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=403, detail="Only available in development mode")

    try:
        results = {
            "tenant": None,
            "user": None,
            "sites": [],
            "plants": [],
            "assets": [],
            "storage_units": [],
            "consumers": [],
            "cers": [],
            "cer_members": [],
        }

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
            },
        ]

        created_sites = []
        for site_data in sites_data:
            existing_site = (
                db.query(Site)
                .filter(Site.tenant_id == "demo", Site.code == site_data["code"])
                .first()
            )

            if not existing_site:
                site = Site(tenant_id="demo", **site_data)
                db.add(site)
                db.flush()
                created_sites.append(site)
                results["sites"].append({"id": site.id, "name": site.name, "code": site.code})

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
            },
        ]

        created_plants = []
        for plant_data in plants_data:
            # Remove site_id from plant_data since column doesn't exist yet
            plant_dict = {k: v for k, v in plant_data.items() if k != "site_id"}

            # Check if plant exists using raw SQL to avoid site_id column issue
            existing_count = db.execute(
                text("SELECT COUNT(*) FROM plants WHERE tenant_id = :tenant_id AND code = :code"),
                {"tenant_id": "demo", "code": plant_dict["code"]},
            ).scalar()

            if existing_count == 0:
                # Create plant using raw SQL insert to avoid site_id column issue
                result = db.execute(
                    text(
                        """
                        INSERT INTO plants 
                        (name, code, power, power_kw, status, type, location, address, municipality, 
                         province, region, latitude, longitude, gse_integration, tags, tenant_id, created_by, created_at)
                        VALUES 
                        (:name, :code, :power, :power_kw, :status, :type, :location, :address, :municipality,
                         :province, :region, :latitude, :longitude, :gse_integration, :tags, :tenant_id, :created_by, NOW())
                        RETURNING id
                    """
                    ),
                    {
                        "name": plant_dict["name"],
                        "code": plant_dict["code"],
                        "power": plant_dict["power"],
                        "power_kw": plant_dict["power_kw"],
                        "status": (
                            plant_dict["status"].value
                            if hasattr(plant_dict["status"], "value")
                            else str(plant_dict["status"])
                        ),
                        "type": (
                            plant_dict["type"].value
                            if hasattr(plant_dict["type"], "value")
                            else str(plant_dict["type"])
                        ),
                        "location": plant_dict["location"],
                        "address": plant_dict.get("address"),
                        "municipality": plant_dict.get("municipality"),
                        "province": plant_dict.get("province"),
                        "region": plant_dict.get("region"),
                        "latitude": plant_dict.get("latitude"),
                        "longitude": plant_dict.get("longitude"),
                        "gse_integration": plant_dict.get("gse_integration", False),
                        "tags": json.dumps(plant_dict.get("tags", [])),
                        "tenant_id": "demo",
                        "created_by": user.id,
                    },
                )
                plant_id = result.scalar()
                db.flush()
                # Store plant info without reloading (to avoid site_id column issue)
                created_plants.append({"id": plant_id})  # Store minimal info
                results["plants"].append(
                    {"id": plant_id, "name": plant_dict["name"], "code": plant_dict["code"]}
                )

        db.commit()

        # 5. Create Asset Types
        asset_types_data = [
            {
                "name": "Solar Panel",
                "normalized_name": "solar_panel",
                "description": "Photovoltaic solar panel",
            },
            {
                "name": "Inverter",
                "normalized_name": "inverter",
                "description": "DC to AC power inverter",
            },
            {
                "name": "Battery",
                "normalized_name": "battery",
                "description": "Energy storage battery",
            },
            {
                "name": "Transformer",
                "normalized_name": "transformer",
                "description": "Power transformer",
            },
        ]

        created_asset_types = {}
        for at_data in asset_types_data:
            existing_at = (
                db.query(AssetType)
                .filter(
                    AssetType.tenant_id == "demo",
                    AssetType.normalized_name == at_data["normalized_name"],
                )
                .first()
            )

            if not existing_at:
                asset_type = AssetType(tenant_id="demo", **at_data)
                db.add(asset_type)
                db.flush()
                created_asset_types[at_data["normalized_name"]] = asset_type
            else:
                # Use existing asset type
                created_asset_types[at_data["normalized_name"]] = existing_at

        db.commit()

        # 6. Create Assets
        # Get all existing plants if we didn't create new ones
        if not created_plants:
            existing_plants = db.query(Plant).filter(Plant.tenant_id == "demo").all()
            created_plants = [{"id": p.id} for p in existing_plants]
            # Map plant IDs to their types from database
            plant_id_to_type = {p.id: p.type for p in existing_plants}
        else:
            # For newly created plants, get types from plants_data
            plant_id_to_type = {}
            for idx, plant_info in enumerate(created_plants):
                if idx < len(plants_data):
                    plant_id_to_type[plant_info["id"]] = plants_data[idx].get("type")

        if created_plants and created_asset_types:
            assets_data = []

            # Create assets for all plants
            for plant_info in created_plants:
                plant_id = plant_info["id"]
                plant_type = plant_id_to_type.get(plant_id)

                # Skip if we don't know the plant type
                if not plant_type:
                    continue

                if plant_type == PlantTypeEnum.PHOTOVOLTAIC:
                    # Create solar panel arrays
                    for i in range(1, 4):
                        assets_data.append(
                            {
                                "name": f"Panel Array {i}",
                                "plant_id": plant_info["id"],
                                "type_id": created_asset_types["solar_panel"].id,
                                "component_type": ComponentType.PANEL.value,
                                "status": AssetStatus.OPERATIONAL.value,
                                "manufacturer": "SunPower",
                                "model": "SPR-400",
                                "rated_power": 0.4,  # kW per panel, array of ~100 panels = 40kW
                                "voltage": 40.0,
                                "current": 10.0,
                                "efficiency": 22.8,
                                "location": f"Zone {chr(64+i)}",
                                "dynamic_attributes": {
                                    "power_w": 400,
                                    "voltage_v": 40,
                                    "current_a": 10,
                                    "panels_count": 100,
                                },
                            }
                        )

                    # Create inverters
                    for i in range(1, 3):
                        assets_data.append(
                            {
                                "name": f"Inverter {i}",
                                "plant_id": plant_info["id"],
                                "type_id": created_asset_types["inverter"].id,
                                "component_type": ComponentType.INVERTER.value,
                                "status": AssetStatus.OPERATIONAL.value,
                                "manufacturer": "SMA",
                                "model": "Sunny Boy 5000",
                                "rated_power": 5.0,  # kW
                                "efficiency": 98.5,
                                "location": f"Inverter Station {i}",
                                "dynamic_attributes": {
                                    "power_kw": 5.0,
                                    "efficiency": 98.5,
                                    "mppt_trackers": 2,
                                },
                            }
                        )

                elif plant_type == PlantTypeEnum.WIND:
                    assets_data.append(
                        {
                            "name": "Wind Turbine 1",
                            "plant_id": plant_info["id"],
                            "type_id": created_asset_types["transformer"].id,
                            "component_type": ComponentType.TRANSFORMER.value,
                            "status": AssetStatus.OPERATIONAL.value,
                            "manufacturer": "Vestas",
                            "model": "V150-3.0",
                            "rated_power": 3000.0,  # kW
                            "location": "Turbine Field - Position 1",
                            "dynamic_attributes": {
                                "power_mw": 3.0,
                                "rotor_diameter_m": 150,
                                "hub_height_m": 105,
                            },
                        }
                    )

                elif plant_type == PlantTypeEnum.HYDROELECTRIC:
                    assets_data.append(
                        {
                            "name": "Hydro Generator 1",
                            "plant_id": plant_info["id"],
                            "type_id": created_asset_types["transformer"].id,
                            "component_type": ComponentType.TRANSFORMER.value,
                            "status": AssetStatus.OPERATIONAL.value,
                            "manufacturer": "Andritz",
                            "model": "HydroGen-5000",
                            "rated_power": 5000.0,  # kW
                            "efficiency": 92.0,
                            "location": "Main Turbine Hall",
                            "dynamic_attributes": {
                                "power_mw": 5.0,
                                "flow_rate_m3s": 50,
                                "head_m": 100,
                            },
                        }
                    )

            # Only create assets that don't already exist
            for asset_data in assets_data:
                # Check if asset already exists
                existing_asset = (
                    db.query(Asset)
                    .filter(
                        Asset.tenant_id == "demo",
                        Asset.plant_id == asset_data["plant_id"],
                        Asset.name == asset_data["name"],
                    )
                    .first()
                )

                if not existing_asset:
                    asset = Asset(tenant_id="demo", created_by=user.id, **asset_data)
                    db.add(asset)
                    db.flush()
                    results["assets"].append({"id": asset.id, "name": asset.name})

            db.commit()

        # 7. Create Storage Units
        if created_sites:
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
                },
            ]

            for su_data in storage_units_data:
                existing_su = (
                    db.query(StorageUnit)
                    .filter(StorageUnit.tenant_id == "demo", StorageUnit.code == su_data["code"])
                    .first()
                )

                if not existing_su:
                    storage_unit = StorageUnit(tenant_id="demo", **su_data)
                    db.add(storage_unit)
                    db.flush()
                    results["storage_units"].append(
                        {"id": storage_unit.id, "name": storage_unit.name}
                    )

            db.commit()

        # 8. Create Consumers
        if created_sites:
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
                },
            ]

            for cons_data in consumers_data:
                existing_cons = (
                    db.query(Consumer)
                    .filter(Consumer.tenant_id == "demo", Consumer.code == cons_data["code"])
                    .first()
                )

                if not existing_cons:
                    consumer = Consumer(tenant_id="demo", **cons_data)
                    db.add(consumer)
                    db.flush()
                    results["consumers"].append({"id": consumer.id, "name": consumer.name})

            db.commit()

        # 9. Create CERs (Renewable Energy Communities)
        if created_plants:
            cers_data = [
                {
                    "name": "Green Energy Community Milano",
                    "description": "Renewable energy community in Northern Italy",
                    "legal_type": CERLegalType.COOPERATIVE,
                    "type": CERType.ACTIVE,
                    "status": CERStatus.ACTIVE,
                    "address": "Via Solare 1, Milan",
                    "region": "Lombardy",
                    "province": "MI",
                    "municipality": "Milan",
                    "primary_substation_id": "PS-MIL-001",
                    "location": [9.1900, 45.4642],  # [lon, lat]
                    "boundary": [
                        [9.18, 45.45],
                        [9.20, 45.45],
                        [9.20, 45.48],
                        [9.18, 45.48],
                        [9.18, 45.45],
                    ],
                    "technical_info": {"total_capacity_kw": 4300.0},
                    "billing_settings": {"tariff_type": "standard"},
                },
                {
                    "name": "Solar Community Lazio",
                    "description": "Community energy project in Central Italy",
                    "legal_type": CERLegalType.ASSOCIATION,
                    "type": CERType.ACTIVE,
                    "status": CERStatus.ACTIVE,
                    "address": "Via Vento 10, Rome",
                    "region": "Lazio",
                    "province": "RM",
                    "municipality": "Rome",
                    "primary_substation_id": "PS-ROM-001",
                    "location": [12.4964, 41.9028],
                    "boundary": [
                        [12.48, 41.89],
                        [12.51, 41.89],
                        [12.51, 41.92],
                        [12.48, 41.92],
                        [12.48, 41.89],
                    ],
                    "technical_info": {"total_capacity_kw": 8000.0},
                    "billing_settings": {"tariff_type": "premium"},
                },
                {
                    "name": "Campania Energy Cooperative",
                    "description": "Southern Italy renewable energy cooperative",
                    "legal_type": CERLegalType.COOPERATIVE,
                    "type": CERType.ACTIVE,
                    "status": CERStatus.PENDING,
                    "address": "Via Sole 5, Naples",
                    "region": "Campania",
                    "province": "NA",
                    "municipality": "Naples",
                    "primary_substation_id": "PS-NAP-001",
                    "location": [14.2681, 40.8518],
                    "boundary": [
                        [14.26, 40.84],
                        [14.28, 40.84],
                        [14.28, 40.86],
                        [14.26, 40.86],
                        [14.26, 40.84],
                    ],
                    "technical_info": {"total_capacity_kw": 2000.0},
                    "billing_settings": {"tariff_type": "standard"},
                },
            ]

            created_cers = []
            for cer_data in cers_data:
                existing_cer = (
                    db.query(CER)
                    .filter(CER.tenant_id == "demo", CER.name == cer_data["name"])
                    .first()
                )

                if not existing_cer:
                    # Create location point
                    location_wkt = None
                    if cer_data.get("location"):
                        location_wkt = create_point(
                            cer_data["location"][0], cer_data["location"][1]
                        )

                    # Create boundary polygon
                    boundary_wkt = None
                    if cer_data.get("boundary"):
                        boundary_wkt = create_polygon(cer_data["boundary"])

                    cer = CER(
                        tenant_id="demo",
                        created_by=user.id,
                        name=cer_data["name"],
                        description=cer_data["description"],
                        legal_type=cer_data["legal_type"],
                        type=cer_data["type"],
                        status=cer_data["status"],
                        address=cer_data["address"],
                        region=cer_data["region"],
                        province=cer_data["province"],
                        municipality=cer_data["municipality"],
                        primary_substation_id=cer_data["primary_substation_id"],
                        location=location_wkt,
                        boundary=boundary_wkt,
                        technical_info=cer_data.get("technical_info", {}),
                        billing_settings=cer_data.get("billing_settings", {}),
                        total_capacity=cer_data.get("technical_info", {}).get(
                            "total_capacity_kw", 0.0
                        ),
                    )
                    db.add(cer)
                    db.flush()
                    created_cers.append(cer)
                    results["cers"].append({"id": cer.id, "name": cer.name})

            db.commit()

            # 10. Link plants to CERs
            if created_cers and created_plants:
                # Link first 2 plants to first CER
                for i, plant_info in enumerate(created_plants[:2]):
                    if i < len(created_cers):
                        db.execute(
                            text("UPDATE plants SET cer_id = :cer_id WHERE id = :plant_id"),
                            {"cer_id": created_cers[0].id, "plant_id": plant_info["id"]},
                        )

                # Link next 2 plants to second CER
                for i, plant_info in enumerate(created_plants[2:4]):
                    if i < len(created_cers):
                        db.execute(
                            text("UPDATE plants SET cer_id = :cer_id WHERE id = :plant_id"),
                            {"cer_id": created_cers[1].id, "plant_id": plant_info["id"]},
                        )

                db.commit()

            # 11. Create CER Members
            if created_cers:
                members_data = [
                    {
                        "cer_id": created_cers[0].id,
                        "name": "Consumer Member A",
                        "address": "Via Milano 1, Milan",
                        "member_type": "consumer",
                        "pod_id": "IT001E12345681",
                        "load_profile_type": "residential",
                        "contracted_power": 3.0,
                        "status": "active",
                    },
                    {
                        "cer_id": created_cers[0].id,
                        "name": "Producer Member B",
                        "address": "Via Milano 2, Milan",
                        "member_type": "producer",
                        "pod_id": "IT001E12345682",
                        "load_profile_type": "commercial",
                        "contracted_power": 5.0,
                        "status": "active",
                    },
                    {
                        "cer_id": created_cers[0].id,
                        "name": "Prosumer Member C",
                        "address": "Via Milano 3, Milan",
                        "member_type": "prosumer",
                        "pod_id": "IT001E12345683",
                        "load_profile_type": "residential",
                        "contracted_power": 4.5,
                        "status": "active",
                    },
                    {
                        "cer_id": created_cers[1].id,
                        "name": "Consumer Member D",
                        "address": "Via Roma 1, Rome",
                        "member_type": "consumer",
                        "pod_id": "IT001E12345684",
                        "load_profile_type": "residential",
                        "contracted_power": 2.5,
                        "status": "active",
                    },
                    {
                        "cer_id": created_cers[1].id,
                        "name": "Producer Member E",
                        "address": "Via Roma 2, Rome",
                        "member_type": "producer",
                        "pod_id": "IT001E12345685",
                        "load_profile_type": "industrial",
                        "contracted_power": 10.0,
                        "status": "active",
                    },
                    {
                        "cer_id": created_cers[2].id,
                        "name": "Consumer Member F",
                        "address": "Via Napoli 1, Naples",
                        "member_type": "consumer",
                        "pod_id": "IT001E12345686",
                        "load_profile_type": "residential",
                        "contracted_power": 2.0,
                        "status": "active",
                    },
                ]

                for member_data in members_data:
                    existing_member = (
                        db.query(CERMember)
                        .filter(
                            CERMember.tenant_id == "demo", CERMember.pod_id == member_data["pod_id"]
                        )
                        .first()
                    )

                    if not existing_member:
                        member = CERMember(tenant_id="demo", created_by=user.id, **member_data)
                        db.add(member)
                        db.flush()
                        results["cer_members"].append(
                            {"id": member.id, "name": member.name, "cer_id": member.cer_id}
                        )

                db.commit()

                # Update CER total capacity from linked plants
                for cer in created_cers:
                    total_capacity = (
                        db.execute(
                            text(
                                "SELECT COALESCE(SUM(power_kw), 0) FROM plants WHERE cer_id = :cer_id AND deleted_at IS NULL"
                            ),
                            {"cer_id": cer.id},
                        ).scalar()
                        or 0.0
                    )

                    cer.total_capacity = total_capacity
                    db.commit()

        return {
            "success": True,
            "message": "Test data seeded successfully",
            "results": results,
            "summary": {
                "sites": len(results["sites"]),
                "plants": len(results["plants"]),
                "assets": len(results["assets"]),
                "storage_units": len(results["storage_units"]),
                "consumers": len(results["consumers"]),
                "cers": len(results["cers"]),
                "cer_members": len(results["cer_members"]),
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding test data: {str(e)}")
