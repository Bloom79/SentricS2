"""
CER Compliance endpoints - Compliance tracking and requirements
Split from monolithic cer.py for better maintainability
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.cer_service import cer_service

logger = logging.getLogger(__name__)
router = APIRouter()


def _serialize_requirement(req) -> dict:
    """Helper to serialize compliance requirement"""
    try:
        return {
            "id": req.id,
            "name": req.name,
            "description": req.description,
            "type": req.type.value if hasattr(req.type, "value") else str(req.type),
            "frequency_days": req.frequency_days,
            "authority": req.authority,
            "portal_name": req.portal_name,
            "requirement_data": req.requirement_data or {},
        }
    except Exception as e:
        logger.error(f"Error serializing requirement {req.id}: {e}")
        return {"id": req.id, "name": str(req.name) if req.name else "Unknown"}


def _serialize_record(rec) -> dict:
    """Helper to serialize compliance record"""
    try:
        return {
            "id": rec.id,
            "requirement_id": rec.requirement_id,
            "status": rec.status.value if hasattr(rec.status, "value") else str(rec.status),
            "due_date": rec.due_date.isoformat() if rec.due_date else None,
            "completed_date": (
                rec.completed_date.isoformat() if rec.completed_date else None
            ),
            "is_overdue": rec.is_overdue if hasattr(rec, "is_overdue") else False,
            "days_overdue": rec.days_overdue if hasattr(rec, "days_overdue") else 0,
            "notes": rec.notes,
        }
    except Exception as e:
        logger.error(f"Error serializing record {rec.id}: {e}")
        return {
            "id": rec.id,
            "requirement_id": rec.requirement_id,
            "status": str(rec.status),
        }


@router.get("/communities/{cer_id}/compliance", response_model=dict)
async def get_cer_compliance(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get compliance overview for a CER (requirements, records, status) including linked plants"""
    try:
        from app.services.compliance_service import compliance_service
        from app.models.plant import Plant

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        # Get CER-specific requirements and overdue records
        cer_requirements = compliance_service.list_requirements(
            db=db, tenant_id=current_user.tenant_id, cer_id=cer_id
        )
        cer_overdue = compliance_service.get_overdue_records(
            db=db, tenant_id=current_user.tenant_id, cer_id=cer_id
        )

        # Get all plants linked to this CER
        linked_plants = (
            db.query(Plant)
            .filter(
                and_(
                    Plant.cer_id == cer_id,
                    Plant.tenant_id == current_user.tenant_id,
                    Plant.deleted_at.is_(None),
                )
            )
            .all()
        )

        # Aggregate plant compliance
        plant_requirements = []
        plant_overdue = []
        plant_compliance_summary = []

        for plant in linked_plants:
            try:
                plant_reqs = compliance_service.list_requirements(
                    db=db, tenant_id=current_user.tenant_id, plant_id=plant.id
                )
                plant_requirements.extend(plant_reqs)

                plant_ovr = compliance_service.get_overdue_records(
                    db=db, tenant_id=current_user.tenant_id, plant_id=plant.id
                )
                plant_overdue.extend(plant_ovr)

                plant_compliance_summary.append(
                    {
                        "plant_id": plant.id,
                        "plant_name": plant.name,
                        "requirements_count": len(plant_reqs),
                        "overdue_count": len(plant_ovr),
                        "compliance_status": (
                            "compliant" if len(plant_ovr) == 0 else "non_compliant"
                        ),
                    }
                )
            except Exception as e:
                logger.error(f"Error processing plant {plant.id} compliance: {e}")
                continue

        all_overdue = cer_overdue + plant_overdue

        return {
            "cer_id": cer_id,
            "cer_name": cer.name,
            "cer_requirements": [_serialize_requirement(req) for req in cer_requirements],
            "cer_overdue": [_serialize_record(rec) for rec in cer_overdue],
            "cer_compliance_status": "compliant" if len(cer_overdue) == 0 else "non_compliant",
            "plant_requirements": [_serialize_requirement(req) for req in plant_requirements],
            "plant_overdue": [_serialize_record(rec) for rec in plant_overdue],
            "plant_compliance_summary": plant_compliance_summary,
            "total_requirements": len(cer_requirements) + len(plant_requirements),
            "total_overdue": len(all_overdue),
            "overdue_count": len(all_overdue),
            "compliance_status": "compliant" if len(all_overdue) == 0 else "non_compliant",
            "linked_plants_count": len(linked_plants),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting CER compliance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get compliance data: {str(e)}")


@router.get("/communities/{cer_id}/compliance/requirements", response_model=List[dict])
async def get_cer_compliance_requirements(
    cer_id: int,
    include_plants: bool = Query(True, description="Include requirements from linked plants"),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get compliance requirements for a CER, optionally including linked plants"""
    try:
        from app.services.compliance_service import compliance_service
        from app.models.plant import Plant

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        # Get CER requirements
        cer_requirements = compliance_service.list_requirements(
            db=db, tenant_id=current_user.tenant_id, cer_id=cer_id
        )

        requirements = []

        # Add CER requirements
        for req in cer_requirements:
            try:
                requirements.append(
                    {
                        "id": req.id,
                        "name": req.name,
                        "description": req.description,
                        "type": req.type.value if hasattr(req.type, "value") else str(req.type),
                        "frequency_days": req.frequency_days,
                        "authority": req.authority,
                        "portal_name": req.portal_name,
                        "entity_type": "cer",
                        "entity_id": cer_id,
                        "entity_name": cer.name,
                        "requirement_data": req.requirement_data or {},
                    }
                )
            except Exception as e:
                logger.error(f"Error serializing requirement {req.id}: {e}")
                continue

        # Include plant requirements if requested
        if include_plants:
            linked_plants = (
                db.query(Plant)
                .filter(
                    and_(
                        Plant.cer_id == cer_id,
                        Plant.tenant_id == current_user.tenant_id,
                        Plant.deleted_at.is_(None),
                    )
                )
                .all()
            )

            for plant in linked_plants:
                try:
                    plant_requirements = compliance_service.list_requirements(
                        db=db, tenant_id=current_user.tenant_id, plant_id=plant.id
                    )

                    for req in plant_requirements:
                        try:
                            requirements.append(
                                {
                                    "id": req.id,
                                    "name": req.name,
                                    "description": req.description,
                                    "type": (
                                        req.type.value
                                        if hasattr(req.type, "value")
                                        else str(req.type)
                                    ),
                                    "frequency_days": req.frequency_days,
                                    "authority": req.authority,
                                    "portal_name": req.portal_name,
                                    "entity_type": "plant",
                                    "entity_id": plant.id,
                                    "entity_name": plant.name,
                                    "requirement_data": req.requirement_data or {},
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error serializing plant requirement {req.id}: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error processing plant {plant.id} requirements: {e}")
                    continue

        return requirements
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting compliance requirements: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get requirements: {str(e)}")


@router.get("/communities/{cer_id}/compliance/records", response_model=List[dict])
async def get_cer_compliance_records(
    cer_id: int,
    status: Optional[str] = Query(None, description="Filter by status"),
    include_plants: bool = Query(True, description="Include compliance from linked plants"),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get compliance records for a CER, optionally including linked plants"""
    try:
        from app.models.compliance import ComplianceRecord, ComplianceStatusEnum
        from app.models.plant import Plant

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        # Get all records for this CER
        query = db.query(ComplianceRecord).filter(
            and_(
                ComplianceRecord.cer_id == cer_id,
                ComplianceRecord.tenant_id == current_user.tenant_id,
                ComplianceRecord.deleted_at.is_(None),
            )
        )

        if status:
            try:
                status_enum = ComplianceStatusEnum[status.upper()]
                query = query.filter(ComplianceRecord.status == status_enum)
            except (KeyError, AttributeError):
                query = query.filter(ComplianceRecord.status == status)

        cer_records = query.all()
        records = []

        # Add CER records
        for r in cer_records:
            try:
                records.append(
                    {
                        "id": r.id,
                        "requirement_id": r.requirement_id,
                        "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                        "due_date": r.due_date.isoformat() if r.due_date else None,
                        "completed_date": (
                            r.completed_date.isoformat() if r.completed_date else None
                        ),
                        "is_overdue": r.is_overdue if hasattr(r, "is_overdue") else False,
                        "days_overdue": r.days_overdue if hasattr(r, "days_overdue") else 0,
                        "entity_type": "cer",
                        "entity_id": cer_id,
                        "entity_name": cer.name,
                        "notes": r.notes,
                    }
                )
            except Exception as e:
                logger.error(f"Error serializing CER record {r.id}: {e}")
                continue

        # Include plant records if requested
        if include_plants:
            linked_plants = (
                db.query(Plant)
                .filter(
                    and_(
                        Plant.cer_id == cer_id,
                        Plant.tenant_id == current_user.tenant_id,
                        Plant.deleted_at.is_(None),
                    )
                )
                .all()
            )

            for plant in linked_plants:
                try:
                    plant_query = db.query(ComplianceRecord).filter(
                        and_(
                            ComplianceRecord.plant_id == plant.id,
                            ComplianceRecord.tenant_id == current_user.tenant_id,
                            ComplianceRecord.deleted_at.is_(None),
                        )
                    )

                    if status:
                        try:
                            status_enum = ComplianceStatusEnum[status.upper()]
                            plant_query = plant_query.filter(ComplianceRecord.status == status_enum)
                        except (KeyError, AttributeError):
                            plant_query = plant_query.filter(ComplianceRecord.status == status)

                    plant_records = plant_query.all()

                    for r in plant_records:
                        try:
                            records.append(
                                {
                                    "id": r.id,
                                    "requirement_id": r.requirement_id,
                                    "status": (
                                        r.status.value
                                        if hasattr(r.status, "value")
                                        else str(r.status)
                                    ),
                                    "due_date": r.due_date.isoformat() if r.due_date else None,
                                    "completed_date": (
                                        r.completed_date.isoformat() if r.completed_date else None
                                    ),
                                    "is_overdue": (
                                        r.is_overdue if hasattr(r, "is_overdue") else False
                                    ),
                                    "days_overdue": (
                                        r.days_overdue if hasattr(r, "days_overdue") else 0
                                    ),
                                    "entity_type": "plant",
                                    "entity_id": plant.id,
                                    "entity_name": plant.name,
                                    "notes": r.notes,
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error serializing plant record {r.id}: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error processing plant {plant.id} records: {e}")
                    continue

        return records
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting compliance records: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get records: {str(e)}")
