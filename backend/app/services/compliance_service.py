"""
Compliance Service - Business logic for compliance management
Consolidated from Kronos EAM
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import logging

from app.models.compliance import (
    ComplianceRequirement,
    ComplianceRecord,
    ComplianceTypeEnum,
    ComplianceStatusEnum,
)
from app.models.plant import Plant
from app.models.cer import CER

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for compliance management"""

    @staticmethod
    def create_requirement(
        db: Session, requirement_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> ComplianceRequirement:
        """Create a new compliance requirement"""
        try:
            # Verify plant if linked
            if requirement_data.get("plant_id"):
                plant = (
                    db.query(Plant)
                    .filter(
                        and_(
                            Plant.id == requirement_data["plant_id"],
                            Plant.tenant_id == tenant_id,
                            Plant.deleted_at.is_(None),
                        )
                    )
                    .first()
                )
                if not plant:
                    raise ValueError(f"Plant {requirement_data['plant_id']} not found")

            # Verify CER if linked
            if requirement_data.get("cer_id"):
                cer = (
                    db.query(CER)
                    .filter(
                        and_(
                            CER.id == requirement_data["cer_id"],
                            CER.tenant_id == tenant_id,
                            CER.deleted_at.is_(None),
                        )
                    )
                    .first()
                )
                if not cer:
                    raise ValueError(f"CER {requirement_data['cer_id']} not found")

            # Ensure only one entity is linked
            if requirement_data.get("plant_id") and requirement_data.get("cer_id"):
                raise ValueError("Cannot link requirement to both plant and CER")

            requirement = ComplianceRequirement(
                tenant_id=tenant_id,
                name=requirement_data["name"],
                description=requirement_data.get("description"),
                type=requirement_data.get("type", ComplianceTypeEnum.ANNUAL),
                frequency_days=requirement_data.get("frequency_days"),
                due_date_offset=requirement_data.get("due_date_offset", 0),
                authority=requirement_data.get("authority"),
                portal_name=requirement_data.get("portal_name"),
                plant_id=requirement_data.get("plant_id"),
                cer_id=requirement_data.get("cer_id"),
                requirement_data=requirement_data.get("requirement_data", {}),
                created_by=user_id,
            )

            db.add(requirement)
            db.commit()
            db.refresh(requirement)

            logger.info(f"Created compliance requirement {requirement.id}")
            return requirement

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating compliance requirement: {e}")
            raise

    @staticmethod
    def get_requirement(
        db: Session, requirement_id: int, tenant_id: str
    ) -> Optional[ComplianceRequirement]:
        """Get compliance requirement by ID"""
        return (
            db.query(ComplianceRequirement)
            .filter(
                and_(
                    ComplianceRequirement.id == requirement_id,
                    ComplianceRequirement.tenant_id == tenant_id,
                    ComplianceRequirement.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def list_requirements(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        plant_id: Optional[int] = None,
        cer_id: Optional[int] = None,
        type: Optional[str] = None,
    ) -> List[ComplianceRequirement]:
        """List compliance requirements"""
        query = db.query(ComplianceRequirement).filter(
            and_(
                ComplianceRequirement.tenant_id == tenant_id,
                ComplianceRequirement.deleted_at.is_(None),
            )
        )

        if plant_id:
            query = query.filter(ComplianceRequirement.plant_id == plant_id)
        if cer_id:
            query = query.filter(ComplianceRequirement.cer_id == cer_id)
        if type:
            query = query.filter(ComplianceRequirement.type == type)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_record(
        db: Session, requirement_id: int, due_date: datetime, tenant_id: str, user_id: int
    ) -> ComplianceRecord:
        """Create a compliance record"""
        requirement = ComplianceService.get_requirement(db, requirement_id, tenant_id)
        if not requirement:
            raise ValueError(f"Requirement {requirement_id} not found")

        # Inherit plant_id/cer_id from requirement
        record = ComplianceRecord(
            tenant_id=tenant_id,
            requirement_id=requirement_id,
            status=ComplianceStatusEnum.PENDING,
            due_date=due_date,
            plant_id=requirement.plant_id,
            cer_id=requirement.cer_id,
            created_by=user_id,
        )

        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def get_overdue_records(
        db: Session, tenant_id: str, plant_id: Optional[int] = None, cer_id: Optional[int] = None
    ) -> List[ComplianceRecord]:
        """Get overdue compliance records"""
        query = (
            db.query(ComplianceRecord)
            .join(ComplianceRequirement)
            .filter(
                and_(
                    ComplianceRecord.tenant_id == tenant_id,
                    ComplianceRecord.status != ComplianceStatusEnum.COMPLETED,
                    ComplianceRecord.due_date < datetime.utcnow(),
                    ComplianceRecord.deleted_at.is_(None),
                )
            )
        )

        if plant_id:
            query = query.filter(ComplianceRequirement.plant_id == plant_id)
        if cer_id:
            query = query.filter(ComplianceRequirement.cer_id == cer_id)

        return query.all()

    @staticmethod
    def list_records(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        plant_id: Optional[int] = None,
        cer_id: Optional[int] = None,
        status: Optional[str] = None,
        requirement_id: Optional[int] = None,
    ) -> List[ComplianceRecord]:
        """List compliance records"""
        query = db.query(ComplianceRecord).filter(
            and_(ComplianceRecord.tenant_id == tenant_id, ComplianceRecord.deleted_at.is_(None))
        )

        if plant_id:
            query = query.filter(ComplianceRecord.plant_id == plant_id)
        if cer_id:
            query = query.filter(ComplianceRecord.cer_id == cer_id)
        if status:
            # Handle status filtering - convert string to enum if needed
            try:
                from app.models.compliance import ComplianceStatusEnum

                # Map common status strings to enum values
                status_map = {
                    "pending": ComplianceStatusEnum.PENDING,
                    "in_progress": ComplianceStatusEnum.IN_PROGRESS,
                    "in progress": ComplianceStatusEnum.IN_PROGRESS,
                    "completed": ComplianceStatusEnum.COMPLETED,
                    "overdue": ComplianceStatusEnum.OVERDUE,
                    "cancelled": ComplianceStatusEnum.CANCELLED,
                }
                status_lower = status.lower()
                if status_lower in status_map:
                    query = query.filter(ComplianceRecord.status == status_map[status_lower])
                else:
                    # Try direct enum value match
                    for enum_status in ComplianceStatusEnum:
                        if enum_status.value.lower() == status_lower:
                            query = query.filter(ComplianceRecord.status == enum_status)
                            break
            except Exception as e:
                logger.warning(f"Error filtering by status '{status}': {e}")
                # Fallback: don't filter by status if there's an error
                pass
        if requirement_id:
            query = query.filter(ComplianceRecord.requirement_id == requirement_id)

        return query.order_by(ComplianceRecord.due_date).offset(skip).limit(limit).all()

    @staticmethod
    def complete_record(
        db: Session,
        record_id: int,
        tenant_id: str,
        user_id: int,
        submitted_date: Optional[datetime] = None,
    ) -> Optional[ComplianceRecord]:
        """Mark compliance record as completed"""
        record = (
            db.query(ComplianceRecord)
            .filter(
                and_(
                    ComplianceRecord.id == record_id,
                    ComplianceRecord.tenant_id == tenant_id,
                    ComplianceRecord.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not record:
            return None

        record.status = ComplianceStatusEnum.COMPLETED
        record.completed_date = datetime.utcnow()
        record.submitted_date = submitted_date or datetime.utcnow()
        record.updated_by = user_id

        db.commit()
        db.refresh(record)
        return record


# Export service instance
compliance_service = ComplianceService()
