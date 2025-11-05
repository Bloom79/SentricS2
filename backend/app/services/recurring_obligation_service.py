"""
Recurring Obligation Service
Manages automatic creation and tracking of recurring compliance obligations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import logging

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Fallback to timedelta if dateutil not available
    def relativedelta(**kwargs):
        years = kwargs.get("years", 0)
        months = kwargs.get("months", 0)
        days = kwargs.get("days", 0)
        return timedelta(days=days + months * 30 + years * 365)


from app.models.recurring_obligation import RecurringObligation
from app.models.plant import Plant
from app.models.workflow import Workflow, WorkflowStatusEnum
from app.services.workflow_service import workflow_service

# CER import is optional - may not exist in all setups
try:
    from app.models.cer import CER
except ImportError:
    CER = None

logger = logging.getLogger(__name__)


class RecurringObligationService:
    """Service for managing recurring obligations"""

    # Italian compliance obligations configuration
    ITALIAN_OBLIGATIONS = [
        {
            "obligation_type": "fuel_mix_disclosure",
            "entity": "GSE",
            "recurrence_pattern": "annual",
            "base_deadline": {"day": 31, "month": 3},
            "auto_create_workflow": True,
            "notification_days": [90, 60, 30, 7],
            "applies_to": "all_plants",
        },
        {
            "obligation_type": "consumption_declaration",
            "entity": "ADM",
            "recurrence_pattern": "annual",
            "base_deadline": {"day": 31, "month": 3},
            "auto_create_workflow": True,
            "notification_days": [60, 30, 14, 7],
            "applies_to": "plants_above_20kw",
        },
        {
            "obligation_type": "license_fee_payment",
            "entity": "ADM",
            "recurrence_pattern": "annual",
            "base_deadline": {"day": 16, "month": 12},
            "auto_create_workflow": True,
            "notification_days": [60, 30, 14, 7],
            "applies_to": "plants_above_20kw",
        },
        {
            "obligation_type": "anti_mafia_declaration",
            "entity": "GSE",
            "recurrence_pattern": "annual",
            "base_deadline": {"day": 31, "month": 12},
            "auto_create_workflow": True,
            "notification_days": [90, 60, 30, 7],
            "applies_to": "plants_with_high_incentives",  # >€150k/year
            "conditional": lambda plant: plant.power_kw
            and plant.power_kw > 100,  # Simplified check
        },
        {
            "obligation_type": "meter_calibration",
            "entity": "DSO",
            "recurrence_pattern": "years",
            "base_deadline": {"years": 3},
            "auto_create_workflow": True,
            "notification_days": [90, 60, 30],
            "applies_to": "all_plants",
        },
        {
            "obligation_type": "protection_system_verification",
            "entity": "DSO",
            "recurrence_pattern": "years",
            "base_deadline": {"years": 5},
            "auto_create_workflow": True,
            "notification_days": [120, 90, 60],
            "applies_to": "all_plants",
        },
        {
            "obligation_type": "gaudi_annual_reconciliation",
            "entity": "Terna",
            "recurrence_pattern": "annual",
            "base_deadline": {"day": 31, "month": 3},  # Q1
            "auto_create_workflow": True,
            "notification_days": [60, 30, 14],
            "applies_to": "all_plants",
        },
        {
            "obligation_type": "property_tax_imu_tasi",
            "entity": "Comune",
            "recurrence_pattern": "annual",
            "base_deadline": {"day": 16, "month": 6},
            "auto_create_workflow": False,  # Usually handled separately
            "notification_days": [60, 30, 14],
            "applies_to": "all_plants",
        },
    ]

    @staticmethod
    def create_recurring_obligations_for_plant(
        db: Session, plant_id: int, tenant_id: str, base_date: Optional[datetime] = None
    ) -> List[RecurringObligation]:
        """Create recurring obligations for a plant based on connection date"""
        plant = (
            db.query(Plant)
            .filter(Plant.id == plant_id, Plant.tenant_id == tenant_id, Plant.deleted_at.is_(None))
            .first()
        )

        if not plant:
            raise ValueError(f"Plant {plant_id} not found")

        # Use connection date or current date
        if not base_date:
            base_date = plant.created_at or datetime.utcnow()

        created_obligations = []

        for obligation_config in RecurringObligationService.ITALIAN_OBLIGATIONS:
            # Check if obligation applies to this plant
            applies_to = obligation_config.get("applies_to", "all_plants")

            if applies_to == "plants_above_20kw" and (not plant.power_kw or plant.power_kw < 20):
                continue

            if applies_to == "plants_with_high_incentives":
                conditional = obligation_config.get("conditional")
                if conditional and not conditional(plant):
                    continue

            # Check if obligation already exists
            existing = (
                db.query(RecurringObligation)
                .filter(
                    RecurringObligation.tenant_id == tenant_id,
                    RecurringObligation.plant_id == plant_id,
                    RecurringObligation.obligation_type == obligation_config["obligation_type"],
                    RecurringObligation.deleted_at.is_(None),
                )
                .first()
            )

            if existing:
                logger.info(
                    f"Obligation {obligation_config['obligation_type']} already exists for plant {plant_id}"
                )
                continue

            # Calculate next due date
            next_due_date = RecurringObligationService._calculate_next_due_date(
                base_date,
                obligation_config["base_deadline"],
                obligation_config["recurrence_pattern"],
            )

            # Create obligation
            obligation = RecurringObligation(
                tenant_id=tenant_id,
                plant_id=plant_id,
                obligation_type=obligation_config["obligation_type"],
                entity=obligation_config["entity"],
                recurrence_pattern=obligation_config["recurrence_pattern"],
                base_deadline=obligation_config["base_deadline"],
                next_due_date=next_due_date,
                auto_create_workflow=obligation_config.get("auto_create_workflow", True),
                notification_days=obligation_config.get("notification_days", [90, 60, 30, 7]),
                is_active=True,
                obligation_data={
                    "applies_to": applies_to,
                    "description": RecurringObligationService._get_obligation_description(
                        obligation_config["obligation_type"]
                    ),
                },
            )

            db.add(obligation)
            created_obligations.append(obligation)
            logger.info(
                f"Created obligation {obligation_config['obligation_type']} for plant {plant_id}"
            )

        db.commit()
        return created_obligations

    @staticmethod
    def _calculate_next_due_date(
        base_date: datetime, base_deadline: Dict[str, Any], recurrence_pattern: str
    ) -> datetime:
        """Calculate next due date based on recurrence pattern"""
        now = datetime.utcnow()

        if recurrence_pattern == "annual":
            # Annual deadline like March 31
            year = now.year
            if "month" in base_deadline and "day" in base_deadline:
                deadline_this_year = datetime(year, base_deadline["month"], base_deadline["day"])
                if deadline_this_year < now:
                    deadline_this_year = datetime(
                        year + 1, base_deadline["month"], base_deadline["day"]
                    )
                return deadline_this_year

        elif recurrence_pattern == "years":
            # Every N years from base date
            years = base_deadline.get("years", 1)
            next_due = base_date + relativedelta(years=years)
            # If past, add another cycle
            while next_due < now:
                next_due = next_due + relativedelta(years=years)
            return next_due

        elif recurrence_pattern == "quarterly":
            # Every 3 months
            months = 3
            next_due = base_date + relativedelta(months=months)
            while next_due < now:
                next_due = next_due + relativedelta(months=months)
            return next_due

        elif recurrence_pattern == "monthly":
            # Every month
            next_due = base_date + relativedelta(months=1)
            while next_due < now:
                next_due = next_due + relativedelta(months=1)
            return next_due

        # Default: 1 year from base date
        return base_date + relativedelta(years=1)

    @staticmethod
    def _get_obligation_description(obligation_type: str) -> str:
        """Get human-readable description for obligation type"""
        descriptions = {
            "fuel_mix_disclosure": "Annual fuel mix disclosure to GSE",
            "consumption_declaration": "Annual consumption declaration to ADM",
            "license_fee_payment": "Annual license fee payment to ADM",
            "anti_mafia_declaration": "Annual anti-mafia declaration to GSE",
            "meter_calibration": "Meter calibration certificate renewal",
            "protection_system_verification": "Protection system verification",
            "gaudi_annual_reconciliation": "GAUDÌ annual data reconciliation",
            "property_tax_imu_tasi": "Property tax (IMU/TASI) declaration",
        }
        return descriptions.get(obligation_type, obligation_type.replace("_", " ").title())

    @staticmethod
    def check_upcoming_deadlines(
        db: Session,
        tenant_id: str,
        days_ahead: int = 30,
        plant_id: Optional[int] = None,
        entity: Optional[str] = None,
    ) -> List[RecurringObligation]:
        """Get obligations due within specified days"""
        now = datetime.utcnow()
        end_date = now + timedelta(days=days_ahead)

        query = db.query(RecurringObligation).filter(
            RecurringObligation.tenant_id == tenant_id,
            RecurringObligation.is_active == True,
            RecurringObligation.next_due_date.between(now, end_date),
            RecurringObligation.deleted_at.is_(None),
        )

        if plant_id:
            query = query.filter(RecurringObligation.plant_id == plant_id)
        if entity:
            query = query.filter(RecurringObligation.entity == entity)

        return query.order_by(RecurringObligation.next_due_date).all()

    @staticmethod
    def mark_completed(
        db: Session,
        obligation_id: int,
        tenant_id: str,
        completion_date: Optional[datetime] = None,
        user_id: Optional[int] = None,
    ) -> RecurringObligation:
        """Mark obligation as completed and calculate next due date"""
        obligation = (
            db.query(RecurringObligation)
            .filter(
                RecurringObligation.id == obligation_id,
                RecurringObligation.tenant_id == tenant_id,
                RecurringObligation.deleted_at.is_(None),
            )
            .first()
        )

        if not obligation:
            raise ValueError(f"Obligation {obligation_id} not found")

        # Update completion
        obligation.last_completed_date = completion_date or datetime.utcnow()

        # Calculate next due date
        base_date = obligation.last_completed_date
        obligation.next_due_date = RecurringObligationService._calculate_next_due_date(
            base_date, obligation.base_deadline, obligation.recurrence_pattern
        )

        obligation.updated_by = user_id
        obligation.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(obligation)

        logger.info(
            f"Marked obligation {obligation_id} as completed. Next due: {obligation.next_due_date}"
        )

        return obligation

    @staticmethod
    def auto_create_workflows(db: Session, tenant_id: str, days_ahead: int = 30) -> List[Workflow]:
        """Automatically create workflows for due obligations"""
        due_obligations = RecurringObligationService.check_upcoming_deadlines(
            db, tenant_id, days_ahead
        )

        created_workflows = []

        for obligation in due_obligations:
            if not obligation.auto_create_workflow:
                continue

            # Check if workflow already exists for this obligation
            existing_workflow = (
                db.query(Workflow)
                .filter(
                    Workflow.tenant_id == tenant_id,
                    Workflow.plant_id == obligation.plant_id,
                    Workflow.workflow_data["obligation_id"].astext == str(obligation.id),
                    Workflow.status != WorkflowStatusEnum.COMPLETED,
                    Workflow.deleted_at.is_(None),
                )
                .first()
            )

            if existing_workflow:
                continue

            # Create workflow from template or default
            workflow_name = f"{RecurringObligationService._get_obligation_description(obligation.obligation_type)} - {obligation.plant.name if obligation.plant else 'Plant'}"

            workflow_data = {
                "name": workflow_name,
                "description": f"Annual compliance obligation: {obligation.obligation_type}",
                "type": "Compliance",
                "plant_id": obligation.plant_id,
                "due_date": obligation.next_due_date.isoformat(),
                "workflow_data": {
                    "obligation_id": obligation.id,
                    "obligation_type": obligation.obligation_type,
                    "entity": obligation.entity,
                },
                "template_id": obligation.workflow_template_id,
            }

            try:
                workflow = workflow_service.create_workflow(
                    db=db,
                    workflow_data=workflow_data,
                    tenant_id=tenant_id,
                    user_id=1,  # System user
                )
                created_workflows.append(workflow)
                logger.info(f"Created workflow for obligation {obligation.id}")
            except Exception as e:
                logger.error(f"Error creating workflow for obligation {obligation.id}: {e}")

        return created_workflows


# Export service instance
recurring_obligation_service = RecurringObligationService()
