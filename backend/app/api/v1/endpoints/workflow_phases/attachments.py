"""
Workflow phase documents and comments
Split from monolithic workflow_phases.py for better maintainability
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.workflow import WorkflowPhase
from app.models.document import Document
from app.services.workflow_service import workflow_service

logger = logging.getLogger(__name__)
router = APIRouter()


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
