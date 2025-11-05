"""
Energy Transaction models for CER energy sharing
Implements energy sharing calculations and transaction tracking
"""

from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, JSON, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class TransactionType(str, enum.Enum):
    """Energy transaction types"""

    PRODUCTION = "production"  # Energy produced
    CONSUMPTION = "consumption"  # Energy consumed
    SHARED = "shared"  # Energy shared within CER
    SELF_CONSUMED = "self_consumed"  # Energy self-consumed at production site
    GRID_EXPORT = "grid_export"  # Energy exported to grid
    GRID_IMPORT = "grid_import"  # Energy imported from grid


class EnergyTransaction(BaseModel):
    """Energy transaction model - tracks hourly energy flows"""

    __tablename__ = "energy_transactions"

    # Timestamp (hourly granularity)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Transaction type
    transaction_type = Column(Enum(TransactionType), nullable=False)

    # Energy values (in kWh)
    energy_kwh = Column(Float, nullable=False)

    # References
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False)
    member_id = Column(
        Integer, ForeignKey("cer_members.id"), nullable=True
    )  # Optional - can be CER-level
    plant_id = Column(
        Integer, ForeignKey("plants.id"), nullable=True
    )  # Optional - if from specific plant

    # Calculation metadata
    calculation_data = Column(JSON, nullable=True, server_default="{}")  # Store calculation details
    is_calculated = Column(String(50), default="manual")  # manual, calculated, imported

    # Relationships
    cer = relationship("CER", back_populates="energy_transactions")
    member = relationship("CERMember", back_populates="energy_transactions")
    plant = relationship("Plant")

    # Indexes for performance
    __table_args__ = (
        Index("idx_cer_timestamp", "cer_id", "timestamp"),
        Index("idx_member_timestamp", "member_id", "timestamp"),
        Index("idx_cer_type_timestamp", "cer_id", "transaction_type", "timestamp"),
    )

    def __repr__(self):
        return f"<EnergyTransaction {self.transaction_type.value} {self.energy_kwh}kWh @ {self.timestamp}>"


class EnergySharingCalculation(BaseModel):
    """Stores calculated energy sharing results for a CER"""

    __tablename__ = "energy_sharing_calculations"

    # Time period
    calculation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # CER reference
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False)

    # Calculated values (in kWh)
    total_production = Column(Float, default=0.0)
    total_consumption = Column(Float, default=0.0)
    shared_energy = Column(Float, default=0.0)  # min(production, consumption)
    self_consumed_energy = Column(Float, default=0.0)
    grid_export = Column(Float, default=0.0)  # production - shared - self_consumed
    grid_import = Column(Float, default=0.0)  # consumption - shared - self_consumed

    # Incentivized energy (portion eligible for incentives)
    incentivized_energy = Column(Float, default=0.0)
    incentive_rate = Column(Float, nullable=True)  # €/MWh

    # Member allocation (JSON: {member_id: {energy_shared, percentage}})
    member_allocation = Column(JSON, nullable=True, server_default="{}")

    # Calculation metadata
    calculation_method = Column(String(50), default="standard")  # standard, optimized, custom
    calculation_data = Column(JSON, nullable=True, server_default="{}")

    # Status
    status = Column(String(50), default="calculated")  # calculated, validated, finalized

    # Relationships
    cer = relationship("CER", back_populates="energy_sharing_calculations")

    def __repr__(self):
        return (
            f"<EnergySharingCalculation CER {self.cer_id} {self.period_start}->{self.period_end}>"
        )
