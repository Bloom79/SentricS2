"""
Seed plants and asset types for development testing
Split from monolithic dev.py for better maintainability
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import json

from app.models.user import User
from app.models.site import Site
from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.asset import AssetType


def seed_asset_types(db: Session) -> dict:
    """
    Create standard asset types

    Returns:
        dict: Created asset types keyed by normalized_name
    """
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
    return created_asset_types


def seed_plants(db: Session, user: User, sites: List[Site]) -> tuple[dict, List[dict]]:
    """
    Create test plants

    Args:
        user: User to set as creator
        sites: List of sites to attach plants to

    Returns:
        tuple: (results dict, list of created plant info dicts with id and type)
    """
    results = {"plants": []}

    plants_data = [
        {
            "name": "Solar Array Alpha",
            "code": "PLT-001",
            "power": "2.5 MW",
            "power_kw": 2500.0,
            "status": PlantStatusEnum.IN_OPERATION,
            "type": PlantTypeEnum.PHOTOVOLTAIC,
            "site_id": sites[0].id if sites else None,
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
            "site_id": sites[0].id if sites else None,
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
            "site_id": sites[1].id if len(sites) > 1 else None,
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
            "site_id": sites[2].id if len(sites) > 2 else None,
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
            "site_id": sites[1].id if len(sites) > 1 else None,
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
            "site_id": sites[2].id if len(sites) > 2 else None,
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
            # Store plant info with type for asset creation
            created_plants.append({"id": plant_id, "type": plant_data["type"]})
            results["plants"].append(
                {"id": plant_id, "name": plant_dict["name"], "code": plant_dict["code"]}
            )

    db.commit()

    # If no plants were created, get existing plants
    if not created_plants:
        existing_plants = db.query(Plant).filter(Plant.tenant_id == "demo").all()
        created_plants = [{"id": p.id, "type": p.type} for p in existing_plants]

    return results, created_plants
