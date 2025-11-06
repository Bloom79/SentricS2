"""
BESS Monitoring Router - Insanely Great Edition
Handles performance scoring and loss prevention
"""

from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/performance")
async def get_performance_score():
    """
    Get BESS performance score and identified issues

    This endpoint will:
    1. Analyze BESS operation patterns
    2. Compare against optimal dispatch strategy
    3. Calculate performance score (0-100)
    4. Identify revenue loss opportunities
    5. Generate specific fixes

    TODO: Connect to existing backend BESS service
    """

    return {
        "id": "bess_001",
        "name": "Milan Depot BESS",
        "score": 87,
        "totalLoss": 15284,
        "issues": [
            {
                "id": "issue_1",
                "severity": "warning",
                "title": "Missing Negative Price Opportunities",
                "description": "Your BESS isn't charging during negative prices",
                "annualLoss": 8400,
                "fix": "Enable auto-trading mode",
                "fixDetails": "We'll charge when prices go negative automatically",
                "stats": {
                    "last30Days": {
                        "negativeHours": 47,
                        "missedEnergy": 2115
                    }
                }
            },
            {
                "id": "issue_2",
                "severity": "warning",
                "title": "Suboptimal Discharge Timing",
                "description": "You're discharging at average prices, not peaks",
                "annualLoss": 4900,
                "fix": "Shift discharge to 7-9pm peak window",
                "fixDetails": "We'll predict peaks and optimize timing",
                "stats": {
                    "avgDischargePrice": 67,
                    "optimalPrice": 142
                }
            },
            {
                "id": "issue_3",
                "severity": "warning",
                "title": "Conservative Depth of Discharge",
                "description": "You're only using 75% of battery capacity",
                "annualLoss": 1984,
                "fix": "Increase DOD to 90% (safe per warranty)",
                "fixDetails": "Adds 2,800 years to cycle life vs revenue gain",
                "stats": {
                    "currentDOD": 75,
                    "warrantyDOD": 90,
                    "underutilizedCapacity": 22.5
                }
            }
        ]
    }


@router.get("/status/{bess_id}")
async def get_bess_status(bess_id: str):
    """Get live BESS status"""

    # Mock response
    # TODO: Connect to vendor APIs or existing backend
    return {
        "id": bess_id,
        "name": "Milan Depot BESS",
        "soc": 78,
        "status": "charging",
        "power": 45,
        "currentPrice": 12,
        "priceStatus": "good",
        "nextAction": {
            "time": "7:15pm",
            "action": "Discharge at peak",
            "expectedRevenue": 84
        }
    }


@router.post("/apply-fixes")
async def apply_fixes():
    """Apply all recommended fixes"""

    # TODO: Connect to existing backend to apply configuration changes
    return {
        "status": "success",
        "message": "All fixes applied",
        "estimatedSavings": 15284,
        "appliedFixes": [
            "Enabled auto-trading mode",
            "Optimized discharge schedule",
            "Increased DOD to 90%"
        ]
    }


@router.post("/apply-fix/{fix_id}")
async def apply_single_fix(fix_id: str):
    """Apply a single fix"""

    fix_map = {
        "issue_1": {"message": "Auto-trading enabled", "savings": 8400},
        "issue_2": {"message": "Discharge schedule optimized", "savings": 4900},
        "issue_3": {"message": "DOD increased to 90%", "savings": 1984}
    }

    if fix_id not in fix_map:
        return {"status": "error", "message": "Fix not found"}

    return {
        "status": "success",
        **fix_map[fix_id]
    }
