"""
CER Service - Business logic for Renewable Energy Communities
Migrated from Sentrics with Kronos EAM patterns
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timezone
import logging

from app.models.cer import (
    CER,
    CERMember,
    CERParticipationRequest,
    CERStatus,
    ParticipationRequestStatus,
)
from app.models.plant import Plant
from app.core.geography import create_point, create_polygon, validate_boundary
from app.schemas.cer import (
    CERCreate,
    CERUpdate,
    CERMemberCreate,
    CERMemberUpdate,
    CERParticipationRequestCreate,
    CERParticipationRequestUpdate,
)

logger = logging.getLogger(__name__)


class CERService:
    """Service for CER management"""

    @staticmethod
    def create_cer(db: Session, cer_data: CERCreate, tenant_id: str, user_id: int) -> CER:
        """Create a new CER"""
        try:
            # Validate boundary if provided
            if cer_data.boundary:
                if not validate_boundary(cer_data.boundary):
                    raise ValueError("Invalid boundary coordinates")
                boundary_wkt = create_polygon(cer_data.boundary)
            else:
                boundary_wkt = None

            # Create location point if provided
            location_wkt = None
            if cer_data.location and len(cer_data.location) == 2:
                location_wkt = create_point(cer_data.location[0], cer_data.location[1])

            # Create CER
            cer = CER(
                tenant_id=tenant_id,
                name=cer_data.name,
                description=cer_data.description,
                legal_type=cer_data.legal_type,
                type=cer_data.type,
                address=cer_data.address,
                region=cer_data.region,
                primary_substation_id=cer_data.primary_substation_id,
                location=location_wkt,
                boundary=boundary_wkt,
                technical_info=cer_data.technical_info,
                billing_settings=cer_data.billing_settings,
                status=CERStatus.DRAFT,
                created_by=user_id,
            )

            db.add(cer)
            db.commit()
            db.refresh(cer)

            logger.info(f"Created CER {cer.id} for tenant {tenant_id}")
            return cer

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating CER: {e}")
            raise

    @staticmethod
    def get_cer(db: Session, cer_id: int, tenant_id: str) -> Optional[CER]:
        """Get CER by ID"""
        return (
            db.query(CER)
            .filter(and_(CER.id == cer_id, CER.tenant_id == tenant_id, CER.deleted_at.is_(None)))
            .first()
        )

    @staticmethod
    def list_cer(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        legal_type: Optional[str] = None,
    ) -> List[CER]:
        """List CERs for tenant"""
        query = db.query(CER).filter(and_(CER.tenant_id == tenant_id, CER.deleted_at.is_(None)))

        if status:
            query = query.filter(CER.status == status)
        if legal_type:
            query = query.filter(CER.legal_type == legal_type)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_cer(
        db: Session, cer_id: int, cer_data: CERUpdate, tenant_id: str, user_id: int
    ) -> Optional[CER]:
        """Update CER"""
        cer = CERService.get_cer(db, cer_id, tenant_id)
        if not cer:
            return None

        # Update fields
        update_data = cer_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(cer, key):
                setattr(cer, key, value)

        cer.updated_by = user_id
        cer.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(cer)

        logger.info(f"Updated CER {cer_id}")
        return cer

    @staticmethod
    def delete_cer(db: Session, cer_id: int, tenant_id: str, user_id: int) -> bool:
        """Soft delete CER"""
        cer = CERService.get_cer(db, cer_id, tenant_id)
        if not cer:
            return False

        cer.soft_delete(user_id)
        db.commit()

        logger.info(f"Deleted CER {cer_id}")
        return True

    @staticmethod
    def add_member(
        db: Session, cer_id: int, member_data: CERMemberCreate, tenant_id: str, user_id: int
    ) -> Optional[CERMember]:
        """Add member to CER"""
        # Verify CER exists
        cer = CERService.get_cer(db, cer_id, tenant_id)
        if not cer:
            return None

        # Check if POD already exists
        existing = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.pod_id == member_data.pod_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .first()
        )

        if existing:
            raise ValueError(f"Member with POD {member_data.pod_id} already exists")

        # Build technical_info from production fields
        technical_info = member_data.technical_info or {}
        if member_data.member_type in ["producer", "prosumer"]:
            # Store production fields in technical_info
            if member_data.plant_type:
                technical_info["plant_type"] = member_data.plant_type
            if member_data.plant_capacity is not None:
                technical_info["plant_capacity"] = member_data.plant_capacity
            if member_data.commissioning_date:
                technical_info["commissioning_date"] = member_data.commissioning_date.isoformat()
            if member_data.is_incentivized is not None:
                technical_info["is_incentivized"] = member_data.is_incentivized
            if member_data.capital_contribution is not None:
                technical_info["capital_contribution"] = member_data.capital_contribution

            # Storage fields
            if member_data.has_storage is not None:
                technical_info["has_storage"] = member_data.has_storage
            if member_data.storage_capacity is not None:
                technical_info["storage_capacity"] = member_data.storage_capacity

        # Create member
        member = CERMember(
            tenant_id=tenant_id,
            cer_id=cer_id,
            name=member_data.name,
            address=member_data.address,
            member_type=member_data.member_type,
            user_type=member_data.user_type or "real",
            pod_id=member_data.pod_id,
            load_profile_type=member_data.load_profile_type,
            contracted_power=member_data.contracted_power,
            smart_meter_id=member_data.smart_meter_id,
            meter_type=member_data.meter_type,
            fiscal_code=member_data.fiscal_code,
            vat_number=member_data.vat_number,
            billing_address=member_data.billing_address,
            voltage_level=member_data.voltage_level,
            activation_date=member_data.activation_date,
            verification_status=member_data.verification_status,
            technical_info=technical_info,
            load_profile_data=member_data.load_profile_data,
            device_info=member_data.device_info,
            energy_sharing_preferences=member_data.energy_sharing_preferences,
            billing_preferences=member_data.billing_preferences,
            created_by=user_id,
        )

        db.add(member)
        db.commit()
        db.refresh(member)

        logger.info(f"Added member {member.id} to CER {cer_id}")
        return member

    @staticmethod
    def list_members(db: Session, cer_id: int, tenant_id: str) -> List[CERMember]:
        """List members of a CER"""
        return (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.cer_id == cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .all()
        )

    @staticmethod
    def update_member(
        db: Session,
        cer_id: int,
        member_id: int,
        member_data: CERMemberUpdate,
        tenant_id: str,
        user_id: int,
    ) -> Optional[CERMember]:
        """Update CER member"""
        member = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.id == member_id,
                    CERMember.cer_id == cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not member:
            return None

        # Update basic fields
        if member_data.name:
            member.name = member_data.name
        if member_data.address:
            member.address = member_data.address
        if member_data.status:
            member.status = member_data.status
        if member_data.member_type:
            member.member_type = member_data.member_type
        if member_data.contracted_power is not None:
            member.contracted_power = member_data.contracted_power

        # Update production/storage fields in technical_info
        if (
            member_data.plant_capacity is not None
            or member_data.has_storage is not None
            or member_data.storage_capacity is not None
            or member_data.is_incentivized is not None
            or member_data.capital_contribution is not None
        ):
            technical_info = member.technical_info or {}
            if member_data.plant_capacity is not None:
                technical_info["plant_capacity"] = member_data.plant_capacity
            if member_data.has_storage is not None:
                technical_info["has_storage"] = member_data.has_storage
            if member_data.storage_capacity is not None:
                technical_info["storage_capacity"] = member_data.storage_capacity
            if member_data.is_incentivized is not None:
                technical_info["is_incentivized"] = member_data.is_incentivized
            if member_data.capital_contribution is not None:
                technical_info["capital_contribution"] = member_data.capital_contribution
            member.technical_info = technical_info

        # Update JSON fields
        if member_data.energy_sharing_preferences:
            member.energy_sharing_preferences = member_data.energy_sharing_preferences
        if member_data.technical_info:
            # Merge with existing technical_info
            existing = member.technical_info or {}
            existing.update(member_data.technical_info)
            member.technical_info = existing
        if member_data.load_profile_data:
            member.load_profile_data = member_data.load_profile_data

        member.updated_by = user_id
        member.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(member)

        logger.info(f"Updated member {member_id} in CER {cer_id}")
        return member

    @staticmethod
    def delete_member(
        db: Session, cer_id: int, member_id: int, tenant_id: str, user_id: int
    ) -> bool:
        """Remove member from CER"""
        member = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.id == member_id,
                    CERMember.cer_id == cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not member:
            return False

        member.soft_delete(user_id)
        db.commit()
        return True

    @staticmethod
    def link_plant(db: Session, cer_id: int, plant_id: int, tenant_id: str) -> bool:
        """Link plant to CER"""
        cer = CERService.get_cer(db, cer_id, tenant_id)
        if not cer:
            return False

        plant = (
            db.query(Plant)
            .filter(
                and_(Plant.id == plant_id, Plant.tenant_id == tenant_id, Plant.deleted_at.is_(None))
            )
            .first()
        )

        if not plant:
            return False

        plant.cer_id = cer_id
        db.commit()

        # Update CER total capacity
        CERService._update_capacity(db, cer_id, tenant_id)

        return True

    @staticmethod
    def _update_capacity(db: Session, cer_id: int, tenant_id: str):
        """Update CER total capacity from linked plants"""
        cer = CERService.get_cer(db, cer_id, tenant_id)
        if not cer:
            return

        total = (
            db.query(Plant)
            .filter(
                and_(
                    Plant.cer_id == cer_id, Plant.tenant_id == tenant_id, Plant.deleted_at.is_(None)
                )
            )
            .with_entities(db.func.sum(Plant.power_kw))
            .scalar()
            or 0.0
        )

        cer.total_capacity = total
        db.commit()

    # Participation Request Methods
    @staticmethod
    def create_participation_request(
        db: Session, request_data: CERParticipationRequestCreate, tenant_id: str, user_id: int
    ) -> CERParticipationRequest:
        """Create a participation request"""
        # Verify CER exists
        cer = CERService.get_cer(db, request_data.cer_id, tenant_id)
        if not cer:
            raise ValueError("CER not found")

        # Check if user already has a pending request for this CER
        existing_request = (
            db.query(CERParticipationRequest)
            .filter(
                and_(
                    CERParticipationRequest.user_id == user_id,
                    CERParticipationRequest.cer_id == request_data.cer_id,
                    CERParticipationRequest.status == ParticipationRequestStatus.PENDING,
                    CERParticipationRequest.deleted_at.is_(None),
                )
            )
            .first()
        )

        if existing_request:
            raise ValueError("User already has a pending request for this CER")

        # Check if user is already a member
        existing_member = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.cer_id == request_data.cer_id,
                    CERMember.user_id == user_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                    CERMember.status == "active",
                )
            )
            .first()
        )

        if existing_member:
            raise ValueError("User is already a member of this CER")

        # Create request
        request = CERParticipationRequest(
            tenant_id=tenant_id,
            user_id=user_id,
            cer_id=request_data.cer_id,
            notes=request_data.notes,
            status=ParticipationRequestStatus.PENDING,
            created_by=user_id,
        )

        db.add(request)
        db.commit()
        db.refresh(request)

        logger.info(f"Created participation request {request.id} for CER {request_data.cer_id}")
        return request

    @staticmethod
    def list_participation_requests(
        db: Session,
        tenant_id: str,
        cer_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CERParticipationRequest]:
        """List participation requests"""
        query = db.query(CERParticipationRequest).filter(
            and_(
                CERParticipationRequest.tenant_id == tenant_id,
                CERParticipationRequest.deleted_at.is_(None),
            )
        )

        if cer_id:
            query = query.filter(CERParticipationRequest.cer_id == cer_id)

        if status:
            query = query.filter(CERParticipationRequest.status == status)

        return (
            query.order_by(CERParticipationRequest.request_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_participation_request(
        db: Session, request_id: int, tenant_id: str
    ) -> Optional[CERParticipationRequest]:
        """Get participation request by ID"""
        return (
            db.query(CERParticipationRequest)
            .filter(
                and_(
                    CERParticipationRequest.id == request_id,
                    CERParticipationRequest.tenant_id == tenant_id,
                    CERParticipationRequest.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def update_participation_request(
        db: Session,
        request_id: int,
        request_data: CERParticipationRequestUpdate,
        tenant_id: str,
        user_id: int,
    ) -> Optional[CERParticipationRequest]:
        """Update participation request status (approve/reject)"""
        request = CERService.get_participation_request(db, request_id, tenant_id)
        if not request:
            return None

        # Validate status
        try:
            new_status = ParticipationRequestStatus(request_data.status)
        except ValueError:
            raise ValueError(f"Invalid status: {request_data.status}")

        # Update status
        old_status = request.status
        request.status = new_status
        request.processed_date = datetime.now(timezone.utc)

        if request_data.notes:
            request.notes = request_data.notes

        request.updated_by = user_id
        request.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(request)

        # If approved, optionally create member (can be done separately)
        if (
            new_status == ParticipationRequestStatus.APPROVED
            and old_status == ParticipationRequestStatus.PENDING
        ):
            logger.info(f"Participation request {request_id} approved for CER {request.cer_id}")
            # Note: Member creation should be done via separate endpoint for better control

        logger.info(f"Updated participation request {request_id} to {new_status.value}")
        return request

    @staticmethod
    def delete_participation_request(
        db: Session, request_id: int, tenant_id: str, user_id: int
    ) -> bool:
        """Delete participation request (soft delete)"""
        request = CERService.get_participation_request(db, request_id, tenant_id)
        if not request:
            return False

        # Only allow deletion of pending or cancelled requests
        if request.status not in [
            ParticipationRequestStatus.PENDING,
            ParticipationRequestStatus.CANCELLED,
        ]:
            raise ValueError("Cannot delete approved or rejected requests")

        request.soft_delete(user_id)
        db.commit()

        logger.info(f"Deleted participation request {request_id}")
        return True

    @staticmethod
    def get_user_participation_requests(
        db: Session, user_id: int, tenant_id: str
    ) -> List[CERParticipationRequest]:
        """Get all participation requests for a user"""
        return (
            db.query(CERParticipationRequest)
            .filter(
                and_(
                    CERParticipationRequest.user_id == user_id,
                    CERParticipationRequest.tenant_id == tenant_id,
                    CERParticipationRequest.deleted_at.is_(None),
                )
            )
            .order_by(CERParticipationRequest.request_date.desc())
            .all()
        )

    @staticmethod
    def get_member(db: Session, cer_id: int, member_id: int, tenant_id: str) -> Optional[CERMember]:
        """Get a single member by ID"""
        return (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.id == member_id,
                    CERMember.cer_id == cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def get_cer_stats(db: Session, cer_id: int, tenant_id: str) -> Dict[str, Any]:
        """Get statistics for a CER"""
        cer = CERService.get_cer(db, cer_id, tenant_id)
        if not cer:
            return {}

        members = CERService.list_members(db, cer_id, tenant_id)

        # Count by type
        producers = len([m for m in members if m.member_type == "producer"])
        consumers = len([m for m in members if m.member_type == "consumer"])
        prosumers = len([m for m in members if m.member_type == "prosumer"])

        # Calculate totals
        total_capacity = sum(
            (m.technical_info or {}).get("plant_capacity", 0)
            for m in members
            if m.member_type in ["producer", "prosumer"]
        )
        total_energy_produced = sum((m.energy_produced or 0.0) for m in members)
        total_energy_consumed = sum((m.energy_consumed or 0.0) for m in members)
        total_energy_shared = sum((m.energy_shared or 0.0) for m in members)

        return {
            "cer_id": cer_id,
            "total_members": len(members),
            "producers": producers,
            "consumers": consumers,
            "prosumers": prosumers,
            "total_capacity": total_capacity,
            "total_energy_produced": total_energy_produced,
            "total_energy_consumed": total_energy_consumed,
            "total_energy_shared": total_energy_shared,
            "member_count": {
                "producers": producers,
                "consumers": consumers,
                "prosumers": prosumers,
            },
        }


# Export service instance
cer_service = CERService()
