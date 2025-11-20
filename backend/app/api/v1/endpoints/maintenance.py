"""
Maintenance Management API
Endpoints for scheduling and managing maintenance tasks
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.base import BaseModel as DBBaseModel
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum
import enum

logger = logging.getLogger(__name__)

router = APIRouter()


# Enums
class MaintenanceType(str, enum.Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    INSPECTION = "inspection"


class MaintenanceStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenancePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Model (inline for now, should be in app/models/maintenance.py)
class MaintenanceTask(DBBaseModel):
    """Maintenance task model"""
    __tablename__ = "maintenance_tasks"

    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    plant_id = Column(Integer)
    asset_id = Column(Integer)
    type = Column(Enum(MaintenanceType), nullable=False, default=MaintenanceType.PREVENTIVE)
    status = Column(Enum(MaintenanceStatus), nullable=False, default=MaintenanceStatus.SCHEDULED)
    priority = Column(Enum(MaintenancePriority), nullable=False, default=MaintenancePriority.MEDIUM)
    scheduled_date = Column(DateTime, nullable=False)
    completed_date = Column(DateTime)
    assigned_to = Column(Integer)  # User ID
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    cost_estimate = Column(Float)
    actual_cost = Column(Float)
    notes = Column(String(2000))
    recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50))  # e.g., "monthly", "quarterly"
    next_occurrence = Column(DateTime)


# Schemas
class MaintenanceTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    plant_id: Optional[int] = None
    asset_id: Optional[int] = None
    type: MaintenanceType = MaintenanceType.PREVENTIVE
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    scheduled_date: datetime
    estimated_hours: Optional[float] = None
    cost_estimate: Optional[float] = None
    recurring: bool = False
    recurrence_pattern: Optional[str] = None


class MaintenanceTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[MaintenanceStatus] = None
    priority: Optional[MaintenancePriority] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    actual_hours: Optional[float] = None
    actual_cost: Optional[float] = None
    notes: Optional[str] = None


class MaintenanceTaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    plant_id: Optional[int]
    plant_name: Optional[str]
    asset_id: Optional[int]
    asset_name: Optional[str]
    type: MaintenanceType
    status: MaintenanceStatus
    priority: MaintenancePriority
    scheduled_date: datetime
    completed_date: Optional[datetime]
    assigned_to: Optional[int]
    technician_name: Optional[str]
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    cost_estimate: Optional[float]
    actual_cost: Optional[float]
    notes: Optional[str]
    recurring: bool
    recurrence_pattern: Optional[str]
    next_occurrence: Optional[datetime]

    class Config:
        from_attributes = True


# Endpoints
@router.get("/tasks", response_model=List[MaintenanceTaskResponse])
async def list_maintenance_tasks(
    status: Optional[MaintenanceStatus] = None,
    priority: Optional[MaintenancePriority] = None,
    plant_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List maintenance tasks with optional filters"""
    try:
        query = db.query(MaintenanceTask).filter(
            and_(
                MaintenanceTask.tenant_id == current_user.tenant_id,
                MaintenanceTask.deleted_at.is_(None)
            )
        )

        if status:
            query = query.filter(MaintenanceTask.status == status)
        if priority:
            query = query.filter(MaintenanceTask.priority == priority)
        if plant_id:
            query = query.filter(MaintenanceTask.plant_id == plant_id)

        tasks = query.order_by(MaintenanceTask.scheduled_date).offset(skip).limit(limit).all()

        # Enrich with related data (plant names, etc.)
        result = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "plant_id": task.plant_id,
                "plant_name": None,  # TODO: Join with Plant model
                "asset_id": task.asset_id,
                "asset_name": None,  # TODO: Join with Asset model
                "type": task.type,
                "status": task.status,
                "priority": task.priority,
                "scheduled_date": task.scheduled_date,
                "completed_date": task.completed_date,
                "assigned_to": task.assigned_to,
                "technician_name": None,  # TODO: Join with User model
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "cost_estimate": task.cost_estimate,
                "actual_cost": task.actual_cost,
                "notes": task.notes,
                "recurring": task.recurring,
                "recurrence_pattern": task.recurrence_pattern,
                "next_occurrence": task.next_occurrence,
            }
            result.append(task_dict)

        return result

    except Exception as e:
        logger.error(f"Error listing maintenance tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list maintenance tasks")


@router.post("/tasks", response_model=MaintenanceTaskResponse, status_code=201)
async def create_maintenance_task(
    task_data: MaintenanceTaskCreate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new maintenance task"""
    try:
        task = MaintenanceTask(
            **task_data.model_dump(),
            tenant_id=current_user.tenant_id,
            created_by=int(current_user.sub)
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "plant_id": task.plant_id,
            "plant_name": None,
            "asset_id": task.asset_id,
            "asset_name": None,
            "type": task.type,
            "status": task.status,
            "priority": task.priority,
            "scheduled_date": task.scheduled_date,
            "completed_date": task.completed_date,
            "assigned_to": task.assigned_to,
            "technician_name": None,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "cost_estimate": task.cost_estimate,
            "actual_cost": task.actual_cost,
            "notes": task.notes,
            "recurring": task.recurring,
            "recurrence_pattern": task.recurrence_pattern,
            "next_occurrence": task.next_occurrence,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating maintenance task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create maintenance task")


@router.patch("/tasks/{task_id}", response_model=MaintenanceTaskResponse)
async def update_maintenance_task(
    task_id: int,
    task_update: MaintenanceTaskUpdate,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a maintenance task"""
    try:
        task = db.query(MaintenanceTask).filter(
            and_(
                MaintenanceTask.id == task_id,
                MaintenanceTask.tenant_id == current_user.tenant_id,
                MaintenanceTask.deleted_at.is_(None)
            )
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Maintenance task not found")

        # Update fields
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        db.commit()
        db.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "plant_id": task.plant_id,
            "plant_name": None,
            "asset_id": task.asset_id,
            "asset_name": None,
            "type": task.type,
            "status": task.status,
            "priority": task.priority,
            "scheduled_date": task.scheduled_date,
            "completed_date": task.completed_date,
            "assigned_to": task.assigned_to,
            "technician_name": None,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "cost_estimate": task.cost_estimate,
            "actual_cost": task.actual_cost,
            "notes": task.notes,
            "recurring": task.recurring,
            "recurrence_pattern": task.recurrence_pattern,
            "next_occurrence": task.next_occurrence,
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating maintenance task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update maintenance task")


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_maintenance_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete (soft delete) a maintenance task"""
    try:
        task = db.query(MaintenanceTask).filter(
            and_(
                MaintenanceTask.id == task_id,
                MaintenanceTask.tenant_id == current_user.tenant_id,
                MaintenanceTask.deleted_at.is_(None)
            )
        ).first()

        if not task:
            raise HTTPException(status_code=404, detail="Maintenance task not found")

        task.deleted_at = datetime.utcnow()
        db.commit()

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting maintenance task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete maintenance task")
