"""
Asset models for equipment management
Migrated from Sentrics with multi-tenant support
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class AssetStatus(str, enum.Enum):
    """Asset status"""

    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    DECOMMISSIONED = "decommissioned"


class ComponentType(str, enum.Enum):
    """Component types"""

    PANEL = "panel"
    INVERTER = "inverter"
    BATTERY = "battery"
    TRANSFORMER = "transformer"
    METER = "meter"
    MONITORING = "monitoring"
    OTHER = "other"


class AssetType(BaseModel):
    """Asset Type model - defines asset templates"""

    __tablename__ = "asset_types"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    normalized_name = Column(String(100), index=True)  # For search/filtering

    # Dynamic attributes schema (JSON schema for validation)
    attributes = Column(JSON, nullable=True, server_default="{}")

    # Default values
    default_attributes = Column(JSON, nullable=True, server_default="{}")

    # Relationships
    assets = relationship("Asset", back_populates="asset_type")

    def __repr__(self):
        return f"<AssetType {self.name}>"


class Asset(BaseModel):
    """Asset model - individual equipment instances"""

    __tablename__ = "assets"

    # Basic info
    name = Column(String(200), nullable=False)
    model = Column(String(100), nullable=True)
    manufacturer = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True, unique=True, index=True)

    # Type and classification
    type_id = Column(Integer, ForeignKey("asset_types.id"), nullable=False)
    component_type = Column(String(50), nullable=True)  # panel, inverter, battery, etc.

    # Plant relationship
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)

    # Status
    status = Column(String(50), default="operational")

    # Installation
    installation_date = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(200), nullable=True)  # Physical location within plant

    # Technical specifications
    rated_power = Column(Float, nullable=True)  # kW
    efficiency = Column(Float, nullable=True)  # percentage
    voltage = Column(Float, nullable=True)  # V
    current = Column(Float, nullable=True)  # A

    # Dynamic attributes (type-specific)
    dynamic_attributes = Column(JSON, nullable=True, server_default="{}")

    # Hierarchy (for complex assets like solar arrays)
    parent_id = Column(Integer, ForeignKey("assets.id"), nullable=True)

    # Notes and metadata
    notes = Column(Text, nullable=True)
    warranty_expiry = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    plant = relationship("Plant", back_populates="assets")
    asset_type = relationship("AssetType", back_populates="assets")
    parent = relationship("Asset", remote_side="Asset.id", backref="children")
    maintenance_records = relationship("AssetMaintenance", back_populates="asset")

    def __repr__(self):
        return f"<Asset {self.name} ({self.asset_type.name if self.asset_type else 'Unknown'})>"

    @property
    def is_operational(self) -> bool:
        """Check if asset is operational"""
        return self.status == "operational"


class AssetMaintenance(BaseModel):
    """Asset Maintenance record"""

    __tablename__ = "asset_maintenance"

    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)

    # Maintenance details
    maintenance_type = Column(String(50), nullable=False)  # preventive, corrective, inspection
    description = Column(Text, nullable=True)
    performed_by = Column(String(200), nullable=True)

    # Dates
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    performed_date = Column(DateTime(timezone=True), nullable=True)
    next_maintenance_date = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(String(50), default="planned")  # planned, in_progress, completed, cancelled

    # Results
    findings = Column(Text, nullable=True)
    actions_taken = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)

    # Documents
    documents = Column(JSON, nullable=True, server_default="[]")  # List of document IDs

    # Relationships
    asset = relationship("Asset", back_populates="maintenance_records")

    def __repr__(self):
        return f"<AssetMaintenance {self.asset_id} - {self.maintenance_type}>"
