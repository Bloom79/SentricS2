"""
Dashboard endpoints
Consolidated from Kronos EAM
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.dashboard_service import dashboard_service

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: TokenData = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get comprehensive dashboard statistics"""
    stats = dashboard_service.get_dashboard_stats(db=db, tenant_id=current_user.tenant_id)
    return stats


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=50),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get recent activity"""
    activity = dashboard_service.get_recent_activity(
        db=db, tenant_id=current_user.tenant_id, limit=limit
    )
    return activity
