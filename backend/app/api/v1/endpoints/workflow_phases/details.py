"""
Workflow phase details endpoint
Split from monolithic workflow_phases.py for better maintainability
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.workflow import WorkflowPhase
from app.models.document import Document
from app.services.workflow_service import workflow_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{workflow_id}/phases/{phase_id}", response_model=dict)
async def get_phase_detail(
    workflow_id: int,
    phase_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get detailed phase information with all related data"""
    try:
        # Get workflow and verify ownership
        workflow = workflow_service.get_workflow(db, workflow_id, current_user.tenant_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Get phase
        phase = (
            db.query(WorkflowPhase)
            .filter(
                WorkflowPhase.id == phase_id,
                WorkflowPhase.workflow_id == workflow_id,
                WorkflowPhase.tenant_id == current_user.tenant_id,
                WorkflowPhase.deleted_at.is_(None),
            )
            .first()
        )

        if not phase:
            raise HTTPException(status_code=404, detail="Phase not found")

        # Load documents linked to this phase
        documents = []
        if phase.phase_data and "documents" in phase.phase_data:
            for doc_ref in phase.phase_data["documents"]:
                doc_id = doc_ref.get("document_id")
                if doc_id:
                    doc = (
                        db.query(Document)
                        .filter(
                            Document.id == doc_id,
                            Document.tenant_id == current_user.tenant_id,
                            Document.deleted_at.is_(None),
                        )
                        .first()
                    )
                    if doc:
                        documents.append(
                            {
                                "id": doc.id,
                                "name": doc.name,
                                "type": doc.document_type,
                                "file_type": doc.file_type,
                                "file_size": doc.file_size,
                                "description": doc.description,
                                "uploaded_at": (
                                    doc.created_at.isoformat() if doc.created_at else None
                                ),
                                "uploaded_by": doc.created_by,
                            }
                        )

        # Build phase response with all enhanced fields
        phase_dict = {
            "id": phase.id,
            "name": phase.name,
            "description": phase.description,
            "order": phase.order,
            "status": phase.status,
            "due_date": phase.due_date.isoformat() if phase.due_date else None,
            "completed_date": phase.completed_date.isoformat() if phase.completed_date else None,
            "estimated_days": phase.estimated_days,
            "phase_data": phase.phase_data or {},
            "documents": documents,
            # Enhanced fields
            "required_documents": phase.required_documents or [],
            "official_form_fields": phase.official_form_fields or {},
            "portal_url": phase.portal_url,
            "portal_login_url": phase.portal_login_url,
            "required_credentials": phase.required_credentials,
            "submission_method": phase.submission_method,
            "regulatory_deadline": (
                phase.regulatory_deadline.isoformat() if phase.regulatory_deadline else None
            ),
            "deadline_type": phase.deadline_type,
            "deadline_consequences": phase.deadline_consequences,
            "external_protocol_number": phase.external_protocol_number,
            "submission_date": phase.submission_date.isoformat() if phase.submission_date else None,
            "response_date": phase.response_date.isoformat() if phase.response_date else None,
            "cost_amount": phase.cost_amount,
            "cost_description": phase.cost_description,
            "payment_method": phase.payment_method,
            "payment_reference": phase.payment_reference,
            "requires_human_auth": phase.requires_human_auth or False,
            "requires_physical_signature": phase.requires_physical_signature or False,
            "requires_site_inspection": phase.requires_site_inspection or False,
            "human_checkpoint_notes": phase.human_checkpoint_notes,
            "checklist_items": phase.checklist_items or [],
            "instructions": phase.instructions,
            "external_resources": phase.external_resources or [],
            "responsible_entity": phase.responsible_entity,
            "practice_type": phase.practice_type,
            "document_templates": phase.document_templates or [],
            "workflow": {
                "id": workflow.id,
                "name": workflow.name,
                "plant_id": workflow.plant_id,
                "plant_name": workflow.plant.name if workflow.plant else None,
            },
            "created_at": (
                phase.created_at.isoformat()
                if hasattr(phase, "created_at") and phase.created_at
                else None
            ),
            "updated_at": (
                phase.updated_at.isoformat()
                if hasattr(phase, "updated_at") and phase.updated_at
                else None
            ),
        }

        return phase_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting phase detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get phase detail: {str(e)}")
