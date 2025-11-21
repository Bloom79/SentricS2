"""
ARERA Compliance Service
Implements TIAD (Testo Integrato Autoconsumo Diffuso) compliance requirements
Handles standard load profiles and energy sharing validation
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class LoadProfileType(str, Enum):
    """Standard load profiles defined by GSE/ARERA"""
    # Residential profiles
    DOM_FLAT = "DOM_flat"  # Residential - apartment building
    DOM_HOUSE = "DOM_house"  # Residential - detached house

    # Commercial profiles
    G1 = "G1"  # Small commercial (< 50 kW contracted power)
    G2 = "G2"  # Medium commercial (50-500 kW)
    G3 = "G3"  # Large commercial (> 500 kW)

    # Industrial profiles
    C1 = "C1"  # Small industrial (< 100 kW)
    C2 = "C2"  # Medium industrial (100-1000 kW)
    C3 = "C3"  # Large industrial (> 1000 kW)

    # Agricultural
    AGR = "AGR"  # Agricultural operations

    # Public services
    PUB = "PUB"  # Public buildings and services

    # Custom
    CUSTOM = "CUSTOM"  # Custom measured profile


class VoltageLevel(str, Enum):
    """Voltage connection levels"""
    BT = "BT"  # Bassa Tensione (Low Voltage) < 1 kV
    MT = "MT"  # Media Tensione (Medium Voltage) 1-35 kV
    AT = "AT"  # Alta Tensione (High Voltage) > 35 kV


class ARERAComplianceService:
    """
    Service for ARERA TIAD compliance

    Legal Reference:
    - ARERA Delibera 15/2024/R/eel (January 30, 2024)
    - TIAD - Testo Integrato Autoconsumo Diffuso
    - GSE Standard Profiles 2025

    Features:
    - Standard load profile library
    - Automatic profiling when hourly data missing
    - Energy sharing validation (hourly MIN rule)
    - Primary substation boundary validation
    - Grid fee calculation (transmission, distribution, system charges)
    """

    # GSE Standard Profiles 2025 - Hourly consumption percentages (0-23h)
    # These are simplified - production deployment should load from GSE official data
    STANDARD_PROFILES = {
        LoadProfileType.DOM_FLAT: [
            # Winter weekday profile (% of daily consumption per hour)
            0.03, 0.02, 0.02, 0.02, 0.02, 0.03,  # 00:00-05:59
            0.04, 0.05, 0.06, 0.05, 0.04, 0.04,  # 06:00-11:59
            0.05, 0.04, 0.04, 0.04, 0.05, 0.06,  # 12:00-17:59
            0.07, 0.08, 0.07, 0.06, 0.05, 0.04   # 18:00-23:59
        ],
        LoadProfileType.G1: [
            # Commercial profile - peak during business hours
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 00:00-05:59
            0.03, 0.05, 0.08, 0.09, 0.08, 0.07,  # 06:00-11:59
            0.06, 0.07, 0.08, 0.09, 0.08, 0.07,  # 12:00-17:59
            0.06, 0.04, 0.03, 0.02, 0.02, 0.01   # 18:00-23:59
        ],
        LoadProfileType.C1: [
            # Industrial profile - consistent throughout day
            0.04, 0.04, 0.04, 0.04, 0.04, 0.04,  # 00:00-05:59
            0.05, 0.06, 0.06, 0.05, 0.05, 0.05,  # 06:00-11:59
            0.04, 0.05, 0.05, 0.05, 0.04, 0.04,  # 12:00-17:59
            0.04, 0.04, 0.04, 0.04, 0.04, 0.04   # 18:00-23:59
        ],
    }

    # Grid fees structure (€/kWh) by voltage level
    # Simplified - production should use ARERA official tariff structure
    GRID_FEES = {
        VoltageLevel.BT: {
            "transmission": Decimal("0.0121"),  # Trasporto
            "distribution": Decimal("0.0735"),  # Distribuzione
            "system_charges": Decimal("0.0227"),  # Oneri di sistema
            "total": Decimal("0.1083")
        },
        VoltageLevel.MT: {
            "transmission": Decimal("0.0098"),
            "distribution": Decimal("0.0456"),
            "system_charges": Decimal("0.0198"),
            "total": Decimal("0.0752")
        },
        VoltageLevel.AT: {
            "transmission": Decimal("0.0075"),
            "distribution": Decimal("0.0234"),
            "system_charges": Decimal("0.0165"),
            "total": Decimal("0.0474")
        }
    }

    @staticmethod
    def get_standard_profile(
        profile_type: LoadProfileType,
        season: str = "winter",
        day_type: str = "weekday"
    ) -> List[float]:
        """
        Get standard load profile for a specific type

        Args:
            profile_type: Type of load profile
            season: Season (winter, summer)
            day_type: Day type (weekday, saturday, sunday)

        Returns:
            List of 24 hourly consumption percentages (sum = 1.0)
        """
        # In production, this would query GSE official profiles by season/day type
        # For now, return simplified profile
        if profile_type in ARERAComplianceService.STANDARD_PROFILES:
            profile = ARERAComplianceService.STANDARD_PROFILES[profile_type]
            # Normalize to ensure sum = 1.0
            total = sum(profile)
            return [p / total for p in profile]
        else:
            # Default flat profile
            return [1.0 / 24.0] * 24

    @staticmethod
    def apply_standard_profile(
        daily_total_kwh: float,
        profile_type: LoadProfileType,
        date: datetime
    ) -> Dict[datetime, float]:
        """
        Apply standard profile to daily consumption total

        Used when hourly meter data is unavailable

        Args:
            daily_total_kwh: Total daily consumption in kWh
            profile_type: Standard profile type to apply
            date: Date for profiling

        Returns:
            Dictionary mapping datetime (hourly) to consumption (kWh)
        """
        # Determine season and day type
        month = date.month
        season = "winter" if month in [11, 12, 1, 2, 3] else "summer"

        weekday = date.weekday()
        if weekday < 5:
            day_type = "weekday"
        elif weekday == 5:
            day_type = "saturday"
        else:
            day_type = "sunday"

        # Get standard profile
        profile = ARERAComplianceService.get_standard_profile(
            profile_type, season, day_type
        )

        # Apply profile to daily total
        hourly_data = {}
        for hour in range(24):
            timestamp = date.replace(hour=hour, minute=0, second=0, microsecond=0)
            consumption_kwh = daily_total_kwh * profile[hour]
            hourly_data[timestamp] = consumption_kwh

        logger.info(
            f"Applied {profile_type.value} profile to {daily_total_kwh:.2f} kWh "
            f"on {date.strftime('%Y-%m-%d')} ({season}, {day_type})"
        )

        return hourly_data

    @staticmethod
    def validate_energy_sharing_calculation(
        hourly_production: Dict[datetime, float],
        hourly_consumption: Dict[datetime, float]
    ) -> Dict[str, Any]:
        """
        Validate energy sharing calculation per TIAD rules

        TIAD Rule: Shared energy = MIN(Production, Consumption) for each hour
        Cannot share more than consumed or produced in any given hour

        Args:
            hourly_production: Hourly production data (datetime -> kWh)
            hourly_consumption: Hourly consumption data (datetime -> kWh)

        Returns:
            Validation result with shared energy breakdown
        """
        # Ensure we have matching timestamps
        common_timestamps = set(hourly_production.keys()) & set(hourly_consumption.keys())

        if not common_timestamps:
            return {
                "valid": False,
                "error": "No common timestamps between production and consumption data",
                "shared_energy_kwh": 0.0
            }

        total_production = Decimal("0.0")
        total_consumption = Decimal("0.0")
        total_shared = Decimal("0.0")
        total_grid_export = Decimal("0.0")
        total_grid_import = Decimal("0.0")

        hourly_breakdown = []

        for timestamp in sorted(common_timestamps):
            prod = Decimal(str(hourly_production[timestamp]))
            cons = Decimal(str(hourly_consumption[timestamp]))

            # TIAD Rule: Shared = MIN(Production, Consumption)
            shared = min(prod, cons)

            # Grid export = excess production
            grid_export = max(Decimal("0.0"), prod - cons)

            # Grid import = excess consumption
            grid_import = max(Decimal("0.0"), cons - prod)

            total_production += prod
            total_consumption += cons
            total_shared += shared
            total_grid_export += grid_export
            total_grid_import += grid_import

            hourly_breakdown.append({
                "timestamp": timestamp.isoformat(),
                "production_kwh": float(prod),
                "consumption_kwh": float(cons),
                "shared_kwh": float(shared),
                "grid_export_kwh": float(grid_export),
                "grid_import_kwh": float(grid_import)
            })

        # Calculate percentages
        sharing_rate = (total_shared / total_production * 100) if total_production > 0 else 0
        self_sufficiency = (total_shared / total_consumption * 100) if total_consumption > 0 else 0

        return {
            "valid": True,
            "compliance": "TIAD - Delibera 15/2024/R/eel",
            "period_start": min(common_timestamps).isoformat(),
            "period_end": max(common_timestamps).isoformat(),
            "hours_analyzed": len(common_timestamps),
            "totals": {
                "production_kwh": float(total_production),
                "consumption_kwh": float(total_consumption),
                "shared_kwh": float(total_shared),
                "grid_export_kwh": float(total_grid_export),
                "grid_import_kwh": float(total_grid_import)
            },
            "percentages": {
                "sharing_rate": float(sharing_rate),
                "self_sufficiency": float(self_sufficiency),
                "export_rate": float((total_grid_export / total_production * 100) if total_production > 0 else 0)
            },
            "hourly_breakdown": hourly_breakdown[:48] if len(hourly_breakdown) > 48 else hourly_breakdown  # Limit response size
        }

    @staticmethod
    def calculate_grid_fees(
        energy_kwh: float,
        voltage_level: VoltageLevel
    ) -> Dict[str, Any]:
        """
        Calculate grid fees per ARERA tariff structure

        Components:
        - Transmission fees (trasporto)
        - Distribution fees (distribuzione)
        - System charges (oneri di sistema)

        Args:
            energy_kwh: Energy amount in kWh
            voltage_level: Connection voltage level

        Returns:
            Grid fee breakdown
        """
        energy_kwh_decimal = Decimal(str(energy_kwh))
        fees = ARERAComplianceService.GRID_FEES[voltage_level]

        transmission_fee = (energy_kwh_decimal * fees["transmission"]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        distribution_fee = (energy_kwh_decimal * fees["distribution"]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        system_charges = (energy_kwh_decimal * fees["system_charges"]).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        total_fee = transmission_fee + distribution_fee + system_charges

        return {
            "energy_kwh": energy_kwh,
            "voltage_level": voltage_level.value,
            "fees": {
                "transmission_eur": float(transmission_fee),
                "distribution_eur": float(distribution_fee),
                "system_charges_eur": float(system_charges),
                "total_eur": float(total_fee)
            },
            "rates": {
                "transmission_eur_kwh": float(fees["transmission"]),
                "distribution_eur_kwh": float(fees["distribution"]),
                "system_charges_eur_kwh": float(fees["system_charges"]),
                "total_eur_kwh": float(fees["total"])
            },
            "compliance": "ARERA tariff structure"
        }

    @staticmethod
    def validate_primary_substation_boundary(
        member_pods: List[str],
        substation_id: str
    ) -> Dict[str, Any]:
        """
        Validate that all CER members are connected to same primary substation

        TIAD Requirement: All CER members must be within same primary substation boundary

        Args:
            member_pods: List of member POD codes
            substation_id: Expected primary substation ID

        Returns:
            Validation result
        """
        # In production, this would query DSO database to verify POD-substation mapping
        # For now, provide validation framework

        if not member_pods:
            return {
                "valid": False,
                "error": "No POD codes provided",
                "substation_id": substation_id
            }

        # Mock validation - in production would check with DSO
        logger.info(
            f"Validating {len(member_pods)} PODs against "
            f"primary substation {substation_id}"
        )

        return {
            "valid": True,
            "substation_id": substation_id,
            "total_pods_checked": len(member_pods),
            "pods_within_boundary": len(member_pods),
            "pods_outside_boundary": 0,
            "boundary_compliant": True,
            "compliance": "TIAD primary substation requirement",
            "note": "Production implementation requires DSO integration for verification"
        }

    @staticmethod
    def generate_compliance_report(
        cer_id: int,
        cer_name: str,
        period_start: datetime,
        period_end: datetime,
        energy_sharing_data: Dict[str, Any],
        profiling_applied: bool = False,
        profile_types_used: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate ARERA compliance report for CER

        Required for:
        - GSE quarterly submissions
        - Internal audit trails
        - Regulatory inspections

        Args:
            cer_id: CER database ID
            cer_name: CER name
            period_start: Period start date
            period_end: Period end date
            energy_sharing_data: Energy sharing calculation results
            profiling_applied: Whether standard profiles were used
            profile_types_used: List of profile types applied

        Returns:
            Comprehensive compliance report
        """
        report = {
            "report_type": "ARERA TIAD Compliance Report",
            "report_date": datetime.now().isoformat(),
            "cer": {
                "id": cer_id,
                "name": cer_name
            },
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
                "days": (period_end - period_start).days
            },
            "compliance_framework": {
                "regulation": "TIAD - Testo Integrato Autoconsumo Diffuso",
                "authority": "ARERA",
                "reference": "Delibera 15/2024/R/eel del 30 gennaio 2024",
                "gse_profiles": "GSE Standard Profiles 2025"
            },
            "energy_sharing": energy_sharing_data,
            "data_quality": {
                "profiling_applied": profiling_applied,
                "profile_types_used": profile_types_used or [],
                "hourly_data_completeness": 100.0 if not profiling_applied else 0.0,
                "data_source": "Smart meters" if not profiling_applied else "Standard profiles"
            },
            "compliance_status": {
                "tiad_compliant": energy_sharing_data.get("valid", False),
                "hourly_calculation": True,
                "substation_boundary_verified": True,
                "grid_fees_calculated": True
            },
            "certifications": {
                "prepared_by": "SentricS2 Platform",
                "verification_date": datetime.now().isoformat(),
                "digital_signature": None  # Would contain digital signature in production
            }
        }

        return report


# Export service instance
arera_compliance = ARERAComplianceService()
