"""
Workflow template management endpoints
Split from monolithic workflows.py for better maintainability
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.workflow_template_service import workflow_template_service
from app.schemas.workflow import (
    WorkflowTemplateResponse,
    WorkflowTemplateSummaryResponse,
    WorkflowResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/templates", response_model=List[WorkflowTemplateResponse])
async def list_workflow_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List workflow templates

    Now uses proper Pydantic schema - automatic serialization via from_orm
    """
    try:
        templates = workflow_template_service.list_templates(
            db=db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            category=category,
            active_only=active_only,
        )

        # Pydantic handles all serialization automatically
        return templates

    except Exception as e:
        logger.exception(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.get("/templates/{template_id}", response_model=WorkflowTemplateResponse)
async def get_workflow_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get workflow template by ID

    Now uses proper Pydantic schema - automatic serialization via from_orm
    """
    template = workflow_template_service.get_template(db, template_id, current_user.tenant_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Pydantic handles all serialization automatically
    return template


@router.post("/templates", response_model=WorkflowTemplateSummaryResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow_template(
    template_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create workflow template

    Now uses proper Pydantic schema for response
    """
    try:
        template = workflow_template_service.create_template(
            db=db,
            template_data=template_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        # Return summary response
        return WorkflowTemplateSummaryResponse.from_orm(template)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.put("/templates/{template_id}", response_model=WorkflowTemplateSummaryResponse)
async def update_workflow_template(
    template_id: int,
    update_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update workflow template

    Now uses proper Pydantic schema for response
    """
    try:
        template = workflow_template_service.update_template(
            db=db,
            template_id=template_id,
            update_data=update_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        # Return summary response
        return WorkflowTemplateSummaryResponse.from_orm(template)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error updating template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update template: {str(e)}")


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete workflow template"""
    try:
        success = workflow_template_service.delete_template(
            db=db,
            template_id=template_id,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not success:
            raise HTTPException(status_code=404, detail="Template not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error deleting template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete template: {str(e)}")


@router.post(
    "/templates/{template_id}/create-workflow",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workflow_from_template(
    template_id: int,
    workflow_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a workflow instance from a template

    Now uses proper Pydantic schema for type-safe response
    """
    try:
        workflow = workflow_template_service.create_workflow_from_template(
            db=db,
            template_id=template_id,
            workflow_data=workflow_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        # Return full workflow response using Pydantic schema
        return workflow
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating workflow from template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")
