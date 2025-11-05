"""
Compliance models
Consolidated from Kronos EAM
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    Enum,
    Text,
    Float,
)
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class ComplianceTypeEnum(str, enum.Enum):
    """Compliance types"""

    ANNUAL = "Annual"
    QUARTERLY = "Quarterly"
    MONTHLY = "Monthly"
    ONE_TIME = "One-Time"
    EVENT_BASED = "Event-Based"


class ComplianceStatusEnum(str, enum.Enum):
    """Compliance status"""

    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class ComplianceRequirement(BaseModel):
    """Compliance requirement model"""

    __tablename__ = "compliance_requirements"

    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(ComplianceTypeEnum), nullable=False)

    # Timing
    frequency_days = Column(Integer)  # Days between requirements
    due_date_offset = Column(Integer, default=0)  # Days before deadline

    # Portal/Authority
    authority = Column(String(100))  # GSE, Terna, DSO, ADM
    portal_name = Column(String(100))

    # Entity relationships (can be linked to Plant or CER)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=True)

    # Metadata
    requirement_data = Column(JSON, default=dict)

    # Relationships
    plant = relationship(
        "Plant",
        back_populates="compliance_requirements",
        foreign_keys="[ComplianceRequirement.plant_id]",
    )
    cer = relationship("CER", back_populates="compliance_requirements")
    records = relationship("ComplianceRecord", back_populates="requirement")

    def __repr__(self):
        return f"<ComplianceRequirement {self.name}>"


class ComplianceRecord(BaseModel):
    """Compliance record - tracks actual compliance"""

    __tablename__ = "compliance_records"

    # Requirement reference
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.id"), nullable=False)

    # Status
    status = Column(
        Enum(ComplianceStatusEnum), nullable=False, default=ComplianceStatusEnum.PENDING
    )

    # Dates
    due_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime)
    submitted_date = Column(DateTime)

    # Penalties
    penalty_amount = Column(Float, default=0.0)
    penalty_applied = Column(Boolean, default=False)

    # Notes
    notes = Column(Text)

    # Entity relationships (can be linked to Plant or CER)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=True)

    # Metadata
    record_data = Column(JSON, default=dict)

    # Relationships
    requirement = relationship("ComplianceRequirement", back_populates="records")
    plant = relationship("Plant")
    cer = relationship("CER")
    documents = relationship("Document", back_populates="compliance_record")

    def __repr__(self):
        return f"<ComplianceRecord {self.requirement_id} - {self.status}>"

    @property
    def is_overdue(self) -> bool:
        """Check if compliance is overdue"""
        if self.status == ComplianceStatusEnum.COMPLETED:
            return False
        from datetime import datetime

        return datetime.utcnow() > self.due_date

    @property
    def days_overdue(self) -> int:
        """Get days overdue"""
        if not self.is_overdue:
            return 0
        from datetime import datetime

        delta = datetime.utcnow() - self.due_date
        return delta.days
