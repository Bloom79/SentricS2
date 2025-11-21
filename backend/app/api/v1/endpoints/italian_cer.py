"""
Italian CER Regulatory API Endpoints
Exposes Italian-specific services for GSE, Terna, tax, compliance, and notifications
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData

# Import Italian services
from app.services.gse_client import gse_client, SPIDAuthLevel, ApplicationType
from app.services.terna_gaudi_client import terna_gaudi_client
from app.services.italian_tax_calculator import (
    italian_tax_calculator,
    IVARateType,
    TransactionCategory,
    CERLegalType as TaxCERLegalType
)
from app.services.incentive_rate_manager import incentive_rate_manager, ItalianZone
from app.services.modello_unico_generator import (
    modello_unico_generator,
    ConnectionType,
    AuthorizationType
)
from app.services.cer_statute_generator import cer_statute_generator
from app.services.arera_compliance import arera_compliance, LoadProfileType, VoltageLevel
from app.services.smart_meter_client import smart_meter_client
from app.services.notification_service import notification_service
from app.services.email_service import email_service, EmailPriority

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# GSE CLIENT ENDPOINTS - GSE Portal Integration
# ============================================================================

@router.post("/gse/authenticate")
async def authenticate_with_gse(
    fiscal_code: str,
    auth_level: str = "level2",
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Authenticate with GSE portal using SPID.
    Returns access token valid for 8 hours.
    """
    try:
        level = SPIDAuthLevel(auth_level)
        result = gse_client.authenticate_with_spid(fiscal_code, level)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"GSE authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")


@router.post("/gse/rid-application")
async def submit_rid_application(
    plant_data: Dict[str, Any],
    producer_data: Dict[str, Any],
    documents: List[str],
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit RID (Ritiro Dedicato) application to GSE.
    GSE response time: 45 days.
    """
    try:
        result = gse_client.submit_rid_application(
            plant_data=plant_data,
            producer_data=producer_data,
            documents=documents
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"RID application error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit RID application")


@router.post("/gse/tcec-application")
async def submit_tcec_application(
    cer_id: int,
    cer_data: Dict[str, Any],
    plants: List[Dict[str, Any]],
    members: List[Dict[str, Any]],
    documents: List[str],
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit TCEC incentive application to GSE.
    CRITICAL: Must be submitted within 120 days of plant commissioning.
    Incentive period: 20 years.
    """
    try:
        result = gse_client.submit_tcec_application(
            cer_id=cer_id,
            cer_data=cer_data,
            plants=plants,
            members=members,
            documents=documents
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TCEC application error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit TCEC application")


@router.post("/gse/pnrr-application")
async def submit_pnrr_application(
    cer_id: int,
    investment_data: Dict[str, Any],
    comune_data: Dict[str, Any],
    documents: List[str],
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit PNRR funding application (40% of investment).
    Deadline: November 30, 2025.
    Eligibility: comuni ≤50,000 population, plants ≤1 MW.
    """
    try:
        result = gse_client.submit_pnrr_application(
            cer_id=cer_id,
            investment_data=investment_data,
            comune_data=comune_data,
            documents=documents
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"PNRR application error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit PNRR application")


@router.post("/gse/upload-meter-data")
async def upload_hourly_meter_data(
    tracking_number: str,
    period_month: int,
    period_year: int,
    hourly_data: List[Dict[str, Any]],
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload monthly hourly meter data to GSE.
    Required format: POD, timestamp, production_kwh, consumption_kwh.
    """
    try:
        result = gse_client.upload_hourly_meter_data(
            tracking_number=tracking_number,
            period_month=period_month,
            period_year=period_year,
            hourly_data=hourly_data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Meter data upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload meter data")


@router.get("/gse/application-status/{tracking_number}")
async def get_gse_application_status(
    tracking_number: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get status of GSE application (RID, TCEC, or PNRR)."""
    try:
        result = gse_client.get_application_status(tracking_number)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Application status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get application status")


# ============================================================================
# TERNA GAUDÌ ENDPOINTS - Plant Registration
# ============================================================================

@router.post("/terna/register-producer")
async def register_producer(
    producer_data: Dict[str, Any],
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Register producer in Terna GAUDÌ system."""
    try:
        result = terna_gaudi_client.register_producer(producer_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Producer registration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to register producer")


@router.post("/terna/register-plant")
async def register_plant(
    producer_id: str,
    plant_data: Dict[str, Any],
    grid_connection_date: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Register plant in Terna GAUDÌ system.
    CRITICAL: Must be completed within 30 days of grid connection.
    Returns CENSIMP code (14-digit plant identifier).
    Penalty: €1,000-10,000 for late registration.
    """
    try:
        connection_date = datetime.fromisoformat(grid_connection_date)
        result = terna_gaudi_client.register_plant(
            producer_id=producer_id,
            plant_data=plant_data,
            grid_connection_date=connection_date
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Plant registration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to register plant")


@router.get("/terna/validation-status/{censimp_code}")
async def check_dso_validation_status(
    censimp_code: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check DSO validation status for registered plant.
    DSO has 15 working days to validate.
    """
    try:
        result = terna_gaudi_client.check_dso_validation_status(censimp_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Validation status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check validation status")


# ============================================================================
# ITALIAN TAX CALCULATOR ENDPOINTS
# ============================================================================

@router.post("/tax/calculate-iva")
async def calculate_iva(
    amount: float,
    transaction_category: str,
    cer_legal_type: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Calculate Italian IVA (VAT) for CER transaction.
    Rates: 0% (exempt), 4%, 5%, 10%, 22%.
    Returns: base_amount, iva_rate, iva_amount, total_amount, exemption_reason.
    """
    try:
        category = TransactionCategory(transaction_category)
        legal_type = TaxCERLegalType(cer_legal_type)

        result = italian_tax_calculator.calculate_iva(
            amount=Decimal(str(amount)),
            transaction_category=category,
            cer_legal_type=legal_type
        )

        # Convert Decimal to float for JSON serialization
        return {
            "base_amount": float(result["base_amount"]),
            "iva_rate": result["iva_rate"],
            "iva_amount": float(result["iva_amount"]),
            "total_amount": float(result["total_amount"]),
            "iva_rate_type": result["iva_rate_type"],
            "exemption_reason": result.get("exemption_reason")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"IVA calculation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate IVA")


@router.post("/tax/calculate-ritenuta")
async def calculate_ritenuta_acconto(
    gse_payment_amount: float,
    cer_legal_type: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Calculate Ritenuta d'Acconto (withholding tax) on GSE payments.
    Rate: 4% for cooperatives, 0% for associations.
    Returns: gross_amount, ritenuta_rate, ritenuta_amount, net_amount.
    """
    try:
        legal_type = TaxCERLegalType(cer_legal_type)

        result = italian_tax_calculator.calculate_ritenuta_acconto(
            gse_payment_amount=Decimal(str(gse_payment_amount)),
            cer_legal_type=legal_type
        )

        return {
            "gross_amount": float(result["gross_amount"]),
            "ritenuta_rate": result["ritenuta_rate"],
            "ritenuta_amount": float(result["ritenuta_amount"]),
            "net_amount": float(result["net_amount"]),
            "applies": result["applies"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ritenuta calculation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate ritenuta")


@router.post("/tax/calculate-ires")
async def calculate_ires_tax(
    gross_income: float,
    deductible_expenses: float,
    ritenute_paid: float,
    cer_legal_type: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Calculate IRES (corporate income tax).
    Rate: 24% on net taxable income.
    Returns: taxable_income, ires_amount, ritenute_credit, total_due.
    """
    try:
        legal_type = TaxCERLegalType(cer_legal_type)

        result = italian_tax_calculator.calculate_ires_tax(
            gross_income=Decimal(str(gross_income)),
            deductible_expenses=Decimal(str(deductible_expenses)),
            ritenute_paid=Decimal(str(ritenute_paid)),
            cer_legal_type=legal_type
        )

        return {
            "gross_income": float(result["gross_income"]),
            "deductible_expenses": float(result["deductible_expenses"]),
            "taxable_income": float(result["taxable_income"]),
            "ires_rate": result["ires_rate"],
            "ires_amount": float(result["ires_amount"]),
            "ritenute_credit": float(result["ritenute_credit"]),
            "total_due": float(result["total_due"])
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"IRES calculation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate IRES")


@router.post("/tax/generate-f24")
async def generate_f24_payment(
    cer_fiscal_code: str,
    tax_type: str,
    amount: float,
    payment_period: str,
    cer_legal_type: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Generate F24 unified tax payment form data.
    Tax types: iva, ritenuta, ires.
    Returns: F24 form data for payment submission.
    """
    try:
        legal_type = TaxCERLegalType(cer_legal_type)

        result = italian_tax_calculator.generate_f24_payment_data(
            cer_fiscal_code=cer_fiscal_code,
            tax_type=tax_type,
            amount=Decimal(str(amount)),
            payment_period=payment_period,
            cer_legal_type=legal_type
        )

        # Convert Decimal values to float
        result["amount"] = float(result["amount"])

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"F24 generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate F24")


@router.get("/tax/rates")
async def get_current_tax_rates(
    current_user: TokenData = Depends(get_current_active_user)
):
    """Get current Italian tax rates for CER transactions."""
    return {
        "iva_rates": {
            "exempt": 0.0,
            "reduced_4": 0.04,
            "reduced_5": 0.05,
            "reduced_10": 0.10,
            "standard_22": 0.22
        },
        "ritenuta_acconto": {
            "cooperative": 0.04,
            "association": 0.0,
            "consortium": 0.04
        },
        "ires": 0.24,
        "detrazioni": {
            "photovoltaic_50": 0.50,
            "photovoltaic_70": 0.70
        }
    }


# ============================================================================
# INCENTIVE RATE MANAGER ENDPOINTS
# ============================================================================

@router.get("/incentives/tcec-rate")
async def calculate_tcec_rate(
    power_kw: float,
    zone: str,
    timestamp: Optional[str] = None,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Calculate TCEC incentive rate (€/MWh).
    Plant size: Small ≤200kW (€60-120/MWh), Medium ≤600kW, Large ≤1MW.
    Zonal pricing: NORD, CNOR, CSUD, SUD, SICI, SARD.
    Time-of-use: F1 (+15%), F2 (base), F3 (-15%).
    """
    try:
        italian_zone = ItalianZone(zone)
        ts = datetime.fromisoformat(timestamp) if timestamp else datetime.now()

        result = incentive_rate_manager.calculate_tcec_rate(
            power_kw=power_kw,
            zone=italian_zone,
            timestamp=ts
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TCEC rate calculation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate TCEC rate")


@router.post("/incentives/calculate-hourly")
async def calculate_hourly_incentives(
    power_kw: float,
    zone: str,
    hourly_energy_kwh: Dict[str, float],
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Calculate incentives for hourly energy production.
    Returns: total_incentives, average_tcec_rate, hourly_breakdown.
    """
    try:
        italian_zone = ItalianZone(zone)

        # Convert string timestamps to datetime
        hourly_data = {
            datetime.fromisoformat(ts): kwh
            for ts, kwh in hourly_energy_kwh.items()
        }

        result = incentive_rate_manager.calculate_hourly_incentives(
            power_kw=power_kw,
            zone=italian_zone,
            hourly_energy_kwh=hourly_data
        )

        # Convert datetime keys back to strings for JSON
        result["hourly_breakdown"] = {
            ts.isoformat(): data
            for ts, data in result["hourly_breakdown"].items()
        }

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Hourly incentives calculation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate hourly incentives")


@router.post("/incentives/pnrr-eligibility")
async def check_pnrr_eligibility(
    total_investment_eur: float,
    comune_population: int,
    plant_power_kw: float,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Check PNRR funding eligibility.
    Requirements: comuni ≤50,000 population, plants ≤1 MW.
    Funding: 40% of investment.
    """
    try:
        result = incentive_rate_manager.calculate_pnrr_funding(
            total_investment_eur=Decimal(str(total_investment_eur)),
            comune_population=comune_population,
            plant_power_kw=plant_power_kw
        )

        # Convert Decimal to float
        result["total_investment_eur"] = float(result["total_investment_eur"])
        result["funding_amount_eur"] = float(result["funding_amount_eur"])

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"PNRR eligibility check error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check PNRR eligibility")


@router.post("/incentives/forecast-20-years")
async def forecast_20_year_financial_benefit(
    plant_power_kw: float,
    zone: str,
    annual_production_kwh: float,
    total_investment_eur: float,
    comune_population: Optional[int] = None,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    20-year financial forecast for CER plant.
    Includes: TCEC incentives, PNRR funding, ROI, payback period.
    """
    try:
        italian_zone = ItalianZone(zone)

        result = incentive_rate_manager.calculate_total_financial_benefit(
            plant_power_kw=plant_power_kw,
            zone=italian_zone,
            annual_production_kwh=annual_production_kwh,
            total_investment_eur=Decimal(str(total_investment_eur)),
            comune_population=comune_population,
            years=20
        )

        # Convert Decimal values to float
        for key in ["total_investment_eur", "total_incentives_20y", "total_benefit_with_pnrr",
                    "pnrr_funding_eur", "net_investment", "net_benefit_20y", "roi_without_pnrr",
                    "roi_with_pnrr", "payback_years_without_pnrr", "payback_years_with_pnrr"]:
            if key in result:
                result[key] = float(result[key])

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"20-year forecast error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate forecast")


# ============================================================================
# SMART METER ENDPOINTS
# ============================================================================

@router.get("/smart-meter/pod-details/{pod_code}")
async def get_pod_details(
    pod_code: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get POD (Point of Delivery) details.
    POD format: 14 characters (IT001Exxxxxxxx).
    Returns: meter_type (1G/2G), voltage_level, contracted_power_kw.
    """
    try:
        result = smart_meter_client.get_pod_details(pod_code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"POD details error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get POD details")


@router.get("/smart-meter/consumption/{pod_code}")
async def get_hourly_consumption(
    pod_code: str,
    from_date: str,
    to_date: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get hourly consumption data for POD."""
    try:
        from_dt = datetime.fromisoformat(from_date)
        to_dt = datetime.fromisoformat(to_date)

        result = smart_meter_client.get_hourly_consumption(
            pod_code=pod_code,
            from_date=from_dt,
            to_date=to_dt
        )

        # Convert datetime keys to strings
        result["hourly_data"] = [
            {**item, "timestamp": item["timestamp"].isoformat()}
            for item in result["hourly_data"]
        ]

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Consumption data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get consumption data")


@router.get("/smart-meter/production/{pod_code}")
async def get_hourly_production(
    pod_code: str,
    from_date: str,
    to_date: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get hourly production data for POD (prosumers)."""
    try:
        from_dt = datetime.fromisoformat(from_date)
        to_dt = datetime.fromisoformat(to_date)

        result = smart_meter_client.get_hourly_production(
            pod_code=pod_code,
            from_date=from_dt,
            to_date=to_dt
        )

        # Convert datetime keys to strings
        result["hourly_data"] = [
            {**item, "timestamp": item["timestamp"].isoformat()}
            for item in result["hourly_data"]
        ]

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Production data error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get production data")


@router.post("/smart-meter/validate-data")
async def validate_smart_meter_data(
    hourly_data: List[Dict[str, Any]],
    expected_hours: int,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Validate smart meter data quality.
    Returns: completeness_percentage, quality_breakdown, recommendation.
    """
    try:
        result = smart_meter_client.validate_data_quality(
            hourly_data=hourly_data,
            expected_hours=expected_hours
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Data validation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate data")


# ============================================================================
# ARERA COMPLIANCE ENDPOINTS
# ============================================================================

@router.post("/arera/apply-standard-profile")
async def apply_standard_load_profile(
    daily_total_kwh: float,
    profile_type: str,
    date_str: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Apply GSE standard load profile to daily energy total.
    Profiles: DOM_FLAT, G1-G3 (commercial), C1-C3 (industrial).
    Returns: 24 hourly values.
    """
    try:
        profile = LoadProfileType(profile_type)
        date_obj = datetime.fromisoformat(date_str).date()

        result = arera_compliance.apply_standard_profile(
            daily_total_kwh=daily_total_kwh,
            profile_type=profile,
            date=date_obj
        )

        # Convert datetime keys to strings
        hourly_values = {
            ts.isoformat(): kwh
            for ts, kwh in result.items()
        }

        return {"hourly_values": hourly_values}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Profile application error: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply standard profile")


@router.post("/arera/validate-energy-sharing")
async def validate_energy_sharing_calculation(
    hourly_production: Dict[str, float],
    hourly_consumption: Dict[str, float],
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Validate energy sharing calculation per TIAD rules.
    Formula: Shared = MIN(Production, Consumption) for each hour.
    """
    try:
        # Convert string keys to datetime
        production = {
            datetime.fromisoformat(ts): kwh
            for ts, kwh in hourly_production.items()
        }
        consumption = {
            datetime.fromisoformat(ts): kwh
            for ts, kwh in hourly_consumption.items()
        }

        result = arera_compliance.validate_energy_sharing_calculation(
            hourly_production=production,
            hourly_consumption=consumption
        )

        # Convert datetime keys back to strings
        result["hourly_breakdown"] = {
            ts.isoformat(): data
            for ts, data in result["hourly_breakdown"].items()
        }

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Energy sharing validation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate energy sharing")


@router.post("/arera/calculate-grid-fees")
async def calculate_grid_fees(
    energy_kwh: float,
    voltage_level: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Calculate grid fees by voltage level.
    Levels: BT (low), MT (medium), AT (high).
    """
    try:
        level = VoltageLevel(voltage_level)

        result = arera_compliance.calculate_grid_fees(
            energy_kwh=energy_kwh,
            voltage_level=level
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Grid fees calculation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate grid fees")


@router.get("/arera/standard-profiles")
async def get_standard_profiles(
    current_user: TokenData = Depends(get_current_active_user)
):
    """Get all GSE standard load profiles."""
    return {
        "profiles": [
            "DOM_FLAT", "DOM_WINTER_WEEKDAY", "DOM_WINTER_SATURDAY", "DOM_WINTER_SUNDAY",
            "DOM_SUMMER_WEEKDAY", "DOM_SUMMER_SATURDAY", "DOM_SUMMER_SUNDAY",
            "G1", "G2", "G3", "C1", "C2", "C3"
        ],
        "description": {
            "DOM": "Domestic residential profiles",
            "G": "General commercial profiles (shops, offices)",
            "C": "Industrial profiles (factories, large consumers)"
        }
    }


# ============================================================================
# MODELLO UNICO & CER STATUTE GENERATORS
# ============================================================================

@router.post("/documents/modello-unico/part1")
async def generate_modello_unico_part1(
    plant_data: Dict[str, Any],
    owner_data: Dict[str, Any],
    connection_type: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """Generate Modello Unico Part I (before work starts)."""
    try:
        conn_type = ConnectionType(connection_type)

        result = modello_unico_generator.generate_part_1(
            plant_data=plant_data,
            owner_data=owner_data,
            connection_type=conn_type
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Modello Unico Part I error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Modello Unico Part I")


@router.post("/documents/modello-unico/part2")
async def generate_modello_unico_part2(
    part_1_data: Dict[str, Any],
    commissioning_data: Dict[str, Any],
    test_results: Dict[str, Any],
    current_user: TokenData = Depends(get_current_active_user)
):
    """Generate Modello Unico Part II (after work completion)."""
    try:
        result = modello_unico_generator.generate_part_2(
            part_1_data=part_1_data,
            commissioning_data=commissioning_data,
            test_results=test_results
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Modello Unico Part II error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Modello Unico Part II")


@router.post("/documents/statute/generate")
async def generate_cer_statute(
    cer_name: str,
    legal_type: str,
    founding_members: List[Dict[str, Any]],
    primary_substation_id: str,
    governance_structure: Dict[str, Any],
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Generate complete CER statute (15 articles).
    Legal types: cooperative, association, consortium.
    Compliant with EU RED II and Italian D.Lgs. 199/2021.
    """
    try:
        from app.models.cer import CERLegalType
        legal = CERLegalType(legal_type)

        result = cer_statute_generator.generate_statute(
            cer_name=cer_name,
            legal_type=legal,
            founding_members=founding_members,
            primary_substation_id=primary_substation_id,
            governance_structure=governance_structure
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Statute generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate statute")


@router.post("/documents/statute/validate")
async def validate_statute_compliance(
    statute_data: Dict[str, Any],
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Validate statute compliance with regulations.
    Checks: EU Directive 2018/2001, D.L. 162/2019, D.Lgs. 199/2021.
    """
    try:
        result = cer_statute_generator.validate_statute_compliance(statute_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Statute validation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate statute")


# ============================================================================
# NOTIFICATION SERVICE ENDPOINTS
# ============================================================================

@router.post("/notifications/welcome")
async def send_member_welcome_email(
    member_email: str,
    member_name: str,
    cer_name: str,
    join_date: str,
    portal_url: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """Send Italian welcome email to new CER member."""
    try:
        join_dt = datetime.fromisoformat(join_date)

        result = notification_service.send_member_welcome(
            member_email=member_email,
            member_name=member_name,
            cer_name=cer_name,
            join_date=join_dt,
            portal_url=portal_url
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Welcome email error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send welcome email")


@router.post("/notifications/monthly-report")
async def send_monthly_energy_report(
    member_email: str,
    member_name: str,
    cer_name: str,
    energy_data: Dict[str, Any],
    financial_data: Dict[str, Any],
    period_month: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """Send monthly energy report to CER member."""
    try:
        result = notification_service.send_monthly_energy_report(
            member_email=member_email,
            member_name=member_name,
            cer_name=cer_name,
            energy_data=energy_data,
            financial_data=financial_data,
            period_month=period_month
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Monthly report error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send monthly report")


@router.post("/notifications/deadline-alert")
async def send_deadline_alert(
    recipient_email: str,
    recipient_name: str,
    deadline_type: str,
    deadline_date: str,
    days_remaining: int,
    action_required: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Send deadline alert email.
    Types: gse_tcec_120d, terna_registration_30d, pnrr_application.
    Urgency color-coded: info (>30d), warning (15-30d), urgent (7-14d), critical (<7d).
    """
    try:
        deadline_dt = datetime.fromisoformat(deadline_date)

        result = notification_service.send_deadline_alert(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            deadline_type=deadline_type,
            deadline_date=deadline_dt,
            days_remaining=days_remaining,
            action_required=action_required
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Deadline alert error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send deadline alert")


@router.post("/notifications/schedule-compliance-reminders")
async def schedule_compliance_reminders(
    plant_commissioning_date: str,
    cer_contact_email: str,
    cer_name: str,
    plant_name: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Schedule all compliance deadline reminders for new plant.
    GSE TCEC: 120-day deadline (reminders at 90, 60, 30, 15, 7 days).
    Terna: 30-day deadline (reminders at 20, 15, 10, 7, 3 days).
    """
    try:
        commissioning_dt = datetime.fromisoformat(plant_commissioning_date)

        result = notification_service.schedule_compliance_reminders(
            plant_commissioning_date=commissioning_dt,
            cer_contact_email=cer_contact_email,
            cer_name=cer_name,
            plant_name=plant_name
        )

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Schedule reminders error: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule reminders")
