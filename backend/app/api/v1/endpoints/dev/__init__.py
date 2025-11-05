"""
Development endpoints for seeding test data
Split from monolithic dev.py (850 lines) into focused modules

Modules:
- seed_tenants.py: Tenant and user creation
- seed_sites.py: Sites, storage units, consumers
- seed_plants.py: Plants and asset types
- seed_assets.py: Assets for plants
- seed_cer.py: CERs, members, plant linking

ONLY ENABLE IN DEVELOPMENT MODE
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings

from .seed_tenants import seed_tenant_and_user
from .seed_sites import seed_sites, seed_storage_units, seed_consumers
from .seed_plants import seed_asset_types, seed_plants
from .seed_assets import seed_assets
from .seed_cer import seed_cers, link_plants_to_cers, seed_cer_members, update_cer_capacities


router = APIRouter()


@router.post("/seed", tags=["development"])
async def seed_test_data(db: Session = Depends(get_db)):
    """
    Seed comprehensive test data for development
    Creates: tenant, user, sites, plants, assets, storage units, consumers, CERs, members
    """
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=403, detail="Only available in development mode")

    try:
        # Initialize results
        all_results = {
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

        # 1. Create tenant and user
        tenant_results, user = seed_tenant_and_user(db)
        all_results.update(tenant_results)

        # 2. Create sites
        sites_results, created_sites = seed_sites(db)
        all_results["sites"] = sites_results["sites"]

        # 3. Create storage units and consumers for sites
        if created_sites:
            storage_results = seed_storage_units(db, created_sites)
            all_results["storage_units"] = storage_results["storage_units"]

            consumer_results = seed_consumers(db, created_sites)
            all_results["consumers"] = consumer_results["consumers"]

        # 4. Create asset types
        asset_types = seed_asset_types(db)

        # 5. Create plants
        plants_results, created_plants = seed_plants(db, user, created_sites)
        all_results["plants"] = plants_results["plants"]

        # 6. Create assets for plants
        if created_plants and asset_types:
            assets_results = seed_assets(db, user, created_plants, asset_types)
            all_results["assets"] = assets_results["assets"]

        # 7. Create CERs
        if created_plants:
            cers_results, created_cers = seed_cers(db, user, created_plants)
            all_results["cers"] = cers_results["cers"]

            # 8. Link plants to CERs
            if created_cers:
                link_plants_to_cers(db, created_cers, created_plants)

                # 9. Create CER members
                members_results = seed_cer_members(db, user, created_cers)
                all_results["cer_members"] = members_results["cer_members"]

                # 10. Update CER capacities from linked plants
                update_cer_capacities(db, created_cers)

        return {
            "success": True,
            "message": "Test data seeded successfully",
            "results": all_results,
            "summary": {
                "sites": len(all_results["sites"]),
                "plants": len(all_results["plants"]),
                "assets": len(all_results["assets"]),
                "storage_units": len(all_results["storage_units"]),
                "consumers": len(all_results["consumers"]),
                "cers": len(all_results["cers"]),
                "cer_members": len(all_results["cer_members"]),
            },
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding test data: {str(e)}")


__all__ = ["router"]
