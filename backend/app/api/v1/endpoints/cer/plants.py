"""
CER Plant Linking endpoints - Managing plant-CER relationships
Split from monolithic cer.py for better maintainability
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.cer_service import cer_service
from app.schemas.plant import PlantResponse

logger = logging.getLogger(__name__)
router = APIRouter()


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
