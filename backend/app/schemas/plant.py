"""
Plant Pydantic schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.plant import PlantStatusEnum, PlantTypeEnum


class PlantBase(BaseModel):
    """Base plant schema"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    power: str = Field(..., description="Power as string, e.g., '1.2 MW'")
    power_kw: float = Field(..., gt=0, description="Power in kW")
    status: PlantStatusEnum
    type: PlantTypeEnum
    location: str
    address: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PlantCreate(PlantBase):
    """Schema for creating plant"""
    site_id: Optional[int] = None  # NEW: Site relationship
    cer_id: Optional[int] = None
    tags: List[str] = []
    notes: Optional[str] = None
    custom_fields: Dict[str, Any] = {}


class PlantUpdate(BaseModel):
    """Schema for updating plant"""
    name: Optional[str] = None
    status: Optional[PlantStatusEnum] = None
    cer_id: Optional[int] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class PlantResponse(PlantBase):
    """Schema for plant response"""
    id: int
    tenant_id: str
    site_id: Optional[int] = None  # NEW: Site relationship
    cer_id: Optional[int] = None
    next_deadline: Optional[datetime] = None
    next_deadline_type: Optional[str] = None
    deadline_color: Optional[str] = None
    gse_integration: bool
    terna_integration: bool
    customs_integration: bool
    dso_integration: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

