"""
Asset Pydantic schemas
"""

from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import json


class AssetTypeBase(BaseModel):
    """Base asset type schema"""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    normalized_name: str
    attributes: Dict[str, Any] = {}


class AssetTypeCreate(AssetTypeBase):
    """Schema for creating asset type"""

    default_attributes: Dict[str, Any] = {}


class AssetTypeResponse(AssetTypeBase):
    """Schema for asset type response"""

    id: int
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AssetBase(BaseModel):
    """Base asset schema"""

    name: str = Field(..., min_length=1, max_length=200)
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    component_type: Optional[str] = None
    status: str = "operational"
    location: Optional[str] = None
    rated_power: Optional[float] = None
    efficiency: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None


class AssetCreate(AssetBase):
    """Schema for creating asset"""

    type_id: int
    plant_id: int
    parent_id: Optional[int] = None
    installation_date: Optional[datetime] = None
    dynamic_attributes: Dict[str, Any] = {}
    notes: Optional[str] = None
    warranty_expiry: Optional[datetime] = None


class AssetUpdate(BaseModel):
    """Schema for updating asset"""

    name: Optional[str] = None
    status: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    dynamic_attributes: Optional[Dict[str, Any]] = None


class AssetResponse(AssetBase):
    """Schema for asset response"""

    id: int
    tenant_id: str
    type_id: int
    plant_id: int
    parent_id: Optional[int] = None
    installation_date: Optional[datetime] = None
    dynamic_attributes: Dict[str, Any] = {}
    notes: Optional[str] = None
    warranty_expiry: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator("dynamic_attributes", mode="before")
    @classmethod
    def parse_dynamic_attributes(cls, v: Union[str, Dict[str, Any], None]) -> Dict[str, Any]:
        """Parse dynamic_attributes from JSON string or dict to dict"""
        if v is None:
            return {}
        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return json.loads(v) if v else {}
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    class Config:
        from_attributes = True
