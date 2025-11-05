"""
Asset API endpoints
Migrated from Sentrics with Kronos EAM patterns
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging
import json

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.asset_service import asset_service
from app.services.string_config_service import StringConfigService
from app.services.bulk_import_service import BulkImportService
from app.schemas.asset import (
    AssetCreate,
    AssetUpdate,
    AssetResponse,
    AssetTypeCreate,
    AssetTypeResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _parse_dynamic_attributes(value: Any) -> Dict[str, Any]:
    """Parse dynamic_attributes from JSON string or dict to dict"""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value) if value else {}
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Failed to parse dynamic_attributes as JSON: {value}")
            return {}
    return {}


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
                    "dynamic_attributes": _parse_dynamic_attributes(asset.dynamic_attributes),
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


# String Configuration endpoints for Solar Arrays
@router.get("/{array_id}/strings/config")
async def get_string_config(
    array_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get string configuration for a solar array"""
    try:
        config = StringConfigService.get_string_config(
            db=db, array_id=array_id, tenant_id=current_user.tenant_id
        )
        return config
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get string config: {str(e)}")


@router.put("/{array_id}/strings/config")
async def update_string_config(
    array_id: int,
    number_of_strings: int = Query(..., ge=1),
    panels_per_string: int = Query(..., ge=1),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update string configuration (number of strings, panels per string)"""
    try:
        asset = StringConfigService.update_string_config(
            db=db,
            array_id=array_id,
            number_of_strings=number_of_strings,
            panels_per_string=panels_per_string,
            tenant_id=current_user.tenant_id,
        )
        from app.schemas.asset import AssetResponse

        return AssetResponse.from_orm(asset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update string config: {str(e)}")


@router.get("/{array_id}/strings")
async def get_all_strings(
    array_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all strings for an array with their status"""
    try:
        strings = StringConfigService.get_all_strings(
            db=db, array_id=array_id, tenant_id=current_user.tenant_id
        )
        return strings
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get strings: {str(e)}")


@router.get("/{array_id}/strings/{string_number}")
async def get_string_details(
    array_id: int,
    string_number: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get details for a specific string including panel list and metrics"""
    try:
        details = StringConfigService.get_string_details(
            db=db, array_id=array_id, string_number=string_number, tenant_id=current_user.tenant_id
        )
        return details
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get string details: {str(e)}")


class PanelAssignmentRequest(BaseModel):
    """Request model for panel assignment"""

    panel_ids: List[int]


@router.post("/{array_id}/strings/{string_number}/assign")
async def assign_panels_to_string(
    array_id: int,
    string_number: int,
    request: PanelAssignmentRequest,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Assign panels to a specific string"""
    try:
        asset = StringConfigService.assign_panels_to_string(
            db=db,
            array_id=array_id,
            string_number=string_number,
            panel_ids=request.panel_ids,
            tenant_id=current_user.tenant_id,
        )
        from app.schemas.asset import AssetResponse

        return AssetResponse.from_orm(asset)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign panels: {str(e)}")


@router.delete("/{array_id}/strings/{panel_id}")
async def remove_panel_from_string(
    array_id: int,
    panel_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove a panel from its assigned string"""
    try:
        asset = StringConfigService.remove_panel_from_string(
            db=db, array_id=array_id, panel_id=panel_id, tenant_id=current_user.tenant_id
        )
        from app.schemas.asset import AssetResponse

        return AssetResponse.from_orm(asset)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove panel: {str(e)}")


# Bulk Import endpoints
class BulkImportRequest(BaseModel):
    """Request model for bulk import"""

    csv_content: str
    has_header: bool = True


@router.post("/plants/{plant_id}/assets/bulk-import")
async def bulk_import_panels(
    plant_id: int,
    request: BulkImportRequest,
    array_id: Optional[int] = Query(None, description="Optional: Array ID for string assignment"),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Bulk import panels from CSV"""
    try:
        result = BulkImportService.import_panels_from_csv(
            db=db,
            plant_id=plant_id,
            array_id=array_id,
            csv_content=request.csv_content,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
            has_header=request.has_header,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import panels: {str(e)}")


@router.get("/plants/{plant_id}/assets/bulk-import/template")
async def get_csv_template(
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get CSV template for bulk import"""
    template = BulkImportService.generate_csv_template()
    from fastapi.responses import Response

    return Response(
        content=template,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=panel_import_template.csv"},
    )
