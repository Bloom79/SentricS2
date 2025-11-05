"""
Energy Service - Business logic for CER energy sharing calculations
Implements the autoconsumo diffuso (diffuse self-consumption) model
REFACTORED: Reduced complexity by extracting helper methods
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta, timezone
import logging

from app.models.cer import CER, CERMember
from app.models.energy_transaction import (
    EnergyTransaction,
    EnergySharingCalculation,
    TransactionType,
)
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class EnergyService(BaseService):
    """Service for energy sharing calculations and transactions"""

    @staticmethod
    def _verify_cer(db: Session, cer_id: int, tenant_id: str) -> CER:
        """
        Verify CER exists and user has access

        Raises:
            ValueError if CER not found
        """
        cer = BaseService._get_by_id(db, CER, cer_id, tenant_id)
        if not cer:
            raise ValueError("CER not found")
        return cer

    @staticmethod
    def _get_active_members(db: Session, cer_id: int, tenant_id: str) -> List[CERMember]:
        """
        Get all active members for a CER

        Returns:
            List of active CERMember instances
        """
        return (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.cer_id == cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                    CERMember.status == "active",
                )
            )
            .all()
        )

    @staticmethod
    def _get_period_transactions(
        db: Session, cer_id: int, tenant_id: str, period_start: datetime, period_end: datetime
    ) -> List[EnergyTransaction]:
        """
        Get all transactions for a CER within a time period

        Returns:
            List of EnergyTransaction instances ordered by timestamp
        """
        return (
            db.query(EnergyTransaction)
            .filter(
                and_(
                    EnergyTransaction.cer_id == cer_id,
                    EnergyTransaction.tenant_id == tenant_id,
                    EnergyTransaction.timestamp >= period_start,
                    EnergyTransaction.timestamp < period_end,
                    EnergyTransaction.deleted_at.is_(None),
                )
            )
            .order_by(EnergyTransaction.timestamp)
            .all()
        )

    @staticmethod
    def _aggregate_hourly_data(transactions: List[EnergyTransaction]) -> Dict[datetime, Dict]:
        """
        Aggregate transactions into hourly buckets

        Returns:
            Dictionary with hour_key -> {production, consumption, by_member}
        """
        hourly_data = {}
        for tx in transactions:
            hour_key = tx.timestamp.replace(minute=0, second=0, microsecond=0)
            if hour_key not in hourly_data:
                hourly_data[hour_key] = {"production": 0.0, "consumption": 0.0, "by_member": {}}

            if tx.transaction_type == TransactionType.PRODUCTION:
                hourly_data[hour_key]["production"] += tx.energy_kwh
            elif tx.transaction_type == TransactionType.CONSUMPTION:
                hourly_data[hour_key]["consumption"] += tx.energy_kwh

                # Track consumption by member
                if tx.member_id:
                    if tx.member_id not in hourly_data[hour_key]["by_member"]:
                        hourly_data[hour_key]["by_member"][tx.member_id] = {
                            "production": 0.0,
                            "consumption": 0.0,
                        }
                    hourly_data[hour_key]["by_member"][tx.member_id]["consumption"] += tx.energy_kwh

        return hourly_data

    @staticmethod
    def _calculate_hourly_sharing(
        hourly_data: Dict[datetime, Dict], members: List[CERMember]
    ) -> Tuple[float, float, float, Dict[int, Dict]]:
        """
        Calculate shared energy for each hour and allocate to members

        Returns:
            Tuple of (total_production, total_consumption, total_shared, member_totals)
        """
        total_production = 0.0
        total_consumption = 0.0
        total_shared = 0.0
        member_totals = {
            m.id: {"production": 0.0, "consumption": 0.0, "shared": 0.0} for m in members
        }

        for hour_key, hour_data in hourly_data.items():
            hour_production = hour_data["production"]
            hour_consumption = hour_data["consumption"]
            hour_shared = min(hour_production, hour_consumption)

            total_production += hour_production
            total_consumption += hour_consumption
            total_shared += hour_shared

            # Allocate shared energy to members proportionally to consumption
            if hour_shared > 0 and hour_consumption > 0:
                for member_id, member_data in hour_data["by_member"].items():
                    if member_id in member_totals:
                        member_share = (member_data["consumption"] / hour_consumption) * hour_shared
                        member_totals[member_id]["shared"] += member_share
                        member_totals[member_id]["consumption"] += member_data["consumption"]

        return total_production, total_consumption, total_shared, member_totals

    @staticmethod
    def _calculate_self_consumed(transactions: List[EnergyTransaction]) -> float:
        """
        Calculate self-consumed energy from transactions

        Returns:
            Total self-consumed energy in kWh
        """
        self_consumed = 0.0
        for tx in transactions:
            if tx.transaction_type == TransactionType.SELF_CONSUMED:
                self_consumed += tx.energy_kwh
        return self_consumed

    @staticmethod
    def _calculate_grid_flows(
        total_production: float, total_shared: float, self_consumed: float, total_consumption: float
    ) -> Tuple[float, float]:
        """
        Calculate grid export and import

        Returns:
            Tuple of (grid_export, grid_import)
        """
        grid_export = max(0.0, total_production - total_shared - self_consumed)
        grid_import = max(0.0, total_consumption - total_shared - self_consumed)
        return grid_export, grid_import

    @staticmethod
    def _calculate_incentivized_energy(total_shared: float) -> float:
        """
        Calculate incentivized energy portion

        Formula: 55% of shared energy, with 90% adjustment for member types
        Returns:
            Incentivized energy in kWh
        """
        incentivized_energy = total_shared * 0.55  # Base rate
        incentivized_energy = incentivized_energy * 0.90  # Adjustment factor for PMI-UC
        return incentivized_energy

    @staticmethod
    def _build_member_allocation(
        member_totals: Dict[int, Dict], total_shared: float
    ) -> Dict[int, Dict]:
        """
        Build member allocation dictionary with percentages

        Returns:
            Dictionary mapping member_id -> {energy_shared, percentage, energy_consumed}
        """
        member_allocation = {}
        for member_id, totals in member_totals.items():
            if total_shared > 0:
                percentage = (totals["shared"] / total_shared) * 100
            else:
                percentage = 0.0

            member_allocation[member_id] = {
                "energy_shared": totals["shared"],
                "percentage": percentage,
                "energy_consumed": totals["consumption"],
            }

        return member_allocation

    @staticmethod
    def calculate_shared_energy(
        db: Session, cer_id: int, period_start: datetime, period_end: datetime, tenant_id: str
    ) -> Dict[str, Any]:
        """
        Calculate shared energy for a CER over a time period

        Formula: Shared Energy = min(Total Production, Total Consumption)
        Calculated hourly, then aggregated

        REFACTORED: Complexity reduced from 16 to ~7 by extracting helpers

        Returns calculation results including member allocations
        """
        # Verify CER exists
        EnergyService._verify_cer(db, cer_id, tenant_id)

        # Get all active members
        members = EnergyService._get_active_members(db, cer_id, tenant_id)

        # Get hourly transactions for the period
        transactions = EnergyService._get_period_transactions(
            db, cer_id, tenant_id, period_start, period_end
        )

        # Aggregate hourly data
        hourly_data = EnergyService._aggregate_hourly_data(transactions)

        # Calculate shared energy for each hour
        total_production, total_consumption, total_shared, member_totals = (
            EnergyService._calculate_hourly_sharing(hourly_data, members)
        )

        # Calculate self-consumed energy
        self_consumed = EnergyService._calculate_self_consumed(transactions)

        # Calculate grid export/import
        grid_export, grid_import = EnergyService._calculate_grid_flows(
            total_production, total_shared, self_consumed, total_consumption
        )

        # Calculate incentivized energy
        incentivized_energy = EnergyService._calculate_incentivized_energy(total_shared)

        # Build member allocation percentages
        member_allocation = EnergyService._build_member_allocation(member_totals, total_shared)

        return {
            "cer_id": cer_id,
            "period_start": period_start,
            "period_end": period_end,
            "total_production": total_production,
            "total_consumption": total_consumption,
            "shared_energy": total_shared,
            "self_consumed_energy": self_consumed,
            "grid_export": grid_export,
            "grid_import": grid_import,
            "incentivized_energy": incentivized_energy,
            "member_allocation": member_allocation,
            "calculation_date": datetime.now(timezone.utc),
        }

    @staticmethod
    def save_sharing_calculation(
        db: Session, calculation_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> EnergySharingCalculation:
        """Save energy sharing calculation result"""
        calculation = EnergySharingCalculation(
            tenant_id=tenant_id,
            cer_id=calculation_data["cer_id"],
            calculation_date=calculation_data["calculation_date"],
            period_start=calculation_data["period_start"],
            period_end=calculation_data["period_end"],
            total_production=calculation_data["total_production"],
            total_consumption=calculation_data["total_consumption"],
            shared_energy=calculation_data["shared_energy"],
            self_consumed_energy=calculation_data["self_consumed_energy"],
            grid_export=calculation_data["grid_export"],
            grid_import=calculation_data["grid_import"],
            incentivized_energy=calculation_data["incentivized_energy"],
            member_allocation=calculation_data["member_allocation"],
            created_by=user_id,
        )

        db.add(calculation)
        db.commit()
        db.refresh(calculation)

        logger.info(f"Saved energy sharing calculation for CER {calculation_data['cer_id']}")
        return calculation

    @staticmethod
    def create_transaction(
        db: Session,
        cer_id: int,
        transaction_type: TransactionType,
        energy_kwh: float,
        timestamp: datetime,
        tenant_id: str,
        user_id: int,
        member_id: Optional[int] = None,
        plant_id: Optional[int] = None,
        calculation_data: Optional[Dict[str, Any]] = None,
    ) -> EnergyTransaction:
        """Create an energy transaction"""
        # Verify CER exists
        EnergyService._verify_cer(db, cer_id, tenant_id)

        transaction = EnergyTransaction(
            tenant_id=tenant_id,
            cer_id=cer_id,
            transaction_type=transaction_type,
            energy_kwh=energy_kwh,
            timestamp=timestamp,
            member_id=member_id,
            plant_id=plant_id,
            calculation_data=calculation_data or {},
            created_by=user_id,
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        # Update member statistics if member_id provided
        if member_id:
            EnergyService._update_member_statistics(
                db, member_id, transaction_type, energy_kwh, tenant_id
            )

        logger.info(
            f"Created {transaction_type.value} transaction {energy_kwh}kWh for CER {cer_id}"
        )
        return transaction

    @staticmethod
    def _update_member_statistics(
        db: Session,
        member_id: int,
        transaction_type: TransactionType,
        energy_kwh: float,
        tenant_id: str,
    ):
        """Update member energy statistics"""
        member = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.id == member_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not member:
            return

        if transaction_type == TransactionType.PRODUCTION:
            member.energy_produced += energy_kwh
        elif transaction_type == TransactionType.CONSUMPTION:
            member.energy_consumed += energy_kwh
        elif transaction_type == TransactionType.SHARED:
            member.energy_shared += energy_kwh

        db.commit()

    @staticmethod
    def list_transactions(
        db: Session,
        cer_id: int,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        transaction_type: Optional[TransactionType] = None,
        member_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 1000,
    ) -> List[EnergyTransaction]:
        """List energy transactions for a CER"""
        query = db.query(EnergyTransaction).filter(
            and_(
                EnergyTransaction.cer_id == cer_id,
                EnergyTransaction.tenant_id == tenant_id,
                EnergyTransaction.deleted_at.is_(None),
            )
        )

        if start_date:
            query = query.filter(EnergyTransaction.timestamp >= start_date)
        if end_date:
            query = query.filter(EnergyTransaction.timestamp < end_date)
        if transaction_type:
            query = query.filter(EnergyTransaction.transaction_type == transaction_type)
        if member_id:
            query = query.filter(EnergyTransaction.member_id == member_id)

        return query.order_by(EnergyTransaction.timestamp.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_energy_statistics(
        db: Session,
        cer_id: int,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get energy statistics for a CER"""
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now(timezone.utc)
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Aggregate transactions
        stats = (
            db.query(
                EnergyTransaction.transaction_type,
                func.sum(EnergyTransaction.energy_kwh).label("total"),
            )
            .filter(
                and_(
                    EnergyTransaction.cer_id == cer_id,
                    EnergyTransaction.tenant_id == tenant_id,
                    EnergyTransaction.timestamp >= start_date,
                    EnergyTransaction.timestamp < end_date,
                    EnergyTransaction.deleted_at.is_(None),
                )
            )
            .group_by(EnergyTransaction.transaction_type)
            .all()
        )

        result = {
            "cer_id": cer_id,
            "period_start": start_date,
            "period_end": end_date,
            "production": 0.0,
            "consumption": 0.0,
            "shared": 0.0,
            "self_consumed": 0.0,
            "grid_export": 0.0,
            "grid_import": 0.0,
        }

        for stat in stats:
            if stat.transaction_type == TransactionType.PRODUCTION:
                result["production"] = stat.total or 0.0
            elif stat.transaction_type == TransactionType.CONSUMPTION:
                result["consumption"] = stat.total or 0.0
            elif stat.transaction_type == TransactionType.SHARED:
                result["shared"] = stat.total or 0.0
            elif stat.transaction_type == TransactionType.SELF_CONSUMED:
                result["self_consumed"] = stat.total or 0.0
            elif stat.transaction_type == TransactionType.GRID_EXPORT:
                result["grid_export"] = stat.total or 0.0
            elif stat.transaction_type == TransactionType.GRID_IMPORT:
                result["grid_import"] = stat.total or 0.0

        return result

    @staticmethod
    def get_latest_calculation(
        db: Session, cer_id: int, tenant_id: str
    ) -> Optional[EnergySharingCalculation]:
        """Get the latest energy sharing calculation for a CER"""
        return (
            db.query(EnergySharingCalculation)
            .filter(
                and_(
                    EnergySharingCalculation.cer_id == cer_id,
                    EnergySharingCalculation.tenant_id == tenant_id,
                    EnergySharingCalculation.deleted_at.is_(None),
                )
            )
            .order_by(EnergySharingCalculation.calculation_date.desc())
            .first()
        )


# Export service instance
energy_service = EnergyService()
