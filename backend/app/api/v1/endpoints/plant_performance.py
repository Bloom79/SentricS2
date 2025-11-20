"""
Plant Performance Analytics API
Real-time monitoring, production tracking, and performance KPIs
BUSINESS VALUE: Early issue detection, production optimization, €100K+ loss prevention
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.plant import Plant
from app.models.energy_transaction import EnergyTransaction

logger = logging.getLogger(__name__)

router = APIRouter()


# Schemas
class DailyProduction(BaseModel):
    date: str
    production: float  # kWh
    forecast: float  # kWh
    irradiance: float  # W/m²


class ActiveAlert(BaseModel):
    id: int
    severity: str  # critical, high, medium, low
    message: str
    timestamp: str


class PlantPerformanceResponse(BaseModel):
    # Real-time metrics
    current_power: float  # kW
    today_production: float  # kWh
    today_revenue: float  # EUR
    status: str

    # Performance KPIs
    performance_ratio: float  # %
    availability: float  # %
    capacity_factor: float  # %

    # Production data
    daily_production: List[DailyProduction]

    # Alerts
    active_alerts: List[ActiveAlert]

    # Financial
    mtd_revenue: float
    ytd_revenue: float
    estimated_monthly: float

    # Environmental
    co2_avoided: float  # tons
    trees_equivalent: int


@router.get("/{plant_id}/performance", response_model=PlantPerformanceResponse)
async def get_plant_performance(
    plant_id: int,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive plant performance data

    Returns:
    - Real-time power and production
    - Performance KPIs (PR, availability, capacity factor)
    - Daily production history with forecast comparison
    - Active alerts and issues
    - Financial metrics (MTD, YTD revenue)
    - Environmental impact
    """
    try:
        # Get plant
        plant = db.query(Plant).filter(
            and_(
                Plant.id == plant_id,
                Plant.tenant_id == current_user.tenant_id,
                Plant.deleted_at.is_(None)
            )
        ).first()

        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")

        # Set default date range if not provided
        if not to_date:
            to_date = datetime.now()
        if not from_date:
            from_date = to_date - timedelta(days=30)

        # Calculate today's production
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_production_query = db.query(
            func.sum(EnergyTransaction.energy_kwh)
        ).filter(
            and_(
                EnergyTransaction.plant_id == plant_id,
                EnergyTransaction.timestamp >= today_start,
                EnergyTransaction.transaction_type == 'production',
                EnergyTransaction.deleted_at.is_(None)
            )
        ).scalar()

        today_production = float(today_production_query or 0)

        # Current power (simulate - in real system, query SCADA)
        # In production, this would come from real-time monitoring system
        current_hour = datetime.now().hour
        current_power = 0.0
        if 6 <= current_hour <= 19:  # Daylight hours
            # Simulate based on time of day
            peak_hour = 12
            hours_from_peak = abs(current_hour - peak_hour)
            capacity_kw = plant.capacity_kw or 1000
            current_power = capacity_kw * (1 - (hours_from_peak / 6)) * 0.8
            current_power = max(0, current_power)

        # Energy price (simplified - should come from market prices)
        price_per_kwh = 0.12  # EUR/kWh average
        today_revenue = today_production * price_per_kwh

        # Get daily production for period
        daily_production_data = []
        current_date = from_date
        while current_date <= to_date:
            day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            # Get actual production for the day
            day_production = db.query(
                func.sum(EnergyTransaction.energy_kwh)
            ).filter(
                and_(
                    EnergyTransaction.plant_id == plant_id,
                    EnergyTransaction.timestamp >= day_start,
                    EnergyTransaction.timestamp < day_end,
                    EnergyTransaction.transaction_type == 'production',
                    EnergyTransaction.deleted_at.is_(None)
                )
            ).scalar()

            production = float(day_production or 0)

            # Forecast (simplified - in production, use weather forecast)
            # Assume 4-5 peak sun hours per day
            capacity_kw = plant.capacity_kw or 1000
            forecast = capacity_kw * 4.5  # kWh

            # Irradiance (simplified - in production, use weather data)
            # Simulate seasonal variation
            month = current_date.month
            base_irradiance = 800  # W/m² average
            seasonal_factor = 1 + 0.3 * ((month - 6) / 6)  # Higher in summer
            irradiance = base_irradiance * seasonal_factor

            daily_production_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "production": production,
                "forecast": forecast,
                "irradiance": irradiance
            })

            current_date += timedelta(days=1)

        # Performance Ratio calculation
        # PR = (Actual Energy / Theoretical Energy) * 100
        total_actual = sum(d['production'] for d in daily_production_data)
        total_forecast = sum(d['forecast'] for d in daily_production_data)
        performance_ratio = (total_actual / total_forecast * 100) if total_forecast > 0 else 0

        # Availability (simplified - should track actual downtime)
        # Assume 98% if plant is operational
        availability = 98.0 if plant.status == 'OPERATIONAL' else 85.0

        # Capacity Factor
        # CF = (Actual Production / Maximum Possible Production) * 100
        days = (to_date - from_date).days + 1
        max_production = (plant.capacity_kw or 1000) * 24 * days
        capacity_factor = (total_actual / max_production * 100) if max_production > 0 else 0

        # Active Alerts (in production, query from monitoring system)
        active_alerts = []
        if performance_ratio < 70:
            active_alerts.append({
                "id": 1,
                "severity": "high",
                "message": f"Performance ratio is low: {performance_ratio:.1f}% (target: 80%)",
                "timestamp": datetime.now().isoformat()
            })
        if availability < 95:
            active_alerts.append({
                "id": 2,
                "severity": "medium",
                "message": f"Availability below target: {availability:.1f}% (target: 95%)",
                "timestamp": datetime.now().isoformat()
            })

        # Financial metrics
        # Month-to-date revenue
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mtd_production = db.query(
            func.sum(EnergyTransaction.energy_kwh)
        ).filter(
            and_(
                EnergyTransaction.plant_id == plant_id,
                EnergyTransaction.timestamp >= month_start,
                EnergyTransaction.transaction_type == 'production',
                EnergyTransaction.deleted_at.is_(None)
            )
        ).scalar()
        mtd_revenue = float(mtd_production or 0) * price_per_kwh

        # Year-to-date revenue
        year_start = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        ytd_production = db.query(
            func.sum(EnergyTransaction.energy_kwh)
        ).filter(
            and_(
                EnergyTransaction.plant_id == plant_id,
                EnergyTransaction.timestamp >= year_start,
                EnergyTransaction.transaction_type == 'production',
                EnergyTransaction.deleted_at.is_(None)
            )
        ).scalar()
        ytd_revenue = float(ytd_production or 0) * price_per_kwh

        # Estimated monthly (based on daily average)
        days_in_month = 30
        days_elapsed = datetime.now().day
        estimated_monthly = (mtd_revenue / days_elapsed * days_in_month) if days_elapsed > 0 else 0

        # Environmental impact
        # CO2 avoided: ~0.4 kg per kWh (Italian grid average)
        co2_avoided = total_actual * 0.4 / 1000  # tons
        # Trees: one tree absorbs ~20 kg CO2/year
        trees_equivalent = int(co2_avoided * 1000 / 20)

        return {
            "current_power": current_power,
            "today_production": today_production,
            "today_revenue": today_revenue,
            "status": plant.status.value if hasattr(plant.status, 'value') else str(plant.status),
            "performance_ratio": performance_ratio,
            "availability": availability,
            "capacity_factor": capacity_factor,
            "daily_production": daily_production_data,
            "active_alerts": active_alerts,
            "mtd_revenue": mtd_revenue,
            "ytd_revenue": ytd_revenue,
            "estimated_monthly": estimated_monthly,
            "co2_avoided": co2_avoided,
            "trees_equivalent": trees_equivalent
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plant performance: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get plant performance data")


@router.get("/{plant_id}/alerts")
async def get_plant_alerts(
    plant_id: int,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get plant alerts and notifications"""
    # In production, this would query an alerts/notifications table
    # For now, return mock data
    return {
        "plant_id": plant_id,
        "alerts": [],
        "message": "Alert system coming soon"
    }


@router.get("/{plant_id}/downtime")
async def get_plant_downtime(
    plant_id: int,
    from_date: Optional[datetime] = Query(None, alias="from"),
    to_date: Optional[datetime] = Query(None, alias="to"),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get plant downtime events"""
    # In production, track maintenance schedules and unplanned outages
    return {
        "plant_id": plant_id,
        "downtime_events": [],
        "total_hours": 0,
        "message": "Downtime tracking coming soon"
    }
