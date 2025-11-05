"""
Workflow Phase Management Endpoints
Handles phase status updates, document uploads, and phase assignments
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.workflow import Workflow, WorkflowPhase, WorkflowStatusEnum
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


@router.put("/{workflow_id}/phases/{phase_id}/status", response_model=dict)
async def update_phase_status(
    workflow_id: int,
    phase_id: int,
    status_update: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update workflow phase status"""
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

        # Update status
        new_status = status_update.get("status", phase.status)
        phase.status = new_status

        # Update completion date if completed
        if new_status.lower() in ["completed", "complete"]:
            if not phase.completed_date:
                phase.completed_date = datetime.utcnow()
            phase.updated_by = int(current_user.sub)
        elif new_status.lower() in ["in_progress", "in progress"]:
            phase.completed_date = None

        # Update notes if provided
        if "notes" in status_update:
            if not phase.phase_data:
                phase.phase_data = {}
            phase.phase_data["notes"] = status_update["notes"]

        # Update form_data if provided
        if "form_data" in status_update:
            if not phase.phase_data:
                phase.phase_data = {}
            phase.phase_data["form_data"] = status_update["form_data"]

        db.commit()
        db.refresh(phase)

        # Recalculate workflow progress
        total_phases = len(workflow.phases)
        completed_phases = len(
            [p for p in workflow.phases if p.status and p.status.lower() == "completed"]
        )
        workflow.progress_percentage = int(
            (completed_phases / total_phases * 100) if total_phases > 0 else 0
        )

        # Update workflow status if all phases completed
        if workflow.progress_percentage == 100 and workflow.status != WorkflowStatusEnum.COMPLETED:
            workflow.status = WorkflowStatusEnum.COMPLETED
            workflow.completed_date = datetime.utcnow()
        elif workflow.progress_percentage > 0 and workflow.status == WorkflowStatusEnum.DRAFT:
            workflow.status = WorkflowStatusEnum.IN_PROGRESS
            if not workflow.start_date:
                workflow.start_date = datetime.utcnow()

        # Update current phase
        in_progress_phases = [
            p for p in workflow.phases if p.status and "in_progress" in p.status.lower()
        ]
        if in_progress_phases:
            workflow.current_phase = in_progress_phases[0].name

        workflow.updated_by = int(current_user.sub)
        workflow.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(workflow)

        return {
            "id": phase.id,
            "status": phase.status,
            "completed_date": phase.completed_date.isoformat() if phase.completed_date else None,
            "workflow_progress": workflow.progress_percentage,
            "workflow_status": (
                workflow.status.value if hasattr(workflow.status, "value") else str(workflow.status)
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating phase status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update phase status: {str(e)}")


@router.post("/{workflow_id}/phases/{phase_id}/documents", response_model=dict)
async def upload_phase_document(
    workflow_id: int,
    phase_id: int,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload document to workflow phase"""
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

        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Create document record
        document = Document(
            tenant_id=current_user.tenant_id,
            name=file.filename or f"document_{datetime.utcnow().isoformat()}",
            file_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            document_type=document_type,
            description=description,
            plant_id=workflow.plant_id,
            compliance_record_id=None,  # Could link to compliance record if exists
            created_by=int(current_user.sub),
            document_data={
                "workflow_id": workflow_id,
                "phase_id": phase_id,
                "uploaded_for": "workflow_phase",
            },
        )

        # TODO: Store file in storage (S3, local, etc.)
        # For now, just create the record
        # In production, implement file storage service

        db.add(document)
        db.commit()
        db.refresh(document)

        # Add document reference to phase
        if not phase.phase_data:
            phase.phase_data = {}
        if "documents" not in phase.phase_data:
            phase.phase_data["documents"] = []
        phase.phase_data["documents"].append(
            {
                "document_id": document.id,
                "name": document.name,
                "type": document_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "uploaded_by": current_user.sub,
            }
        )

        db.commit()

        return {
            "document_id": document.id,
            "name": document.name,
            "type": document_type,
            "phase_id": phase_id,
            "message": "Document uploaded successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading phase document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.post("/{workflow_id}/phases/{phase_id}/comments", response_model=dict)
async def add_phase_comment(
    workflow_id: int,
    phase_id: int,
    comment_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add comment/note to workflow phase"""
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

        # Add comment to phase_data
        if not phase.phase_data:
            phase.phase_data = {}
        if "comments" not in phase.phase_data:
            phase.phase_data["comments"] = []

        comment = {
            "id": len(phase.phase_data["comments"]) + 1,
            "text": comment_data.get("text", ""),
            "author": current_user.sub,
            "author_name": getattr(current_user, "name", "Unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "type": comment_data.get("type", "comment"),  # comment, note, warning
        }

        phase.phase_data["comments"].append(comment)
        phase.updated_by = int(current_user.sub)
        phase.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(phase)

        return {
            "comment": comment,
            "phase_id": phase_id,
            "message": "Comment added successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding phase comment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to add comment: {str(e)}")


@router.put("/{workflow_id}/phases/{phase_id}/assign", response_model=dict)
async def assign_phase(
    workflow_id: int,
    phase_id: int,
    assignment_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Assign workflow phase to a user"""
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

        # Update assignment
        assignee_id = assignment_data.get("assignee_id")
        if not phase.phase_data:
            phase.phase_data = {}

        phase.phase_data["assigned_to"] = assignee_id
        phase.phase_data["assigned_at"] = datetime.utcnow().isoformat()
        phase.phase_data["assigned_by"] = current_user.sub

        # Add comment about assignment
        if "comments" not in phase.phase_data:
            phase.phase_data["comments"] = []
        phase.phase_data["comments"].append(
            {
                "id": len(phase.phase_data["comments"]) + 1,
                "text": f"Phase assigned to user {assignee_id}",
                "author": current_user.sub,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "assignment",
            }
        )

        phase.updated_by = int(current_user.sub)
        phase.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(phase)

        return {
            "phase_id": phase_id,
            "assigned_to": assignee_id,
            "message": "Phase assigned successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error assigning phase: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to assign phase: {str(e)}")
