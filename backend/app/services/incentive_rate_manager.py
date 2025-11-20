"""
Incentive Rate Manager for Italian CER
Handles dynamic TCEC rates, zonale orario pricing, and PNRR funding calculations
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PlantSizeCategory(str, Enum):
    """Plant size categories for TCEC incentives"""
    SMALL = "small"  # ≤ 200 kW
    MEDIUM = "medium"  # > 200 kW and ≤ 600 kW
    LARGE = "large"  # > 600 kW and ≤ 1 MW


class ItalianZone(str, Enum):
    """Italian electricity zones"""
    NORD = "NORD"  # North Italy
    CNOR = "CNOR"  # Center-North Italy
    CSUD = "CSUD"  # Center-South Italy
    SUD = "SUD"  # South Italy
    SICI = "SICI"  # Sicily
    SARD = "SARD"  # Sardinia


class TimeSlot(str, Enum):
    """Italian electricity market time slots"""
    F1 = "F1"  # Peak: Mon-Fri 8:00-19:00
    F2 = "F2"  # Mid: Mon-Fri 7:00-8:00, 19:00-23:00, Sat 7:00-23:00
    F3 = "F3"  # Off-peak: All other hours


class IncentiveRateManager:
    """
    Service for managing Italian TCEC incentive rates and PNRR funding

    Legal Reference:
    - D.M. 414/2023 (Decreto CER)
    - GME (Gestore Mercati Energetici) zonal pricing
    """

    # Base TCEC rates by plant size (€/MWh) - D.M. 414/2023
    BASE_TCEC_RATES = {
        PlantSizeCategory.SMALL: {
            "min": Decimal("60.00"),
            "max": Decimal("120.00"),
            "typical": Decimal("110.00")
        },
        PlantSizeCategory.MEDIUM: {
            "min": Decimal("70.00"),
            "max": Decimal("110.00"),
            "typical": Decimal("100.00")
        },
        PlantSizeCategory.LARGE: {
            "min": Decimal("60.00"),
            "max": Decimal("100.00"),
            "typical": Decimal("90.00")
        }
    }

    # Zonal price adjustments (€/MWh) - Simplified, should come from GME API
    ZONAL_ADJUSTMENTS = {
        ItalianZone.NORD: Decimal("5.00"),
        ItalianZone.CNOR: Decimal("2.00"),
        ItalianZone.CSUD: Decimal("0.00"),
        ItalianZone.SUD: Decimal("-2.00"),
        ItalianZone.SICI: Decimal("-3.00"),
        ItalianZone.SARD: Decimal("-3.00"),
    }

    # Time slot multipliers for zonale orario pricing
    TIME_SLOT_MULTIPLIERS = {
        TimeSlot.F1: Decimal("1.15"),  # +15% during peak hours
        TimeSlot.F2: Decimal("1.00"),  # Base rate
        TimeSlot.F3: Decimal("0.85"),  # -15% during off-peak
    }

    # PNRR funding parameters
    PNRR_MAX_FUNDING_PERCENTAGE = Decimal("0.40")  # 40% of investment
    PNRR_MAX_COMUNE_POPULATION = 50000  # Extended from 5,000

    @staticmethod
    def determine_plant_size_category(power_kw: float) -> PlantSizeCategory:
        """
        Determine plant size category for TCEC rate calculation

        Args:
            power_kw: Plant nominal power in kW

        Returns:
            Plant size category
        """
        if power_kw <= 200:
            return PlantSizeCategory.SMALL
        elif power_kw <= 600:
            return PlantSizeCategory.MEDIUM
        else:
            return PlantSizeCategory.LARGE

    @staticmethod
    def determine_time_slot(timestamp: datetime) -> TimeSlot:
        """
        Determine Italian electricity market time slot

        F1 (Peak): Monday-Friday 8:00-19:00
        F2 (Mid): Monday-Friday 7:00-8:00, 19:00-23:00, Saturday 7:00-23:00
        F3 (Off-peak): All other hours (nights, Sundays, holidays)

        Args:
            timestamp: Datetime to classify

        Returns:
            Time slot
        """
        hour = timestamp.hour
        weekday = timestamp.weekday()  # 0 = Monday, 6 = Sunday

        # Sunday = F3
        if weekday == 6:
            return TimeSlot.F3

        # Saturday
        if weekday == 5:
            if 7 <= hour < 23:
                return TimeSlot.F2
            else:
                return TimeSlot.F3

        # Monday-Friday
        if 8 <= hour < 19:
            return TimeSlot.F1
        elif (7 <= hour < 8) or (19 <= hour < 23):
            return TimeSlot.F2
        else:
            return TimeSlot.F3

    @staticmethod
    def calculate_tcec_rate(
        power_kw: float,
        zone: ItalianZone,
        timestamp: datetime,
        market_price_override: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Calculate TCEC incentive rate for a specific hour

        Formula: TCEC = Base Rate + Zonal Adjustment + Time Slot Adjustment

        Args:
            power_kw: Plant nominal power in kW
            zone: Italian electricity zone
            timestamp: Timestamp for zonale orario calculation
            market_price_override: Optional market price override (€/MWh)

        Returns:
            Dictionary with TCEC rate calculation details
        """
        size_category = IncentiveRateManager.determine_plant_size_category(power_kw)
        time_slot = IncentiveRateManager.determine_time_slot(timestamp)

        # Get base rate
        base_rate = IncentiveRateManager.BASE_TCEC_RATES[size_category]["typical"]

        # Apply zonal adjustment
        zonal_adjustment = IncentiveRateManager.ZONAL_ADJUSTMENTS.get(zone, Decimal("0.00"))

        # Apply time slot multiplier
        time_slot_multiplier = IncentiveRateManager.TIME_SLOT_MULTIPLIERS[time_slot]

        # Calculate final rate
        tcec_rate = ((base_rate + zonal_adjustment) * time_slot_multiplier).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # If market price override provided, use it (e.g., from GME API)
        if market_price_override:
            tcec_rate = market_price_override

        return {
            "timestamp": timestamp.isoformat(),
            "power_kw": power_kw,
            "size_category": size_category.value,
            "zone": zone.value,
            "time_slot": time_slot.value,
            "base_rate_eur_mwh": float(base_rate),
            "zonal_adjustment_eur_mwh": float(zonal_adjustment),
            "time_slot_multiplier": float(time_slot_multiplier),
            "final_tcec_rate_eur_mwh": float(tcec_rate),
            "rate_source": "calculated" if not market_price_override else "market_override",
            "notes": f"TCEC rate for {size_category.value} plant in zone {zone.value} during {time_slot.value} period"
        }

    @staticmethod
    def calculate_hourly_incentives(
        power_kw: float,
        zone: ItalianZone,
        hourly_energy_kwh: Dict[datetime, float],
        incentivized_percentage: float = 0.55
    ) -> Dict[str, Any]:
        """
        Calculate incentives for hourly energy production

        Args:
            power_kw: Plant nominal power in kW
            zone: Italian electricity zone
            hourly_energy_kwh: Dictionary mapping datetime to energy shared (kWh)
            incentivized_percentage: Percentage of shared energy that is incentivized (default 55%)

        Returns:
            Dictionary with hourly incentive calculations
        """
        total_energy_kwh = Decimal("0.00")
        total_incentivized_energy_kwh = Decimal("0.00")
        total_incentives_eur = Decimal("0.00")

        hourly_calculations = []

        for timestamp, energy_kwh in hourly_energy_kwh.items():
            energy_kwh_decimal = Decimal(str(energy_kwh))

            # Calculate incentivized energy (55% of shared energy)
            incentivized_energy_kwh = energy_kwh_decimal * Decimal(str(incentivized_percentage))

            # Get TCEC rate for this hour
            tcec_data = IncentiveRateManager.calculate_tcec_rate(
                power_kw=power_kw,
                zone=zone,
                timestamp=timestamp
            )

            tcec_rate_eur_mwh = Decimal(str(tcec_data["final_tcec_rate_eur_mwh"]))

            # Calculate incentive (convert kWh to MWh)
            incentive_eur = (incentivized_energy_kwh / Decimal("1000.0")) * tcec_rate_eur_mwh

            total_energy_kwh += energy_kwh_decimal
            total_incentivized_energy_kwh += incentivized_energy_kwh
            total_incentives_eur += incentive_eur

            hourly_calculations.append({
                "timestamp": timestamp.isoformat(),
                "energy_shared_kwh": float(energy_kwh),
                "incentivized_energy_kwh": float(incentivized_energy_kwh),
                "tcec_rate_eur_mwh": float(tcec_rate_eur_mwh),
                "time_slot": tcec_data["time_slot"],
                "incentive_eur": float(incentive_eur)
            })

        return {
            "power_kw": power_kw,
            "zone": zone.value,
            "period_start": min(hourly_energy_kwh.keys()).isoformat(),
            "period_end": max(hourly_energy_kwh.keys()).isoformat(),
            "total_hours": len(hourly_energy_kwh),
            "total_energy_shared_kwh": float(total_energy_kwh),
            "incentivized_percentage": incentivized_percentage,
            "total_incentivized_energy_kwh": float(total_incentivized_energy_kwh),
            "total_incentives_eur": float(total_incentives_eur),
            "average_tcec_rate_eur_mwh": float((total_incentives_eur / (total_incentivized_energy_kwh / Decimal("1000.0")))),
            "hourly_breakdown": hourly_calculations
        }

    @staticmethod
    def calculate_pnrr_funding(
        total_investment_eur: Decimal,
        comune_population: int,
        plant_power_kw: float
    ) -> Dict[str, Any]:
        """
        Calculate PNRR funding eligibility and amount

        Args:
            total_investment_eur: Total investment cost
            comune_population: Population of the comune
            plant_power_kw: Plant nominal power in kW

        Returns:
            Dictionary with PNRR funding calculation
        """
        total_investment_eur = Decimal(str(total_investment_eur))

        # Check eligibility
        is_eligible = (
            comune_population <= IncentiveRateManager.PNRR_MAX_COMUNE_POPULATION and
            plant_power_kw <= 1000  # Max 1 MW for PNRR
        )

        if not is_eligible:
            return {
                "eligible": False,
                "reason": "Comune population exceeds 50,000 inhabitants" if comune_population > IncentiveRateManager.PNRR_MAX_COMUNE_POPULATION else "Plant power exceeds 1 MW",
                "funding_amount_eur": 0.0,
                "funding_percentage": 0.0,
                "total_investment_eur": float(total_investment_eur),
                "comune_population": comune_population,
                "max_comune_population": IncentiveRateManager.PNRR_MAX_COMUNE_POPULATION,
                "deadline": "2025-11-30",
                "notes": "PNRR funding not available for this project"
            }

        # Calculate funding amount (40% of investment)
        funding_amount_eur = (total_investment_eur * IncentiveRateManager.PNRR_MAX_FUNDING_PERCENTAGE).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        return {
            "eligible": True,
            "reason": "Comune qualifies for PNRR funding (population ≤ 50,000)",
            "funding_amount_eur": float(funding_amount_eur),
            "funding_percentage": float(IncentiveRateManager.PNRR_MAX_FUNDING_PERCENTAGE * 100),
            "total_investment_eur": float(total_investment_eur),
            "net_investment_after_funding_eur": float(total_investment_eur - funding_amount_eur),
            "comune_population": comune_population,
            "max_comune_population": IncentiveRateManager.PNRR_MAX_COMUNE_POPULATION,
            "plant_power_kw": plant_power_kw,
            "deadline": "2025-11-30",
            "application_process": [
                "1. Register CER on GSE portal",
                "2. Submit technical-economic feasibility study",
                "3. Submit environmental impact assessment",
                "4. Submit social impact assessment",
                "5. Submit investment plan",
                "6. Wait for GSE approval (90-120 days typical)"
            ],
            "notes": "PNRR funding is non-repayable contribution from EU Recovery Fund"
        }

    @staticmethod
    def calculate_total_financial_benefit(
        plant_power_kw: float,
        zone: ItalianZone,
        annual_production_kwh: float,
        annual_self_consumption_kwh: float,
        shared_energy_percentage: float,
        grid_price_eur_kwh: float,
        total_investment_eur: float,
        comune_population: int,
        years: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate total financial benefit over incentive period (20 years)

        Args:
            plant_power_kw: Plant nominal power in kW
            zone: Italian electricity zone
            annual_production_kwh: Annual energy production in kWh
            annual_self_consumption_kwh: Annual self-consumption in kWh
            shared_energy_percentage: Percentage of non-self-consumed energy that is shared
            grid_price_eur_kwh: Grid electricity price in €/kWh
            total_investment_eur: Total investment cost
            comune_population: Comune population for PNRR eligibility
            years: Incentive period in years (default 20)

        Returns:
            Dictionary with total financial benefit analysis
        """
        # Calculate PNRR funding
        pnrr_funding = IncentiveRateManager.calculate_pnrr_funding(
            Decimal(str(total_investment_eur)),
            comune_population,
            plant_power_kw
        )

        # Calculate annual shared energy
        annual_shared_energy_kwh = (annual_production_kwh - annual_self_consumption_kwh) * shared_energy_percentage

        # Estimate average TCEC rate (simplified - should use hourly calculation)
        size_category = IncentiveRateManager.determine_plant_size_category(plant_power_kw)
        base_rate = IncentiveRateManager.BASE_TCEC_RATES[size_category]["typical"]
        zonal_adjustment = IncentiveRateManager.ZONAL_ADJUSTMENTS.get(zone, Decimal("0.00"))
        estimated_avg_tcec_eur_mwh = base_rate + zonal_adjustment

        # Calculate annual TCEC incentives (55% of shared energy is incentivized)
        incentivized_energy_kwh = Decimal(str(annual_shared_energy_kwh)) * Decimal("0.55")
        annual_tcec_eur = (incentivized_energy_kwh / Decimal("1000.0")) * estimated_avg_tcec_eur_mwh

        # Calculate annual grid savings from self-consumption
        annual_grid_savings_eur = Decimal(str(annual_self_consumption_kwh)) * Decimal(str(grid_price_eur_kwh))

        # Total annual benefit
        annual_total_benefit_eur = annual_tcec_eur + annual_grid_savings_eur

        # Total benefit over 20 years
        total_tcec_20_years_eur = annual_tcec_eur * years
        total_grid_savings_20_years_eur = annual_grid_savings_eur * years
        total_benefit_20_years_eur = annual_total_benefit_eur * years

        # Add PNRR funding to total benefit
        total_benefit_with_pnrr_eur = total_benefit_20_years_eur + Decimal(str(pnrr_funding["funding_amount_eur"]))

        # Calculate payback period
        net_investment = Decimal(str(total_investment_eur)) - Decimal(str(pnrr_funding["funding_amount_eur"]))
        if annual_total_benefit_eur > 0:
            payback_years = float(net_investment / annual_total_benefit_eur)
        else:
            payback_years = float('inf')

        # Calculate ROI
        total_return = total_benefit_with_pnrr_eur - Decimal(str(total_investment_eur))
        roi_percentage = (total_return / Decimal(str(total_investment_eur)) * 100) if total_investment_eur > 0 else 0

        return {
            "plant_power_kw": plant_power_kw,
            "zone": zone.value,
            "size_category": size_category.value,
            "incentive_period_years": years,

            "annual_metrics": {
                "production_kwh": annual_production_kwh,
                "self_consumption_kwh": annual_self_consumption_kwh,
                "shared_energy_kwh": annual_shared_energy_kwh,
                "incentivized_energy_kwh": float(incentivized_energy_kwh),
                "estimated_avg_tcec_rate_eur_mwh": float(estimated_avg_tcec_eur_mwh),
                "tcec_incentives_eur": float(annual_tcec_eur),
                "grid_savings_eur": float(annual_grid_savings_eur),
                "total_annual_benefit_eur": float(annual_total_benefit_eur)
            },

            "20_year_totals": {
                "total_tcec_incentives_eur": float(total_tcec_20_years_eur),
                "total_grid_savings_eur": float(total_grid_savings_20_years_eur),
                "total_benefit_eur": float(total_benefit_20_years_eur)
            },

            "pnrr_funding": pnrr_funding,

            "investment_analysis": {
                "total_investment_eur": total_investment_eur,
                "pnrr_funding_eur": pnrr_funding["funding_amount_eur"],
                "net_investment_eur": float(net_investment),
                "total_benefit_with_pnrr_eur": float(total_benefit_with_pnrr_eur),
                "total_return_eur": float(total_return),
                "roi_percentage": float(roi_percentage),
                "payback_period_years": round(payback_years, 1),
                "npv_10_percent_discount": "Not calculated (requires discount rate)",
                "irr": "Not calculated (requires cash flow analysis)"
            },

            "summary": {
                "is_profitable": roi_percentage > 0,
                "payback_within_20_years": payback_years <= 20,
                "recommendation": "Highly attractive investment" if (roi_percentage > 50 and payback_years < 10) else "Good investment" if roi_percentage > 0 else "Not recommended"
            }
        }


# Export service instance
incentive_rate_manager = IncentiveRateManager()
