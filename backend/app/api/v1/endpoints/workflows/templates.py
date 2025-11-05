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

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/templates", response_model=List[dict])
async def list_workflow_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List workflow templates"""
    try:
        templates = workflow_template_service.list_templates(
            db=db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            category=category,
            active_only=active_only,
        )

        result = []
        for template in templates:
            # Serialize template with phases
            template_dict = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": (
                    template.category.value
                    if hasattr(template.category, "value")
                    else str(template.category)
                ),
                "recurrence": (
                    template.recurrence.value
                    if hasattr(template.recurrence, "value")
                    else str(template.recurrence)
                ),
                "workflow_purpose": template.workflow_purpose,
                "workflow_type": template.workflow_type,
                "is_active": template.is_active,
                "is_system_template": template.is_system_template,
                "estimated_duration_days": template.estimated_duration_days,
                "phases": [
                    {
                        "id": phase.id,
                        "name": phase.name,
                        "description": phase.description,
                        "order": phase.order,
                        "required_documents": phase.required_documents or [],
                        "estimated_days": phase.estimated_days,
                        "auto_advance": phase.auto_advance,
                    }
                    for phase in sorted(template.phases, key=lambda p: p.order)
                ],
                "created_at": template.created_at.isoformat() if template.created_at else None,
            }
            result.append(template_dict)

        return result
    except Exception as e:
        logger.exception(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")


@router.get("/templates/{template_id}", response_model=dict)
async def get_workflow_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get workflow template by ID"""
    template = workflow_template_service.get_template(db, template_id, current_user.tenant_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "category": (
            template.category.value
            if hasattr(template.category, "value")
            else str(template.category)
        ),
        "recurrence": (
            template.recurrence.value
            if hasattr(template.recurrence, "value")
            else str(template.recurrence)
        ),
        "workflow_purpose": template.workflow_purpose,
        "workflow_type": template.workflow_type,
        "is_active": template.is_active,
        "is_system_template": template.is_system_template,
        "estimated_duration_days": template.estimated_duration_days,
        "phases": [
            {
                "id": phase.id,
                "name": phase.name,
                "description": phase.description,
                "order": phase.order,
                "required_documents": phase.required_documents or [],
                "estimated_days": phase.estimated_days,
                "auto_advance": phase.auto_advance,
            }
            for phase in sorted(template.phases, key=lambda p: p.order)
        ],
    }


@router.post("/templates", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_workflow_template(
    template_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create workflow template"""
    try:
        template = workflow_template_service.create_template(
            db=db,
            template_data=template_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": (
                template.category.value
                if hasattr(template.category, "value")
                else str(template.category)
            ),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create template: {str(e)}")


@router.put("/templates/{template_id}", response_model=dict)
async def update_workflow_template(
    template_id: int,
    update_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update workflow template"""
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
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
        }
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
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def create_workflow_from_template(
    template_id: int,
    workflow_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a workflow instance from a template"""
    try:
        workflow = workflow_template_service.create_workflow_from_template(
            db=db,
            template_id=template_id,
            workflow_data=workflow_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return {
            "id": workflow.id,
            "name": workflow.name,
            "template_id": workflow.template_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Error creating workflow from template: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")
