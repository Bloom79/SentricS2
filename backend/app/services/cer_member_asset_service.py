"""
Service for managing CER Member Assets
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.cer_member_asset import CERMemberAsset
from app.models.cer import CERMember
from app.schemas.cer_member_asset import CERMemberAssetCreate, CERMemberAssetUpdate


class CERMemberAssetService:
    """Service for CER member asset management"""

    @staticmethod
    def create_asset(
        db: Session, asset_data: CERMemberAssetCreate, tenant_id: str, user_id: int
    ) -> CERMemberAsset:
        """Create a new member asset"""
        # Verify member exists and belongs to tenant
        member = (
            db.query(CERMember)
            .filter(
                and_(
                    CERMember.id == asset_data.member_id,
                    CERMember.cer_id == asset_data.cer_id,
                    CERMember.tenant_id == tenant_id,
                    CERMember.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not member:
            raise ValueError("Member not found")

        # Create asset
        asset = CERMemberAsset(
            tenant_id=tenant_id,
            member_id=asset_data.member_id,
            cer_id=asset_data.cer_id,
            name=asset_data.name,
            asset_type=asset_data.asset_type,
            capacity=asset_data.capacity,
            installation_date=asset_data.installation_date,
            gse_registration_id=asset_data.gse_registration_id,
            status=asset_data.status,
            asset_metadata=asset_data.asset_metadata or {},
            created_by=user_id,
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    @staticmethod
    def get_asset(db: Session, asset_id: int, tenant_id: str) -> Optional[CERMemberAsset]:
        """Get asset by ID"""
        return (
            db.query(CERMemberAsset)
            .filter(
                and_(
                    CERMemberAsset.id == asset_id,
                    CERMemberAsset.tenant_id == tenant_id,
                    CERMemberAsset.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def list_assets(
        db: Session,
        member_id: Optional[int] = None,
        cer_id: Optional[int] = None,
        tenant_id: Optional[str] = None,
    ) -> List[CERMemberAsset]:
        """List assets with optional filters"""
        query = db.query(CERMemberAsset).filter(CERMemberAsset.deleted_at.is_(None))

        if tenant_id:
            query = query.filter(CERMemberAsset.tenant_id == tenant_id)

        if member_id:
            query = query.filter(CERMemberAsset.member_id == member_id)

        if cer_id:
            query = query.filter(CERMemberAsset.cer_id == cer_id)

        return query.all()

    @staticmethod
    def update_asset(
        db: Session, asset_id: int, asset_data: CERMemberAssetUpdate, tenant_id: str, user_id: int
    ) -> Optional[CERMemberAsset]:
        """Update an asset"""
        asset = CERMemberAssetService.get_asset(db, asset_id, tenant_id)
        if not asset:
            return None

        # Update fields
        update_data = asset_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(asset, field, value)

        asset.updated_by = user_id
        db.commit()
        db.refresh(asset)

        return asset

    @staticmethod
    def delete_asset(db: Session, asset_id: int, tenant_id: str, user_id: int) -> bool:
        """Delete an asset (soft delete)"""
        asset = CERMemberAssetService.get_asset(db, asset_id, tenant_id)
        if not asset:
            return False

        asset.soft_delete(user_id)
        db.commit()
        return True
