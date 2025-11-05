"""
Billing models for CER financial management
Handles billing statements, invoices, transactions, and settlements
"""

from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    String,
    ForeignKey,
    JSON,
    Enum,
    Text,
    Boolean,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class BillingStatus(str, enum.Enum):
    """Billing statement status"""

    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment status"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TransactionType(str, enum.Enum):
    """Billing transaction types"""

    PAYMENT = "payment"
    CREDIT = "credit"
    DEBIT = "debit"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class SettlementStatus(str, enum.Enum):
    """Settlement status"""

    PENDING = "pending"
    CALCULATED = "calculated"
    VALIDATED = "validated"
    FINALIZED = "finalized"
    DISPUTED = "disputed"


class BillingStatement(BaseModel):
    """Billing statement for a CER member for a billing period"""

    __tablename__ = "billing_statements"

    # Member and CER references
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("cer_members.id"), nullable=False, index=True)

    # Billing period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    billing_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)

    # Energy metrics (in kWh)
    energy_shared = Column(Float, default=0.0)  # Energy shared by this member
    energy_consumed = Column(Float, default=0.0)  # Total energy consumed
    energy_produced = Column(Float, default=0.0)  # Total energy produced (if producer/prosumer)

    # Financial amounts (in EUR)
    total_amount = Column(Float, default=0.0)  # Total amount due
    incentives = Column(Float, default=0.0)  # Incentive amount (tariffa incentivante)
    grid_fees = Column(Float, default=0.0)  # Grid connection and distribution fees
    community_fund = Column(Float, default=0.0)  # Contribution to community fund
    energy_cost = Column(Float, default=0.0)  # Cost of energy consumed
    shared_energy_value = Column(Float, default=0.0)  # Value of shared energy

    # Payment information
    amount_paid = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)  # Remaining balance
    status = Column(Enum(BillingStatus), nullable=False, default=BillingStatus.DRAFT)

    # Settlement reference
    settlement_id = Column(Integer, ForeignKey("settlements.id"), nullable=True)

    # Additional metadata
    notes = Column(Text, nullable=True)
    extra_metadata = Column(JSON, nullable=True, server_default="{}")

    # Relationships
    cer = relationship("CER", back_populates="billing_statements", lazy="select")
    member = relationship("CERMember", back_populates="billing_statements", lazy="select")
    invoice = relationship(
        "Invoice",
        back_populates="statement",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
        lazy="select",
    )
    settlement = relationship("Settlement", back_populates="statements", lazy="select")
    transactions = relationship(
        "BillingTransaction",
        back_populates="statement",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # Indexes
    __table_args__ = (
        Index("idx_billing_statements_cer_period", "cer_id", "period_start", "period_end"),
        Index("idx_billing_statements_member_period", "member_id", "period_start", "period_end"),
        Index("idx_billing_statements_status_due_date", "status", "due_date"),
    )

    def __repr__(self):
        return f"<BillingStatement Member {self.member_id} Period {self.period_start}->{self.period_end} {self.status.value}>"


class Invoice(BaseModel):
    """Invoice for billing statement"""

    __tablename__ = "invoices"

    # References
    statement_id = Column(Integer, ForeignKey("billing_statements.id"), nullable=False, unique=True)
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("cer_members.id"), nullable=False)

    # Invoice details
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)

    # Amounts
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    balance = Column(Float, nullable=False)

    # Status
    status = Column(Enum(BillingStatus), nullable=False, default=BillingStatus.DRAFT)
    is_paid = Column(Boolean, default=False)
    paid_date = Column(DateTime(timezone=True), nullable=True)

    # Line items (JSON array of invoice line items)
    line_items = Column(JSON, nullable=True, server_default="[]")

    # Payment method
    payment_method = Column(String(50), nullable=True)
    payment_reference = Column(String(200), nullable=True)

    # Additional info
    notes = Column(Text, nullable=True)
    extra_metadata = Column(JSON, nullable=True, server_default="{}")

    # Relationships
    cer = relationship("CER", back_populates="invoices", lazy="select")
    member = relationship("CERMember", back_populates="invoices", lazy="select")
    statement = relationship(
        "BillingStatement", back_populates="invoice", uselist=False, lazy="select"
    )
    transactions = relationship(
        "BillingTransaction", back_populates="invoice", cascade="all, delete-orphan", lazy="select"
    )

    def __repr__(self):
        return f"<Invoice {self.invoice_number} Amount: €{self.total_amount} Status: {self.status.value}>"


class BillingTransaction(BaseModel):
    """Financial transaction for billing (payments, credits, debits)"""

    __tablename__ = "billing_transactions"

    # References
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("cer_members.id"), nullable=False, index=True)
    statement_id = Column(Integer, ForeignKey("billing_statements.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    # Transaction details
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # Positive for credits/payments, negative for debits
    currency = Column(String(3), default="EUR")

    # Payment information
    payment_method = Column(String(50), nullable=True)  # bank_transfer, credit_card, etc.
    payment_reference = Column(String(200), nullable=True)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    # Description
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    extra_metadata = Column(JSON, nullable=True, server_default="{}")

    # Relationships
    cer = relationship("CER", back_populates="billing_transactions", lazy="select")
    member = relationship("CERMember", back_populates="billing_transactions", lazy="select")
    statement = relationship("BillingStatement", back_populates="transactions", lazy="select")
    invoice = relationship("Invoice", back_populates="transactions", lazy="select")

    # Indexes
    __table_args__ = (
        Index("idx_billing_transactions_member_date", "member_id", "created_at"),
        Index("idx_billing_transactions_cer_date", "cer_id", "created_at"),
        Index("idx_billing_transactions_status_date", "status", "created_at"),
    )

    def __repr__(self):
        return f"<BillingTransaction {self.transaction_type.value} €{self.amount} Member {self.member_id}>"


class Settlement(BaseModel):
    """Settlement calculation for a CER billing period"""

    __tablename__ = "settlements"

    # CER reference
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=False, index=True)

    # Settlement period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    settlement_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Status
    status = Column(Enum(SettlementStatus), nullable=False, default=SettlementStatus.PENDING)

    # Energy totals (in kWh)
    total_production = Column(Float, default=0.0)
    total_consumption = Column(Float, default=0.0)
    total_shared_energy = Column(Float, default=0.0)
    total_self_consumed = Column(Float, default=0.0)
    total_grid_export = Column(Float, default=0.0)
    total_grid_import = Column(Float, default=0.0)
    total_incentivized_energy = Column(Float, default=0.0)

    # Financial totals (in EUR)
    total_incentives = Column(Float, default=0.0)  # Total incentive amount
    total_grid_fees = Column(Float, default=0.0)  # Total grid fees
    total_community_fund = Column(Float, default=0.0)  # Total community fund
    total_energy_cost = Column(Float, default=0.0)  # Total energy cost
    total_amount = Column(Float, default=0.0)  # Total settlement amount

    # Incentive rate (€/MWh)
    incentive_rate = Column(Float, nullable=True)

    # Member allocation summary (JSON: {member_id: {amount, energy_shared, etc.}})
    member_allocation = Column(JSON, nullable=True, server_default="{}")

    # Calculation details
    calculation_data = Column(JSON, nullable=True, server_default="{}")
    calculation_method = Column(String(50), default="standard")

    # Validation
    validated_by = Column(Integer, nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Relationships
    cer = relationship("CER", back_populates="settlements", lazy="select")
    statements = relationship("BillingStatement", back_populates="settlement", lazy="select")

    # Indexes
    __table_args__ = (
        Index("idx_settlements_cer_period", "cer_id", "period_start", "period_end"),
        Index("idx_settlements_status_date", "status", "settlement_date"),
    )

    def __repr__(self):
        return f"<Settlement CER {self.cer_id} Period {self.period_start}->{self.period_end} Status: {self.status.value}>"
