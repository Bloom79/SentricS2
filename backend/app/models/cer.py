"""
CER (Renewable Energy Community) models
Migrated from Sentrics with multi-tenant support
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
    Enum,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.models.base import BaseModel


class CERLegalType(str, enum.Enum):
    """Legal types for CER"""

    COOPERATIVE = "cooperative"
    ASSOCIATION = "association"
    CONSORTIUM = "consortium"


class CERStatus(str, enum.Enum):
    """CER status"""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CERType(str, enum.Enum):
    """CER type"""

    SIMULATION = "simulation"
    ACTIVE = "active"


class CER(BaseModel):
    """Renewable Energy Community model"""

    __tablename__ = "cer_configuration"

    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    legal_type = Column(Enum(CERLegalType), nullable=False)
    type = Column(Enum(CERType), nullable=False, default=CERType.ACTIVE)
    status = Column(Enum(CERStatus), nullable=False, default=CERStatus.DRAFT)

    # Location fields (PostGIS)
    address = Column(String(500), nullable=False)
    location = Column(Geography("POINT"), nullable=True)  # PostGIS point
    boundary = Column(Geography("POLYGON"), nullable=True)  # PostGIS polygon
    region = Column(String(50), nullable=False)
    province = Column(String(10), nullable=True)
    municipality = Column(String(100), nullable=True)
    primary_substation_id = Column(String(100), nullable=False)

    # Energy related
    total_capacity = Column(Float, default=0.0)  # Total capacity in kW
    energy_source = Column(String(50), nullable=True)  # solar, wind, etc.

    # Configuration settings
    technical_info = Column(JSON, nullable=False, server_default="{}")
    gse_compliance = Column(JSON, nullable=False, server_default="{}")
    gse_compliance_status = Column(String(50), default="pending")
    simulation_settings = Column(JSON, nullable=True)
    billing_settings = Column(JSON, nullable=True)
    member_limits = Column(JSON, nullable=False, server_default="{}")

    # PNRR funding
    pnrr_funding_applied = Column(Boolean, default=False)
    pnrr_funding_amount = Column(Float, nullable=True)
    pnrr_funding_status = Column(String(50), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    members = relationship(
        "CERMember", back_populates="cer", cascade="all, delete-orphan", lazy="select"
    )
    plants = relationship("Plant", back_populates="cer", lazy="select")
    participation_requests = relationship(
        "CERParticipationRequest", back_populates="cer", cascade="all, delete-orphan", lazy="select"
    )
    energy_transactions = relationship(
        "EnergyTransaction", back_populates="cer", cascade="all, delete-orphan", lazy="select"
    )
    energy_sharing_calculations = relationship(
        "EnergySharingCalculation",
        back_populates="cer",
        cascade="all, delete-orphan",
        lazy="select",
    )
    compliance_requirements = relationship(
        "ComplianceRequirement", back_populates="cer", lazy="select"
    )
    compliance_records = relationship("ComplianceRecord", back_populates="cer", lazy="select")
    documents = relationship("Document", back_populates="cer", lazy="select")
    billing_statements = relationship(
        "BillingStatement", back_populates="cer", cascade="all, delete-orphan", lazy="select"
    )
    invoices = relationship(
        "Invoice", back_populates="cer", cascade="all, delete-orphan", lazy="select"
    )
    billing_transactions = relationship(
        "BillingTransaction", back_populates="cer", cascade="all, delete-orphan", lazy="select"
    )
    settlements = relationship(
        "Settlement", back_populates="cer", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self):
        return f"<CER {self.name} ({self.legal_type})>"

    @property
    def member_count(self) -> int:
        """Get active member count"""
        return len([m for m in self.members if m.status == "active"])

    @property
    def total_production(self) -> float:
        """Calculate total production from linked plants"""
        return sum(p.power_kw for p in self.plants if p.status == "In Operation")


class CERMember(BaseModel):
    """CER Member model"""

    __tablename__ = "cer_members"

    # Basic info
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=False)

    # Member type
    member_type = Column(String(50), nullable=False)  # consumer, producer, prosumer
    user_type = Column(String(50), default="real")  # real, simulated
    status = Column(String(50), default="active")  # active, inactive, pending

    # POD (Point of Delivery) Information
    pod_id = Column(String(100), unique=True, index=True)
    smart_meter_id = Column(String(100), nullable=True)
    meter_type = Column(String(50), nullable=True)  # 2G, 1G

    # Energy Profile
    load_profile_type = Column(
        String(50), nullable=False
    )  # residential, commercial, industrial, custom
    load_profile_data = Column(JSON, nullable=True)
    contracted_power = Column(Float, nullable=True)  # in kW
    voltage_level = Column(String(50), nullable=True)

    # Status and Dates
    is_active = Column(Boolean, default=True)
    activation_date = Column(DateTime(timezone=True), nullable=True)
    deactivation_date = Column(DateTime(timezone=True), nullable=True)
    verification_status = Column(String(50), nullable=True)

    # Technical Information
    technical_info = Column(JSON, nullable=True, server_default="{}")
    device_info = Column(JSON, nullable=True, server_default="{}")
    energy_sharing_preferences = Column(JSON, nullable=True, server_default="{}")

    # Billing Information
    fiscal_code = Column(String(50), nullable=True)
    vat_number = Column(String(50), nullable=True)
    billing_address = Column(String(500), nullable=True)
    billing_preferences = Column(JSON, nullable=True, server_default="{}")

    # Foreign Keys
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Plant relationship (member can be linked to a plant)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True, index=True)

    # Relationships
    cer = relationship("CER", back_populates="members", lazy="select")
    user = relationship("User", back_populates="cer_members", lazy="select")
    plant = relationship("Plant", lazy="select")  # Link to plant if member has one
    assets = relationship(
        "CERMemberAsset", back_populates="member", cascade="all, delete-orphan", lazy="select"
    )
    energy_transactions = relationship(
        "EnergyTransaction", back_populates="member", cascade="all, delete-orphan", lazy="select"
    )
    billing_statements = relationship(
        "BillingStatement", back_populates="member", cascade="all, delete-orphan", lazy="select"
    )
    invoices = relationship(
        "Invoice", back_populates="member", cascade="all, delete-orphan", lazy="select"
    )
    billing_transactions = relationship(
        "BillingTransaction", back_populates="member", cascade="all, delete-orphan", lazy="select"
    )

    # Energy Statistics
    energy_produced = Column(Float, default=0.0)  # Total energy produced in kWh
    energy_consumed = Column(Float, default=0.0)  # Total energy consumed in kWh
    energy_shared = Column(Float, default=0.0)  # Total energy shared in kWh

    def __repr__(self):
        return f"<CERMember {self.name} ({self.member_type})>"


class ParticipationRequestStatus(str, enum.Enum):
    """Participation request status"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class CERParticipationRequest(BaseModel):
    """CER Participation Request model"""

    __tablename__ = "cer_participation_requests"

    # Request info
    status = Column(
        Enum(ParticipationRequestStatus), nullable=False, default=ParticipationRequestStatus.PENDING
    )
    request_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="cer_participation_requests")
    cer = relationship("CER", back_populates="participation_requests")

    def __repr__(self):
        return f"<CERParticipationRequest {self.user_id} -> CER {self.cer_id} ({self.status})>"
