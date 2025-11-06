"""
Workflow phase status and assignment updates
Split from monolithic workflow_phases.py for better maintainability
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.workflow import WorkflowPhase, WorkflowStatusEnum
from app.services.workflow_service import workflow_service
from app.schemas.workflow import PhaseStatusUpdateResponse, PhaseAssignmentResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.put("/{workflow_id}/phases/{phase_id}/status", response_model=PhaseStatusUpdateResponse)
async def update_phase_status(
    workflow_id: int,
    phase_id: int,
    status_update: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update workflow phase status

    Now uses proper Pydantic schema for type-safe response
    """
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

        # Return Pydantic schema response
        return PhaseStatusUpdateResponse(
            id=phase.id,
            status=phase.status,
            completed_date=phase.completed_date,
            workflow_progress=workflow.progress_percentage,
            workflow_status=(
                workflow.status.value if hasattr(workflow.status, "value") else str(workflow.status)
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating phase status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update phase status: {str(e)}")


@router.put("/{workflow_id}/phases/{phase_id}/assign", response_model=PhaseAssignmentResponse)
async def assign_phase(
    workflow_id: int,
    phase_id: int,
    assignment_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Assign workflow phase to a user

    Now uses proper Pydantic schema for type-safe response
    """
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

        # Return Pydantic schema response
        return PhaseAssignmentResponse(
            phase_id=phase_id,
            assigned_to=assignee_id,
            message="Phase assigned successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error assigning phase: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to assign phase: {str(e)}")
