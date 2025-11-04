"""
Site model for physical locations containing multiple plants
Part of Sites → Plants → Assets hierarchy
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Enum, Text, Numeric
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.models.base import BaseModel


class SiteTypeEnum(str, enum.Enum):
    """Site type enumeration"""
    INDUSTRIAL = "industrial"
    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"
    MIXED = "mixed"


class SiteStatusEnum(str, enum.Enum):
    """Site status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    UNDER_CONSTRUCTION = "under_construction"
    DECOMMISSIONED = "decommissioned"


class Site(BaseModel):
    """Site model - Physical location containing multiple plants"""
    __tablename__ = "sites"
    
    # Basic info
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # Type and status
    site_type = Column(Enum(SiteTypeEnum), nullable=False, default=SiteTypeEnum.INDUSTRIAL, index=True)
    status = Column(String(50), nullable=False, default="active", index=True)
    operational_status = Column(String(50), nullable=True)
    
    # Location (geographic data)
    location = Column(String(200), nullable=True)  # Human-readable location
    address = Column(String(500), nullable=True)
    street_address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    province = Column(String(10), nullable=True)
    region = Column(String(50), nullable=True, index=True)
    country = Column(String(100), nullable=True, default="Italy")
    
    # Geographic coordinates (PostGIS)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    # geography_point = Column(Geography('POINT'), nullable=True)  # PostGIS point - commented for now
    
    # Capacity and efficiency
    capacity = Column(Float, nullable=True, default=0.0)  # Total capacity in kW
    efficiency = Column(Float, nullable=True, default=0.0)  # Efficiency percentage
    
    # Area management
    available_area = Column(Float, nullable=True)  # Available area in m²
    reserved_area = Column(Float, nullable=True)  # Reserved area in m²
    
    # Dates
    commissioning_date = Column(DateTime, nullable=True)
    decommissioning_date = Column(DateTime, nullable=True)
    
    # Ownership and operations
    owner = Column(String(200), nullable=True)
    operator = Column(String(200), nullable=True)
    maintenance_provider = Column(String(200), nullable=True)
    
    # Environmental
    environmental_impact_rating = Column(Integer, nullable=True)  # Rating 1-10
    
    # Grid connection
    grid_connection_status = Column(String(50), nullable=True, default="connected")
    grid_capacity = Column(Float, nullable=True)  # Grid capacity in kW
    
    # Metadata
    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    custom_fields = Column(JSON, default=dict)
    
    # Relationships
    plants = relationship("Plant", back_populates="site", cascade="all, delete-orphan")
    storage_units = relationship("StorageUnit", back_populates="site", cascade="all, delete-orphan")
    consumers = relationship("Consumer", back_populates="site", cascade="all, delete-orphan")
    energy_flows = relationship("EnergyFlow", back_populates="site", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Site {self.id}: {self.name}>"
    
    def to_dict(self) -> dict:
        """Convert site to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "code": self.code,
            "site_type": self.site_type.value if self.site_type else None,
            "status": self.status,
            "location": self.location,
            "address": self.address,
            "city": self.city,
            "region": self.region,
            "latitude": float(self.latitude) if self.latitude else None,
            "longitude": float(self.longitude) if self.longitude else None,
            "capacity": self.capacity,
            "efficiency": self.efficiency,
            "plants_count": len(self.plants) if self.plants else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StorageUnit(BaseModel):
    """Battery Energy Storage System (BESS) per site"""
    __tablename__ = "storage_units"
    
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True)
    
    # Capacity
    capacity_kwh = Column(Float, nullable=False)  # Storage capacity in kWh
    rated_power_kw = Column(Float, nullable=False)  # Rated power in kW
    
    # Technical details
    chemistry_type = Column(String(50), nullable=True)  # Li-ion, Lead-acid, etc.
    efficiency = Column(Float, nullable=True)  # Round-trip efficiency %
    
    # Status
    status = Column(String(50), nullable=False, default="operational")
    
    # Current state
    state_of_charge = Column(Float, nullable=True)  # SoC percentage
    state_of_health = Column(Float, nullable=True)  # SoH percentage
    
    # Cycles
    total_cycles = Column(Integer, nullable=True, default=0)
    cycle_life = Column(Integer, nullable=True)  # Expected cycle life
    
    # Metadata
    manufacturer = Column(String(200), nullable=True)
    model = Column(String(200), nullable=True)
    installation_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="storage_units")
    
    def __repr__(self):
        return f"<StorageUnit {self.id}: {self.name}>"


class Consumer(BaseModel):
    """Consumer per site"""
    __tablename__ = "consumers"
    
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False, index=True)
    
    # Basic info
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=True)
    consumer_type = Column(String(50), nullable=False)  # residential, commercial, industrial
    
    # Consumption
    average_consumption_kw = Column(Float, nullable=True)  # Average consumption in kW
    peak_consumption_kw = Column(Float, nullable=True)  # Peak consumption in kW
    
    # POD
    pod_id = Column(String(100), nullable=True, index=True)
    smart_meter_id = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="active")
    activation_date = Column(DateTime, nullable=True)
    
    # Location
    address = Column(String(500), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)
    
    # Load profile
    load_profile = Column(JSON, nullable=True)  # Consumption pattern data
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="consumers")
    
    def __repr__(self):
        return f"<Consumer {self.id}: {self.name}>"


class EnergyFlow(BaseModel):
    """Energy flow visualization layout (React Flow) per site"""
    __tablename__ = "energy_flows"
    
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True, index=True)
    
    # React Flow data (stored as JSON)
    nodes = Column(JSON, nullable=False)  # List of React Flow nodes
    edges = Column(JSON, nullable=False)  # List of React Flow edges
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="energy_flows")
    
    def __repr__(self):
        return f"<EnergyFlow {self.id}: Site {self.site_id}>"


