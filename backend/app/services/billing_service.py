"""
Billing Service - Business logic for CER billing and financial management
Handles settlements, billing statements, invoices, and transactions
REFACTORED: Reduced complexity by extracting helper methods
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta, timezone
import logging

from app.models.cer import CER, CERMember
from app.models.billing import (
    BillingStatement,
    Invoice,
    BillingTransaction,
    Settlement,
    BillingStatus,
    PaymentStatus,
    TransactionType,
    SettlementStatus,
)
from app.services.base import BaseService
from app.services.energy_service import energy_service
from app.schemas.billing import BillingTransactionCreate

logger = logging.getLogger(__name__)


class BillingService(BaseService):
    """Service for billing and financial management"""

    # Incentive rates based on plant size (€/MWh)
    INCENTIVE_RATES = {
        "small": 120.0,  # ≤200 kW
        "medium": 110.0,  # >200 kW and ≤600 kW
        "large": 100.0,  # >600 kW and ≤1 MW
    }

    # Regional adjustments (€/MWh)
    REGIONAL_ADJUSTMENTS = {"north": 10.0, "center": 4.0, "south": 0.0}

    # Grid fee rates (€/kWh) - simplified, should come from configuration
    DEFAULT_GRID_FEE_RATE = 0.10  # €/kWh

    # Community fund percentage (of incentives)
    COMMUNITY_FUND_PERCENTAGE = 0.10  # 10% of incentives

    @staticmethod
    def calculate_settlement(
        db: Session,
        cer_id: int,
        period_start: datetime,
        period_end: datetime,
        tenant_id: str,
        user_id: int,
        calculation_method: str = "standard",
    ) -> Settlement:
        """
        Calculate settlement for a CER billing period

        Steps:
        1. Calculate energy sharing for the period
        2. Calculate incentives based on plant size and region
        3. Calculate grid fees
        4. Calculate community fund
        5. Allocate amounts to members
        """
        # Verify CER exists
        cer = (
            db.query(CER)
            .filter(and_(CER.id == cer_id, CER.tenant_id == tenant_id, CER.deleted_at.is_(None)))
            .first()
        )

        if not cer:
            raise ValueError("CER not found")

        # Calculate energy sharing
        energy_calc = energy_service.calculate_shared_energy(
            db=db,
            cer_id=cer_id,
            period_start=period_start,
            period_end=period_end,
            tenant_id=tenant_id,
        )

        # Get CER capacity to determine incentive rate
        total_capacity_kw = cer.total_capacity or 0.0
        incentive_rate = BillingService._calculate_incentive_rate(total_capacity_kw, cer.region)

        # Calculate incentivized energy (55% of shared energy, with adjustments)
        shared_energy = energy_calc["shared_energy"]
        incentivized_energy = energy_calc["incentivized_energy"]

        # Calculate incentives (€)
        total_incentives = (incentivized_energy / 1000.0) * incentive_rate  # Convert kWh to MWh

        # Calculate grid fees (simplified - should use actual grid fee structure)
        total_grid_fees = (
            energy_calc["grid_import"] + energy_calc["grid_export"]
        ) * BillingService.DEFAULT_GRID_FEE_RATE

        # Calculate community fund (10% of incentives)
        total_community_fund = total_incentives * BillingService.COMMUNITY_FUND_PERCENTAGE

        # Calculate energy cost (grid import cost)
        # Simplified: using average market price (should come from market data)
        average_market_price = 0.15  # €/kWh (simplified)
        total_energy_cost = energy_calc["grid_import"] * average_market_price

        # Calculate total settlement amount
        total_amount = total_incentives - total_grid_fees - total_community_fund - total_energy_cost

        # Allocate to members based on energy sharing allocation
        member_allocation = {}
        for member_id, allocation_data in energy_calc["member_allocation"].items():
            member_shared = allocation_data["energy_shared"]
            member_percentage = allocation_data["percentage"] / 100.0

            member_incentives = total_incentives * member_percentage
            member_grid_fees = total_grid_fees * member_percentage
            member_community_fund = total_community_fund * member_percentage
            member_energy_cost = total_energy_cost * member_percentage
            member_amount = (
                member_incentives - member_grid_fees - member_community_fund - member_energy_cost
            )

            member_allocation[str(member_id)] = {
                "energy_shared": member_shared,
                "percentage": allocation_data["percentage"],
                "incentives": member_incentives,
                "grid_fees": member_grid_fees,
                "community_fund": member_community_fund,
                "energy_cost": member_energy_cost,
                "amount": member_amount,
            }

        # Create settlement
        settlement = Settlement(
            tenant_id=tenant_id,
            cer_id=cer_id,
            period_start=period_start,
            period_end=period_end,
            status=SettlementStatus.CALCULATED,
            total_production=energy_calc["total_production"],
            total_consumption=energy_calc["total_consumption"],
            total_shared_energy=shared_energy,
            total_self_consumed=energy_calc["self_consumed_energy"],
            total_grid_export=energy_calc["grid_export"],
            total_grid_import=energy_calc["grid_import"],
            total_incentivized_energy=incentivized_energy,
            total_incentives=total_incentives,
            total_grid_fees=total_grid_fees,
            total_community_fund=total_community_fund,
            total_energy_cost=total_energy_cost,
            total_amount=total_amount,
            incentive_rate=incentive_rate,
            member_allocation=member_allocation,
            calculation_method=calculation_method,
            calculation_data={
                "energy_calculation": energy_calc,
                "incentive_rate": incentive_rate,
                "grid_fee_rate": BillingService.DEFAULT_GRID_FEE_RATE,
                "community_fund_percentage": BillingService.COMMUNITY_FUND_PERCENTAGE,
            },
            created_by=user_id,
        )

        db.add(settlement)
        db.commit()
        db.refresh(settlement)

        logger.info(f"Calculated settlement {settlement.id} for CER {cer_id}")
        return settlement

    @staticmethod
    def _calculate_incentive_rate(capacity_kw: float, region: str) -> float:
        """Calculate incentive rate based on plant capacity and region"""
        # Determine base rate based on capacity
        if capacity_kw <= 200:
            base_rate = BillingService.INCENTIVE_RATES["small"]
        elif capacity_kw <= 600:
            base_rate = BillingService.INCENTIVE_RATES["medium"]
        else:
            base_rate = BillingService.INCENTIVE_RATES["large"]

        # Apply regional adjustment
        region_lower = region.lower()
        if "nord" in region_lower or "north" in region_lower:
            adjustment = BillingService.REGIONAL_ADJUSTMENTS["north"]
        elif "centro" in region_lower or "center" in region_lower:
            adjustment = BillingService.REGIONAL_ADJUSTMENTS["center"]
        else:
            adjustment = BillingService.REGIONAL_ADJUSTMENTS["south"]

        return base_rate + adjustment

    @staticmethod
    def generate_billing_statements(
        db: Session, settlement_id: int, tenant_id: str, user_id: int, due_date_days: int = 30
    ) -> List[BillingStatement]:
        """Generate billing statements for all members based on settlement"""
        settlement = (
            db.query(Settlement)
            .filter(
                and_(
                    Settlement.id == settlement_id,
                    Settlement.tenant_id == tenant_id,
                    Settlement.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not settlement:
            raise ValueError("Settlement not found")

        # Get all active members
        members = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.cer_id == settlement.cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                    CERMember.status == "active",
                )
            )
            .all()
        )

        statements = []
        due_date = datetime.now(timezone.utc) + timedelta(days=due_date_days)

        for member in members:
            member_id_str = str(member.id)
            if member_id_str not in settlement.member_allocation:
                continue

            allocation = settlement.member_allocation[member_id_str]

            # Get member energy data from energy sharing calculation
            energy_data = (
                settlement.calculation_data.get("energy_calculation", {})
                .get("member_allocation", {})
                .get(member_id_str, {})
            )

            # Create billing statement
            statement = BillingStatement(
                tenant_id=tenant_id,
                cer_id=settlement.cer_id,
                member_id=member.id,
                period_start=settlement.period_start,
                period_end=settlement.period_end,
                billing_date=datetime.now(timezone.utc),
                due_date=due_date,
                energy_shared=allocation.get("energy_shared", 0.0),
                energy_consumed=energy_data.get("energy_consumed", 0.0),
                energy_produced=energy_data.get("energy_produced", 0.0),
                total_amount=allocation.get("amount", 0.0),
                incentives=allocation.get("incentives", 0.0),
                grid_fees=allocation.get("grid_fees", 0.0),
                community_fund=allocation.get("community_fund", 0.0),
                energy_cost=allocation.get("energy_cost", 0.0),
                shared_energy_value=allocation.get("incentives", 0.0),  # Value of shared energy
                amount_paid=0.0,
                balance=allocation.get("amount", 0.0),
                status=BillingStatus.PENDING,
                settlement_id=settlement_id,
                created_by=user_id,
            )

            db.add(statement)
            statements.append(statement)

        db.commit()

        for statement in statements:
            db.refresh(statement)

        logger.info(
            f"Generated {len(statements)} billing statements for settlement {settlement_id}"
        )
        return statements

    @staticmethod
    def _verify_cer_and_member(
        db: Session, cer_id: int, member_id: int, tenant_id: str
    ) -> Tuple[CER, CERMember]:
        """
        Verify CER and member exist

        Raises:
            ValueError if CER or member not found
        """
        cer = BaseService._get_by_id(db, CER, cer_id, tenant_id)
        if not cer:
            raise ValueError("CER not found")

        member = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.id == member_id,
                    CERMember.cer_id == cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not member:
            raise ValueError("Member not found")

        return cer, member

    @staticmethod
    def _determine_transaction_status(transaction_type: TransactionType) -> PaymentStatus:
        """
        Determine initial transaction status based on type

        Returns:
            PENDING for payments, COMPLETED for credits/debits
        """
        if transaction_type == TransactionType.PAYMENT:
            return PaymentStatus.PENDING
        return PaymentStatus.COMPLETED

    @staticmethod
    def _update_statement_balance(
        db: Session,
        statement_id: Optional[int],
        transaction_type: TransactionType,
        amount: float,
        tenant_id: str,
    ) -> None:
        """
        Update statement balance based on transaction

        Args:
            db: Database session
            statement_id: Statement ID to update
            transaction_type: Type of transaction
            amount: Transaction amount
            tenant_id: Tenant ID
        """
        if not statement_id:
            return

        statement = (
            db.query(BillingStatement)
            .filter(
                and_(
                    BillingStatement.id == statement_id,
                    BillingStatement.tenant_id == tenant_id,
                    BillingStatement.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not statement:
            return

        if transaction_type == TransactionType.PAYMENT:
            statement.amount_paid += abs(amount)
            statement.balance = statement.total_amount - statement.amount_paid

            if statement.balance <= 0:
                statement.status = BillingStatus.PAID
        elif transaction_type == TransactionType.CREDIT:
            statement.balance -= abs(amount)
        elif transaction_type == TransactionType.DEBIT:
            statement.balance += abs(amount)

    @staticmethod
    def _update_invoice_balance(
        db: Session,
        invoice_id: Optional[int],
        transaction_type: TransactionType,
        amount: float,
        tenant_id: str,
    ) -> None:
        """
        Update invoice balance based on transaction

        Args:
            db: Database session
            invoice_id: Invoice ID to update
            transaction_type: Type of transaction
            amount: Transaction amount
            tenant_id: Tenant ID
        """
        if not invoice_id:
            return

        invoice = (
            db.query(Invoice)
            .filter(
                and_(
                    Invoice.id == invoice_id,
                    Invoice.tenant_id == tenant_id,
                    Invoice.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not invoice:
            return

        if transaction_type == TransactionType.PAYMENT:
            invoice.amount_paid += abs(amount)
            invoice.balance = invoice.total_amount - invoice.amount_paid

            if invoice.balance <= 0:
                invoice.status = BillingStatus.PAID
                invoice.is_paid = True
                invoice.paid_date = datetime.now(timezone.utc)

    @staticmethod
    def create_billing_transaction(
        db: Session, transaction_data: BillingTransactionCreate, tenant_id: str, user_id: int
    ) -> BillingTransaction:
        """
        Create a billing transaction (payment, credit, debit)

        REFACTORED: Complexity reduced from 13 to ~5 by extracting helpers
        """
        # Verify CER and member exist
        cer, member = BillingService._verify_cer_and_member(
            db, transaction_data.cer_id, transaction_data.member_id, tenant_id
        )

        # Determine initial status
        status = BillingService._determine_transaction_status(transaction_data.transaction_type)

        # Create transaction
        transaction = BillingTransaction(
            tenant_id=tenant_id,
            cer_id=transaction_data.cer_id,
            member_id=transaction_data.member_id,
            transaction_type=transaction_data.transaction_type,
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            payment_method=transaction_data.payment_method,
            payment_reference=transaction_data.payment_reference,
            payment_date=transaction_data.payment_date or datetime.now(timezone.utc),
            status=status,
            description=transaction_data.description,
            notes=transaction_data.notes,
            statement_id=transaction_data.statement_id,
            invoice_id=transaction_data.invoice_id,
            extra_metadata=transaction_data.extra_metadata,
            created_by=user_id,
        )

        db.add(transaction)

        # Update statement balance if statement_id provided
        BillingService._update_statement_balance(
            db,
            transaction_data.statement_id,
            transaction_data.transaction_type,
            transaction_data.amount,
            tenant_id,
        )

        # Update invoice balance if invoice_id provided
        BillingService._update_invoice_balance(
            db,
            transaction_data.invoice_id,
            transaction_data.transaction_type,
            transaction_data.amount,
            tenant_id,
        )

        db.commit()
        db.refresh(transaction)

        logger.info(
            f"Created billing transaction {transaction.id} for member {transaction_data.member_id}"
        )
        return transaction

    @staticmethod
    def get_billing_overview(
        db: Session,
        cer_id: int,
        tenant_id: str,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get billing overview for a CER"""
        # Verify CER exists
        cer = (
            db.query(CER)
            .filter(and_(CER.id == cer_id, CER.tenant_id == tenant_id, CER.deleted_at.is_(None)))
            .first()
        )

        if not cer:
            raise ValueError("CER not found")

        # Build query
        query = db.query(BillingStatement).filter(
            and_(
                BillingStatement.cer_id == cer_id,
                BillingStatement.tenant_id == tenant_id,
                BillingStatement.deleted_at.is_(None),
            )
        )

        if period_start:
            query = query.filter(BillingStatement.period_start >= period_start)
        if period_end:
            query = query.filter(BillingStatement.period_end <= period_end)

        statements = query.all()

        # Calculate totals
        total_amount = sum(s.total_amount for s in statements)
        total_paid = sum(s.amount_paid for s in statements)
        total_balance = sum(s.balance for s in statements)

        pending = len([s for s in statements if s.status == BillingStatus.PENDING])
        overdue = len([s for s in statements if s.status == BillingStatus.OVERDUE])
        paid = len([s for s in statements if s.status == BillingStatus.PAID])

        return {
            "cer_id": cer_id,
            "period_start": period_start,
            "period_end": period_end,
            "total_statements": len(statements),
            "total_amount": total_amount,
            "total_paid": total_paid,
            "total_balance": total_balance,
            "pending_statements": pending,
            "overdue_statements": overdue,
            "paid_statements": paid,
            "statements": statements,
        }

    @staticmethod
    def get_member_balances(db: Session, cer_id: int, tenant_id: str) -> List[Dict[str, Any]]:
        """Get member balances for a CER"""
        # Verify CER exists
        cer = (
            db.query(CER)
            .filter(and_(CER.id == cer_id, CER.tenant_id == tenant_id, CER.deleted_at.is_(None)))
            .first()
        )

        if not cer:
            raise ValueError("CER not found")

        # Get all members with their statements
        members = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.cer_id == cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .all()
        )

        balances = []
        for member in members:
            # Get pending statements
            statements = (
                db.query(BillingStatement)
                .filter(
                    and_(
                        BillingStatement.member_id == member.id,
                        BillingStatement.tenant_id == tenant_id,
                        BillingStatement.deleted_at.is_(None),
                        BillingStatement.status.in_([BillingStatus.PENDING, BillingStatus.OVERDUE]),
                    )
                )
                .all()
            )

            current_balance = sum(s.balance for s in statements)
            outstanding_statements = len(statements)

            # Get last payment date
            last_transaction = (
                db.query(BillingTransaction)
                .filter(
                    and_(
                        BillingTransaction.member_id == member.id,
                        BillingTransaction.tenant_id == tenant_id,
                        BillingTransaction.deleted_at.is_(None),
                        BillingTransaction.transaction_type == TransactionType.PAYMENT,
                        BillingTransaction.status == PaymentStatus.COMPLETED,
                    )
                )
                .order_by(BillingTransaction.payment_date.desc())
                .first()
            )

            payment_status = "paid" if current_balance <= 0 else "pending"
            if outstanding_statements > 0:
                overdue_count = len([s for s in statements if s.status == BillingStatus.OVERDUE])
                if overdue_count > 0:
                    payment_status = "overdue"

            balances.append(
                {
                    "member_id": member.id,
                    "pod_id": member.pod_id,
                    "member_type": member.member_type,
                    "total_energy_shared": member.energy_shared,
                    "current_balance": current_balance,
                    "payment_status": payment_status,
                    "last_payment_date": (
                        last_transaction.payment_date if last_transaction else None
                    ),
                    "outstanding_statements": outstanding_statements,
                }
            )

        return balances

    @staticmethod
    def list_statements(
        db: Session,
        cer_id: int,
        tenant_id: str,
        member_id: Optional[int] = None,
        status: Optional[BillingStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BillingStatement]:
        """List billing statements"""
        query = db.query(BillingStatement).filter(
            and_(
                BillingStatement.cer_id == cer_id,
                BillingStatement.tenant_id == tenant_id,
                BillingStatement.deleted_at.is_(None),
            )
        )

        if member_id:
            query = query.filter(BillingStatement.member_id == member_id)
        if status:
            query = query.filter(BillingStatement.status == status)

        return query.order_by(BillingStatement.billing_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def list_transactions(
        db: Session,
        cer_id: int,
        tenant_id: str,
        member_id: Optional[int] = None,
        statement_id: Optional[int] = None,
        transaction_type: Optional[TransactionType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BillingTransaction]:
        """List billing transactions"""
        query = db.query(BillingTransaction).filter(
            and_(
                BillingTransaction.cer_id == cer_id,
                BillingTransaction.tenant_id == tenant_id,
                BillingTransaction.deleted_at.is_(None),
            )
        )

        if member_id:
            query = query.filter(BillingTransaction.member_id == member_id)
        if statement_id:
            query = query.filter(BillingTransaction.statement_id == statement_id)
        if transaction_type:
            query = query.filter(BillingTransaction.transaction_type == transaction_type)

        return query.order_by(BillingTransaction.created_at.desc()).offset(skip).limit(limit).all()


# Export service instance
billing_service = BillingService()
