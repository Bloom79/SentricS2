"""
Site service for managing sites and site-level operations
Part of Sites → Plants → Assets hierarchy
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from app.models.site import Site, SiteStatusEnum, SiteTypeEnum, StorageUnit, Consumer, EnergyFlow
from app.models.plant import Plant

logger = logging.getLogger(__name__)


class SiteService:
    """Service for site management"""

    @staticmethod
    def create_site(
        db: Session,
        site_data: Dict[str, Any],
        tenant_id: str
    ) -> Site:
        """Create a new site"""
        try:
            site = Site(
                tenant_id=tenant_id,
                name=site_data.get("name"),
                code=site_data.get("code"),
                description=site_data.get("description"),
                site_type=SiteTypeEnum(site_data.get("site_type", "industrial")),
                status=site_data.get("status", "active"),
                operational_status=site_data.get("operational_status"),
                location=site_data.get("location"),
                address=site_data.get("address"),
                street_address=site_data.get("street_address"),
                city=site_data.get("city"),
                postal_code=site_data.get("postal_code"),
                province=site_data.get("province"),
                region=site_data.get("region"),
                country=site_data.get("country", "Italy"),
                latitude=site_data.get("latitude"),
                longitude=site_data.get("longitude"),
                capacity=site_data.get("capacity", 0.0),
                efficiency=site_data.get("efficiency", 0.0),
                available_area=site_data.get("available_area"),
                reserved_area=site_data.get("reserved_area"),
                commissioning_date=site_data.get("commissioning_date"),
                decommissioning_date=site_data.get("decommissioning_date"),
                owner=site_data.get("owner"),
                operator=site_data.get("operator"),
                maintenance_provider=site_data.get("maintenance_provider"),
                environmental_impact_rating=site_data.get("environmental_impact_rating"),
                grid_connection_status=site_data.get("grid_connection_status", "connected"),
                grid_capacity=site_data.get("grid_capacity"),
                tags=site_data.get("tags", []),
                notes=site_data.get("notes"),
                custom_fields=site_data.get("custom_fields", {}),
            )
            
            db.add(site)
            db.commit()
            db.refresh(site)
            
            logger.info(f"Created site {site.id}: {site.name} for tenant {tenant_id}")
            return site
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating site: {e}")
            raise

    @staticmethod
    def get_site(
        db: Session,
        site_id: int,
        tenant_id: str,
        include_relations: bool = True
    ) -> Optional[Site]:
        """Get site by ID with optional relations"""
        try:
            query = db.query(Site).filter(
                and_(
                    Site.id == site_id,
                    Site.tenant_id == tenant_id
                )
            )
            
            if include_relations:
                query = query.options(
                    selectinload(Site.plants),
                    selectinload(Site.storage_units),
                    selectinload(Site.consumers),
                    selectinload(Site.energy_flows)
                )
            
            site = query.first()
            return site
            
        except Exception as e:
            logger.error(f"Error getting site {site_id}: {e}")
            raise

    @staticmethod
    def list_sites(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        site_type: Optional[str] = None,
        region: Optional[str] = None
    ) -> List[Site]:
        """List sites with filters"""
        try:
            query = db.query(Site).filter(Site.tenant_id == tenant_id)
            
            if status:
                query = query.filter(Site.status == status)
            if site_type:
                query = query.filter(Site.site_type == SiteTypeEnum(site_type))
            if region:
                query = query.filter(Site.region == region)
            
            sites = query.options(
                selectinload(Site.plants)  # Eager load plants for count
            ).offset(skip).limit(limit).all()
            
            return sites
            
        except Exception as e:
            logger.error(f"Error listing sites: {e}")
            raise

    @staticmethod
    def update_site(
        db: Session,
        site_id: int,
        site_data: Dict[str, Any],
        tenant_id: str
    ) -> Optional[Site]:
        """Update site"""
        try:
            site = db.query(Site).filter(
                and_(
                    Site.id == site_id,
                    Site.tenant_id == tenant_id
                )
            ).first()
            
            if not site:
                return None
            
            # Update fields
            updatable_fields = [
                "name", "code", "description", "status", "operational_status",
                "location", "address", "street_address", "city", "postal_code",
                "province", "region", "country", "latitude", "longitude",
                "capacity", "efficiency", "available_area", "reserved_area",
                "commissioning_date", "decommissioning_date", "owner", "operator",
                "maintenance_provider", "environmental_impact_rating",
                "grid_connection_status", "grid_capacity", "tags", "notes", "custom_fields"
            ]
            
            for field in updatable_fields:
                if field in site_data:
                    if field == "site_type" and site_data[field]:
                        setattr(site, field, SiteTypeEnum(site_data[field]))
                    else:
                        setattr(site, field, site_data[field])
            
            db.commit()
            db.refresh(site)
            
            logger.info(f"Updated site {site_id}")
            return site
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating site {site_id}: {e}")
            raise

    @staticmethod
    def delete_site(
        db: Session,
        site_id: int,
        tenant_id: str,
        soft: bool = True
    ) -> bool:
        """Delete site (soft or hard delete)"""
        try:
            site = db.query(Site).filter(
                and_(
                    Site.id == site_id,
                    Site.tenant_id == tenant_id
                )
            ).first()
            
            if not site:
                return False
            
            if soft:
                site.soft_delete()
            else:
                db.delete(site)
            
            db.commit()
            
            logger.info(f"Deleted site {site_id} (soft={soft})")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting site {site_id}: {e}")
            raise

    @staticmethod
    def get_site_stats(
        db: Session,
        site_id: int,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get site statistics"""
        try:
            site = db.query(Site).filter(
                and_(
                    Site.id == site_id,
                    Site.tenant_id == tenant_id
                )
            ).first()
            
            if not site:
                return {}
            
            # Count plants
            plants_count = db.query(func.count(Plant.id)).filter(
                and_(
                    Plant.site_id == site_id,
                    Plant.tenant_id == tenant_id
                )
            ).scalar() or 0
            
            # Calculate total capacity from plants
            total_capacity = db.query(func.sum(Plant.power_kw)).filter(
                and_(
                    Plant.site_id == site_id,
                    Plant.tenant_id == tenant_id
                )
            ).scalar() or 0.0
            
            # Count storage units
            storage_count = len(site.storage_units) if site.storage_units else 0
            total_storage_capacity = sum(
                s.capacity_kwh for s in site.storage_units
            ) if site.storage_units else 0.0
            
            # Count consumers
            consumers_count = len(site.consumers) if site.consumers else 0
            
            return {
                "site_id": site_id,
                "plants_count": plants_count,
                "total_capacity_kw": float(total_capacity),
                "storage_units_count": storage_count,
                "total_storage_capacity_kwh": float(total_storage_capacity),
                "consumers_count": consumers_count,
                "site_capacity": site.capacity or 0.0,
                "site_efficiency": site.efficiency or 0.0,
            }
            
        except Exception as e:
            logger.error(f"Error getting site stats {site_id}: {e}")
            raise

    @staticmethod
    def get_site_energy_flow(
        db: Session,
        site_id: int,
        tenant_id: str
    ) -> Optional[EnergyFlow]:
        """Get active energy flow layout for site"""
        try:
            energy_flow = db.query(EnergyFlow).filter(
                and_(
                    EnergyFlow.site_id == site_id,
                    EnergyFlow.is_active == True
                )
            ).first()
            
            return energy_flow
            
        except Exception as e:
            logger.error(f"Error getting energy flow for site {site_id}: {e}")
            raise

    @staticmethod
    def save_site_energy_flow(
        db: Session,
        site_id: int,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        tenant_id: str,
        description: Optional[str] = None
    ) -> EnergyFlow:
        """Save energy flow layout for site"""
        try:
            # Check if active flow exists
            existing_flow = db.query(EnergyFlow).filter(
                and_(
                    EnergyFlow.site_id == site_id,
                    EnergyFlow.is_active == True
                )
            ).first()
            
            if existing_flow:
                # Update existing
                existing_flow.nodes = nodes
                existing_flow.edges = edges
                existing_flow.description = description
                db.commit()
                db.refresh(existing_flow)
                return existing_flow
            else:
                # Create new
                energy_flow = EnergyFlow(
                    tenant_id=tenant_id,
                    site_id=site_id,
                    nodes=nodes,
                    edges=edges,
                    description=description,
                    is_active=True
                )
                db.add(energy_flow)
                db.commit()
                db.refresh(energy_flow)
                return energy_flow
                
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving energy flow for site {site_id}: {e}")
            raise


