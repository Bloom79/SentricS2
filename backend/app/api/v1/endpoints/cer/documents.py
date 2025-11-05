"""
CER Documents endpoints - Document management for CER
Split from monolithic cer.py for better maintainability
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.cer_service import cer_service
from app.services.cer_member_asset_service import CERMemberAssetService
from app.schemas.cer_member_asset import (
    CERMemberAssetCreate,
    CERMemberAssetUpdate,
    CERMemberAssetResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/communities/{cer_id}/documents", response_model=List[dict])
async def get_cer_documents(
    cer_id: int,
    type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get documents for a CER"""
    try:
        from app.services.document_service import document_service

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        documents = document_service.list_documents(
            db=db,
            tenant_id=current_user.tenant_id,
            cer_id=cer_id,
            type=type,
            status=status,
            skip=skip,
            limit=limit,
        )
        return documents
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/communities/{cer_id}/documents/overview", response_model=dict)
async def get_cer_documents_overview(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get document overview for a CER (counts by type, expired, etc.)"""
    try:
        from app.models.document import Document, DocumentTypeEnum, DocumentStatusEnum

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        # Get all documents for this CER
        documents = (
            db.query(Document)
            .filter(
                Document.cer_id == cer_id,
                Document.tenant_id == current_user.tenant_id,
                Document.deleted_at.is_(None),
            )
            .all()
        )

        # Count by type
        by_type = {}
        for doc_type in DocumentTypeEnum:
            by_type[doc_type.value] = len([d for d in documents if d.type == doc_type])

        # Count expired
        expired = len([d for d in documents if d.is_expired])

        # Count by status
        by_status = {}
        for doc_status in DocumentStatusEnum:
            by_status[doc_status.value] = len([d for d in documents if d.status == doc_status])

        return {
            "cer_id": cer_id,
            "total_documents": len(documents),
            "by_type": by_type,
            "by_status": by_status,
            "expired_count": expired,
            "expiring_soon_count": len(
                [
                    d
                    for d in documents
                    if hasattr(d, "days_until_expiry")
                    and d.days_until_expiry is not None
                    and 0 < d.days_until_expiry <= 30
                ]
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents overview for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# Member Asset Endpoints
@router.post(
    "/communities/{cer_id}/members/{member_id}/assets",
    response_model=CERMemberAssetResponse,
    status_code=201,
)
async def create_member_asset(
    cer_id: int,
    member_id: int,
    asset_data: CERMemberAssetCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new asset for a CER member"""
    try:
        # Verify member exists
        member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Create asset data with IDs from path
        asset_create = CERMemberAssetCreate(**asset_data.dict(), member_id=member_id, cer_id=cer_id)

        asset = CERMemberAssetService.create_asset(
            db=db,
            asset_data=asset_create,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to create member asset")
        raise HTTPException(status_code=500, detail="Failed to create asset")


@router.get(
    "/communities/{cer_id}/members/{member_id}/assets", response_model=List[CERMemberAssetResponse]
)
async def list_member_assets(
    cer_id: int,
    member_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all assets for a CER member"""
    try:
        # Verify member exists
        member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        assets = CERMemberAssetService.list_assets(
            db=db, member_id=member_id, cer_id=cer_id, tenant_id=current_user.tenant_id
        )
        return assets
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error listing assets for member {member_id} in CER {cer_id}: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/communities/{cer_id}/members/{member_id}/assets/{asset_id}",
    response_model=CERMemberAssetResponse,
)
async def get_member_asset(
    cer_id: int,
    member_id: int,
    asset_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific member asset"""
    # Verify member exists
    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    asset = CERMemberAssetService.get_asset(db, asset_id, current_user.tenant_id)
    if not asset or asset.member_id != member_id or asset.cer_id != cer_id:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.put(
    "/communities/{cer_id}/members/{member_id}/assets/{asset_id}",
    response_model=CERMemberAssetResponse,
)
async def update_member_asset(
    cer_id: int,
    member_id: int,
    asset_id: int,
    asset_data: CERMemberAssetUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a member asset"""
    # Verify member exists
    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    asset = CERMemberAssetService.update_asset(
        db=db,
        asset_id=asset_id,
        asset_data=asset_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )

    if not asset or asset.member_id != member_id or asset.cer_id != cer_id:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.delete(
    "/communities/{cer_id}/members/{member_id}/assets/{asset_id}",
    status_code=204,
)
async def delete_member_asset(
    cer_id: int,
    member_id: int,
    asset_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a member asset"""
    # Verify member exists
    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    success = CERMemberAssetService.delete_asset(
        db=db, asset_id=asset_id, tenant_id=current_user.tenant_id, user_id=int(current_user.sub)
    )

    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")

    return None
