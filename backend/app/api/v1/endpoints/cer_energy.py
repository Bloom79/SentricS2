"""
Energy Sharing API Endpoints
Exposes energy sharing calculation and visualization functionality
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.energy_sharing_calculator import (
    energy_share_calculator,
    EnergySharingResult,
)
from app.models.cer import CER
from app.models.billing import BillingStatement
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================


class CalculateSharingRequest(BaseModel):
    """Request to calculate energy sharing"""

    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2020, le=2030, description="Year")


class MemberSharingResult(BaseModel):
    """Energy sharing result for one member"""

    member_id: int
    member_name: str
    shared_energy_kwh: float
    total_consumption_kwh: float
    incentive_amount_eur: float
    hours_with_sharing: int


class EnergySharingResponse(BaseModel):
    """Energy sharing calculation response"""

    cer_id: int
    cer_name: str
    period_start: date
    period_end: date
    total_shared_energy_kwh: float
    total_incentives_eur: float
    member_count: int
    member_results: List[MemberSharingResult]
    calculation_timestamp: datetime


class HourlyDataPoint(BaseModel):
    """Hourly energy data point"""

    timestamp: datetime
    production_kwh: float
    consumption_kwh: float
    shared_energy_kwh: float


class EnergyVisualizationResponse(BaseModel):
    """Energy sharing visualization data"""

    cer_id: int
    from_date: date
    to_date: date
    hourly_data: List[HourlyDataPoint]
    total_production_kwh: float
    total_consumption_kwh: float
    total_shared_kwh: float
    sharing_percentage: float


# ============================================================================
# API Endpoints
# ============================================================================


@router.post("/cer/{cer_id}/calculate-sharing", response_model=EnergySharingResponse)
async def calculate_energy_sharing(
    cer_id: int,
    request: CalculateSharingRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """
    Calculate energy sharing for a CER for a given month.

    This endpoint triggers the energy sharing calculation algorithm which:
    1. Fetches hourly production data from CER plants
    2. Fetches hourly consumption data from all members
    3. Matches production with consumption hour-by-hour
    4. Calculates TCEC incentives based on shared energy
    5. Generates billing data for each member

    **Authorization**: User must have access to the CER

    **Rate Limits**: Limited to prevent excessive calculations

    **Returns**: Detailed sharing results with per-member breakdown
    """
    # Verify CER exists and user has access
    cer = db.query(CER).filter(CER.id == cer_id).first()
    if not cer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CER {cer_id} not found",
        )

    # Check tenant access
    if cer.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this CER",
        )

    try:
        # Perform calculation
        logger.info(
            f"User {current_user.email} requested energy sharing calculation "
            f"for CER {cer.name} ({cer_id}), period {request.year}-{request.month:02d}"
        )

        result = await energy_share_calculator.calculate_monthly_sharing(
            db=db,
            cer_id=cer_id,
            month=request.month,
            year=request.year,
        )

        # Convert to response model
        member_results = [
            MemberSharingResult(
                member_id=m["member_id"],
                member_name=m["member_name"],
                shared_energy_kwh=float(m["shared_energy_kwh"]),
                total_consumption_kwh=float(m["total_consumption_kwh"]),
                incentive_amount_eur=float(m["incentive_amount_eur"]),
                hours_with_sharing=m["hours_with_sharing"],
            )
            for m in result.member_results.values()
        ]

        return EnergySharingResponse(
            cer_id=cer_id,
            cer_name=cer.name,
            period_start=result.period_start,
            period_end=result.period_end,
            total_shared_energy_kwh=float(result.total_shared_energy_kwh),
            total_incentives_eur=float(result.total_incentives_eur),
            member_count=len(member_results),
            member_results=member_results,
            calculation_timestamp=datetime.now(),
        )

    except ValueError as e:
        logger.error(f"Validation error in energy sharing calculation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error calculating energy sharing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate energy sharing. Please try again later.",
        )


@router.post("/cer/{cer_id}/generate-billing")
async def generate_billing_statements(
    cer_id: int,
    request: CalculateSharingRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """
    Calculate energy sharing AND generate billing statements.

    This endpoint:
    1. Calculates energy sharing (same as /calculate-sharing)
    2. Creates BillingStatement records in the database
    3. Returns the created billing statements

    **Warning**: This creates database records. Use /calculate-sharing for dry-run.

    **Returns**: List of created billing statements
    """
    # Verify CER exists and user has access
    cer = db.query(CER).filter(CER.id == cer_id).first()
    if not cer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CER {cer_id} not found",
        )

    if cer.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this CER",
        )

    try:
        # Calculate sharing
        result = await energy_share_calculator.calculate_monthly_sharing(
            db=db,
            cer_id=cer_id,
            month=request.month,
            year=request.year,
        )

        # Generate billing statements
        statements = await energy_share_calculator.generate_billing_statements(
            db=db,
            cer_id=cer_id,
            sharing_result=result,
        )

        logger.info(
            f"Generated {len(statements)} billing statements for CER {cer.name}"
        )

        return {
            "success": True,
            "message": f"Generated {len(statements)} billing statements",
            "cer_id": cer_id,
            "period": f"{request.year}-{request.month:02d}",
            "statements_created": len(statements),
            "total_incentives_eur": float(result.total_incentives_eur),
        }

    except ValueError as e:
        logger.error(f"Validation error generating billing: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error generating billing: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate billing statements",
        )


@router.get(
    "/cer/{cer_id}/sharing-visualization", response_model=EnergyVisualizationResponse
)
async def get_sharing_visualization(
    cer_id: int,
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """
    Get hourly energy sharing data for visualization.

    Returns production, consumption, and shared energy for each hour
    in the specified date range. Used by the frontend to display:
    - Energy flow diagrams
    - Production vs consumption charts
    - Sharing efficiency graphs

    **Date Range**: Maximum 31 days

    **Returns**: Hourly breakdown of energy flows
    """
    # Verify CER exists and user has access
    cer = db.query(CER).filter(CER.id == cer_id).first()
    if not cer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CER {cer_id} not found",
        )

    if cer.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this CER",
        )

    # Validate date range
    if (to_date - from_date).days > 31:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 31 days",
        )

    try:
        # Calculate sharing for the period
        # Note: This is simplified - in production, we'd query pre-calculated data
        month = from_date.month
        year = from_date.year

        result = await energy_share_calculator.calculate_monthly_sharing(
            db=db,
            cer_id=cer_id,
            month=month,
            year=year,
        )

        # Filter hourly data to date range
        filtered_hourly = [
            hour
            for hour in result.hourly_details
            if from_date <= hour["timestamp"].date() <= to_date
        ]

        # Convert to response format
        hourly_data = [
            HourlyDataPoint(
                timestamp=hour["timestamp"],
                production_kwh=hour["production_kwh"],
                consumption_kwh=hour["consumption_kwh"],
                shared_energy_kwh=hour["shared_energy_kwh"],
            )
            for hour in filtered_hourly
        ]

        # Calculate totals
        total_production = sum(h["production_kwh"] for h in filtered_hourly)
        total_consumption = sum(h["consumption_kwh"] for h in filtered_hourly)
        total_shared = sum(h["shared_energy_kwh"] for h in filtered_hourly)

        sharing_percentage = (
            (total_shared / total_production * 100) if total_production > 0 else 0
        )

        return EnergyVisualizationResponse(
            cer_id=cer_id,
            from_date=from_date,
            to_date=to_date,
            hourly_data=hourly_data,
            total_production_kwh=total_production,
            total_consumption_kwh=total_consumption,
            total_shared_kwh=total_shared,
            sharing_percentage=sharing_percentage,
        )

    except Exception as e:
        logger.error(f"Error fetching visualization data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch visualization data",
        )


@router.get("/cer/{cer_id}/billing-statements")
async def get_billing_statements(
    cer_id: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020, le=2030),
    member_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """
    Get billing statements for a CER.

    Filters:
    - month, year: Filter by billing period
    - member_id: Filter by specific member

    **Returns**: List of billing statements
    """
    # Verify CER access
    cer = db.query(CER).filter(CER.id == cer_id).first()
    if not cer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CER {cer_id} not found",
        )

    if cer.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this CER",
        )

    # Build query
    query = db.query(BillingStatement).filter(BillingStatement.cer_id == cer_id)

    if member_id:
        query = query.filter(BillingStatement.member_id == member_id)

    if month and year:
        # Filter by period
        from datetime import datetime

        period_start = datetime(year, month, 1)
        if month == 12:
            period_end = datetime(year + 1, 1, 1)
        else:
            period_end = datetime(year, month + 1, 1)

        query = query.filter(
            BillingStatement.period_start >= period_start,
            BillingStatement.period_start < period_end,
        )

    statements = query.order_by(BillingStatement.period_start.desc()).all()

    return {
        "cer_id": cer_id,
        "total_statements": len(statements),
        "statements": [
            {
                "id": s.id,
                "member_id": s.member_id,
                "period_start": s.period_start.isoformat(),
                "period_end": s.period_end.isoformat(),
                "energy_shared": s.energy_shared,
                "incentives": s.incentives,
                "total_amount": s.total_amount,
                "status": s.status,
            }
            for s in statements
        ],
    }
