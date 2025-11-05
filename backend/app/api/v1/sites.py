"""
Sites API endpoints
Part of Sites → Plants → Assets hierarchy
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.services.site_service import SiteService
from app.schemas.site import (
    SiteCreate,
    SiteUpdate,
    SiteResponse,
    SiteStatsResponse,
    StorageUnitCreate,
    StorageUnitUpdate,
    StorageUnitResponse,
    ConsumerCreate,
    ConsumerUpdate,
    ConsumerResponse,
    EnergyFlowCreate,
    EnergyFlowUpdate,
    EnergyFlowResponse,
)

router = APIRouter(prefix="/sites", tags=["sites"])


@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Create a new site"""
    try:
        site = SiteService.create_site(
            db=db, site_data=site_data.dict(exclude_unset=True), tenant_id=current_user.tenant_id
        )
        return SiteResponse.from_orm(site)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating site: {str(e)}"
        )


@router.get("", response_model=List[SiteResponse])
async def list_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    site_type: Optional[str] = None,
    region: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """List sites with optional filters"""
    try:
        sites = SiteService.list_sites(
            db=db,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            status=status,
            site_type=site_type,
            region=region,
        )
        return [SiteResponse.from_orm(site) for site in sites]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing sites: {str(e)}",
        )


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get site by ID"""
    site = SiteService.get_site(
        db=db, site_id=site_id, tenant_id=current_user.tenant_id, include_relations=True
    )
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )
    return SiteResponse.from_orm(site)


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Update site"""
    site = SiteService.update_site(
        db=db,
        site_id=site_id,
        site_data=site_data.dict(exclude_unset=True),
        tenant_id=current_user.tenant_id,
    )
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )
    return SiteResponse.from_orm(site)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    soft: bool = Query(True, description="Soft delete (default) or hard delete"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Delete site"""
    success = SiteService.delete_site(
        db=db, site_id=site_id, tenant_id=current_user.tenant_id, soft=soft
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )


@router.get("/{site_id}/stats", response_model=SiteStatsResponse)
async def get_site_stats(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get site statistics"""
    stats = SiteService.get_site_stats(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )
    return SiteStatsResponse(**stats)


# Storage Units endpoints
@router.post(
    "/{site_id}/storage-units",
    response_model=StorageUnitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_storage_unit(
    site_id: int,
    storage_data: StorageUnitCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Create storage unit for a site"""
    # Verify site exists
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    from app.models.site import StorageUnit

    storage_unit = StorageUnit(
        tenant_id=current_user.tenant_id, site_id=site_id, **storage_data.dict(exclude_unset=True)
    )
    db.add(storage_unit)
    db.commit()
    db.refresh(storage_unit)
    return StorageUnitResponse.from_orm(storage_unit)


@router.get("/{site_id}/storage-units", response_model=List[StorageUnitResponse])
async def list_storage_units(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """List storage units for a site"""
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )
    return [StorageUnitResponse.from_orm(su) for su in site.storage_units]


@router.get("/{site_id}/storage-units/{storage_unit_id}", response_model=StorageUnitResponse)
async def get_storage_unit(
    site_id: int,
    storage_unit_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get storage unit by ID"""
    from app.models.site import StorageUnit

    storage_unit = (
        db.query(StorageUnit)
        .filter(
            StorageUnit.id == storage_unit_id,
            StorageUnit.site_id == site_id,
            StorageUnit.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not storage_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Storage unit {storage_unit_id} not found",
        )
    return StorageUnitResponse.from_orm(storage_unit)


@router.put("/{site_id}/storage-units/{storage_unit_id}", response_model=StorageUnitResponse)
async def update_storage_unit(
    site_id: int,
    storage_unit_id: int,
    storage_data: StorageUnitUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Update storage unit"""
    from app.models.site import StorageUnit

    storage_unit = (
        db.query(StorageUnit)
        .filter(
            StorageUnit.id == storage_unit_id,
            StorageUnit.site_id == site_id,
            StorageUnit.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not storage_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Storage unit {storage_unit_id} not found",
        )

    # Update fields
    update_data = storage_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(storage_unit, field):
            setattr(storage_unit, field, value)

    db.commit()
    db.refresh(storage_unit)
    return StorageUnitResponse.from_orm(storage_unit)


@router.delete("/{site_id}/storage-units/{storage_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_storage_unit(
    site_id: int,
    storage_unit_id: int,
    soft: bool = Query(True, description="Soft delete (default) or hard delete"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Delete storage unit"""
    from app.models.site import StorageUnit

    storage_unit = (
        db.query(StorageUnit)
        .filter(
            StorageUnit.id == storage_unit_id,
            StorageUnit.site_id == site_id,
            StorageUnit.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not storage_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Storage unit {storage_unit_id} not found",
        )

    if soft:
        storage_unit.soft_delete(user_id=int(current_user.sub))
    else:
        db.delete(storage_unit)

    db.commit()


# Consumers endpoints
@router.post(
    "/{site_id}/consumers", response_model=ConsumerResponse, status_code=status.HTTP_201_CREATED
)
async def create_consumer(
    site_id: int,
    consumer_data: ConsumerCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Create consumer for a site"""
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    from app.models.site import Consumer

    consumer = Consumer(
        tenant_id=current_user.tenant_id, site_id=site_id, **consumer_data.dict(exclude_unset=True)
    )
    db.add(consumer)
    db.commit()
    db.refresh(consumer)
    return ConsumerResponse.from_orm(consumer)


@router.get("/{site_id}/consumers", response_model=List[ConsumerResponse])
async def list_consumers(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """List consumers for a site"""
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )
    return [ConsumerResponse.from_orm(c) for c in site.consumers]


@router.get("/{site_id}/consumers/{consumer_id}", response_model=ConsumerResponse)
async def get_consumer(
    site_id: int,
    consumer_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get consumer by ID"""
    from app.models.site import Consumer

    consumer = (
        db.query(Consumer)
        .filter(
            Consumer.id == consumer_id,
            Consumer.site_id == site_id,
            Consumer.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Consumer {consumer_id} not found"
        )
    return ConsumerResponse.from_orm(consumer)


@router.put("/{site_id}/consumers/{consumer_id}", response_model=ConsumerResponse)
async def update_consumer(
    site_id: int,
    consumer_id: int,
    consumer_data: ConsumerUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Update consumer"""
    from app.models.site import Consumer

    consumer = (
        db.query(Consumer)
        .filter(
            Consumer.id == consumer_id,
            Consumer.site_id == site_id,
            Consumer.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Consumer {consumer_id} not found"
        )

    # Update fields
    update_data = consumer_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(consumer, field):
            setattr(consumer, field, value)

    db.commit()
    db.refresh(consumer)
    return ConsumerResponse.from_orm(consumer)


@router.delete("/{site_id}/consumers/{consumer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consumer(
    site_id: int,
    consumer_id: int,
    soft: bool = Query(True, description="Soft delete (default) or hard delete"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Delete consumer"""
    from app.models.site import Consumer

    consumer = (
        db.query(Consumer)
        .filter(
            Consumer.id == consumer_id,
            Consumer.site_id == site_id,
            Consumer.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not consumer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Consumer {consumer_id} not found"
        )

    if soft:
        consumer.soft_delete(user_id=int(current_user.sub))
    else:
        db.delete(consumer)

    db.commit()


# Energy Flow endpoints
@router.get("/{site_id}/energy-flow", response_model=Optional[EnergyFlowResponse])
async def get_site_energy_flow(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get active energy flow layout for a site"""
    # Verify site exists
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    energy_flow = SiteService.get_site_energy_flow(
        db=db, site_id=site_id, tenant_id=current_user.tenant_id
    )
    if not energy_flow:
        return None
    return EnergyFlowResponse.from_orm(energy_flow)


@router.get("/{site_id}/energy-flow/{energy_flow_id}", response_model=EnergyFlowResponse)
async def get_energy_flow_by_id(
    site_id: int,
    energy_flow_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Get energy flow by ID"""
    from app.models.site import EnergyFlow

    # Verify site exists
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    energy_flow = (
        db.query(EnergyFlow)
        .filter(
            EnergyFlow.id == energy_flow_id,
            EnergyFlow.site_id == site_id,
            EnergyFlow.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not energy_flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Energy flow {energy_flow_id} not found"
        )

    return EnergyFlowResponse.from_orm(energy_flow)


@router.post("/{site_id}/energy-flow", response_model=EnergyFlowResponse)
async def save_site_energy_flow(
    site_id: int,
    energy_flow_data: EnergyFlowCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Save energy flow layout for a site (creates or updates active flow)"""
    # Verify site exists
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    energy_flow = SiteService.save_site_energy_flow(
        db=db,
        site_id=site_id,
        nodes=energy_flow_data.nodes,
        edges=energy_flow_data.edges,
        tenant_id=current_user.tenant_id,
        description=energy_flow_data.description,
    )
    return EnergyFlowResponse.from_orm(energy_flow)


@router.put("/{site_id}/energy-flow/{energy_flow_id}", response_model=EnergyFlowResponse)
async def update_site_energy_flow(
    site_id: int,
    energy_flow_id: int,
    energy_flow_data: EnergyFlowUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Update energy flow layout for a site"""
    from app.models.site import EnergyFlow

    # Verify site exists
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    energy_flow = (
        db.query(EnergyFlow)
        .filter(
            EnergyFlow.id == energy_flow_id,
            EnergyFlow.site_id == site_id,
            EnergyFlow.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not energy_flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Energy flow {energy_flow_id} not found"
        )

    # Update fields
    update_data = energy_flow_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(energy_flow, field):
            setattr(energy_flow, field, value)

    db.commit()
    db.refresh(energy_flow)
    return EnergyFlowResponse.from_orm(energy_flow)


@router.delete("/{site_id}/energy-flow/{energy_flow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site_energy_flow(
    site_id: int,
    energy_flow_id: int,
    soft: bool = Query(True, description="Soft delete (deactivate) or hard delete"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_active_user),
):
    """Delete energy flow layout for a site"""
    from app.models.site import EnergyFlow

    # Verify site exists
    site = SiteService.get_site(db=db, site_id=site_id, tenant_id=current_user.tenant_id)
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    energy_flow = (
        db.query(EnergyFlow)
        .filter(
            EnergyFlow.id == energy_flow_id,
            EnergyFlow.site_id == site_id,
            EnergyFlow.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not energy_flow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Energy flow {energy_flow_id} not found"
        )

    if soft:
        # Deactivate instead of soft delete (since EnergyFlow uses is_active flag)
        energy_flow.is_active = False
    else:
        db.delete(energy_flow)

    db.commit()
