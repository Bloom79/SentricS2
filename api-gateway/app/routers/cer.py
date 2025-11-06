"""
CER Billing Router - Insanely Great Edition
Handles CSV upload, processing, and insights generation
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from datetime import datetime

router = APIRouter()


@router.post("/upload")
async def upload_cer_file(file: UploadFile = File(...)):
    """
    Upload and process CER billing CSV file

    This endpoint will:
    1. Detect file format (GSE, e-distribuzione, etc.)
    2. Parse hourly readings
    3. Match members by POD code
    4. Calculate shared energy using MIN(production, consumption)
    5. Generate insights

    TODO: Connect to existing backend CER service
    """

    # Validate file type
    if not file.filename.endswith(('.csv', '.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Mock response for now
    # In production, this will call existing backend services
    return {
        "id": "cer_002",
        "month": "January",
        "year": 2025,
        "totalEarnings": 13156,
        "changeAmount": 1512,
        "changePercentage": 13.0,
        "lastUpdated": datetime.now().isoformat(),
        "hourlyReadings": 720,
        "membersProcessed": 12,
        "insights": [
            {
                "type": "peak",
                "icon": "🌞",
                "title": "Peak sharing improved: Now 10am-3pm",
                "description": "Was 11am-2pm - expanded by 2 hours"
            },
            {
                "type": "opportunity",
                "icon": "📈",
                "title": "Weekend performance up 18%",
                "description": "Solar production optimization paying off"
            },
            {
                "type": "opportunity",
                "icon": "💡",
                "title": "Shift EV charging to midday",
                "description": "Use excess solar production → +€124/month",
                "impact": "+€124/month"
            }
        ]
    }


@router.get("/data")
async def get_cer_data():
    """Get current CER billing data"""
    return {
        "id": "cer_001",
        "month": "January",
        "year": 2025,
        "totalEarnings": 12847,
        "changeAmount": 1203,
        "changePercentage": 10.3,
        "lastUpdated": datetime.now().isoformat(),
        "hourlyReadings": 720,
        "membersProcessed": 12,
    }


@router.get("/insights")
async def get_insights():
    """Get current insights"""
    return [
        {
            "type": "peak",
            "icon": "🌞",
            "title": "Peak sharing: Weekdays 10am-2pm",
            "description": "Average €94/hour during peak solar production"
        },
        {
            "type": "low",
            "icon": "⚠️",
            "title": "Low sharing: Weekends",
            "description": "Average €23/hour - industrial consumers offline"
        },
        {
            "type": "opportunity",
            "icon": "💡",
            "title": "Add 50kWh storage",
            "description": "Shift excess weekend solar to weekday evenings → +€347/month",
            "impact": "+€347/month"
        }
    ]
