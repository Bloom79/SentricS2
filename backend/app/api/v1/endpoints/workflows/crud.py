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
from app.schemas.workflow import (
    WorkflowResponse,
    WorkflowDetailResponse,
    WorkflowCreate,
    WorkflowUpdate,
)
from .helpers import serialize_workflow_safe

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[WorkflowResponse])
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
    Now uses proper Pydantic schema for type safety
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

        # Pydantic automatically handles serialization
        return workflows

    except Exception as e:
        logger.error(f"Error listing workflows: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


@router.get("/{workflow_id}", response_model=WorkflowDetailResponse)
async def get_workflow(
    workflow_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed workflow information including phases

    Uses Pydantic schema for automatic serialization - eliminating 100+ lines of manual dict construction
    """
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

        # Add plant name if available
        plant_name = None
        try:
            if workflow.plant_id and hasattr(workflow, "plant") and workflow.plant:
                plant_name = workflow.plant.name
        except Exception as e:
            logger.warning(f"Error loading plant for workflow {workflow.id}: {e}")

        # Pydantic handles all serialization automatically via from_orm
        # This replaces 100+ lines of manual dict construction!
        response = WorkflowDetailResponse.from_orm(workflow)
        response.plant_name = plant_name
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get workflow: {str(e)}")


@router.post("/", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new workflow

    Now uses proper Pydantic schemas for request validation and response
    """
    try:
        workflow = workflow_service.create_workflow(
            db=db,
            workflow_data=workflow_data.dict(),
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return workflow
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: int,
    update_data: WorkflowUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update workflow

    Now uses proper Pydantic schemas for request validation and response
    """
    workflow = workflow_service.update_workflow(
        db=db,
        workflow_id=workflow_id,
        update_data=update_data.dict(exclude_unset=True),
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/{workflow_id}/complete", response_model=WorkflowResponse)
async def complete_workflow(
    workflow_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Mark workflow as completed

    Now uses proper Pydantic schema for type-safe response
    """
    workflow = workflow_service.complete_workflow(
        db=db,
        workflow_id=workflow_id,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow
