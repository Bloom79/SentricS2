"""
Workflow Template Service - Business logic for workflow template management
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
import logging

from app.models.workflow_template import (
    WorkflowTemplate,
    WorkflowTemplatePhase,
    WorkflowTemplateCategoryEnum,
    WorkflowTemplateRecurrenceEnum,
)
from app.models.workflow import Workflow, WorkflowPhase, WorkflowTypeEnum, WorkflowStatusEnum

logger = logging.getLogger(__name__)


class WorkflowTemplateService:
    """Service for workflow template management"""

    @staticmethod
    def create_template(
        db: Session, template_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> WorkflowTemplate:
        """Create a new workflow template"""
        try:
            template = WorkflowTemplate(
                tenant_id=tenant_id,
                name=template_data["name"],
                description=template_data.get("description"),
                category=template_data.get("category", WorkflowTemplateCategoryEnum.COMPLIANCE),
                recurrence=template_data.get("recurrence", WorkflowTemplateRecurrenceEnum.ONE_TIME),
                workflow_purpose=template_data.get("workflow_purpose"),
                workflow_type=template_data.get("workflow_type"),
                estimated_duration_days=template_data.get("estimated_duration_days"),
                template_config=template_data.get("template_config", {}),
                is_active=template_data.get("is_active", True),
                is_system_template=template_data.get("is_system_template", False),
                created_by=user_id,
            )

            db.add(template)
            db.flush()  # Get template ID before adding phases

            # Add phases if provided
            if "phases" in template_data:
                for phase_data in template_data["phases"]:
                    phase = WorkflowTemplatePhase(
                        tenant_id=tenant_id,
                        template_id=template.id,
                        name=phase_data["name"],
                        description=phase_data.get("description"),
                        order=phase_data["order"],
                        required_documents=phase_data.get("required_documents", []),
                        estimated_days=phase_data.get("estimated_days"),
                        auto_advance=phase_data.get("auto_advance", False),
                        phase_config=phase_data.get("phase_config", {}),
                        created_by=user_id,
                    )
                    db.add(phase)

            db.commit()
            db.refresh(template)

            logger.info(f"Created workflow template {template.id}")
            return template

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating workflow template: {e}")
            raise

    @staticmethod
    def get_template(db: Session, template_id: int, tenant_id: str) -> Optional[WorkflowTemplate]:
        """Get workflow template by ID"""
        return (
            db.query(WorkflowTemplate)
            .filter(
                and_(
                    WorkflowTemplate.id == template_id,
                    WorkflowTemplate.tenant_id == tenant_id,
                    WorkflowTemplate.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def list_templates(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        active_only: bool = True,
    ) -> List[WorkflowTemplate]:
        """List workflow templates"""
        query = db.query(WorkflowTemplate).filter(
            and_(WorkflowTemplate.tenant_id == tenant_id, WorkflowTemplate.deleted_at.is_(None))
        )

        if active_only:
            query = query.filter(WorkflowTemplate.is_active.is_(True))
        if category:
            query = query.filter(WorkflowTemplate.category == category)

        return query.order_by(WorkflowTemplate.name).offset(skip).limit(limit).all()

    @staticmethod
    def update_template(
        db: Session, template_id: int, update_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> Optional[WorkflowTemplate]:
        """Update workflow template"""
        template = WorkflowTemplateService.get_template(db, template_id, tenant_id)
        if not template:
            return None

        # Prevent editing system templates
        if template.is_system_template and update_data.get("is_system_template") is False:
            raise ValueError("Cannot modify system templates")

        for key, value in update_data.items():
            if key == "phases":
                # Update phases separately
                continue
            if hasattr(template, key):
                setattr(template, key, value)

        # Update phases if provided
        if "phases" in update_data:
            # Delete existing phases
            db.query(WorkflowTemplatePhase).filter(
                and_(
                    WorkflowTemplatePhase.template_id == template_id,
                    WorkflowTemplatePhase.tenant_id == tenant_id,
                )
            ).delete()

            # Add new phases
            for phase_data in update_data["phases"]:
                phase = WorkflowTemplatePhase(
                    tenant_id=tenant_id,
                    template_id=template.id,
                    name=phase_data["name"],
                    description=phase_data.get("description"),
                    order=phase_data["order"],
                    required_documents=phase_data.get("required_documents", []),
                    estimated_days=phase_data.get("estimated_days"),
                    auto_advance=phase_data.get("auto_advance", False),
                    phase_config=phase_data.get("phase_config", {}),
                    created_by=user_id,
                )
                db.add(phase)

        template.updated_by = user_id
        template.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(template)
        return template

    @staticmethod
    def delete_template(db: Session, template_id: int, tenant_id: str, user_id: int) -> bool:
        """Delete workflow template (soft delete)"""
        template = WorkflowTemplateService.get_template(db, template_id, tenant_id)
        if not template:
            return False

        # Prevent deleting system templates
        if template.is_system_template:
            raise ValueError("Cannot delete system templates")

        template.deleted_at = datetime.utcnow()
        template.deleted_by = user_id

        db.commit()
        return True

    @staticmethod
    def create_workflow_from_template(
        db: Session, template_id: int, workflow_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> Workflow:
        """Create a workflow instance from a template"""
        template = WorkflowTemplateService.get_template(db, template_id, tenant_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        if not template.is_active:
            raise ValueError(f"Template {template_id} is not active")

        # Create workflow
        workflow = Workflow(
            tenant_id=tenant_id,
            name=workflow_data.get("name") or template.name,
            description=workflow_data.get("description") or template.description,
            type=(
                WorkflowTypeEnum[template.workflow_type]
                if template.workflow_type
                else WorkflowTypeEnum.COMPLIANCE
            ),
            status=WorkflowStatusEnum.DRAFT,
            plant_id=workflow_data.get("plant_id"),
            template_id=template_id,
            start_date=workflow_data.get("start_date"),
            due_date=workflow_data.get("due_date"),
            workflow_data=workflow_data.get("workflow_data", {}),
            notes=workflow_data.get("notes"),
            created_by=user_id,
        )

        db.add(workflow)
        db.flush()

        # Create phases from template phases
        template_phases = (
            db.query(WorkflowTemplatePhase)
            .filter(
                and_(
                    WorkflowTemplatePhase.template_id == template_id,
                    WorkflowTemplatePhase.tenant_id == tenant_id,
                    WorkflowTemplatePhase.deleted_at.is_(None),
                )
            )
            .order_by(WorkflowTemplatePhase.order)
            .all()
        )

        for template_phase in template_phases:
            phase = WorkflowPhase(
                tenant_id=tenant_id,
                workflow_id=workflow.id,
                name=template_phase.name,
                description=template_phase.description,
                order=template_phase.order,
                status="pending",
                phase_data={
                    "required_documents": template_phase.required_documents or [],
                    "estimated_days": template_phase.estimated_days,
                    "auto_advance": template_phase.auto_advance,
                    **template_phase.phase_config,
                },
                created_by=user_id,
            )
            db.add(phase)

        db.commit()
        db.refresh(workflow)

        logger.info(f"Created workflow {workflow.id} from template {template_id}")
        return workflow


# Export service instance
workflow_template_service = WorkflowTemplateService()
