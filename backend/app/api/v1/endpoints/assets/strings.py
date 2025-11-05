"""
Solar array string configuration endpoints
Split from monolithic assets.py for better maintainability
"""

from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.string_config_service import StringConfigService

router = APIRouter()


class PanelAssignmentRequest(BaseModel):
    """Request model for panel assignment"""

    panel_ids: List[int]


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
