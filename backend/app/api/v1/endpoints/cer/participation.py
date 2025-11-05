"""
CER Participation Request endpoints - Managing join requests for CER
Split from monolithic cer.py for better maintainability
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.cer_service import cer_service
from app.schemas.cer import (
    CERParticipationRequestCreate,
    CERParticipationRequestUpdate,
    CERParticipationRequestResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/participation-requests",
    response_model=CERParticipationRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_participation_request(
    request_data: CERParticipationRequestCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a participation request to join a CER"""
    try:
        request = cer_service.create_participation_request(
            db=db,
            request_data=request_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating participation request: {e}")
        raise HTTPException(status_code=500, detail="Failed to create participation request")


@router.get("/participation-requests", response_model=List[CERParticipationRequestResponse])
async def list_participation_requests(
    cer_id: Optional[int] = Query(None, description="Filter by CER ID"),
    status: Optional[str] = Query(
        None, description="Filter by status (pending, approved, rejected, cancelled)"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List participation requests (filtered by tenant)"""
    requests = cer_service.list_participation_requests(
        db=db,
        tenant_id=current_user.tenant_id,
        cer_id=cer_id,
        status=status,
        skip=skip,
        limit=limit,
    )
    return requests


@router.get("/participation-requests/{request_id}", response_model=CERParticipationRequestResponse)
async def get_participation_request(
    request_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get participation request details"""
    request = cer_service.get_participation_request(db, request_id, current_user.tenant_id)
    if not request:
        raise HTTPException(status_code=404, detail="Participation request not found")
    return request


@router.put("/participation-requests/{request_id}", response_model=CERParticipationRequestResponse)
async def update_participation_request(
    request_id: int,
    request_data: CERParticipationRequestUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update participation request status (approve/reject)"""
    try:
        request = cer_service.update_participation_request(
            db=db,
            request_id=request_id,
            request_data=request_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not request:
            raise HTTPException(status_code=404, detail="Participation request not found")
        return request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating participation request: {e}")
        raise HTTPException(status_code=500, detail="Failed to update participation request")


@router.delete("/participation-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participation_request(
    request_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete participation request (only pending or cancelled)"""
    try:
        success = cer_service.delete_participation_request(
            db=db,
            request_id=request_id,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not success:
            raise HTTPException(status_code=404, detail="Participation request not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/participation-requests/user/me", response_model=List[CERParticipationRequestResponse])
async def get_my_participation_requests(
    current_user: TokenData = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get current user's participation requests"""
    requests = cer_service.get_user_participation_requests(
        db=db, user_id=int(current_user.sub), tenant_id=current_user.tenant_id
    )
    return requests
