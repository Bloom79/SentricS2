"""
Plant Layout schemas for API requests/responses
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PlantLayoutBase(BaseModel):
    """Base plant layout schema"""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class PlantLayoutCreate(PlantLayoutBase):
    """Schema for creating/updating plant layout"""
    pass


class PlantLayoutResponse(PlantLayoutBase):
    """Schema for plant layout response"""
    id: int
    plant_id: int
    tenant_id: str
    version: int
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True

