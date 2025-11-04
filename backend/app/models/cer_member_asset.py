"""
CER Member Asset models
Links production assets (solar panels, wind turbines, etc.) to CER members
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Date
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class CERMemberAssetStatus(str, enum.Enum):
    """Asset status"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"


class CERMemberAssetType(str, enum.Enum):
    """Asset types for CER members"""
    SOLAR = "SOLAR"
    WIND = "WIND"
    STORAGE = "STORAGE"
    BIOMASS = "BIOMASS"
    HYDRO = "HYDRO"


class CERMemberAsset(BaseModel):
    """Asset belonging to a CER member (production/storage unit)"""
    __tablename__ = "cer_member_assets"
    
    # Basic info
    name = Column(String(200), nullable=False)
    asset_type = Column(String(50), nullable=False)  # SOLAR, WIND, STORAGE, etc.
    
    # Member relationship
    member_id = Column(Integer, ForeignKey("cer_members.id"), nullable=False, index=True)
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False, index=True)
    
    # Capacity and specifications
    capacity = Column(Float, nullable=False)  # kW
    installation_date = Column(Date, nullable=False)
    
    # GSE registration
    gse_registration_id = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), default="active")
    
    # Asset metadata (for asset-specific info like panel type, inverter model, etc.)
    asset_metadata = Column(JSON, nullable=True, server_default='{}')
    
    # Relationships
    member = relationship("CERMember", back_populates="assets", lazy="select")
    cer = relationship("CER", lazy="select")
    
    def __repr__(self):
        return f"<CERMemberAsset {self.name} ({self.asset_type}) - {self.capacity}kW>"

