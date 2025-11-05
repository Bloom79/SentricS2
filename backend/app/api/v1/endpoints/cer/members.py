"""
CER Member endpoints - Member management for CER
Split from monolithic cer.py for better maintainability
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.cer_service import cer_service
from app.schemas.cer import CERMemberCreate, CERMemberUpdate, CERMemberResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/communities/{cer_id}/members",
    response_model=CERMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    cer_id: int,
    member_data: CERMemberCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add member to CER"""
    try:
        member = cer_service.add_member(
            db=db,
            cer_id=cer_id,
            member_data=member_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not member:
            raise HTTPException(status_code=404, detail="CER not found")
        return member
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/communities/{cer_id}/members", response_model=List[CERMemberResponse])
async def list_members(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List CER members"""
    try:
        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        members = cer_service.list_members(db, cer_id, current_user.tenant_id)
        # Ensure energy fields have default values if None
        for member in members:
            if member.energy_produced is None:
                member.energy_produced = 0.0
            if member.energy_consumed is None:
                member.energy_consumed = 0.0
            if member.energy_shared is None:
                member.energy_shared = 0.0
        return members
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing members for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/communities/{cer_id}/members/{member_id}", response_model=CERMemberResponse)
async def get_member(
    cer_id: int,
    member_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a single CER member"""
    # Verify CER exists
    cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")

    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.get("/communities/{cer_id}/stats", response_model=dict)
async def get_cer_stats(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get statistics for a CER"""
    try:
        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        stats = cer_service.get_cer_stats(db, cer_id, current_user.tenant_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/communities/{cer_id}/members/{member_id}", response_model=CERMemberResponse)
async def update_member(
    cer_id: int,
    member_id: int,
    member_data: CERMemberUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update CER member"""
    member = cer_service.update_member(
        db=db,
        cer_id=cer_id,
        member_id=member_id,
        member_data=member_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.delete("/communities/{cer_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    cer_id: int,
    member_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove member from CER"""
    success = cer_service.delete_member(
        db=db,
        cer_id=cer_id,
        member_id=member_id,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return None
