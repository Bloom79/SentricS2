"""
Billing Pydantic schemas for CER financial management
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.billing import (
    BillingStatus, PaymentStatus, TransactionType, SettlementStatus
)


# Billing Statement Schemas
class BillingStatementBase(BaseModel):
    """Base billing statement schema"""
    period_start: datetime
    period_end: datetime
    due_date: datetime
    notes: Optional[str] = None


class BillingStatementCreate(BillingStatementBase):
    """Schema for creating billing statement"""
    cer_id: int
    member_id: int
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class BillingStatementUpdate(BaseModel):
    """Schema for updating billing statement"""
    status: Optional[BillingStatus] = None
    amount_paid: Optional[float] = None
    notes: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class BillingStatementResponse(BillingStatementBase):
    """Schema for billing statement response"""
    id: int
    cer_id: int
    member_id: int
    billing_date: datetime
    energy_shared: float
    energy_consumed: float
    energy_produced: float
    total_amount: float
    incentives: float
    grid_fees: float
    community_fund: float
    energy_cost: float
    shared_energy_value: float
    amount_paid: float
    balance: float
    status: BillingStatus
    settlement_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceBase(BaseModel):
    """Base invoice schema"""
    invoice_date: datetime
    due_date: datetime
    subtotal: float
    tax_amount: float = 0.0
    total_amount: float
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    """Schema for creating invoice"""
    statement_id: int
    cer_id: int
    member_id: int
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class InvoiceUpdate(BaseModel):
    """Schema for updating invoice"""
    status: Optional[BillingStatus] = None
    amount_paid: Optional[float] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    """Schema for invoice response"""
    id: int
    invoice_number: str
    statement_id: int
    cer_id: int
    member_id: int
    amount_paid: float
    balance: float
    status: BillingStatus
    is_paid: bool
    paid_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Billing Transaction Schemas
class BillingTransactionCreate(BaseModel):
    """Schema for creating billing transaction"""
    cer_id: int
    member_id: int
    transaction_type: TransactionType
    amount: float = Field(..., description="Positive for credits/payments, negative for debits")
    currency: str = "EUR"
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_date: Optional[datetime] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    statement_id: Optional[int] = None
    invoice_id: Optional[int] = None
    extra_metadata: Dict[str, Any] = Field(default_factory=dict)


class BillingTransactionUpdate(BaseModel):
    """Schema for updating billing transaction"""
    status: Optional[PaymentStatus] = None
    payment_date: Optional[datetime] = None
    notes: Optional[str] = None


class BillingTransactionResponse(BaseModel):
    """Schema for billing transaction response"""
    id: int
    cer_id: int
    member_id: int
    transaction_type: TransactionType
    amount: float
    currency: str
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_date: Optional[datetime] = None
    status: PaymentStatus
    description: Optional[str] = None
    statement_id: Optional[int] = None
    invoice_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Settlement Schemas
class SettlementCreate(BaseModel):
    """Schema for creating settlement"""
    cer_id: int
    period_start: datetime
    period_end: datetime
    calculation_method: str = "standard"
    notes: Optional[str] = None


class SettlementUpdate(BaseModel):
    """Schema for updating settlement"""
    status: Optional[SettlementStatus] = None
    notes: Optional[str] = None


class SettlementResponse(BaseModel):
    """Schema for settlement response"""
    id: int
    cer_id: int
    period_start: datetime
    period_end: datetime
    settlement_date: datetime
    status: SettlementStatus
    total_production: float
    total_consumption: float
    total_shared_energy: float
    total_self_consumed: float
    total_grid_export: float
    total_grid_import: float
    total_incentivized_energy: float
    total_incentives: float
    total_grid_fees: float
    total_community_fund: float
    total_energy_cost: float
    total_amount: float
    incentive_rate: Optional[float] = None
    member_allocation: Dict[str, Any] = Field(default_factory=dict)
    calculation_method: str
    validated_by: Optional[int] = None
    validated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Billing Overview Schemas
class BillingOverviewResponse(BaseModel):
    """Schema for billing overview"""
    cer_id: int
    period_start: datetime
    period_end: datetime
    total_statements: int
    total_amount: float
    total_paid: float
    total_balance: float
    pending_statements: int
    overdue_statements: int
    paid_statements: int
    statements: List[BillingStatementResponse] = Field(default_factory=list)


class MemberBalanceResponse(BaseModel):
    """Schema for member balance"""
    member_id: int
    pod_id: str
    member_type: str
    total_energy_shared: float
    current_balance: float
    payment_status: str
    last_payment_date: Optional[datetime] = None
    outstanding_statements: int = 0


class CalculateSettlementRequest(BaseModel):
    """Schema for settlement calculation request"""
    cer_id: int
    period_start: datetime
    period_end: datetime
    calculation_method: str = "standard"
    save_settlement: bool = True
    generate_statements: bool = True
    generate_invoices: bool = False


class SettlementCalculationResponse(BaseModel):
    """Schema for settlement calculation response"""
    settlement_id: Optional[int] = None
    calculation: Dict[str, Any]
    statements_generated: int = 0
    invoices_generated: int = 0

