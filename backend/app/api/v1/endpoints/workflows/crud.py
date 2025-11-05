"""
Workflow CRUD endpoints
Split from monolithic workflows.py for better maintainability
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.workflow import Workflow
from app.services.workflow_service import workflow_service
from .helpers import serialize_workflow_safe

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plant_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List workflows with optional filtering

    REFACTORED: Complexity reduced from 11 to ~4 by extracting serialization helpers
    """
    try:
        # Get workflows from service
        workflows = workflow_service.list_workflows(
            db=db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            plant_id=plant_id,
            status=status,
            type=type,
        )

        # Serialize workflows (with safe fallback)
        return [serialize_workflow_safe(workflow) for workflow in workflows]

    except Exception as e:
        logger.error(f"Error listing workflows: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


@router.get("/{workflow_id}", response_model=dict)
async def get_workflow(
    workflow_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get workflow details"""
    try:
        logger.info(f"Getting workflow {workflow_id} for tenant {current_user.tenant_id}")
        workflow = workflow_service.get_workflow(db, workflow_id, current_user.tenant_id)
        if not workflow:
            # Check if workflow exists but belongs to different tenant
            workflow_exists = (
                db.query(Workflow)
                .filter(Workflow.id == workflow_id, Workflow.deleted_at.is_(None))
                .first()
            )
            if workflow_exists:
                logger.warning(
                    f"Workflow {workflow_id} exists but belongs to tenant {workflow_exists.tenant_id}, not {current_user.tenant_id}"
                )
                raise HTTPException(status_code=403, detail="Workflow not found or access denied")
            logger.warning(f"Workflow {workflow_id} not found")
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Serialize workflow to dictionary
        workflow_dict = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "type": workflow.type.value if hasattr(workflow.type, "value") else str(workflow.type),
            "status": (
                workflow.status.value if hasattr(workflow.status, "value") else str(workflow.status)
            ),
            "plant_id": workflow.plant_id,
            "template_id": workflow.template_id,
            "start_date": workflow.start_date.isoformat() if workflow.start_date else None,
            "due_date": workflow.due_date.isoformat() if workflow.due_date else None,
            "completed_date": (
                workflow.completed_date.isoformat() if workflow.completed_date else None
            ),
            "progress_percentage": workflow.progress_percentage or 0,
            "current_phase": workflow.current_phase,
            "notes": workflow.notes,
            "workflow_data": workflow.workflow_data or {},
            "created_at": (
                workflow.created_at.isoformat()
                if hasattr(workflow, "created_at") and workflow.created_at
                else None
            ),
            "updated_at": (
                workflow.updated_at.isoformat()
                if hasattr(workflow, "updated_at") and workflow.updated_at
                else None
            ),
        }

        # Add plant name if available
        try:
            if workflow.plant_id:
                if hasattr(workflow, "plant") and workflow.plant:
                    workflow_dict["plant_name"] = workflow.plant.name
                else:
                    workflow_dict["plant_name"] = f"Plant #{workflow.plant_id}"
        except Exception as e:
            logger.warning(f"Error loading plant for workflow {workflow.id}: {e}")
            if workflow.plant_id:
                workflow_dict["plant_name"] = f"Plant #{workflow.plant_id}"

        # Add phases if available with all enhanced fields
        if workflow.phases:
            try:
                workflow_dict["phases"] = [
                    {
                        "id": phase.id,
                        "name": phase.name or "",
                        "description": phase.description or None,
                        "order": phase.order or 0,
                        "status": str(phase.status) if phase.status else "pending",
                        "due_date": phase.due_date.isoformat() if phase.due_date else None,
                        "completed_date": (
                            phase.completed_date.isoformat() if phase.completed_date else None
                        ),
                        "estimated_days": phase.estimated_days,
                        "phase_data": phase.phase_data or {},
                        # Enhanced fields
                        "required_documents": phase.required_documents or [],
                        "official_form_fields": phase.official_form_fields or {},
                        "portal_url": phase.portal_url,
                        "portal_login_url": phase.portal_login_url,
                        "required_credentials": phase.required_credentials,
                        "submission_method": phase.submission_method,
                        "regulatory_deadline": (
                            phase.regulatory_deadline.isoformat()
                            if phase.regulatory_deadline
                            else None
                        ),
                        "deadline_type": phase.deadline_type,
                        "deadline_consequences": phase.deadline_consequences,
                        "external_protocol_number": phase.external_protocol_number,
                        "submission_date": (
                            phase.submission_date.isoformat() if phase.submission_date else None
                        ),
                        "response_date": (
                            phase.response_date.isoformat() if phase.response_date else None
                        ),
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
                        "created_at": (
                            phase.created_at.isoformat()
                            if hasattr(phase, "created_at") and phase.created_at
                            else None
                        ),
                    }
                    for phase in sorted(workflow.phases, key=lambda p: (p.order or 0))
                ]
            except Exception as e:
                logger.error(
                    f"Error serializing phases for workflow {workflow.id}: {e}", exc_info=True
                )
                workflow_dict["phases"] = []
        else:
            workflow_dict["phases"] = []

        return workflow_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get workflow: {str(e)}")


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create workflow"""
    try:
        workflow = workflow_service.create_workflow(
            db=db,
            workflow_data=workflow_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return workflow
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")


@router.put("/{workflow_id}", response_model=dict)
async def update_workflow(
    workflow_id: int,
    update_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update workflow"""
    workflow = workflow_service.update_workflow(
        db=db,
        workflow_id=workflow_id,
        update_data=update_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/{workflow_id}/complete", response_model=dict)
async def complete_workflow(
    workflow_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark workflow as completed"""
    workflow = workflow_service.complete_workflow(
        db=db,
        workflow_id=workflow_id,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
