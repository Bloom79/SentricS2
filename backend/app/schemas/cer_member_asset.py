"""
Schemas for CER Member Assets
"""

from typing import Optional, Dict, Any
from datetime import date
from pydantic import BaseModel, Field


class CERMemberAssetBase(BaseModel):
    """Base schema for CER member asset"""
    name: str = Field(..., description="Asset name")
    asset_type: str = Field(..., description="Asset type (SOLAR, WIND, STORAGE, etc.)")
    capacity: float = Field(..., gt=0, description="Capacity in kW")
    installation_date: date = Field(..., description="Installation date")
    gse_registration_id: Optional[str] = Field(None, description="GSE registration ID")
    status: str = Field(default="active", description="Asset status")
    asset_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class CERMemberAssetCreate(CERMemberAssetBase):
    """Schema for creating a member asset"""
    member_id: int = Field(..., description="Member ID")
    cer_id: int = Field(..., description="CER ID")


class CERMemberAssetUpdate(BaseModel):
    """Schema for updating a member asset"""
    name: Optional[str] = None
    asset_type: Optional[str] = None
    capacity: Optional[float] = Field(None, gt=0)
    installation_date: Optional[date] = None
    gse_registration_id: Optional[str] = None
    status: Optional[str] = None
    asset_metadata: Optional[Dict[str, Any]] = None


class CERMemberAssetResponse(CERMemberAssetBase):
    """Schema for member asset response"""
    id: int
    member_id: int
    cer_id: int
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

