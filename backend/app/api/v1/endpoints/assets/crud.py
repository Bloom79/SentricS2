"""
Asset CRUD endpoints
Split from monolithic assets.py for better maintainability
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.asset_service import asset_service
from app.schemas.asset import AssetCreate, AssetUpdate, AssetResponse
from .helpers import parse_dynamic_attributes

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/plants/{plant_id}/assets", response_model=List[AssetResponse])
async def list_plant_assets(
    plant_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    type_id: Optional[int] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List assets for a plant"""
    try:
        logger.info(f"Getting assets for plant {plant_id}, tenant {current_user.tenant_id}")

        assets = asset_service.get_plant_assets(
            db=db,
            plant_id=plant_id,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            status=status,
            type_id=type_id,
        )

        logger.info(f"Found {len(assets)} assets")

        # Convert to response models
        result = []
        for asset in assets:
            try:
                asset_dict = {
                    "id": asset.id,
                    "tenant_id": asset.tenant_id,
                    "name": asset.name,
                    "model": asset.model,
                    "manufacturer": asset.manufacturer,
                    "serial_number": asset.serial_number,
                    "component_type": asset.component_type,
                    "status": asset.status,
                    "location": asset.location,
                    "rated_power": asset.rated_power,
                    "efficiency": asset.efficiency,
                    "voltage": asset.voltage,
                    "current": asset.current,
                    "type_id": asset.type_id,
                    "plant_id": asset.plant_id,
                    "parent_id": asset.parent_id,
                    "installation_date": (
                        asset.installation_date.isoformat() if asset.installation_date else None
                    ),
                    "dynamic_attributes": parse_dynamic_attributes(asset.dynamic_attributes),
                    "notes": asset.notes,
                    "warranty_expiry": (
                        asset.warranty_expiry.isoformat() if asset.warranty_expiry else None
                    ),
                    "created_at": (
                        asset.created_at.isoformat()
                        if hasattr(asset, "created_at") and asset.created_at
                        else None
                    ),
                    "updated_at": (
                        asset.updated_at.isoformat()
                        if hasattr(asset, "updated_at") and asset.updated_at
                        else None
                    ),
                }
                result.append(asset_dict)
            except Exception as e:
                logger.error(f"Error serializing asset {asset.id}: {e}", exc_info=True)
                continue

        return result
    except Exception as e:
        logger.error(f"Error getting plant assets: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get plant assets: {str(e)}")


@router.post(
    "/plants/{plant_id}/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED
)
async def create_asset(
    plant_id: int,
    asset_data: AssetCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create asset for a plant"""
    try:
        asset = asset_service.create_asset(
            db=db,
            plant_id=plant_id,
            asset_data=asset_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create asset: {str(e)}")


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get asset details"""
    asset = asset_service.get_asset(db, asset_id, current_user.tenant_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    asset_data: AssetUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update asset"""
    asset = asset_service.update_asset(
        db=db,
        asset_id=asset_id,
        asset_data=asset_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete asset"""
    success = asset_service.delete_asset(
        db=db, asset_id=asset_id, tenant_id=current_user.tenant_id, user_id=int(current_user.sub)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return None
