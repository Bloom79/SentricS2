"""
Tests for Energy Sharing Calculator Service
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, patch

from app.services.energy_sharing_calculator import (
    EnergyShareCalculator,
    MeterData,
    MemberEnergyData,
)


class TestEnergyShareCalculator:
    """Test Energy Sharing Calculator core logic"""

    def test_meter_data_creation(self):
        """Test MeterData dataclass creation"""
        meter = MeterData(
            meter_id="MTR001",
            hourly_readings={
                datetime(2024, 1, 1, 0): Decimal("10.5"),
                datetime(2024, 1, 1, 1): Decimal("12.3"),
            }
        )
        
        assert meter.meter_id == "MTR001"
        assert len(meter.hourly_readings) == 2
        assert meter.hourly_readings[datetime(2024, 1, 1, 0)] == Decimal("10.5")

    def test_member_energy_data_creation(self):
        """Test MemberEnergyData dataclass creation"""
        member_data = MemberEnergyData(
            member_id=1,
            member_name="Test Member",
            consumption_kwh={
                datetime(2024, 1, 1, 0): Decimal("5.0"),
            },
            production_kwh={
                datetime(2024, 1, 1, 0): Decimal("0.0"),
            },
            has_meter_data=True,
        )
        
        assert member_data.member_id == 1
        assert member_data.member_name == "Test Member"
        assert member_data.has_meter_data is True

    def test_hourly_sharing_calculation_simple(self):
        """Test simple case: production matches consumption exactly"""
        calculator = EnergyShareCalculator()
        
        # Mock data: 1 hour, 10 kWh production, 10 kWh consumption (1 member)
        hour = datetime(2024, 1, 1, 12)
        production = Decimal("10.0")
        member_consumption = {
            1: Decimal("10.0")  # Member 1 consumes 10 kWh
        }
        
        # Calculate sharing
        shared_per_member = calculator._calculate_hourly_sharing(
            production, member_consumption
        )
        
        # Member should get all 10 kWh
        assert shared_per_member[1] == Decimal("10.0")

    def test_hourly_sharing_calculation_proportional(self):
        """Test proportional sharing among multiple members"""
        calculator = EnergyShareCalculator()
        
        # Mock data: 10 kWh production, 20 kWh total consumption (2 members)
        production = Decimal("10.0")
        member_consumption = {
            1: Decimal("12.0"),  # Member 1: 60% of consumption
            2: Decimal("8.0"),   # Member 2: 40% of consumption
        }
        
        # Calculate sharing (should be proportional)
        shared_per_member = calculator._calculate_hourly_sharing(
            production, member_consumption
        )
        
        # Production < Consumption, so limited by production
        # Member 1 should get 60% of 10 = 6.0 kWh
        # Member 2 should get 40% of 10 = 4.0 kWh
        assert shared_per_member[1] == Decimal("6.0")
        assert shared_per_member[2] == Decimal("4.0")
        assert sum(shared_per_member.values()) == Decimal("10.0")

    def test_hourly_sharing_excess_production(self):
        """Test case where production exceeds consumption"""
        calculator = EnergyShareCalculator()
        
        # 20 kWh production, 10 kWh consumption
        production = Decimal("20.0")
        member_consumption = {
            1: Decimal("10.0")
        }
        
        shared_per_member = calculator._calculate_hourly_sharing(
            production, member_consumption
        )
        
        # Should only share what's consumed (10 kWh)
        # Excess 10 kWh goes to grid
        assert shared_per_member[1] == Decimal("10.0")

    def test_hourly_sharing_zero_production(self):
        """Test case with no production"""
        calculator = EnergyShareCalculator()
        
        production = Decimal("0.0")
        member_consumption = {
            1: Decimal("10.0"),
            2: Decimal("5.0"),
        }
        
        shared_per_member = calculator._calculate_hourly_sharing(
            production, member_consumption
        )
        
        # No production = no sharing
        assert shared_per_member[1] == Decimal("0.0")
        assert shared_per_member[2] == Decimal("0.0")

    def test_hourly_sharing_zero_consumption(self):
        """Test case with no consumption"""
        calculator = EnergyShareCalculator()
        
        production = Decimal("10.0")
        member_consumption = {}
        
        shared_per_member = calculator._calculate_hourly_sharing(
            production, member_consumption
        )
        
        # No consumers = no sharing (all to grid)
        assert len(shared_per_member) == 0

    def test_period_calculation(self):
        """Test period start/end calculation"""
        calculator = EnergyShareCalculator()
        
        period_start, period_end = calculator._get_period_dates(1, 2024)
        
        assert period_start == datetime(2024, 1, 1, 0, 0, 0)
        assert period_end == datetime(2024, 2, 1, 0, 0, 0)

    def test_period_calculation_december(self):
        """Test period calculation for December (year rollover)"""
        calculator = EnergyShareCalculator()
        
        period_start, period_end = calculator._get_period_dates(12, 2024)
        
        assert period_start == datetime(2024, 12, 1, 0, 0, 0)
        assert period_end == datetime(2025, 1, 1, 0, 0, 0)

    @pytest.mark.asyncio
    async def test_load_profile_application(self):
        """Test ARERA load profile application when meter data missing"""
        from app.services.arera_compliance import LoadProfileType
        
        calculator = EnergyShareCalculator()
        
        # Mock member without meter data
        member_data = MemberEnergyData(
            member_id=1,
            member_name="Residential Member",
            consumption_kwh={},  # Empty - no meter data
            production_kwh={},
            has_meter_data=False,
        )
        
        # Mock monthly consumption
        monthly_consumption_kwh = Decimal("300.0")  # 300 kWh/month
        profile_type = LoadProfileType.RESIDENTIAL
        period_start = datetime(2024, 1, 1)
        period_end = datetime(2024, 2, 1)
        
        # Apply profile
        hourly_consumption = calculator._apply_load_profile(
            member_data=member_data,
            monthly_consumption_kwh=monthly_consumption_kwh,
            profile_type=profile_type,
            period_start=period_start,
            period_end=period_end,
        )
        
        # Should have hourly data for entire month
        expected_hours = 31 * 24  # January has 31 days
        assert len(hourly_consumption) == expected_hours
        
        # Total should match monthly consumption
        total = sum(hourly_consumption.values())
        # Allow small rounding difference
        assert abs(total - monthly_consumption_kwh) < Decimal("0.01")


class TestEnergySharingIntegration:
    """Integration tests requiring database"""
    
    @pytest.mark.skip(reason="Requires database setup")
    @pytest.mark.asyncio
    async def test_monthly_calculation_end_to_end(self):
        """
        End-to-end test of monthly sharing calculation
        (Skipped by default - run with database)
        """
        # This would require:
        # - Database with test CER
        # - Test members
        # - Test plants
        # - Mock meter data
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
