"""
Plant API endpoints
Enhanced with CER and Asset relationships
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.plant import Plant
from app.schemas.plant import PlantCreate, PlantUpdate, PlantResponse
from app.schemas.plant_layout import PlantLayoutCreate, PlantLayoutResponse
from app.services.plant_service import plant_service
from app.services.plant_layout_service import PlantLayoutService

router = APIRouter()


@router.get("/", response_model=List[PlantResponse])
async def list_plants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    cer_id: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List plants with optional filters"""
    plants = plant_service.list_plants(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        type=type,
        status=status,
        cer_id=cer_id,
        region=region,
    )
    return plants


@router.get("/{plant_id}", response_model=PlantResponse)
async def get_plant(
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get plant details including CER and Assets"""
    plant = plant_service.get_plant(
        db=db, plant_id=plant_id, tenant_id=current_user.tenant_id, include_relations=True
    )

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return plant


@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
async def create_plant(
    plant_data: PlantCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create new plant"""
    try:
        plant = plant_service.create_plant(
            db=db,
            plant_data=plant_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return plant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plant: {str(e)}")


@router.put("/{plant_id}", response_model=PlantResponse)
async def update_plant(
    plant_id: int,
    plant_data: PlantUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update plant"""
    plant = plant_service.update_plant(
        db=db,
        plant_id=plant_id,
        plant_data=plant_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub),
    )

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    return plant


@router.delete("/{plant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant(
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete plant (soft delete)"""
    success = plant_service.delete_plant(
        db=db, plant_id=plant_id, tenant_id=current_user.tenant_id, user_id=int(current_user.sub)
    )

    if not success:
        raise HTTPException(status_code=404, detail="Plant not found")

    return None


@router.get("/{plant_id}/stats")
async def get_plant_stats(
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get plant statistics"""
    stats = plant_service.get_plant_stats(
        db=db, plant_id=plant_id, tenant_id=current_user.tenant_id
    )
    if not stats:
        raise HTTPException(status_code=404, detail="Plant not found")
    return stats


@router.post("/{plant_id}/link-cer/{cer_id}", response_model=PlantResponse)
async def link_plant_to_cer(
    plant_id: int,
    cer_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Link plant to CER"""
    plant = (
        db.query(Plant)
        .filter(Plant.id == plant_id, Plant.tenant_id == current_user.tenant_id)
        .first()
    )

    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    # Verify CER exists and belongs to tenant
    from app.models.cer import CER

    cer = db.query(CER).filter(CER.id == cer_id, CER.tenant_id == current_user.tenant_id).first()

    if not cer:
        raise HTTPException(status_code=404, detail="CER not found")

    plant.cer_id = cer_id
    db.commit()
    db.refresh(plant)
    return plant


# Plant Layout endpoints
@router.get("/{plant_id}/layout", response_model=Optional[PlantLayoutResponse])
async def get_plant_layout(
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get plant layout (React Flow canvas data)"""
    layout = PlantLayoutService.get_layout(
        db=db, plant_id=plant_id, tenant_id=current_user.tenant_id
    )
    if not layout:
        return None
    return PlantLayoutResponse.from_orm(layout)


@router.post("/{plant_id}/layout", response_model=PlantLayoutResponse)
async def save_plant_layout(
    plant_id: int,
    layout_data: PlantLayoutCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Save or update plant layout"""
    try:
        layout = PlantLayoutService.save_layout(
            db=db,
            plant_id=plant_id,
            nodes=layout_data.nodes,
            edges=layout_data.edges,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return PlantLayoutResponse.from_orm(layout)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save layout: {str(e)}")


@router.delete("/{plant_id}/layout", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plant_layout(
    plant_id: int,
    soft: bool = Query(True, description="Soft delete (default) or hard delete"),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete plant layout"""
    success = PlantLayoutService.delete_layout(
        db=db, plant_id=plant_id, tenant_id=current_user.tenant_id, soft=soft
    )
    if not success:
        raise HTTPException(status_code=404, detail="Layout not found")
    return None


@router.post("/{plant_id}/layout/generate-from-assets", response_model=PlantLayoutResponse)
async def generate_layout_from_assets(
    plant_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Generate plant layout from existing assets"""
    try:
        layout = PlantLayoutService.generate_layout_from_assets(
            db=db,
            plant_id=plant_id,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
        )
        return PlantLayoutResponse.from_orm(layout)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate layout: {str(e)}")
