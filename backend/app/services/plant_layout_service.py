"""
Plant Layout Service for Visual Plant Designer
Manages React Flow canvas data persistence
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.models.plant_layout import PlantLayout
from app.models.plant import Plant

logger = logging.getLogger(__name__)


class PlantLayoutService:
    """Service for plant layout management"""

    @staticmethod
    def get_layout(db: Session, plant_id: int, tenant_id: str) -> Optional[PlantLayout]:
        """Get plant layout by plant ID"""
        try:
            layout = (
                db.query(PlantLayout)
                .filter(
                    and_(
                        PlantLayout.plant_id == plant_id,
                        PlantLayout.tenant_id == tenant_id,
                        PlantLayout.is_active == True,
                    )
                )
                .first()
            )
            return layout
        except Exception as e:
            logger.error(f"Error getting layout for plant {plant_id}: {e}")
            raise

    @staticmethod
    def save_layout(
        db: Session,
        plant_id: int,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        tenant_id: str,
        user_id: Optional[int] = None,
    ) -> PlantLayout:
        """Save or update plant layout"""
        try:
            # Verify plant exists and belongs to tenant
            plant = (
                db.query(Plant)
                .filter(and_(Plant.id == plant_id, Plant.tenant_id == tenant_id))
                .first()
            )

            if not plant:
                raise ValueError(f"Plant {plant_id} not found")

            # Check if layout exists
            existing_layout = (
                db.query(PlantLayout)
                .filter(and_(PlantLayout.plant_id == plant_id, PlantLayout.tenant_id == tenant_id))
                .first()
            )

            if existing_layout:
                # Update existing
                existing_layout.nodes = nodes
                existing_layout.edges = edges
                existing_layout.version += 1
                existing_layout.is_active = True
                existing_layout.updated_by = user_id
                db.commit()
                db.refresh(existing_layout)
                logger.info(f"Updated layout for plant {plant_id}")
                return existing_layout
            else:
                # Create new
                layout = PlantLayout(
                    tenant_id=tenant_id,
                    plant_id=plant_id,
                    nodes=nodes,
                    edges=edges,
                    version=1,
                    is_active=True,
                    created_by=user_id,
                )
                db.add(layout)
                db.commit()
                db.refresh(layout)
                logger.info(f"Created layout for plant {plant_id}")
                return layout

        except Exception as e:
            db.rollback()
            logger.error(f"Error saving layout for plant {plant_id}: {e}")
            raise

    @staticmethod
    def delete_layout(db: Session, plant_id: int, tenant_id: str, soft: bool = True) -> bool:
        """Delete plant layout (soft or hard delete)"""
        try:
            layout = (
                db.query(PlantLayout)
                .filter(and_(PlantLayout.plant_id == plant_id, PlantLayout.tenant_id == tenant_id))
                .first()
            )

            if not layout:
                return False

            if soft:
                layout.is_active = False
            else:
                db.delete(layout)

            db.commit()
            logger.info(f"Deleted layout for plant {plant_id} (soft={soft})")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting layout for plant {plant_id}: {e}")
            raise

    @staticmethod
    def generate_layout_from_assets(
        db: Session, plant_id: int, tenant_id: str, user_id: Optional[int] = None
    ) -> PlantLayout:
        """Generate layout from existing plant assets"""
        try:
            from app.models.asset import Asset

            # Get all assets for plant
            assets = (
                db.query(Asset)
                .filter(and_(Asset.plant_id == plant_id, Asset.tenant_id == tenant_id))
                .all()
            )

            # Generate nodes from assets
            nodes = []
            edges = []
            position_x = 100
            position_y = 100
            grid_spacing = 200

            for idx, asset in enumerate(assets):
                # Create node from asset
                node = {
                    "id": f"asset-{asset.id}",
                    "type": asset.component_type or "default",
                    "position": {
                        "x": position_x + (idx % 5) * grid_spacing,
                        "y": position_y + (idx // 5) * grid_spacing,
                    },
                    "data": {
                        "id": str(asset.id),
                        "label": asset.name,
                        "type": asset.component_type or "default",
                        "specs": {
                            "power": asset.power_rating,
                            "efficiency": asset.efficiency,
                        },
                        "status": asset.status.value if asset.status else "active",
                    },
                    "draggable": True,
                    "connectable": True,
                }
                nodes.append(node)

            # Save generated layout
            layout = PlantLayoutService.save_layout(
                db=db,
                plant_id=plant_id,
                nodes=nodes,
                edges=edges,
                tenant_id=tenant_id,
                user_id=user_id,
            )

            logger.info(f"Generated layout from {len(assets)} assets for plant {plant_id}")
            return layout

        except Exception as e:
            logger.error(f"Error generating layout from assets for plant {plant_id}: {e}")
            raise
