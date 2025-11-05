"""
Database models for Kronos EAM Consolidated
All models support multi-tenant architecture
"""

from app.models.base import BaseModel, TenantMixin, TimestampMixin, AuditMixin, SoftDeleteMixin
from app.models.tenant import Tenant, TenantStatusEnum
from app.models.user import User, UserRoleEnum, UserStatusEnum
from app.models.site import Site, SiteTypeEnum, SiteStatusEnum, StorageUnit, Consumer, EnergyFlow
from app.models.plant import (
    Plant,
    PlantStatusEnum,
    PlantTypeEnum,
    PlantRegistry,
    PlantPerformance,
    Maintenance,
    ComplianceChecklist,
)
from app.models.cer import (
    CER,
    CERMember,
    CERParticipationRequest,
    CERLegalType,
    CERStatus,
    CERType,
    ParticipationRequestStatus,
)
from app.models.cer_member_asset import CERMemberAsset, CERMemberAssetStatus, CERMemberAssetType
from app.models.energy_transaction import (
    EnergyTransaction,
    EnergySharingCalculation,
    TransactionType,
)
from app.models.billing import (
    BillingStatement,
    Invoice,
    BillingTransaction,
    Settlement,
    BillingStatus,
    PaymentStatus,
    TransactionType as BillingTransactionType,
    SettlementStatus,
)
from app.models.asset import Asset, AssetType, AssetMaintenance, AssetStatus, ComponentType
from app.models.document import Document, DocumentTypeEnum, DocumentStatusEnum
from app.models.workflow import Workflow, WorkflowPhase, WorkflowStatusEnum, WorkflowTypeEnum
from app.models.workflow_template import (
    WorkflowTemplate,
    WorkflowTemplatePhase,
    WorkflowTemplateCategoryEnum,
    WorkflowTemplateRecurrenceEnum,
)
from app.models.compliance import (
    ComplianceRequirement,
    ComplianceRecord,
    ComplianceTypeEnum,
    ComplianceStatusEnum,
)
from app.models.plant_layout import PlantLayout
from app.models.recurring_obligation import RecurringObligation

__all__ = [
    # Base classes
    "BaseModel",
    "TenantMixin",
    "TimestampMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    # Tenant models
    "Tenant",
    "TenantStatusEnum",
    # User models
    "User",
    "UserRoleEnum",
    "UserStatusEnum",
    # Site models
    "Site",
    "SiteTypeEnum",
    "SiteStatusEnum",
    "StorageUnit",
    "Consumer",
    "EnergyFlow",
    # Plant models
    "Plant",
    "PlantStatusEnum",
    "PlantTypeEnum",
    "PlantRegistry",
    "PlantPerformance",
    "Maintenance",
    "ComplianceChecklist",
    # CER models
    "CER",
    "CERMember",
    "CERParticipationRequest",
    "CERLegalType",
    "CERStatus",
    "CERType",
    "ParticipationRequestStatus",
    # Energy models
    "EnergyTransaction",
    "EnergySharingCalculation",
    "TransactionType",
    # Billing models
    "BillingStatement",
    "Invoice",
    "BillingTransaction",
    "Settlement",
    "BillingStatus",
    "PaymentStatus",
    "BillingTransactionType",
    "SettlementStatus",
    # Asset models
    "Asset",
    "AssetType",
    "AssetMaintenance",
    "AssetStatus",
    "ComponentType",
    # Document models
    "Document",
    "DocumentTypeEnum",
    "DocumentStatusEnum",
    # Workflow models
    "Workflow",
    "WorkflowPhase",
    "WorkflowStatusEnum",
    "WorkflowTypeEnum",
    # Workflow Template models
    "WorkflowTemplate",
    "WorkflowTemplatePhase",
    "WorkflowTemplateCategoryEnum",
    "WorkflowTemplateRecurrenceEnum",
    # Compliance models
    "ComplianceRequirement",
    "ComplianceRecord",
    "ComplianceTypeEnum",
    "ComplianceStatusEnum",
    # Plant Layout models
    "PlantLayout",
    # Recurring Obligation models
    "RecurringObligation",
]
