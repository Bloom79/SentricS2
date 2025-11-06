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
from app.schemas.workflow import WorkflowPhaseDetailResponse, WorkflowSummary, DocumentSummary

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{workflow_id}/phases/{phase_id}", response_model=WorkflowPhaseDetailResponse)
async def get_phase_detail(
    workflow_id: int,
    phase_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed phase information with all related data

    Now uses proper Pydantic schema - automatic serialization via from_orm
    Eliminates 100+ lines of manual dict construction
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
                            DocumentSummary(
                                id=doc.id,
                                name=doc.name,
                                type=doc.document_type,
                                file_type=doc.file_type,
                                file_size=doc.file_size,
                                description=doc.description,
                                uploaded_at=doc.created_at,
                                uploaded_by=doc.created_by,
                            )
                        )

        # Build workflow summary
        workflow_summary = WorkflowSummary(
            id=workflow.id,
            name=workflow.name,
            plant_id=workflow.plant_id,
            plant_name=workflow.plant.name if workflow.plant else None,
        )

        # Pydantic handles all serialization automatically via from_orm
        # This replaces 100+ lines of manual dict construction!
        response = WorkflowPhaseDetailResponse.from_orm(phase)
        response.documents = documents
        response.workflow = workflow_summary

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting phase detail: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get phase detail: {str(e)}")
