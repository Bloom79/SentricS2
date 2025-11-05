"""
Bulk asset import endpoints
Split from monolithic assets.py for better maintainability
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.bulk_import_service import BulkImportService

router = APIRouter()


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
