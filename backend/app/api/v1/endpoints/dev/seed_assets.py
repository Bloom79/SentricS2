"""
Seed assets for development testing
Split from monolithic dev.py for better maintainability
"""

from sqlalchemy.orm import Session
from typing import List, Dict

from app.models.user import User
from app.models.plant import PlantTypeEnum
from app.models.asset import Asset, AssetType, AssetStatus, ComponentType


def seed_assets(
    db: Session, user: User, plants: List[dict], asset_types: Dict[str, AssetType]
) -> dict:
    """
    Create test assets for plants

    Args:
        user: User to set as creator
        plants: List of plant dicts with id and type
        asset_types: Dict of asset types keyed by normalized_name

    Returns:
        dict: Results with asset info
    """
    results = {"assets": []}

    if not plants or not asset_types:
        return results

    assets_data = []

    # Create assets for all plants
    for plant_info in plants:
        plant_id = plant_info["id"]
        plant_type = plant_info.get("type")

        # Skip if we don't know the plant type
        if not plant_type:
            continue

        if plant_type == PlantTypeEnum.PHOTOVOLTAIC:
            # Create solar panel arrays
            for i in range(1, 4):
                assets_data.append(
                    {
                        "name": f"Panel Array {i}",
                        "plant_id": plant_id,
                        "type_id": asset_types["solar_panel"].id,
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
                        "plant_id": plant_id,
                        "type_id": asset_types["inverter"].id,
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
                    "plant_id": plant_id,
                    "type_id": asset_types["transformer"].id,
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
                    "plant_id": plant_id,
                    "type_id": asset_types["transformer"].id,
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
    return results
