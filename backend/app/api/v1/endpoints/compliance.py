"""
Compliance endpoints
Consolidated from Kronos EAM
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.compliance_service import compliance_service
from app.models.plant import Plant
from app.models.cer import CER
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/requirements", response_model=List[dict])
async def list_requirements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plant_id: Optional[int] = Query(None),
    cer_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List compliance requirements"""
    requirements = compliance_service.list_requirements(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        plant_id=plant_id,
        cer_id=cer_id,
        type=type,
    )
    return requirements


@router.get("/requirements/{requirement_id}", response_model=dict)
async def get_requirement(
    requirement_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get compliance requirement"""
    requirement = compliance_service.get_requirement(db, requirement_id, current_user.tenant_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement


@router.post("/requirements", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    requirement_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create compliance requirement"""
    try:
        requirement = compliance_service.create_requirement(
            db=db,
            requirement_data=requirement_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return requirement
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create requirement: {str(e)}")


@router.get("/overdue", response_model=List[dict])
async def get_overdue_records(
    plant_id: Optional[int] = Query(None),
    cer_id: Optional[int] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get overdue compliance records"""
    records = compliance_service.get_overdue_records(
        db=db, tenant_id=current_user.tenant_id, plant_id=plant_id, cer_id=cer_id
    )
    return records


@router.get("/records", response_model=List[dict])
async def list_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plant_id: Optional[int] = Query(None),
    cer_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    requirement_id: Optional[int] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List compliance records"""
    try:
        # Validate status parameter if provided
        if status:
            from app.models.compliance import ComplianceStatusEnum

            valid_statuses = [e.value.lower() for e in ComplianceStatusEnum] + [
                "pending",
                "in_progress",
                "completed",
                "overdue",
                "cancelled",
            ]
            if status.lower() not in valid_statuses:
                logger.warning(f"Invalid status parameter: {status}")

        records = compliance_service.list_records(
            db=db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            plant_id=plant_id,
            cer_id=cer_id,
            status=status,
            requirement_id=requirement_id,
        )

        # Serialize records with requirement and entity information
        result = []
        for record in records:
            try:
                record_dict = {
                    "id": record.id,
                    "requirement_id": record.requirement_id,
                    "status": (
                        record.status.value
                        if hasattr(record.status, "value")
                        else str(record.status)
                    ),
                    "due_date": record.due_date.isoformat() if record.due_date else None,
                    "completed_date": (
                        record.completed_date.isoformat() if record.completed_date else None
                    ),
                    "submitted_date": (
                        record.submitted_date.isoformat() if record.submitted_date else None
                    ),
                    "penalty_amount": record.penalty_amount or 0.0,
                    "penalty_applied": record.penalty_applied or False,
                    "notes": record.notes,
                    "plant_id": record.plant_id,
                    "cer_id": record.cer_id,
                }

                # Add requirement information if available - use eager loading or explicit query
                try:
                    from app.models.compliance import ComplianceRequirement

                    if record.requirement_id:
                        requirement = (
                            db.query(ComplianceRequirement)
                            .filter(
                                ComplianceRequirement.id == record.requirement_id,
                                ComplianceRequirement.tenant_id == current_user.tenant_id,
                            )
                            .first()
                        )

                        if requirement:
                            record_dict["requirement_name"] = requirement.name
                            record_dict["requirement"] = {
                                "id": requirement.id,
                                "name": requirement.name,
                                "authority": requirement.authority or None,
                                "portal_name": requirement.portal_name or None,
                            }
                            record_dict["required_documents"] = (
                                requirement.requirement_data or {}
                            ).get("required_documents", [])
                        else:
                            record_dict["requirement_name"] = None
                            record_dict["required_documents"] = []
                    else:
                        record_dict["requirement_name"] = None
                        record_dict["required_documents"] = []
                except Exception as e:
                    logger.warning(
                        f"Error loading requirement for record {record.id}: {e}", exc_info=True
                    )
                    record_dict["requirement_name"] = None
                    record_dict["required_documents"] = []

                # Add entity information
                if record.plant_id:
                    try:
                        plant = (
                            db.query(Plant)
                            .filter(
                                Plant.id == record.plant_id,
                                Plant.tenant_id == current_user.tenant_id,
                            )
                            .first()
                        )
                        if plant:
                            record_dict["plant_name"] = plant.name
                            record_dict["entity_type"] = "plant"
                            record_dict["entity_id"] = record.plant_id
                            record_dict["entity_name"] = plant.name
                        else:
                            record_dict["plant_name"] = f"Plant #{record.plant_id}"
                            record_dict["entity_type"] = "plant"
                            record_dict["entity_id"] = record.plant_id
                            record_dict["entity_name"] = f"Plant #{record.plant_id}"
                    except Exception as e:
                        logger.warning(
                            f"Error loading plant for record {record.id}: {e}", exc_info=True
                        )
                        record_dict["plant_name"] = f"Plant #{record.plant_id}"
                        record_dict["entity_type"] = "plant"
                        record_dict["entity_id"] = record.plant_id
                        record_dict["entity_name"] = f"Plant #{record.plant_id}"

                if record.cer_id:
                    try:
                        # CER table is actually cer_configuration
                        cer = (
                            db.query(CER)
                            .filter(
                                CER.id == record.cer_id, CER.tenant_id == current_user.tenant_id
                            )
                            .first()
                        )
                        if cer:
                            record_dict["cer_name"] = getattr(cer, "name", f"CER #{record.cer_id}")
                            record_dict["entity_type"] = "cer"
                            record_dict["entity_id"] = record.cer_id
                            record_dict["entity_name"] = getattr(
                                cer, "name", f"CER #{record.cer_id}"
                            )
                        else:
                            # Fallback if CER not found
                            record_dict["cer_name"] = f"CER #{record.cer_id}"
                            record_dict["entity_type"] = "cer"
                            record_dict["entity_id"] = record.cer_id
                            record_dict["entity_name"] = f"CER #{record.cer_id}"
                    except Exception as e:
                        logger.warning(
                            f"Error loading CER for record {record.id}: {e}", exc_info=True
                        )
                        record_dict["cer_name"] = f"CER #{record.cer_id}"
                        record_dict["entity_type"] = "cer"
                        record_dict["entity_id"] = record.cer_id
                        record_dict["entity_name"] = f"CER #{record.cer_id}"

                result.append(record_dict)
            except Exception as e:
                logger.error(f"Error serializing record {record.id}: {e}", exc_info=True)
                # Include basic record info even if enrichment fails
                result.append(
                    {
                        "id": record.id,
                        "requirement_id": record.requirement_id,
                        "status": str(record.status),
                        "due_date": record.due_date.isoformat() if record.due_date else None,
                        "plant_id": record.plant_id,
                        "cer_id": record.cer_id,
                    }
                )

        return result
    except Exception as e:
        logger.error(f"Error listing compliance records: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list compliance records: {str(e)}")


@router.post("/records", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_record(
    record_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new compliance record from a requirement"""
    try:
        requirement_id = record_data.get("requirement_id")
        due_date_str = record_data.get("due_date")
        notes = record_data.get("notes")

        if not requirement_id:
            raise HTTPException(status_code=400, detail="requirement_id is required")
        if not due_date_str:
            raise HTTPException(status_code=400, detail="due_date is required")

        # Parse due date
        try:
            due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
        except ValueError:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid due_date format. Use ISO format or YYYY-MM-DD"
                )

        record = compliance_service.create_record(
            db=db,
            requirement_id=requirement_id,
            due_date=due_date,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )

        # Update notes if provided
        if notes:
            record.notes = notes
            db.commit()
            db.refresh(record)

        return {
            "id": record.id,
            "requirement_id": record.requirement_id,
            "status": (
                record.status.value if hasattr(record.status, "value") else str(record.status)
            ),
            "due_date": record.due_date.isoformat() if record.due_date else None,
            "notes": record.notes,
            "plant_id": record.plant_id,
            "cer_id": record.cer_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create record: {str(e)}")


@router.post("/records/{record_id}/complete", response_model=dict)
async def complete_record(
    record_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark compliance record as completed"""
    record = compliance_service.complete_record(
        db=db, record_id=record_id, tenant_id=current_user.tenant_id, user_id=int(current_user.sub)
    )
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record
