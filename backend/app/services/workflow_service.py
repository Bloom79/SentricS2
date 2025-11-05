"""
Workflow Service - Business logic for workflow management
Consolidated from Kronos EAM
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from datetime import datetime
import logging

from app.models.workflow import Workflow, WorkflowPhase, WorkflowStatusEnum, WorkflowTypeEnum
from app.models.plant import Plant

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for workflow management"""

    @staticmethod
    def create_workflow(
        db: Session, workflow_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> Workflow:
        """Create a new workflow"""
        try:
            # Verify plant if linked
            if workflow_data.get("plant_id"):
                plant = (
                    db.query(Plant)
                    .filter(
                        and_(
                            Plant.id == workflow_data["plant_id"],
                            Plant.tenant_id == tenant_id,
                            Plant.deleted_at.is_(None),
                        )
                    )
                    .first()
                )
                if not plant:
                    raise ValueError(f"Plant {workflow_data['plant_id']} not found")

            workflow = Workflow(
                tenant_id=tenant_id,
                name=workflow_data["name"],
                description=workflow_data.get("description"),
                type=workflow_data.get("type", WorkflowTypeEnum.COMPLIANCE),
                status=WorkflowStatusEnum.DRAFT,
                plant_id=workflow_data.get("plant_id"),
                template_id=workflow_data.get("template_id"),
                start_date=workflow_data.get("start_date"),
                due_date=workflow_data.get("due_date"),
                workflow_data=workflow_data.get("workflow_data", {}),
                notes=workflow_data.get("notes"),
                created_by=user_id,
            )

            db.add(workflow)
            db.commit()
            db.refresh(workflow)

            logger.info(f"Created workflow {workflow.id}")
            return workflow

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating workflow: {e}")
            raise

    @staticmethod
    def get_workflow(db: Session, workflow_id: int, tenant_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return (
            db.query(Workflow)
            .options(joinedload(Workflow.plant), joinedload(Workflow.phases))
            .filter(
                and_(
                    Workflow.id == workflow_id,
                    Workflow.tenant_id == tenant_id,
                    Workflow.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def list_workflows(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        plant_id: Optional[int] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
    ) -> List[Workflow]:
        """List workflows"""
        query = (
            db.query(Workflow)
            .options(joinedload(Workflow.plant))
            .filter(and_(Workflow.tenant_id == tenant_id, Workflow.deleted_at.is_(None)))
        )

        if plant_id:
            query = query.filter(Workflow.plant_id == plant_id)

        if status:
            # Handle status filtering - convert string to enum if needed
            try:
                status_map = {
                    "draft": WorkflowStatusEnum.DRAFT,
                    "in_progress": WorkflowStatusEnum.IN_PROGRESS,
                    "in progress": WorkflowStatusEnum.IN_PROGRESS,
                    "completed": WorkflowStatusEnum.COMPLETED,
                    "cancelled": WorkflowStatusEnum.CANCELLED,
                    "on_hold": WorkflowStatusEnum.ON_HOLD,
                    "on hold": WorkflowStatusEnum.ON_HOLD,
                }
                status_lower = status.lower()
                if status_lower in status_map:
                    query = query.filter(Workflow.status == status_map[status_lower])
                else:
                    # Try direct enum value match
                    for enum_status in WorkflowStatusEnum:
                        if enum_status.value.lower() == status_lower:
                            query = query.filter(Workflow.status == enum_status)
                            break
            except Exception as e:
                logger.warning(f"Error filtering by status '{status}': {e}")
                # Fallback: don't filter by status if there's an error
                pass

        if type:
            # Handle type filtering - convert string to enum if needed
            try:
                type_map = {
                    "activation": WorkflowTypeEnum.ACTIVATION,
                    "compliance": WorkflowTypeEnum.COMPLIANCE,
                    "fiscal": WorkflowTypeEnum.FISCAL,
                    "maintenance": WorkflowTypeEnum.MAINTENANCE,
                    "document_submission": WorkflowTypeEnum.DOCUMENT_SUBMISSION,
                    "document submission": WorkflowTypeEnum.DOCUMENT_SUBMISSION,
                }
                type_lower = type.lower()
                if type_lower in type_map:
                    query = query.filter(Workflow.type == type_map[type_lower])
                else:
                    # Try direct enum value match
                    for enum_type in WorkflowTypeEnum:
                        if enum_type.value.lower() == type_lower:
                            query = query.filter(Workflow.type == enum_type)
                            break
            except Exception as e:
                logger.warning(f"Error filtering by type '{type}': {e}")
                # Fallback: don't filter by type if there's an error
                pass

        return query.order_by(Workflow.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_workflow(
        db: Session, workflow_id: int, update_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> Optional[Workflow]:
        """Update workflow"""
        workflow = WorkflowService.get_workflow(db, workflow_id, tenant_id)
        if not workflow:
            return None

        for key, value in update_data.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)

        workflow.updated_by = user_id
        workflow.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(workflow)
        return workflow

    @staticmethod
    def complete_workflow(
        db: Session, workflow_id: int, tenant_id: str, user_id: int
    ) -> Optional[Workflow]:
        """Mark workflow as completed"""
        workflow = WorkflowService.get_workflow(db, workflow_id, tenant_id)
        if not workflow:
            return None

        workflow.status = WorkflowStatusEnum.COMPLETED
        workflow.completed_date = datetime.utcnow()
        workflow.progress_percentage = 100
        workflow.updated_by = user_id

        db.commit()
        db.refresh(workflow)
        return workflow


# Export service instance
workflow_service = WorkflowService()
