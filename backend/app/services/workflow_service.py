"""
Workflow Service - Business logic for workflow management
Consolidated from Kronos EAM
REFACTORED: Reduced complexity by extracting helper methods
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload, Query
from sqlalchemy import and_
from datetime import datetime
import logging

from app.models.workflow import Workflow, WorkflowStatusEnum, WorkflowTypeEnum
from app.models.plant import Plant
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class WorkflowService(BaseService):
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
    def _parse_status_enum(status: str) -> Optional[WorkflowStatusEnum]:
        """
        Parse status string to enum value

        Returns:
            WorkflowStatusEnum if valid, None if invalid
        """
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

        # Try mapped values first
        if status_lower in status_map:
            return status_map[status_lower]

        # Try direct enum value match
        for enum_status in WorkflowStatusEnum:
            if enum_status.value.lower() == status_lower:
                return enum_status

        return None

    @staticmethod
    def _parse_type_enum(type_str: str) -> Optional[WorkflowTypeEnum]:
        """
        Parse type string to enum value

        Returns:
            WorkflowTypeEnum if valid, None if invalid
        """
        type_map = {
            "activation": WorkflowTypeEnum.ACTIVATION,
            "compliance": WorkflowTypeEnum.COMPLIANCE,
            "fiscal": WorkflowTypeEnum.FISCAL,
            "maintenance": WorkflowTypeEnum.MAINTENANCE,
            "document_submission": WorkflowTypeEnum.DOCUMENT_SUBMISSION,
            "document submission": WorkflowTypeEnum.DOCUMENT_SUBMISSION,
        }

        type_lower = type_str.lower()

        # Try mapped values first
        if type_lower in type_map:
            return type_map[type_lower]

        # Try direct enum value match
        for enum_type in WorkflowTypeEnum:
            if enum_type.value.lower() == type_lower:
                return enum_type

        return None

    @staticmethod
    def _filter_by_status(query: Query, status: Optional[str]) -> Query:
        """
        Apply status filter to query

        Returns:
            Filtered query (or original if status is None or invalid)
        """
        if not status:
            return query

        try:
            status_enum = WorkflowService._parse_status_enum(status)
            if status_enum:
                return query.filter(Workflow.status == status_enum)
        except Exception as e:
            logger.warning(f"Error filtering by status '{status}': {e}")

        return query

    @staticmethod
    def _filter_by_type(query: Query, type_str: Optional[str]) -> Query:
        """
        Apply type filter to query

        Returns:
            Filtered query (or original if type is None or invalid)
        """
        if not type_str:
            return query

        try:
            type_enum = WorkflowService._parse_type_enum(type_str)
            if type_enum:
                return query.filter(Workflow.type == type_enum)
        except Exception as e:
            logger.warning(f"Error filtering by type '{type_str}': {e}")

        return query

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
        """
        List workflows with optional filtering

        REFACTORED: Complexity reduced from 14 to ~5 by extracting helpers
        """
        # Build base query
        query = (
            db.query(Workflow)
            .options(joinedload(Workflow.plant))
            .filter(and_(Workflow.tenant_id == tenant_id, Workflow.deleted_at.is_(None)))
        )

        # Apply filters
        if plant_id:
            query = query.filter(Workflow.plant_id == plant_id)

        query = WorkflowService._filter_by_status(query, status)
        query = WorkflowService._filter_by_type(query, type)

        # Return results
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
