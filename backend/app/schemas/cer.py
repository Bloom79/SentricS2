"""
CER Pydantic schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.cer import CERLegalType, CERStatus, CERType


class CERBase(BaseModel):
    """Base CER schema"""

    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    legal_type: CERLegalType
    type: CERType = CERType.ACTIVE
    address: str
    region: str
    primary_substation_id: str


class CERCreate(CERBase):
    """Schema for creating CER"""

    location: Optional[List[float]] = None  # [longitude, latitude]
    boundary: Optional[List[List[float]]] = None  # List of [lon, lat] pairs
    technical_info: Dict[str, Any] = {}
    billing_settings: Dict[str, Any] = {}


class CERUpdate(BaseModel):
    """Schema for updating CER"""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CERStatus] = None
    technical_info: Optional[Dict[str, Any]] = None
    billing_settings: Optional[Dict[str, Any]] = None


class CERResponse(CERBase):
    """Schema for CER response"""

    id: int
    status: CERStatus
    total_capacity: float
    gse_compliance_status: str
    pnrr_funding_applied: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CERMemberBase(BaseModel):
    """Base CER member schema"""

    name: str
    address: str
    member_type: str  # consumer, producer, prosumer
    pod_id: str
    load_profile_type: str
    contracted_power: Optional[float] = None
    user_type: Optional[str] = "real"  # real, simulated
    consumption_class: Optional[str] = None  # CLASS_1 through CLASS_5


class CERMemberCreate(CERMemberBase):
    """Schema for creating CER member - supports all fields from old project"""

    smart_meter_id: Optional[str] = None
    meter_type: Optional[str] = None
    fiscal_code: Optional[str] = None
    vat_number: Optional[str] = None
    billing_address: Optional[str] = None
    voltage_level: Optional[str] = None
    activation_date: Optional[datetime] = None
    verification_status: Optional[str] = None

    # Production fields (for PRODUCER/PROSUMER) - stored in technical_info
    plant_type: Optional[str] = None  # PHOTOVOLTAIC, WIND, HYDRO, BIOMASS
    plant_capacity: Optional[float] = None  # in kW
    commissioning_date: Optional[datetime] = None
    is_incentivized: Optional[bool] = False
    capital_contribution: Optional[float] = None  # percentage 0-100

    # Storage fields - stored in technical_info
    has_storage: Optional[bool] = False
    storage_capacity: Optional[float] = None  # in kWh

    # Additional fields stored in JSON columns
    technical_info: Optional[Dict[str, Any]] = None
    load_profile_data: Optional[Dict[str, Any]] = None
    device_info: Optional[Dict[str, Any]] = None
    energy_sharing_preferences: Optional[Dict[str, Any]] = None
    billing_preferences: Optional[Dict[str, Any]] = None


class CERMemberUpdate(BaseModel):
    """Schema for updating CER member"""

    name: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    member_type: Optional[str] = None
    contracted_power: Optional[float] = None
    plant_capacity: Optional[float] = None
    storage_capacity: Optional[float] = None
    is_incentivized: Optional[bool] = None
    capital_contribution: Optional[float] = None
    has_storage: Optional[bool] = None
    energy_sharing_preferences: Optional[Dict[str, Any]] = None
    technical_info: Optional[Dict[str, Any]] = None
    load_profile_data: Optional[Dict[str, Any]] = None


class CERMemberResponse(CERMemberBase):
    """Schema for CER member response"""

    id: int
    cer_id: int
    status: str
    user_type: str
    consumption_class: Optional[str] = None
    smart_meter_id: Optional[str] = None
    meter_type: Optional[str] = None
    voltage_level: Optional[str] = None
    activation_date: Optional[datetime] = None
    verification_status: Optional[str] = None
    energy_produced: float
    energy_consumed: float
    energy_shared: float
    technical_info: Optional[Dict[str, Any]] = None
    load_profile_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CERStatsResponse(BaseModel):
    """Schema for CER statistics"""

    cer_id: int
    total_members: int
    producers: int
    consumers: int
    prosumers: int
    total_capacity: float
    total_energy_produced: float
    total_energy_consumed: float
    total_energy_shared: float
    member_count: Dict[str, int]  # by type


class CERParticipationRequestCreate(BaseModel):
    """Schema for creating participation request"""

    cer_id: int
    notes: Optional[str] = None


class CERParticipationRequestUpdate(BaseModel):
    """Schema for updating participation request"""

    status: str  # pending, approved, rejected, cancelled
    notes: Optional[str] = None


class CERParticipationRequestResponse(BaseModel):
    """Schema for participation request response"""

    id: int
    cer_id: int
    user_id: int
    status: str
    request_date: datetime
    processed_date: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class CERParticipationRequestWithDetails(CERParticipationRequestResponse):
    """Schema for participation request with user and CER details"""

    user_name: Optional[str] = None
    user_email: Optional[str] = None
    cer_name: Optional[str] = None

    class Config:
        from_attributes = True
