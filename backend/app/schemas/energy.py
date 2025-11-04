"""
Energy schemas for CER energy sharing
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class EnergyTransactionCreate(BaseModel):
    """Schema for creating energy transaction"""
    cer_id: int
    transaction_type: str  # production, consumption, shared, self_consumed, grid_export, grid_import
    energy_kwh: float = Field(..., gt=0)
    timestamp: datetime
    member_id: Optional[int] = None
    plant_id: Optional[int] = None
    calculation_data: Optional[Dict[str, Any]] = None


class EnergyTransactionResponse(BaseModel):
    """Schema for energy transaction response"""
    id: int
    cer_id: int
    transaction_type: str
    energy_kwh: float
    timestamp: datetime
    member_id: Optional[int] = None
    plant_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class EnergySharingCalculationResponse(BaseModel):
    """Schema for energy sharing calculation response"""
    id: int
    cer_id: int
    calculation_date: datetime
    period_start: datetime
    period_end: datetime
    total_production: float
    total_consumption: float
    shared_energy: float
    self_consumed_energy: float
    grid_export: float
    grid_import: float
    incentivized_energy: float
    member_allocation: Dict[str, Any]
    
    class Config:
        from_attributes = True


class EnergyStatisticsResponse(BaseModel):
    """Schema for energy statistics response"""
    cer_id: int
    period_start: datetime
    period_end: datetime
    production: float
    consumption: float
    shared: float
    self_consumed: float
    grid_export: float
    grid_import: float


class CalculateSharingRequest(BaseModel):
    """Schema for energy sharing calculation request"""
    period_start: datetime
    period_end: datetime
    save_calculation: bool = True  # Whether to save the calculation result

