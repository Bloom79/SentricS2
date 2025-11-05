"""
Workflow serialization helpers
Split from monolithic workflows.py for better maintainability
"""

from typing import Dict, Any
import logging

from app.models.workflow import Workflow

logger = logging.getLogger(__name__)


def serialize_workflow(workflow: Workflow) -> Dict[str, Any]:
    """
    Serialize workflow model to dictionary

    Returns:
        Dictionary with workflow data
    """
    workflow_dict = {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "type": (
            workflow.type.value
            if hasattr(workflow.type, "value")
            else str(workflow.type)
        ),
        "status": (
            workflow.status.value
            if hasattr(workflow.status, "value")
            else str(workflow.status)
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

    return workflow_dict


def serialize_workflow_safe(workflow: Workflow) -> Dict[str, Any]:
    """
    Safely serialize workflow with fallback to basic info

    Returns:
        Dictionary with workflow data (full or minimal)
    """
    try:
        return serialize_workflow(workflow)
    except Exception as e:
        logger.warning(f"Error serializing workflow {workflow.id}: {e}", exc_info=True)
        # Return basic info if full serialization fails
        return {
            "id": workflow.id,
            "name": workflow.name,
            "status": str(workflow.status),
            "type": str(workflow.type),
            "plant_id": workflow.plant_id,
        }
