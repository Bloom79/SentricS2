"""
Asset type management endpoints
Split from monolithic assets.py for better maintainability
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.asset_service import asset_service
from app.schemas.asset import AssetTypeCreate, AssetTypeResponse

router = APIRouter()


@router.get("/types", response_model=List[AssetTypeResponse])
async def list_asset_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List asset types"""
    types = asset_service.get_asset_types(
        db=db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
    )
    return types


@router.post("/types", response_model=AssetTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_asset_type(
    asset_type_data: AssetTypeCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create asset type"""
    try:
        asset_type = asset_service.create_asset_type(
            db=db,
            asset_type_data=asset_type_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return asset_type
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create asset type: {str(e)}")
