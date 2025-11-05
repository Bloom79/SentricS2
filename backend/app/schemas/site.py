"""
Site schemas for API requests/responses
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class SiteBase(BaseModel):
    """Base site schema"""

    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    site_type: str = Field(default="industrial")
    status: str = Field(default="active")
    operational_status: Optional[str] = None

    # Location
    location: Optional[str] = None
    address: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    country: str = Field(default="Italy")
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Capacity
    capacity: Optional[float] = Field(None, ge=0)
    efficiency: Optional[float] = Field(None, ge=0, le=100)

    # Area
    available_area: Optional[float] = Field(None, ge=0)
    reserved_area: Optional[float] = Field(None, ge=0)

    # Dates
    commissioning_date: Optional[datetime] = None
    decommissioning_date: Optional[datetime] = None

    # Ownership
    owner: Optional[str] = None
    operator: Optional[str] = None
    maintenance_provider: Optional[str] = None

    # Environmental
    environmental_impact_rating: Optional[int] = Field(None, ge=1, le=10)

    # Grid
    grid_connection_status: str = Field(default="connected")
    grid_capacity: Optional[float] = Field(None, ge=0)

    # Metadata
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class SiteCreate(SiteBase):
    """Schema for creating a site"""

    pass


class SiteUpdate(BaseModel):
    """Schema for updating a site"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    site_type: Optional[str] = None
    status: Optional[str] = None
    operational_status: Optional[str] = None

    # Location
    location: Optional[str] = None
    address: Optional[str] = None
    street_address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Capacity
    capacity: Optional[float] = Field(None, ge=0)
    efficiency: Optional[float] = Field(None, ge=0, le=100)

    # Area
    available_area: Optional[float] = Field(None, ge=0)
    reserved_area: Optional[float] = Field(None, ge=0)

    # Dates
    commissioning_date: Optional[datetime] = None
    decommissioning_date: Optional[datetime] = None

    # Ownership
    owner: Optional[str] = None
    operator: Optional[str] = None
    maintenance_provider: Optional[str] = None

    # Environmental
    environmental_impact_rating: Optional[int] = Field(None, ge=1, le=10)

    # Grid
    grid_connection_status: Optional[str] = None
    grid_capacity: Optional[float] = Field(None, ge=0)

    # Metadata
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class SiteResponse(SiteBase):
    """Schema for site response"""

    id: int
    tenant_id: str
    plants_count: Optional[int] = 0
    storage_units_count: Optional[int] = 0
    consumers_count: Optional[int] = 0
    total_capacity_kw: Optional[float] = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class SiteStatsResponse(BaseModel):
    """Schema for site statistics"""

    site_id: int
    plants_count: int
    total_capacity_kw: float
    storage_units_count: int
    total_storage_capacity_kwh: float
    consumers_count: int
    site_capacity: float
    site_efficiency: float


class StorageUnitBase(BaseModel):
    """Base storage unit schema"""

    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    capacity_kwh: float = Field(..., gt=0)
    rated_power_kw: float = Field(..., gt=0)
    chemistry_type: Optional[str] = None
    efficiency: Optional[float] = Field(None, ge=0, le=100)
    status: str = Field(default="operational")
    state_of_charge: Optional[float] = Field(None, ge=0, le=100)
    state_of_health: Optional[float] = Field(None, ge=0, le=100)
    total_cycles: int = Field(default=0, ge=0)
    cycle_life: Optional[int] = Field(None, ge=0)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    installation_date: Optional[datetime] = None
    notes: Optional[str] = None


class StorageUnitCreate(StorageUnitBase):
    """Schema for creating storage unit"""

    pass


class StorageUnitUpdate(BaseModel):
    """Schema for updating storage unit"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    capacity_kwh: Optional[float] = Field(None, gt=0)
    rated_power_kw: Optional[float] = Field(None, gt=0)
    chemistry_type: Optional[str] = None
    efficiency: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    state_of_charge: Optional[float] = Field(None, ge=0, le=100)
    state_of_health: Optional[float] = Field(None, ge=0, le=100)
    total_cycles: Optional[int] = Field(None, ge=0)
    cycle_life: Optional[int] = Field(None, ge=0)
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    installation_date: Optional[datetime] = None
    notes: Optional[str] = None


class StorageUnitResponse(StorageUnitBase):
    """Schema for storage unit response"""

    id: int
    site_id: int
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsumerBase(BaseModel):
    """Base consumer schema"""

    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    consumer_type: str = Field(..., description="residential, commercial, industrial")
    average_consumption_kw: Optional[float] = Field(None, ge=0)
    peak_consumption_kw: Optional[float] = Field(None, ge=0)
    pod_id: Optional[str] = None
    smart_meter_id: Optional[str] = None
    status: str = Field(default="active")
    activation_date: Optional[datetime] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    load_profile: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ConsumerCreate(ConsumerBase):
    """Schema for creating consumer"""

    pass


class ConsumerUpdate(BaseModel):
    """Schema for updating consumer"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    consumer_type: Optional[str] = None
    average_consumption_kw: Optional[float] = Field(None, ge=0)
    peak_consumption_kw: Optional[float] = Field(None, ge=0)
    pod_id: Optional[str] = None
    smart_meter_id: Optional[str] = None
    status: Optional[str] = None
    activation_date: Optional[datetime] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    load_profile: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class ConsumerResponse(ConsumerBase):
    """Schema for consumer response"""

    id: int
    site_id: int
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EnergyFlowBase(BaseModel):
    """Base energy flow schema"""

    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)
    description: Optional[str] = None
    is_active: bool = Field(default=True)


class EnergyFlowCreate(EnergyFlowBase):
    """Schema for creating energy flow"""

    pass


class EnergyFlowUpdate(BaseModel):
    """Schema for updating energy flow"""

    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EnergyFlowResponse(EnergyFlowBase):
    """Schema for energy flow response"""

    id: int
    site_id: Optional[int] = None
    plant_id: Optional[int] = None
    tenant_id: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
