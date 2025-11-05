"""
Asset Service - Business logic for asset management
Migrated from Sentrics with Kronos EAM patterns
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import logging

from app.models.asset import Asset, AssetType, AssetMaintenance
from app.models.plant import Plant
from app.schemas.asset import AssetCreate, AssetUpdate, AssetTypeCreate

logger = logging.getLogger(__name__)


class AssetService:
    """Service for asset management"""

    @staticmethod
    def create_asset_type(
        db: Session, asset_type_data: AssetTypeCreate, tenant_id: str, user_id: int
    ) -> AssetType:
        """Create asset type"""
        try:
            asset_type = AssetType(
                tenant_id=tenant_id,
                name=asset_type_data.name,
                description=asset_type_data.description,
                normalized_name=asset_type_data.normalized_name.lower().replace(" ", "_"),
                attributes=asset_type_data.attributes,
                default_attributes=(
                    asset_type_data.default_attributes
                    if hasattr(asset_type_data, "default_attributes")
                    else {}
                ),
                created_by=user_id,
            )

            db.add(asset_type)
            db.commit()
            db.refresh(asset_type)

            logger.info(f"Created asset type {asset_type.id}")
            return asset_type

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating asset type: {e}")
            raise

    @staticmethod
    def get_asset_types(
        db: Session, tenant_id: str, skip: int = 0, limit: int = 100
    ) -> List[AssetType]:
        """List asset types"""
        return (
            db.query(AssetType)
            .filter(and_(AssetType.tenant_id == tenant_id, AssetType.deleted_at.is_(None)))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_asset_type(db: Session, type_id: int, tenant_id: str) -> Optional[AssetType]:
        """Get asset type by ID"""
        return (
            db.query(AssetType)
            .filter(
                and_(
                    AssetType.id == type_id,
                    AssetType.tenant_id == tenant_id,
                    AssetType.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def create_asset(
        db: Session, plant_id: int, asset_data: AssetCreate, tenant_id: str, user_id: int
    ) -> Asset:
        """Create asset for a plant"""
        try:
            # Verify plant exists
            plant = (
                db.query(Plant)
                .filter(
                    and_(
                        Plant.id == plant_id,
                        Plant.tenant_id == tenant_id,
                        Plant.deleted_at.is_(None),
                    )
                )
                .first()
            )

            if not plant:
                raise ValueError(f"Plant {plant_id} not found")

            # Verify asset type exists
            asset_type = AssetService.get_asset_type(db, asset_data.type_id, tenant_id)
            if not asset_type:
                raise ValueError(f"Asset type {asset_data.type_id} not found")

            # Create asset
            asset = Asset(
                tenant_id=tenant_id,
                plant_id=plant_id,
                type_id=asset_data.type_id,
                name=asset_data.name,
                model=asset_data.model,
                manufacturer=asset_data.manufacturer,
                serial_number=asset_data.serial_number,
                component_type=asset_data.component_type,
                status=asset_data.status or "operational",
                location=asset_data.location,
                installation_date=asset_data.installation_date,
                rated_power=asset_data.rated_power,
                efficiency=asset_data.efficiency,
                voltage=asset_data.voltage,
                current=asset_data.current,
                dynamic_attributes=asset_data.dynamic_attributes or {},
                parent_id=asset_data.parent_id,
                notes=asset_data.notes,
                warranty_expiry=asset_data.warranty_expiry,
                created_by=user_id,
            )

            db.add(asset)
            db.commit()
            db.refresh(asset)

            logger.info(f"Created asset {asset.id} for plant {plant_id}")
            return asset

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating asset: {e}")
            raise

    @staticmethod
    def get_plant_assets(
        db: Session,
        plant_id: int,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        type_id: Optional[int] = None,
    ) -> List[Asset]:
        """List assets for a plant"""
        query = db.query(Asset).filter(
            and_(
                Asset.plant_id == plant_id, Asset.tenant_id == tenant_id, Asset.deleted_at.is_(None)
            )
        )

        if status:
            query = query.filter(Asset.status == status)
        if type_id:
            query = query.filter(Asset.type_id == type_id)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_asset(db: Session, asset_id: int, tenant_id: str) -> Optional[Asset]:
        """Get asset by ID"""
        return (
            db.query(Asset)
            .filter(
                and_(Asset.id == asset_id, Asset.tenant_id == tenant_id, Asset.deleted_at.is_(None))
            )
            .first()
        )

    @staticmethod
    def update_asset(
        db: Session, asset_id: int, asset_data: AssetUpdate, tenant_id: str, user_id: int
    ) -> Optional[Asset]:
        """Update asset"""
        asset = AssetService.get_asset(db, asset_id, tenant_id)
        if not asset:
            return None

        update_data = asset_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(asset, key):
                setattr(asset, key, value)

        asset.updated_by = user_id
        asset.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(asset)

        logger.info(f"Updated asset {asset_id}")
        return asset

    @staticmethod
    def delete_asset(db: Session, asset_id: int, tenant_id: str, user_id: int) -> bool:
        """Delete asset (soft delete)"""
        asset = AssetService.get_asset(db, asset_id, tenant_id)
        if not asset:
            return False

        asset.soft_delete(user_id)
        db.commit()

        logger.info(f"Deleted asset {asset_id}")
        return True

    @staticmethod
    def get_asset_hierarchy(db: Session, asset_id: int, tenant_id: str) -> Dict[str, Any]:
        """Get asset with parent and children"""
        asset = AssetService.get_asset(db, asset_id, tenant_id)
        if not asset:
            return {}

        children = (
            db.query(Asset)
            .filter(
                and_(
                    Asset.parent_id == asset_id,
                    Asset.tenant_id == tenant_id,
                    Asset.deleted_at.is_(None),
                )
            )
            .all()
        )

        parent = None
        if asset.parent_id:
            parent = AssetService.get_asset(db, asset.parent_id, tenant_id)

        return {"asset": asset, "parent": parent, "children": children}


# Export service instance
asset_service = AssetService()
