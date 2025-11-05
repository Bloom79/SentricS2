"""
Plant Layout model for visual plant designer
Stores React Flow nodes and edges as JSON
"""

from sqlalchemy import Column, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class PlantLayout(BaseModel):
    """Plant visual layout model - React Flow canvas data"""

    __tablename__ = "plant_layouts"

    # One-to-one relationship with Plant
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False, unique=True, index=True)

    # React Flow data (stored as JSON)
    nodes = Column(JSON, nullable=False, default=list)  # List of React Flow nodes
    edges = Column(JSON, nullable=False, default=list)  # List of React Flow edges

    # Metadata
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    plant = relationship("Plant", back_populates="layout", uselist=False)

    def __repr__(self):
        return f"<PlantLayout plant_id={self.plant_id} version={self.version}>"

    def to_dict(self) -> dict:
        """Convert layout to dictionary"""
        return {
            "id": self.id,
            "plant_id": self.plant_id,
            "tenant_id": self.tenant_id,
            "nodes": self.nodes,
            "edges": self.edges,
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
