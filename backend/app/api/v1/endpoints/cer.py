"""
CER (Renewable Energy Community) API endpoints
Migrated from Sentrics with Kronos EAM patterns
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.cer_service import cer_service
from app.services.cer_member_asset_service import CERMemberAssetService

logger = logging.getLogger(__name__)
from app.schemas.cer import (
    CERCreate,
    CERUpdate,
    CERResponse,
    CERMemberCreate,
    CERMemberUpdate,
    CERMemberResponse,
    CERParticipationRequestCreate,
    CERParticipationRequestUpdate,
    CERParticipationRequestResponse,
    CERParticipationRequestWithDetails,
    CERStatsResponse,
)
from app.schemas.cer_member_asset import (
    CERMemberAssetCreate,
    CERMemberAssetUpdate,
    CERMemberAssetResponse,
)
from app.services.cer_member_asset_service import CERMemberAssetService
from app.schemas.plant import PlantResponse

router = APIRouter()


@router.post("/communities", response_model=CERResponse, status_code=status.HTTP_201_CREATED)
async def create_cer(
    cer_data: CERCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new CER"""
    try:
        cer = cer_service.create_cer(
            db=db,
            cer_data=cer_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return cer
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create CER")


@router.get("/communities", response_model=List[CERResponse])
async def list_cer(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    legal_type: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List CERs for current tenant"""
    cer_list = cer_service.list_cer(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        status=status,
        legal_type=legal_type,
    )
    return cer_list


@router.get("/communities/{cer_id}", response_model=CERResponse)
async def get_cer(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get CER details"""
    cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")
    return cer


@router.put("/communities/{cer_id}", response_model=CERResponse)
async def update_cer(
    cer_id: int,
    cer_data: CERUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update CER"""
    cer = cer_service.update_cer(
        db=db,
        cer_id=cer_id,
        cer_data=cer_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")
    return cer


@router.delete("/communities/{cer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cer(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete CER (soft delete)"""
    success = cer_service.delete_cer(
        db=db, cer_id=cer_id, tenant_id=current_user.tenant_id, user_id=int(current_user.sub)
    )
    if not success:
        raise HTTPException(status_code=404, detail="CER not found")
    return None


# Member endpoints
@router.post(
    "/communities/{cer_id}/members",
    response_model=CERMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    cer_id: int,
    member_data: CERMemberCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add member to CER"""
    try:
        member = cer_service.add_member(
            db=db,
            cer_id=cer_id,
            member_data=member_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not member:
            raise HTTPException(status_code=404, detail="CER not found")
        return member
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/communities/{cer_id}/members", response_model=List[CERMemberResponse])
async def list_members(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List CER members"""
    try:
        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        members = cer_service.list_members(db, cer_id, current_user.tenant_id)
        # Ensure energy fields have default values if None
        for member in members:
            if member.energy_produced is None:
                member.energy_produced = 0.0
            if member.energy_consumed is None:
                member.energy_consumed = 0.0
            if member.energy_shared is None:
                member.energy_shared = 0.0
        return members
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing members for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/communities/{cer_id}/members/{member_id}", response_model=CERMemberResponse)
async def get_member(
    cer_id: int,
    member_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a single CER member"""
    # Verify CER exists
    cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")

    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.get("/communities/{cer_id}/stats", response_model=dict)
async def get_cer_stats(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get statistics for a CER"""
    try:
        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        stats = cer_service.get_cer_stats(db, cer_id, current_user.tenant_id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/communities/{cer_id}/members/{member_id}", response_model=CERMemberResponse)
async def update_member(
    cer_id: int,
    member_id: int,
    member_data: CERMemberUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update CER member"""
    member = cer_service.update_member(
        db=db,
        cer_id=cer_id,
        member_id=member_id,
        member_data=member_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.delete("/communities/{cer_id}/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    cer_id: int,
    member_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove member from CER"""
    success = cer_service.delete_member(
        db=db,
        cer_id=cer_id,
        member_id=member_id,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return None


# Participation request endpoints
@router.post(
    "/participation-requests",
    response_model=CERParticipationRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_participation_request(
    request_data: CERParticipationRequestCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a participation request to join a CER"""
    try:
        request = cer_service.create_participation_request(
            db=db,
            request_data=request_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating participation request: {e}")
        raise HTTPException(status_code=500, detail="Failed to create participation request")


@router.get("/participation-requests", response_model=List[CERParticipationRequestResponse])
async def list_participation_requests(
    cer_id: Optional[int] = Query(None, description="Filter by CER ID"),
    status: Optional[str] = Query(
        None, description="Filter by status (pending, approved, rejected, cancelled)"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List participation requests (filtered by tenant)"""
    requests = cer_service.list_participation_requests(
        db=db,
        tenant_id=current_user.tenant_id,
        cer_id=cer_id,
        status=status,
        skip=skip,
        limit=limit,
    )
    return requests


@router.get("/participation-requests/{request_id}", response_model=CERParticipationRequestResponse)
async def get_participation_request(
    request_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get participation request details"""
    request = cer_service.get_participation_request(db, request_id, current_user.tenant_id)
    if not request:
        raise HTTPException(status_code=404, detail="Participation request not found")
    return request


@router.put("/participation-requests/{request_id}", response_model=CERParticipationRequestResponse)
async def update_participation_request(
    request_id: int,
    request_data: CERParticipationRequestUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update participation request status (approve/reject)"""
    try:
        request = cer_service.update_participation_request(
            db=db,
            request_id=request_id,
            request_data=request_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not request:
            raise HTTPException(status_code=404, detail="Participation request not found")
        return request
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating participation request: {e}")
        raise HTTPException(status_code=500, detail="Failed to update participation request")


@router.delete("/participation-requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_participation_request(
    request_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete participation request (only pending or cancelled)"""
    try:
        success = cer_service.delete_participation_request(
            db=db,
            request_id=request_id,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        if not success:
            raise HTTPException(status_code=404, detail="Participation request not found")
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/participation-requests/user/me", response_model=List[CERParticipationRequestResponse])
async def get_my_participation_requests(
    current_user: TokenData = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get current user's participation requests"""
    requests = cer_service.get_user_participation_requests(
        db=db, user_id=int(current_user.sub), tenant_id=current_user.tenant_id
    )
    return requests


@router.get(
    "/communities/{cer_id}/participation-requests",
    response_model=List[CERParticipationRequestResponse],
)
async def list_cer_participation_requests(
    cer_id: int,
    status: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List participation requests for a specific CER"""
    # Verify CER exists
    cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")

    requests = cer_service.list_participation_requests(
        db=db, tenant_id=current_user.tenant_id, cer_id=cer_id, status=status
    )
    return requests


# CER Compliance endpoints
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

        # Get CER-specific requirements
        cer_requirements = compliance_service.list_requirements(
            db=db, tenant_id=current_user.tenant_id, cer_id=cer_id
        )

        # Get CER-specific overdue records
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
                # Get plant requirements
                plant_reqs = compliance_service.list_requirements(
                    db=db, tenant_id=current_user.tenant_id, plant_id=plant.id
                )
                plant_requirements.extend(plant_reqs)

                # Get plant overdue records
                plant_ovr = compliance_service.get_overdue_records(
                    db=db, tenant_id=current_user.tenant_id, plant_id=plant.id
                )
                plant_overdue.extend(plant_ovr)

                # Summary per plant
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

        # Combine all overdue records
        all_overdue = cer_overdue + plant_overdue

        # Serialize requirements and records to dicts
        def serialize_requirement(req):
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

        def serialize_record(rec):
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

        return {
            "cer_id": cer_id,
            "cer_name": cer.name,
            "cer_requirements": [serialize_requirement(req) for req in cer_requirements],
            "cer_overdue": [serialize_record(rec) for rec in cer_overdue],
            "cer_compliance_status": "compliant" if len(cer_overdue) == 0 else "non_compliant",
            "plant_requirements": [serialize_requirement(req) for req in plant_requirements],
            "plant_overdue": [serialize_record(rec) for rec in plant_overdue],
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
                    logger.error(f"Error getting requirements for plant {plant.id}: {e}")
                    continue

        return requirements
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting CER compliance requirements: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get compliance requirements: {str(e)}"
        )


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
        from app.services.compliance_service import compliance_service
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
            # Try to match status enum value
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
                    logger.error(f"Error getting records for plant {plant.id}: {e}")
                    continue

        return records
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting CER compliance records: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get compliance records: {str(e)}")


# CER Document endpoints
@router.get("/communities/{cer_id}/documents", response_model=List[dict])
async def get_cer_documents(
    cer_id: int,
    type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get documents for a CER"""
    try:
        from app.services.document_service import document_service

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        documents = document_service.list_documents(
            db=db,
            tenant_id=current_user.tenant_id,
            cer_id=cer_id,
            type=type,
            status=status,
            skip=skip,
            limit=limit,
        )
        return documents
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/communities/{cer_id}/documents/overview", response_model=dict)
async def get_cer_documents_overview(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get document overview for a CER (counts by type, expired, etc.)"""
    try:
        from app.models.document import Document, DocumentTypeEnum, DocumentStatusEnum
        from datetime import datetime

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        # Get all documents for this CER
        documents = (
            db.query(Document)
            .filter(
                Document.cer_id == cer_id,
                Document.tenant_id == current_user.tenant_id,
                Document.deleted_at.is_(None),
            )
            .all()
        )

        # Count by type
        by_type = {}
        for doc_type in DocumentTypeEnum:
            by_type[doc_type.value] = len([d for d in documents if d.type == doc_type])

        # Count expired
        expired = len([d for d in documents if d.is_expired])

        # Count by status
        by_status = {}
        for doc_status in DocumentStatusEnum:
            by_status[doc_status.value] = len([d for d in documents if d.status == doc_status])

        return {
            "cer_id": cer_id,
            "total_documents": len(documents),
            "by_type": by_type,
            "by_status": by_status,
            "expired_count": expired,
            "expiring_soon_count": len(
                [
                    d
                    for d in documents
                    if hasattr(d, "days_until_expiry")
                    and d.days_until_expiry is not None
                    and 0 < d.days_until_expiry <= 30
                ]
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents overview for CER {cer_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# Member Asset Endpoints
@router.post(
    "/communities/{cer_id}/members/{member_id}/assets",
    response_model=CERMemberAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_member_asset(
    cer_id: int,
    member_id: int,
    asset_data: CERMemberAssetCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new asset for a CER member"""
    try:
        # Verify member exists
        member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Create asset data with IDs from path
        asset_create = CERMemberAssetCreate(**asset_data.dict(), member_id=member_id, cer_id=cer_id)

        asset = CERMemberAssetService.create_asset(
            db=db,
            asset_data=asset_create,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to create member asset")
        raise HTTPException(status_code=500, detail="Failed to create asset")


@router.get(
    "/communities/{cer_id}/members/{member_id}/assets", response_model=List[CERMemberAssetResponse]
)
async def list_member_assets(
    cer_id: int,
    member_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all assets for a CER member"""
    try:
        # Verify member exists
        member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        assets = CERMemberAssetService.list_assets(
            db=db, member_id=member_id, cer_id=cer_id, tenant_id=current_user.tenant_id
        )
        return assets
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error listing assets for member {member_id} in CER {cer_id}: {e}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/communities/{cer_id}/members/{member_id}/assets/{asset_id}",
    response_model=CERMemberAssetResponse,
)
async def get_member_asset(
    cer_id: int,
    member_id: int,
    asset_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific member asset"""
    # Verify member exists
    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    asset = CERMemberAssetService.get_asset(db, asset_id, current_user.tenant_id)
    if not asset or asset.member_id != member_id or asset.cer_id != cer_id:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.put(
    "/communities/{cer_id}/members/{member_id}/assets/{asset_id}",
    response_model=CERMemberAssetResponse,
)
async def update_member_asset(
    cer_id: int,
    member_id: int,
    asset_id: int,
    asset_data: CERMemberAssetUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a member asset"""
    # Verify member exists
    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    asset = CERMemberAssetService.update_asset(
        db=db,
        asset_id=asset_id,
        asset_data=asset_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )

    if not asset or asset.member_id != member_id or asset.cer_id != cer_id:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset


@router.delete(
    "/communities/{cer_id}/members/{member_id}/assets/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_member_asset(
    cer_id: int,
    member_id: int,
    asset_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a member asset"""
    # Verify member exists
    member = cer_service.get_member(db, cer_id, member_id, current_user.tenant_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    success = CERMemberAssetService.delete_asset(
        db=db, asset_id=asset_id, tenant_id=current_user.tenant_id, user_id=int(current_user.sub)
    )

    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")

    return None


# Plant Linking Endpoints
@router.post("/communities/{cer_id}/plants/{plant_id}/link", status_code=status.HTTP_200_OK)
async def link_plant_to_cer(
    cer_id: int,
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Link a plant to a CER"""
    try:
        success = cer_service.link_plant(
            db=db, cer_id=cer_id, plant_id=plant_id, tenant_id=current_user.tenant_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="CER or Plant not found")
        return {"message": "Plant linked successfully", "cer_id": cer_id, "plant_id": plant_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to link plant")
        raise HTTPException(status_code=500, detail="Failed to link plant")


@router.delete("/communities/{cer_id}/plants/{plant_id}/link", status_code=status.HTTP_200_OK)
async def unlink_plant_from_cer(
    cer_id: int,
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Unlink a plant from a CER"""
    try:
        from app.models.plant import Plant
        from sqlalchemy import and_

        # Verify CER exists
        cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
        if not cer:
            raise HTTPException(status_code=404, detail="CER not found")

        # Get plant and verify it's linked to this CER
        plant = (
            db.query(Plant)
            .filter(
                and_(
                    Plant.id == plant_id,
                    Plant.cer_id == cer_id,
                    Plant.tenant_id == current_user.tenant_id,
                    Plant.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found or not linked to this CER")

        # Unlink plant
        plant.cer_id = None
        db.commit()

        # Update CER capacity
        cer_service._update_capacity(db, cer_id, current_user.tenant_id)

        return {"message": "Plant unlinked successfully", "cer_id": cer_id, "plant_id": plant_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.exception("Failed to unlink plant")
        raise HTTPException(status_code=500, detail="Failed to unlink plant")


@router.get("/communities/{cer_id}/plants", response_model=List[PlantResponse])
async def get_cer_plants(
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all plants linked to a CER"""
    from app.models.plant import Plant
    from sqlalchemy import and_

    # Verify CER exists
    cer = cer_service.get_cer(db, cer_id, current_user.tenant_id)
    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")

    # Get linked plants
    plants = (
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

    return plants
