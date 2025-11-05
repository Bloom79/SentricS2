"""
Energy endpoints for CER energy sharing
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.energy_service import energy_service
from app.models.energy_transaction import TransactionType
from app.schemas.energy import (
    EnergyTransactionCreate,
    EnergyTransactionResponse,
    EnergySharingCalculationResponse,
    EnergyStatisticsResponse,
    CalculateSharingRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/cer/communities/{cer_id}/energy/calculate", response_model=Dict)
async def calculate_energy_sharing(
    cer_id: int,
    request: CalculateSharingRequest,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Calculate energy sharing for a CER over a time period"""
    try:
        result = energy_service.calculate_shared_energy(
            db=db,
            cer_id=cer_id,
            period_start=request.period_start,
            period_end=request.period_end,
            tenant_id=current_user.tenant_id,
        )

        # Save calculation if requested
        if request.save_calculation:
            calculation = energy_service.save_sharing_calculation(
                db=db,
                calculation_data=result,
                tenant_id=current_user.tenant_id,
                user_id=int(current_user.sub),
            )
            result["calculation_id"] = calculation.id

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating energy sharing: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate energy sharing")


@router.get("/cer/communities/{cer_id}/energy/shared", response_model=Dict)
async def get_shared_energy(
    cer_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get shared energy calculation for a CER"""
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.now(timezone.utc)
    if not start_date:
        start_date = end_date - timedelta(days=30)

    try:
        result = energy_service.calculate_shared_energy(
            db=db,
            cer_id=cer_id,
            period_start=start_date,
            period_end=end_date,
            tenant_id=current_user.tenant_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting shared energy: {e}")
        raise HTTPException(status_code=500, detail="Failed to get shared energy")


@router.get(
    "/cer/communities/{cer_id}/energy/transactions", response_model=List[EnergyTransactionResponse]
)
async def list_energy_transactions(
    cer_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    transaction_type: Optional[str] = Query(None),
    member_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List energy transactions for a CER"""
    tx_type = None
    if transaction_type:
        try:
            tx_type = TransactionType(transaction_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid transaction type: {transaction_type}"
            )

    transactions = energy_service.list_transactions(
        db=db,
        cer_id=cer_id,
        tenant_id=current_user.tenant_id,
        start_date=start_date,
        end_date=end_date,
        transaction_type=tx_type,
        member_id=member_id,
        skip=skip,
        limit=limit,
    )
    return transactions


@router.post(
    "/cer/communities/{cer_id}/energy/transactions",
    response_model=EnergyTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_energy_transaction(
    cer_id: int,
    transaction_data: EnergyTransactionCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create an energy transaction"""
    # Verify cer_id matches
    if transaction_data.cer_id != cer_id:
        raise HTTPException(status_code=400, detail="CER ID mismatch")

    try:
        tx_type = TransactionType(transaction_data.transaction_type)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Invalid transaction type: {transaction_data.transaction_type}"
        )

    try:
        transaction = energy_service.create_transaction(
            db=db,
            cer_id=cer_id,
            transaction_type=tx_type,
            energy_kwh=transaction_data.energy_kwh,
            timestamp=transaction_data.timestamp,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
            member_id=transaction_data.member_id,
            plant_id=transaction_data.plant_id,
            calculation_data=transaction_data.calculation_data,
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating energy transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to create energy transaction")


@router.get("/cer/communities/{cer_id}/energy/statistics", response_model=EnergyStatisticsResponse)
async def get_energy_statistics(
    cer_id: int,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get energy statistics for a CER"""
    stats = energy_service.get_energy_statistics(
        db=db,
        cer_id=cer_id,
        tenant_id=current_user.tenant_id,
        start_date=start_date,
        end_date=end_date,
    )
    return stats


@router.get(
    "/cer/communities/{cer_id}/energy/calculations",
    response_model=List[EnergySharingCalculationResponse],
)
async def list_energy_calculations(
    cer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List energy sharing calculations for a CER"""
    from app.models.energy_transaction import EnergySharingCalculation
    from sqlalchemy import and_

    calculations = (
        db.query(EnergySharingCalculation)
        .filter(
            and_(
                EnergySharingCalculation.cer_id == cer_id,
                EnergySharingCalculation.tenant_id == current_user.tenant_id,
                EnergySharingCalculation.deleted_at.is_(None),
            )
        )
        .order_by(EnergySharingCalculation.calculation_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return calculations


@router.get(
    "/cer/communities/{cer_id}/energy/calculations/latest",
    response_model=EnergySharingCalculationResponse,
)
async def get_latest_calculation(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the latest energy sharing calculation for a CER"""
    calculation = energy_service.get_latest_calculation(
        db=db, cer_id=cer_id, tenant_id=current_user.tenant_id
    )

    if not calculation:
        raise HTTPException(status_code=404, detail="No calculations found")

    return calculation
