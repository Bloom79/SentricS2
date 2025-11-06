"""
Workflow schemas
Enhanced with Italian bureaucratic process requirements
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class WorkflowPhaseBase(BaseModel):
    """Base workflow phase schema"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    order: int = Field(..., ge=0)
    status: str = "pending"
    due_date: Optional[datetime] = None
    estimated_days: Optional[int] = None


class WorkflowPhaseCreate(WorkflowPhaseBase):
    """Schema for creating workflow phase"""

    required_documents: List[str] = []
    official_form_fields: Dict[str, Any] = {}
    portal_url: Optional[str] = None
    portal_login_url: Optional[str] = None
    required_credentials: Optional[str] = None
    submission_method: Optional[str] = None
    regulatory_deadline: Optional[datetime] = None
    deadline_type: Optional[str] = None
    deadline_consequences: Optional[str] = None
    cost_amount: Optional[float] = None
    cost_description: Optional[str] = None
    payment_method: Optional[str] = None
    requires_human_auth: bool = False
    requires_physical_signature: bool = False
    requires_site_inspection: bool = False
    human_checkpoint_notes: Optional[str] = None
    checklist_items: List[str] = []
    instructions: Optional[str] = None
    external_resources: List[str] = []
    responsible_entity: Optional[str] = None
    practice_type: Optional[str] = None
    document_templates: List[str] = []
    phase_data: Dict[str, Any] = {}


class WorkflowPhaseUpdate(BaseModel):
    """Schema for updating workflow phase"""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    external_protocol_number: Optional[str] = None
    submission_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    phase_data: Optional[Dict[str, Any]] = None
    official_form_fields: Optional[Dict[str, Any]] = None


class WorkflowPhaseResponse(WorkflowPhaseBase):
    """Schema for workflow phase response"""

    id: int
    workflow_id: int
    tenant_id: str
    required_documents: List[str] = []
    official_form_fields: Dict[str, Any] = {}
    portal_url: Optional[str] = None
    portal_login_url: Optional[str] = None
    required_credentials: Optional[str] = None
    submission_method: Optional[str] = None
    regulatory_deadline: Optional[datetime] = None
    deadline_type: Optional[str] = None
    deadline_consequences: Optional[str] = None
    external_protocol_number: Optional[str] = None
    submission_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    cost_amount: Optional[float] = None
    cost_description: Optional[str] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    requires_human_auth: bool = False
    requires_physical_signature: bool = False
    requires_site_inspection: bool = False
    human_checkpoint_notes: Optional[str] = None
    checklist_items: List[str] = []
    instructions: Optional[str] = None
    external_resources: List[str] = []
    responsible_entity: Optional[str] = None
    practice_type: Optional[str] = None
    document_templates: List[str] = []
    phase_data: Dict[str, Any] = {}
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowBase(BaseModel):
    """Base workflow schema"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    type: str
    plant_id: Optional[int] = None
    template_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    """Schema for creating workflow"""

    workflow_data: Dict[str, Any] = {}


class WorkflowUpdate(BaseModel):
    """Schema for updating workflow"""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress_percentage: Optional[int] = None
    current_phase: Optional[str] = None
    notes: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    """Schema for workflow response"""

    id: int
    tenant_id: str
    status: str
    progress_percentage: int = 0
    current_phase: Optional[str] = None
    workflow_data: Dict[str, Any] = {}
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowDetailResponse(WorkflowResponse):
    """Schema for detailed workflow response with nested phases"""

    phases: List[WorkflowPhaseResponse] = []
    plant_name: Optional[str] = None


class WorkflowSummary(BaseModel):
    """Minimal workflow info for nested responses"""

    id: int
    name: str
    plant_id: Optional[int] = None
    plant_name: Optional[str] = None


class DocumentSummary(BaseModel):
    """Document summary for phase detail response"""

    id: int
    name: str
    type: str
    file_type: str
    file_size: int
    description: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    uploaded_by: int


class WorkflowPhaseDetailResponse(WorkflowPhaseResponse):
    """Schema for detailed phase response with documents and workflow info"""

    documents: List[DocumentSummary] = []
    workflow: WorkflowSummary


class PhaseStatusUpdateResponse(BaseModel):
    """Schema for phase status update response"""

    id: int
    status: str
    completed_date: Optional[datetime] = None
    workflow_progress: int
    workflow_status: str


class PhaseAssignmentResponse(BaseModel):
    """Schema for phase assignment response"""

    phase_id: int
    assigned_to: int
    message: str


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""

    document_id: int
    name: str
    type: str
    phase_id: int
    message: str


class CommentData(BaseModel):
    """Comment data structure"""

    id: int
    text: str
    author: str
    author_name: str
    timestamp: str
    type: str = "comment"


class CommentAddResponse(BaseModel):
    """Schema for comment add response"""

    comment: CommentData
    phase_id: int
    message: str


class WorkflowTemplatePhase(BaseModel):
    """Template phase summary"""

    id: int
    name: str
    description: Optional[str] = None
    order: int
    required_documents: List[str] = []
    estimated_days: Optional[int] = None
    auto_advance: bool = False


class WorkflowTemplateBase(BaseModel):
    """Base workflow template schema"""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: str
    recurrence: str
    workflow_purpose: Optional[str] = None
    workflow_type: Optional[str] = None
    is_active: bool = True
    estimated_duration_days: Optional[int] = None


class WorkflowTemplateResponse(WorkflowTemplateBase):
    """Schema for workflow template response with phases"""

    id: int
    is_system_template: bool = False
    phases: List[WorkflowTemplatePhase] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowTemplateSummaryResponse(BaseModel):
    """Schema for template summary (after create/update)"""

    id: int
    name: str
    description: Optional[str] = None
    category: str
