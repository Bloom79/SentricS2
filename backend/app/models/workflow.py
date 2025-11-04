"""
Workflow models
Consolidated from Kronos EAM
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class WorkflowStatusEnum(str, enum.Enum):
    """Workflow status"""
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"


class WorkflowTypeEnum(str, enum.Enum):
    """Workflow types"""
    ACTIVATION = "Activation"
    COMPLIANCE = "Compliance"
    FISCAL = "Fiscal"
    MAINTENANCE = "Maintenance"
    DOCUMENT_SUBMISSION = "Document Submission"


class WorkflowPhase(BaseModel):
    """Workflow phase - Enhanced with Italian bureaucratic process requirements"""
    __tablename__ = "workflow_phases"
    
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    status = Column(String(50), default="pending")
    due_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Phase metadata
    phase_data = Column(JSON, default=dict)
    
    # Required documents (list of document names/types)
    required_documents = Column(JSON, default=list)  # ["RID Application Form", "Plant Technical Specifications", ...]
    
    # Form fields/data structure for official forms
    official_form_fields = Column(JSON, default=dict)  # {"produttore_denominazione": "Denominazione", ...}
    
    # Portal information
    portal_url = Column(String(500))  # Main portal URL
    portal_login_url = Column(String(500))  # Login page URL
    required_credentials = Column(String(100))  # SPID, CIE, CNS, Digital Certificate, Email, etc.
    submission_method = Column(String(100))  # Portal upload, PEC, EDI, System-to-System, Manual
    
    # Regulatory deadlines
    regulatory_deadline = Column(DateTime)  # Legal deadline
    deadline_type = Column(String(50))  # peremptory, ordinary, suspensive
    deadline_consequences = Column(Text)  # What happens if missed
    
    # External tracking
    external_protocol_number = Column(String(200))  # Protocol/reference from entity
    submission_date = Column(DateTime)  # When submitted
    response_date = Column(DateTime)  # When response received
    
    # Costs
    cost_amount = Column(Float)  # Cost in EUR
    cost_description = Column(String(500))  # Description of cost
    payment_method = Column(String(100))  # F24, Bank transfer, Portal payment
    payment_reference = Column(String(200))  # F24 code, transfer reference
    
    # Human checkpoints
    requires_human_auth = Column(Boolean, default=False)  # Needs SPID/CIE/CNS
    requires_physical_signature = Column(Boolean, default=False)  # Requires physical signature
    requires_site_inspection = Column(Boolean, default=False)  # Requires site inspection
    human_checkpoint_notes = Column(Text)  # Notes about human checkpoints
    
    # Process tracking
    checklist_items = Column(JSON, default=list)  # ["Verifica firma tecnico", "Controllo completezza", ...]
    instructions = Column(Text)  # Detailed step-by-step instructions
    external_resources = Column(JSON, default=list)  # Links to guides, forms, portals
    
    # Responsible entity
    responsible_entity = Column(String(100))  # GSE, Terna, DSO, ADM, Comune, CER
    practice_type = Column(String(200))  # Type of practice/procedure
    
    # Document templates
    document_templates = Column(JSON, default=list)  # Template references
    
    # Estimated duration
    estimated_days = Column(Integer)  # Estimated days to complete
    
    # Relationships
    workflow = relationship("Workflow", back_populates="phases")
    
    def __repr__(self):
        return f"<WorkflowPhase {self.name} (order: {self.order})>"


class Workflow(BaseModel):
    """Workflow model"""
    __tablename__ = "workflows"
    
    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(WorkflowTypeEnum), nullable=False)
    status = Column(Enum(WorkflowStatusEnum), nullable=False, default=WorkflowStatusEnum.DRAFT)
    
    # Plant relationship
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    
    # Template reference
    template_id = Column(Integer, nullable=True)
    
    # Dates
    start_date = Column(DateTime)
    due_date = Column(DateTime)
    completed_date = Column(DateTime)
    
    # Progress
    progress_percentage = Column(Integer, default=0)
    current_phase = Column(String(200))
    
    # Metadata
    workflow_data = Column(JSON, default=dict)
    notes = Column(Text)
    
    # Relationships
    plant = relationship("Plant", back_populates="workflows")
    phases = relationship("WorkflowPhase", back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowPhase.order")
    
    def __repr__(self):
        return f"<Workflow {self.name} ({self.type})>"
    
    @property
    def is_completed(self) -> bool:
        """Check if workflow is completed"""
        return self.status == WorkflowStatusEnum.COMPLETED
    
    @property
    def is_in_progress(self) -> bool:
        """Check if workflow is in progress"""
        return self.status == WorkflowStatusEnum.IN_PROGRESS

