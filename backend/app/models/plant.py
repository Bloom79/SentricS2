"""
Power Plant models with multi-tenant support
Enhanced with CER and Asset relationships
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.orm import relationship, foreign
import enum

from app.models.base import BaseModel


class PlantStatusEnum(str, enum.Enum):
    IN_OPERATION = "IN_OPERATION"
    IN_AUTHORIZATION = "IN_AUTHORIZATION"
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    DECOMMISSIONED = "DECOMMISSIONED"

    @property
    def label(self) -> str:
        return {
            "IN_OPERATION": "In Operation",
            "IN_AUTHORIZATION": "In Authorization",
            "UNDER_CONSTRUCTION": "Under Construction",
            "DECOMMISSIONED": "Decommissioned",
        }[self.value]


class PlantTypeEnum(str, enum.Enum):
    PHOTOVOLTAIC = "PHOTOVOLTAIC"
    WIND = "WIND"
    HYDROELECTRIC = "HYDROELECTRIC"
    BIOMASS = "BIOMASS"
    GEOTHERMAL = "GEOTHERMAL"

    @property
    def label(self) -> str:
        return {
            "PHOTOVOLTAIC": "Photovoltaic",
            "WIND": "Wind",
            "HYDROELECTRIC": "Hydroelectric",
            "BIOMASS": "Biomass",
            "GEOTHERMAL": "Geothermal",
        }[self.value]


class Plant(BaseModel):
    """Main power plant model - Enhanced with CER and Asset support"""

    __tablename__ = "plants"

    # Basic info
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    power = Column(String(50), nullable=False)  # e.g., "1.2 MW"
    power_kw = Column(Float, nullable=False, index=True)  # Numeric value in kW

    # Status
    status = Column(Enum(PlantStatusEnum), nullable=False, index=True)
    type = Column(Enum(PlantTypeEnum), nullable=False, index=True)

    # NEW: Site relationship (Sites → Plants → Assets hierarchy)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True, index=True)

    # Location
    location = Column(String(200), nullable=False)
    address = Column(String(500))
    municipality = Column(String(100))
    province = Column(String(10))
    region = Column(String(50), index=True)
    latitude = Column(Float)
    longitude = Column(Float)

    # NEW: CER relationship
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=True, index=True)

    # Next deadline tracking
    next_deadline = Column(DateTime, index=True)
    next_deadline_type = Column(String(100))
    deadline_color = Column(String(20))  # Color coding for UI

    # Technical details (stored as related record via PlantRegistry.plant_id)
    # Note: Registry relationship is one-to-one via PlantRegistry.plant_id (unique)

    # Integration status
    gse_integration = Column(Boolean, default=False)
    terna_integration = Column(Boolean, default=False)
    customs_integration = Column(Boolean, default=False)
    dso_integration = Column(Boolean, default=False)

    # Metadata
    tags = Column(JSON, default=list)
    notes = Column(Text)
    custom_fields = Column(JSON, default=dict)

    # Relationships
    tenant = relationship(
        "Tenant",
        back_populates="plants",
        foreign_keys="[Plant.tenant_id]",
        primaryjoin="Plant.tenant_id == Tenant.id",
        lazy="select",
    )
    site = relationship("Site", back_populates="plants")  # NEW: Site relationship
    registry = relationship(
        "PlantRegistry", back_populates="plant", uselist=False
    )  # One-to-one via PlantRegistry.plant_id (unique)
    performance_data = relationship("PlantPerformance", back_populates="plant")
    maintenances = relationship("Maintenance", back_populates="plant")
    checklist = relationship("ComplianceChecklist", back_populates="plant", uselist=False)

    # NEW: CER relationship
    cer = relationship("CER", back_populates="plants")

    # NEW: Asset relationship
    assets = relationship("Asset", back_populates="plant", cascade="all, delete-orphan")

    # Compliance and workflow relationships
    documents = relationship("Document", back_populates="plant")
    workflows = relationship("Workflow", back_populates="plant")
    compliance_requirements = relationship("ComplianceRequirement", back_populates="plant")
    recurring_obligations = relationship(
        "RecurringObligation", back_populates="plant", foreign_keys="[RecurringObligation.plant_id]"
    )

    # NEW: Visual Designer layout
    layout = relationship(
        "PlantLayout", back_populates="plant", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Plant {self.code}: {self.name}>"

    def is_active(self) -> bool:
        """Check if plant is active"""
        return self.status == PlantStatusEnum.IN_OPERATION

    @property
    def asset_count(self) -> int:
        """Get total asset count"""
        return len(self.assets) if self.assets else 0

    @property
    def operational_assets(self) -> int:
        """Get count of operational assets"""
        return len([a for a in self.assets if a.status == "operational"]) if self.assets else 0


# Import other plant-related models (simplified - copy from Kronos EAM)
class PlantRegistry(BaseModel):
    """Plant registry for technical details"""

    __tablename__ = "plant_registries"

    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, unique=True)

    # Technical specifications
    installation_date = Column(DateTime)
    commissioning_date = Column(DateTime)
    censimp_code = Column(String(50), unique=True, index=True)
    pod_code = Column(String(50), index=True)

    # Technical data
    technical_specs = Column(JSON, default=dict)

    # Relationships - One-to-one: PlantRegistry belongs to Plant (plant_id is unique)
    plant = relationship(
        "Plant", back_populates="registry", foreign_keys="[PlantRegistry.plant_id]", uselist=False
    )


class PlantPerformance(BaseModel):
    """Plant performance data"""

    __tablename__ = "plant_performance"

    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)

    # Performance metrics
    date = Column(DateTime, nullable=False, index=True)
    production_kwh = Column(Float)
    efficiency = Column(Float)

    # Relationships
    plant = relationship("Plant", back_populates="performance_data")


class Maintenance(BaseModel):
    """Maintenance record"""

    __tablename__ = "maintenances"

    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)

    maintenance_type = Column(String(50))
    description = Column(Text)
    scheduled_date = Column(DateTime)
    performed_date = Column(DateTime)

    # Relationships
    plant = relationship("Plant", back_populates="maintenances")


class ComplianceChecklist(BaseModel):
    """Compliance checklist"""

    __tablename__ = "compliance_checklists"

    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, unique=True)
    checklist_items = Column(JSON, default=dict)

    # Relationships
    plant = relationship("Plant", back_populates="checklist", uselist=False)
