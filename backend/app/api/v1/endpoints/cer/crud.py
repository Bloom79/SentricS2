"""
CER CRUD endpoints - Create, Read, Update, Delete operations for CER
Split from monolithic cer.py for better maintainability
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.cer_service import cer_service
from app.schemas.cer import CERCreate, CERUpdate, CERResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/communities", response_model=CERResponse, status_code=status.HTTP_201_CREATED)
async def create_cer(
    cer_data: CERCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new CER"""
    try:
        cer = cer_service.create_cer(
            db=db,
            cer_data=cer_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return cer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create CER")


@router.get("/communities", response_model=List[CERResponse])
async def list_cer(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    legal_type: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List CERs for current tenant"""
    cer_list = cer_service.list_cer(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        status=status,
        legal_type=legal_type,
    )
    return cer_list


@router.get("/communities/{cer_id}", response_model=CERResponse)
async def get_cer(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get CER details"""
    cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")
    return cer


@router.put("/communities/{cer_id}", response_model=CERResponse)
async def update_cer(
    cer_id: int,
    cer_data: CERUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update CER"""
    cer = cer_service.update_cer(
        db=db,
        cer_id=cer_id,
        cer_data=cer_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")
    return cer


@router.delete("/communities/{cer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cer(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete CER (soft delete)"""
    success = cer_service.delete_cer(
        db=db, cer_id=cer_id, tenant_id=current_user.tenant_id, user_id=int(current_user.sub)
    )
    if not success:
        raise HTTPException(status_code=404, detail="CER not found")
    return None
