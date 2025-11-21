"""
Energy Sharing Calculator Service
Calculates energy sharing within a CER according to Italian ARERA regulations

This is the CORE service for CER platforms - calculates how energy is shared
between producers and consumers, and distributes TCEC incentives.

Legal Framework:
- D.M. 414/2023 (Decreto CER)
- ARERA Resolution 727/2022/R/eel
- Testo Integrato Autoconsumo Diffuso (TIAD)
"""

from typing import Dict, List, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import logging

from app.models.cer import CER, CERMember
from app.models.billing import BillingStatement
from app.services.incentive_rate_manager import (
    IncentiveRateManager,
    ItalianZone,
    PlantSizeCategory,
    TimeSlot,
)
from app.services.arera_compliance import arera_compliance, LoadProfileType

logger = logging.getLogger(__name__)


class MeterData:
    """Container for hourly meter readings"""

    def __init__(
        self,
        timestamp: datetime,
        production_kwh: Decimal = Decimal("0"),
        consumption_kwh: Decimal = Decimal("0"),
    ):
        self.timestamp = timestamp
        self.production_kwh = production_kwh
        self.consumption_kwh = consumption_kwh


class MemberEnergyData:
    """Container for member's energy data"""

    def __init__(
        self,
        member_id: int,
        member_name: str,
        member_type: str,
        load_profile_type: str,
    ):
        self.member_id = member_id
        self.member_name = member_name
        self.member_type = member_type
        self.load_profile_type = load_profile_type
        self.hourly_consumption: Dict[datetime, Decimal] = {}
        self.hourly_production: Dict[datetime, Decimal] = {}


class EnergySharingResult:
    """Result of energy sharing calculation for one billing period"""

    def __init__(self, cer_id: int, period_start: date, period_end: date):
        self.cer_id = cer_id
        self.period_start = period_start
        self.period_end = period_end
        self.member_results: Dict[int, Dict] = {}
        self.total_shared_energy_kwh: Decimal = Decimal("0")
        self.total_incentives_eur: Decimal = Decimal("0")
        self.hourly_details: List[Dict] = []


class EnergyShareCalculator:
    """
    Core energy sharing calculation engine for CER.

    Algorithm Overview:
    1. Fetch all hourly production data from CER plants
    2. Fetch all hourly consumption data from CER members
    3. For each hour:
       - Calculate shared energy: min(total_production, total_consumption)
       - Allocate shared energy to members proportionally to their consumption
       - Calculate TCEC incentive based on zone, time-of-use, plant size
    4. Aggregate monthly totals
    5. Generate billing statements

    Energy Matching Rules (ARERA):
    - Production and consumption must occur in same hour
    - Shared energy = MIN(production, consumption) in that hour
    - Self-consumption is excluded (already incentivized differently)
    """

    def __init__(self):
        self.incentive_manager = IncentiveRateManager()

    async def calculate_monthly_sharing(
        self,
        db: Session,
        cer_id: int,
        month: int,
        year: int,
    ) -> EnergySharingResult:
        """
        Calculate energy sharing for all members for a given month.

        Args:
            db: Database session
            cer_id: CER ID
            month: Month (1-12)
            year: Year

        Returns:
            EnergySharingResult with member billing data

        Raises:
            ValueError: If CER not found or no data available
        """
        # Get CER
        cer = db.query(CER).filter(CER.id == cer_id).first()
        if not cer:
            raise ValueError(f"CER {cer_id} not found")

        # Define period
        period_start = date(year, month, 1)
        if month == 12:
            period_end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = date(year, month + 1, 1) - timedelta(days=1)

        logger.info(
            f"Calculating energy sharing for CER {cer.name} ({cer_id}) "
            f"for period {period_start} to {period_end}"
        )

        # Initialize result
        result = EnergySharingResult(cer_id, period_start, period_end)

        # Step 1: Fetch production data from all CER plants
        production_data = await self._fetch_plant_production_data(
            db, cer, period_start, period_end
        )

        # Step 2: Fetch consumption data from all CER members
        member_data = await self._fetch_member_consumption_data(
            db, cer, period_start, period_end
        )

        # Step 3: Calculate hourly sharing
        hourly_results = self._calculate_hourly_sharing(
            cer, production_data, member_data
        )
        result.hourly_details = hourly_results

        # Step 4: Aggregate member totals
        member_totals = self._aggregate_member_totals(hourly_results)
        result.member_results = member_totals

        # Step 5: Calculate totals
        result.total_shared_energy_kwh = sum(
            m["shared_energy_kwh"] for m in member_totals.values()
        )
        result.total_incentives_eur = sum(
            m["incentive_amount_eur"] for m in member_totals.values()
        )

        logger.info(
            f"Calculation complete: {result.total_shared_energy_kwh:.2f} kWh shared, "
            f"€{result.total_incentives_eur:.2f} in incentives"
        )

        return result

    async def _fetch_plant_production_data(
        self,
        db: Session,
        cer: CER,
        period_start: date,
        period_end: date,
    ) -> Dict[datetime, Decimal]:
        """
        Fetch hourly production data from all plants linked to the CER.

        In production, this would query a meter_readings or energy_production table.
        For now, returns empty dict - will be implemented when meter data tables exist.

        Args:
            db: Database session
            cer: CER instance
            period_start: Start date
            period_end: End date

        Returns:
            Dict mapping timestamp -> total_production_kwh
        """
        # TODO: Implement actual meter data fetching
        # Query structure would be:
        #
        # SELECT
        #     timestamp,
        #     SUM(production_kwh) as total_production
        # FROM plant_meter_readings
        # WHERE plant_id IN (SELECT id FROM plants WHERE cer_id = :cer_id)
        #   AND timestamp BETWEEN :start AND :end
        # GROUP BY timestamp
        # ORDER BY timestamp

        logger.warning(
            f"Plant production data fetching not yet implemented. "
            f"Using mock data for CER {cer.id}"
        )

        # Return empty dict for now
        # In real implementation, this would return hourly production data
        return {}

    async def _fetch_member_consumption_data(
        self,
        db: Session,
        cer: CER,
        period_start: date,
        period_end: date,
    ) -> List[MemberEnergyData]:
        """
        Fetch hourly consumption data for all active CER members.

        If hourly meter data is not available, applies ARERA standard load profiles.

        Args:
            db: Database session
            cer: CER instance
            period_start: Start date
            period_end: End date

        Returns:
            List of MemberEnergyData instances
        """
        # Get all active members
        members = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.cer_id == cer.id,
                    CERMember.status == "active",
                    CERMember.is_active == True,
                )
            )
            .all()
        )

        member_data_list = []

        for member in members:
            member_data = MemberEnergyData(
                member_id=member.id,
                member_name=member.name,
                member_type=member.member_type,
                load_profile_type=member.load_profile_type,
            )

            # Try to fetch actual meter data
            hourly_data = await self._fetch_member_meter_data(
                db, member, period_start, period_end
            )

            if not hourly_data:
                # No meter data available - apply ARERA load profile
                logger.info(
                    f"No meter data for member {member.name} ({member.id}). "
                    f"Applying ARERA {member.load_profile_type} load profile."
                )
                hourly_data = self._apply_load_profile(
                    member, period_start, period_end
                )

            member_data.hourly_consumption = hourly_data
            member_data_list.append(member_data)

        logger.info(f"Fetched data for {len(member_data_list)} members")
        return member_data_list

    async def _fetch_member_meter_data(
        self,
        db: Session,
        member: CERMember,
        period_start: date,
        period_end: date,
    ) -> Dict[datetime, Decimal]:
        """
        Fetch actual hourly meter data for a member.

        TODO: Implement when meter_readings table exists

        Args:
            db: Database session
            member: CERMember instance
            period_start: Start date
            period_end: End date

        Returns:
            Dict mapping timestamp -> consumption_kwh (empty if no data)
        """
        # TODO: Query meter_readings table
        # SELECT timestamp, consumption_kwh
        # FROM member_meter_readings
        # WHERE member_id = :member_id
        #   AND timestamp BETWEEN :start AND :end
        # ORDER BY timestamp

        return {}

    def _apply_load_profile(
        self,
        member: CERMember,
        period_start: date,
        period_end: date,
    ) -> Dict[datetime, Decimal]:
        """
        Apply ARERA standard load profile when meter data is unavailable.

        Uses the member's monthly consumption (if known) and distributes it
        across hours using ARERA's standard profiles.

        Args:
            member: CERMember instance
            period_start: Start date
            period_end: End date

        Returns:
            Dict mapping timestamp -> estimated_consumption_kwh
        """
        # Map member load profile type to ARERA profile type
        profile_mapping = {
            "residential": LoadProfileType.RESIDENTIAL,
            "commercial": LoadProfileType.COMMERCIAL,
            "industrial": LoadProfileType.INDUSTRIAL,
        }

        profile_type = profile_mapping.get(
            member.load_profile_type, LoadProfileType.RESIDENTIAL
        )

        # TODO: Get member's known monthly consumption from historical data
        # For now, use a default based on contracted power
        estimated_monthly_kwh = Decimal("300")  # Default 300 kWh/month
        if member.contracted_power:
            # Rough estimate: 150 hours/month * contracted_power_kw
            estimated_monthly_kwh = Decimal(str(member.contracted_power)) * Decimal(
                "150"
            )

        # Generate hourly profile for the period
        hourly_data = {}
        current_date = period_start

        while current_date <= period_end:
            # Get daily profile from ARERA compliance service
            daily_kwh = estimated_monthly_kwh / Decimal("30")  # Rough daily average
            daily_profile = arera_compliance.apply_standard_load_profile(
                float(daily_kwh), profile_type, current_date
            )

            # Add to hourly_data
            for hour_str, kwh in daily_profile.items():
                timestamp = datetime.fromisoformat(hour_str)
                hourly_data[timestamp] = Decimal(str(kwh))

            current_date += timedelta(days=1)

        return hourly_data

    def _calculate_hourly_sharing(
        self,
        cer: CER,
        production_data: Dict[datetime, Decimal],
        member_data: List[MemberEnergyData],
    ) -> List[Dict]:
        """
        Calculate energy sharing for each hour.

        Core Algorithm:
        1. For each hour:
           - shared_energy = MIN(total_production, total_consumption)
           - For each member:
             * member_share = shared_energy * (member_consumption / total_consumption)
             * member_incentive = calculate_tcec_incentive(member_share, hour, zone)

        Args:
            cer: CER instance
            production_data: Hourly production from plants
            member_data: List of MemberEnergyData

        Returns:
            List of hourly calculation results
        """
        hourly_results = []

        # Get all unique timestamps (union of production and consumption timestamps)
        all_timestamps = set(production_data.keys())
        for member in member_data:
            all_timestamps.update(member.hourly_consumption.keys())

        all_timestamps = sorted(all_timestamps)

        logger.info(f"Processing {len(all_timestamps)} hours of data")

        for timestamp in all_timestamps:
            # Get production for this hour
            production_kwh = production_data.get(timestamp, Decimal("0"))

            # Get total consumption for this hour
            member_consumptions = {}
            total_consumption_kwh = Decimal("0")

            for member in member_data:
                consumption = member.hourly_consumption.get(timestamp, Decimal("0"))
                member_consumptions[member.member_id] = consumption
                total_consumption_kwh += consumption

            # Calculate shared energy (min of production and consumption)
            shared_energy_kwh = min(production_kwh, total_consumption_kwh)

            # If no energy shared this hour, skip
            if shared_energy_kwh == 0:
                continue

            # Allocate shared energy to members proportionally
            hour_result = {
                "timestamp": timestamp,
                "production_kwh": float(production_kwh),
                "consumption_kwh": float(total_consumption_kwh),
                "shared_energy_kwh": float(shared_energy_kwh),
                "member_shares": {},
            }

            for member in member_data:
                member_consumption = member_consumptions[member.member_id]

                if member_consumption == 0:
                    continue

                # Calculate member's share of shared energy (proportional allocation)
                member_share_kwh = shared_energy_kwh * (
                    member_consumption / total_consumption_kwh
                )

                # Calculate TCEC incentive for this member's share
                incentive_eur = self._calculate_hourly_incentive(
                    cer, member_share_kwh, timestamp
                )

                hour_result["member_shares"][member.member_id] = {
                    "member_name": member.member_name,
                    "consumption_kwh": float(member_consumption),
                    "shared_energy_kwh": float(member_share_kwh),
                    "incentive_eur": float(incentive_eur),
                }

            hourly_results.append(hour_result)

        return hourly_results

    def _calculate_hourly_incentive(
        self,
        cer: CER,
        shared_energy_kwh: Decimal,
        timestamp: datetime,
    ) -> Decimal:
        """
        Calculate TCEC incentive for shared energy in one hour.

        Uses IncentiveRateManager to get the correct rate based on:
        - CER total capacity (determines plant size category)
        - Geographic zone (from CER region)
        - Time of use (F1/F2/F3 based on timestamp)

        Args:
            cer: CER instance
            shared_energy_kwh: Amount of shared energy (kWh)
            timestamp: Timestamp of the hour

        Returns:
            Incentive amount in EUR
        """
        # Convert kWh to MWh for rate calculation
        shared_energy_mwh = shared_energy_kwh / Decimal("1000")

        # Map region to Italian zone (simplified - should use a proper mapping)
        zone_mapping = {
            "Lombardia": ItalianZone.NORD,
            "Piemonte": ItalianZone.NORD,
            "Veneto": ItalianZone.NORD,
            "Emilia-Romagna": ItalianZone.CNOR,
            "Toscana": ItalianZone.CNOR,
            "Lazio": ItalianZone.CSUD,
            "Campania": ItalianZone.CSUD,
            "Puglia": ItalianZone.SUD,
            "Calabria": ItalianZone.SUD,
            "Sicilia": ItalianZone.SICI,
            "Sardegna": ItalianZone.SARD,
        }
        zone = zone_mapping.get(cer.region, ItalianZone.CNOR)

        # Calculate TCEC rate
        try:
            tcec_rate_eur_per_mwh = self.incentive_manager.calculate_tcec_rate(
                power_kw=cer.total_capacity,
                zone=zone,
                timestamp=timestamp,
            )

            # Calculate incentive amount
            incentive_eur = shared_energy_mwh * Decimal(str(tcec_rate_eur_per_mwh))

            return incentive_eur.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        except Exception as e:
            logger.error(f"Error calculating TCEC incentive: {e}")
            return Decimal("0")

    def _aggregate_member_totals(
        self, hourly_results: List[Dict]
    ) -> Dict[int, Dict]:
        """
        Aggregate hourly results into monthly totals per member.

        Args:
            hourly_results: List of hourly calculation results

        Returns:
            Dict mapping member_id -> {shared_energy_kwh, incentive_amount_eur, ...}
        """
        member_totals = {}

        for hour in hourly_results:
            for member_id, member_share in hour["member_shares"].items():
                if member_id not in member_totals:
                    member_totals[member_id] = {
                        "member_id": member_id,
                        "member_name": member_share["member_name"],
                        "shared_energy_kwh": Decimal("0"),
                        "total_consumption_kwh": Decimal("0"),
                        "incentive_amount_eur": Decimal("0"),
                        "hours_with_sharing": 0,
                    }

                member_totals[member_id]["shared_energy_kwh"] += Decimal(
                    str(member_share["shared_energy_kwh"])
                )
                member_totals[member_id]["total_consumption_kwh"] += Decimal(
                    str(member_share["consumption_kwh"])
                )
                member_totals[member_id]["incentive_amount_eur"] += Decimal(
                    str(member_share["incentive_eur"])
                )
                member_totals[member_id]["hours_with_sharing"] += 1

        # Round all decimal values
        for member_data in member_totals.values():
            member_data["shared_energy_kwh"] = member_data[
                "shared_energy_kwh"
            ].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            member_data["total_consumption_kwh"] = member_data[
                "total_consumption_kwh"
            ].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            member_data["incentive_amount_eur"] = member_data[
                "incentive_amount_eur"
            ].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return member_totals

    async def generate_billing_statements(
        self,
        db: Session,
        cer_id: int,
        sharing_result: EnergySharingResult,
    ) -> List[BillingStatement]:
        """
        Generate billing statements from energy sharing results.

        Creates BillingStatement records for each member with:
        - Shared energy amounts
        - TCEC incentive credits
        - Community fund contributions (if applicable)
        - Grid fees (if applicable)

        Args:
            db: Database session
            cer_id: CER ID
            sharing_result: EnergySharingResult from calculation

        Returns:
            List of created BillingStatement instances
        """
        statements = []

        # Calculate billing period dates
        period_start_dt = datetime.combine(
            sharing_result.period_start, datetime.min.time()
        )
        period_end_dt = datetime.combine(
            sharing_result.period_end, datetime.max.time()
        )

        # Due date: 30 days after period end
        due_date = period_end_dt + timedelta(days=30)

        for member_id, member_data in sharing_result.member_results.items():
            # Create billing statement
            statement = BillingStatement(
                tenant_id=db.query(CER).filter(CER.id == cer_id).first().tenant_id,
                cer_id=cer_id,
                member_id=member_id,
                period_start=period_start_dt,
                period_end=period_end_dt,
                billing_date=datetime.now(),
                due_date=due_date,
                # Energy metrics
                energy_shared=float(member_data["shared_energy_kwh"]),
                energy_consumed=float(member_data["total_consumption_kwh"]),
                energy_produced=0.0,  # TODO: Add production for prosumers
                # Financial amounts
                incentives=float(member_data["incentive_amount_eur"]),
                shared_energy_value=float(member_data["incentive_amount_eur"]),
                total_amount=float(member_data["incentive_amount_eur"]),  # Credit
                balance=float(member_data["incentive_amount_eur"]),
                status="draft",
                # Metadata
                extra_metadata={
                    "hours_with_sharing": member_data["hours_with_sharing"],
                    "calculation_date": datetime.now().isoformat(),
                },
            )

            db.add(statement)
            statements.append(statement)

        # Commit all statements
        db.commit()

        logger.info(
            f"Generated {len(statements)} billing statements for CER {cer_id}"
        )

        return statements


# Singleton instance
energy_share_calculator = EnergyShareCalculator()
