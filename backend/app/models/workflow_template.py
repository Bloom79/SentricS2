"""
Workflow Template models
Templates for creating workflows for plant bureaucracy processes
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class WorkflowTemplateCategoryEnum(str, enum.Enum):
    """Workflow template categories"""

    COMPLIANCE = "Compliance"
    REGISTRATION = "Registration"
    MAINTENANCE = "Maintenance"
    FISCAL = "Fiscal"
    DOCUMENT_SUBMISSION = "Document Submission"
    ACTIVATION = "Activation"
    RENEWAL = "Renewal"


class WorkflowTemplateRecurrenceEnum(str, enum.Enum):
    """Template recurrence types"""

    ONE_TIME = "one-time"
    RECURRING = "recurring"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class WorkflowTemplatePhase(BaseModel):
    """Workflow template phase definition"""

    __tablename__ = "workflow_template_phases"

    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)

    # Phase requirements
    required_documents = Column(JSON, default=list)  # List of document types required
    estimated_days = Column(Integer)  # Estimated days to complete this phase
    auto_advance = Column(Boolean, default=False)  # Auto-advance when documents uploaded

    # Phase metadata
    phase_config = Column(JSON, default=dict)

    # Relationships
    template = relationship("WorkflowTemplate", back_populates="phases")

    def __repr__(self):
        return f"<WorkflowTemplatePhase {self.name} (order: {self.order})>"


class WorkflowTemplate(BaseModel):
    """Workflow template - reusable workflow definitions"""

    __tablename__ = "workflow_templates"

    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(WorkflowTemplateCategoryEnum), nullable=False)
    recurrence = Column(
        Enum(WorkflowTemplateRecurrenceEnum), default=WorkflowTemplateRecurrenceEnum.ONE_TIME
    )

    # Workflow purpose/type
    workflow_purpose = Column(String(200))  # e.g., "CER Registration", "Plant Activation"
    workflow_type = Column(String(100))  # Maps to WorkflowTypeEnum

    # Template metadata
    is_active = Column(Boolean, default=True)
    is_system_template = Column(Boolean, default=False)  # System templates cannot be deleted

    # Estimated duration
    estimated_duration_days = Column(Integer)

    # Template configuration
    template_config = Column(JSON, default=dict)

    # Relationships
    phases = relationship(
        "WorkflowTemplatePhase",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="WorkflowTemplatePhase.order",
    )

    def __repr__(self):
        return f"<WorkflowTemplate {self.name} ({self.category})>"
