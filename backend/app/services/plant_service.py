"""
Plant Service - Business logic for plant management
Enhanced with CER and Asset relationships
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import logging

from app.models.plant import Plant, PlantStatusEnum, PlantTypeEnum
from app.models.cer import CER
from app.models.asset import Asset
from app.schemas.plant import PlantCreate, PlantUpdate

logger = logging.getLogger(__name__)


class PlantService:
    """Service for plant management"""
    
    @staticmethod
    def create_plant(
        db: Session,
        plant_data: PlantCreate,
        tenant_id: str,
        user_id: int
    ) -> Plant:
        """Create a new plant"""
        try:
            # Verify CER if linked
            if plant_data.cer_id:
                cer = db.query(CER).filter(
                    and_(
                        CER.id == plant_data.cer_id,
                        CER.tenant_id == tenant_id,
                        CER.deleted_at.is_(None)
                    )
                ).first()
                if not cer:
                    raise ValueError(f"CER {plant_data.cer_id} not found")
            
            # Create plant
            plant = Plant(
                tenant_id=tenant_id,
                name=plant_data.name,
                code=plant_data.code,
                power=plant_data.power,
                power_kw=plant_data.power_kw,
                status=plant_data.status,
                type=plant_data.type,
                location=plant_data.location,
                address=plant_data.address,
                municipality=plant_data.municipality,
                province=plant_data.province,
                region=plant_data.region,
                latitude=plant_data.latitude,
                longitude=plant_data.longitude,
                cer_id=plant_data.cer_id,
                tags=plant_data.tags or [],
                notes=plant_data.notes,
                custom_fields=plant_data.custom_fields or {},
                created_by=user_id,
            )
            
            db.add(plant)
            db.commit()
            db.refresh(plant)
            
            # Update CER capacity if linked
            if plant.cer_id:
                from app.services.cer_service import cer_service
                cer_service._update_capacity(db, plant.cer_id, tenant_id)
            
            logger.info(f"Created plant {plant.id} ({plant.code})")
            return plant
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating plant: {e}")
            raise
    
    @staticmethod
    def get_plant(
        db: Session,
        plant_id: int,
        tenant_id: str,
        include_relations: bool = True
    ) -> Optional[Plant]:
        """Get plant by ID - Optimized with eager loading"""
        from sqlalchemy.orm import joinedload, selectinload
        
        query = db.query(Plant).filter(
            and_(
                Plant.id == plant_id,
                Plant.tenant_id == tenant_id,
                Plant.deleted_at.is_(None)
            )
        )
        
        # Use eager loading to prevent N+1 queries
        if include_relations:
            query = query.options(
                joinedload(Plant.cer),
                selectinload(Plant.assets)
            )
        
        plant = query.first()
        return plant
    
    @staticmethod
    def list_plants(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        type: Optional[str] = None,
        status: Optional[str] = None,
        cer_id: Optional[int] = None,
        region: Optional[str] = None
    ) -> List[Plant]:
        """List plants with filters - Optimized with eager loading"""
        from sqlalchemy.orm import selectinload
        
        query = db.query(Plant).filter(
            and_(
                Plant.tenant_id == tenant_id,
                Plant.deleted_at.is_(None)
            )
        ).options(
            selectinload(Plant.cer)  # Eager load CER to prevent N+1
        )
        
        if type:
            query = query.filter(Plant.type == type)
        if status:
            query = query.filter(Plant.status == status)
        if cer_id:
            query = query.filter(Plant.cer_id == cer_id)
        if region:
            query = query.filter(Plant.region == region)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_plant(
        db: Session,
        plant_id: int,
        plant_data: PlantUpdate,
        tenant_id: str,
        user_id: int
    ) -> Optional[Plant]:
        """Update plant"""
        plant = PlantService.get_plant(db, plant_id, tenant_id, include_relations=False)
        if not plant:
            return None
        
        old_cer_id = plant.cer_id
        
        # Update fields
        update_data = plant_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(plant, key):
                setattr(plant, key, value)
        
        plant.updated_by = user_id
        plant.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(plant)
        
        # Update CER capacity if CER changed
        if old_cer_id != plant.cer_id:
            from app.services.cer_service import cer_service
            if old_cer_id:
                cer_service._update_capacity(db, old_cer_id, tenant_id)
            if plant.cer_id:
                cer_service._update_capacity(db, plant.cer_id, tenant_id)
        
        logger.info(f"Updated plant {plant_id}")
        return plant
    
    @staticmethod
    def delete_plant(
        db: Session,
        plant_id: int,
        tenant_id: str,
        user_id: int
    ) -> bool:
        """Delete plant (soft delete)"""
        plant = PlantService.get_plant(db, plant_id, tenant_id, include_relations=False)
        if not plant:
            return False
        
        cer_id = plant.cer_id
        
        plant.soft_delete(user_id)
        db.commit()
        
        # Update CER capacity
        if cer_id:
            from app.services.cer_service import cer_service
            cer_service._update_capacity(db, cer_id, tenant_id)
        
        logger.info(f"Deleted plant {plant_id}")
        return True
    
    @staticmethod
    def get_plant_stats(
        db: Session,
        plant_id: int,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get plant statistics"""
        plant = PlantService.get_plant(db, plant_id, tenant_id)
        if not plant:
            return {}
        
        # Count assets
        asset_count = db.query(func.count(Asset.id)).filter(
            and_(
                Asset.plant_id == plant_id,
                Asset.tenant_id == tenant_id,
                Asset.deleted_at.is_(None)
            )
        ).scalar() or 0
        
        # Count operational assets
        operational_assets = db.query(func.count(Asset.id)).filter(
            and_(
                Asset.plant_id == plant_id,
                Asset.tenant_id == tenant_id,
                Asset.status == "operational",
                Asset.deleted_at.is_(None)
            )
        ).scalar() or 0
        
        return {
            "plant_id": plant_id,
            "total_assets": asset_count,
            "operational_assets": operational_assets,
            "cer_linked": plant.cer_id is not None,
            "total_capacity_kw": plant.power_kw,
        }


# Export service instance
plant_service = PlantService()

