"""
Billing API endpoints for CER financial management
"""

from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.billing_service import billing_service
from app.models.billing import BillingStatus, TransactionType
from app.schemas.billing import (
    BillingStatementResponse,
    BillingTransactionCreate,
    BillingTransactionResponse,
    SettlementCreate,
    SettlementResponse,
    BillingOverviewResponse,
    MemberBalanceResponse,
    CalculateSettlementRequest,
    SettlementCalculationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/cer/communities/{cer_id}/billing", response_model=BillingOverviewResponse)
async def get_billing_overview(
    cer_id: int,
    period_start: Optional[datetime] = Query(None),
    period_end: Optional[datetime] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get billing overview for a CER"""
    try:
        overview = billing_service.get_billing_overview(
            db=db,
            cer_id=cer_id,
            tenant_id=current_user.tenant_id,
            period_start=period_start,
            period_end=period_end,
        )
        return overview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting billing overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get billing overview")


@router.get(
    "/cer/communities/{cer_id}/billing/statements", response_model=List[BillingStatementResponse]
)
async def list_billing_statements(
    cer_id: int,
    member_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List billing statements for a CER"""
    try:
        billing_status = BillingStatus(status) if status else None
        statements = billing_service.list_statements(
            db=db,
            cer_id=cer_id,
            tenant_id=current_user.tenant_id,
            member_id=member_id,
            status=billing_status,
            skip=skip,
            limit=limit,
        )
        return statements
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing billing statements: {e}")
        raise HTTPException(status_code=500, detail="Failed to list billing statements")


@router.get(
    "/cer/communities/{cer_id}/billing/member-balances", response_model=List[MemberBalanceResponse]
)
async def get_member_balances(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get member balances for a CER"""
    try:
        balances = billing_service.get_member_balances(
            db=db, cer_id=cer_id, tenant_id=current_user.tenant_id
        )
        return balances
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting member balances: {e}")
        raise HTTPException(status_code=500, detail="Failed to get member balances")


@router.get(
    "/cer/communities/{cer_id}/billing/transactions",
    response_model=List[BillingTransactionResponse],
)
async def list_billing_transactions(
    cer_id: int,
    member_id: Optional[int] = Query(None),
    statement_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List billing transactions for a CER"""
    try:
        tx_type = TransactionType(transaction_type) if transaction_type else None
        transactions = billing_service.list_transactions(
            db=db,
            cer_id=cer_id,
            tenant_id=current_user.tenant_id,
            member_id=member_id,
            statement_id=statement_id,
            transaction_type=tx_type,
            skip=skip,
            limit=limit,
        )
        return transactions
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing billing transactions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list billing transactions")


@router.post(
    "/cer/communities/{cer_id}/billing/transactions",
    response_model=BillingTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_billing_transaction(
    cer_id: int,
    transaction_data: BillingTransactionCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a billing transaction (payment, credit, debit)"""
    try:
        # Ensure cer_id matches
        transaction_data.cer_id = cer_id

        transaction = billing_service.create_billing_transaction(
            db=db,
            transaction_data=transaction_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating billing transaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to create billing transaction")


@router.post(
    "/cer/communities/{cer_id}/billing/settle", response_model=SettlementCalculationResponse
)
async def calculate_settlement(
    cer_id: int,
    request: CalculateSettlementRequest,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Calculate settlement for a CER billing period"""
    try:
        # Ensure cer_id matches
        request.cer_id = cer_id

        # Calculate settlement
        settlement = billing_service.calculate_settlement(
            db=db,
            cer_id=cer_id,
            period_start=request.period_start,
            period_end=request.period_end,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
            calculation_method=request.calculation_method,
        )

        statements_generated = 0
        invoices_generated = 0

        # Generate statements if requested
        if request.generate_statements:
            statements = billing_service.generate_billing_statements(
                db=db,
                settlement_id=settlement.id,
                tenant_id=current_user.tenant_id,
                user_id=int(current_user.sub),
            )
            statements_generated = len(statements)

        # TODO: Generate invoices if requested
        # if request.generate_invoices:
        #     invoices = billing_service.generate_invoices(...)
        #     invoices_generated = len(invoices)

        return {
            "settlement_id": settlement.id,
            "calculation": {
                "total_production": settlement.total_production,
                "total_consumption": settlement.total_consumption,
                "total_shared_energy": settlement.total_shared_energy,
                "total_incentives": settlement.total_incentives,
                "total_grid_fees": settlement.total_grid_fees,
                "total_community_fund": settlement.total_community_fund,
                "total_amount": settlement.total_amount,
                "incentive_rate": settlement.incentive_rate,
                "member_allocation": settlement.member_allocation,
            },
            "statements_generated": statements_generated,
            "invoices_generated": invoices_generated,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating settlement: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate settlement")


@router.get(
    "/cer/communities/{cer_id}/billing/settlements", response_model=List[SettlementResponse]
)
async def list_settlements(
    cer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List settlements for a CER"""
    try:
        from app.models.billing import Settlement
        from sqlalchemy import and_

        settlements = (
            db.query(Settlement)
            .filter(
                and_(
                    Settlement.cer_id == cer_id,
                    Settlement.tenant_id == current_user.tenant_id,
                    Settlement.deleted_at.is_(None),
                )
            )
            .order_by(Settlement.settlement_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return settlements
    except Exception as e:
        logger.error(f"Error listing settlements: {e}")
        raise HTTPException(status_code=500, detail="Failed to list settlements")


@router.get(
    "/cer/communities/{cer_id}/billing/settlements/{settlement_id}",
    response_model=SettlementResponse,
)
async def get_settlement(
    cer_id: int,
    settlement_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get settlement details"""
    try:
        from app.models.billing import Settlement
        from sqlalchemy import and_

        settlement = (
            db.query(Settlement)
            .filter(
                and_(
                    Settlement.id == settlement_id,
                    Settlement.cer_id == cer_id,
                    Settlement.tenant_id == current_user.tenant_id,
                    Settlement.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not settlement:
            raise HTTPException(status_code=404, detail="Settlement not found")

        return settlement
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting settlement: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settlement")


@router.get("/cer/communities/{cer_id}/billing/invoices", response_model=List[Dict])
async def list_invoices(
    cer_id: int,
    member_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List invoices for a CER (placeholder - to be implemented)"""
    # TODO: Implement invoice listing
    return []
