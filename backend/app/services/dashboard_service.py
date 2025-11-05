"""
Dashboard Service - Business logic for dashboard analytics
Consolidated from Kronos EAM
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import logging

from app.models.plant import Plant, PlantStatusEnum
from app.models.cer import CER
from app.models.asset import Asset
from app.models.workflow import Workflow, WorkflowStatusEnum
from app.models.compliance import ComplianceRecord, ComplianceStatusEnum
from app.models.document import Document

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for dashboard analytics"""

    @staticmethod
    def get_dashboard_stats(db: Session, tenant_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics - Optimized with batch queries"""
        from sqlalchemy import case

        base_filter = lambda model: and_(model.tenant_id == tenant_id, model.deleted_at.is_(None))

        # Optimized: Single query for plant stats using CASE statements
        plant_stats = (
            db.query(
                func.count(Plant.id).label("total"),
                func.sum(case((Plant.status == PlantStatusEnum.IN_OPERATION, 1), else_=0)).label(
                    "active"
                ),
                func.sum(Plant.power_kw).label("total_capacity"),
            )
            .filter(base_filter(Plant))
            .first()
        )

        total_plants = plant_stats.total or 0
        active_plants = plant_stats.active or 0
        total_capacity = float(plant_stats.total_capacity or 0.0)

        # Optimized: Single query for CER stats
        cer_stats = (
            db.query(
                func.count(CER.id).label("total"),
                func.sum(case((CER.status == "active", 1), else_=0)).label("active"),
            )
            .filter(base_filter(CER))
            .first()
        )

        total_cer = cer_stats.total or 0
        active_cer = cer_stats.active or 0

        # Optimized: Single query for asset stats
        asset_stats = (
            db.query(
                func.count(Asset.id).label("total"),
                func.sum(case((Asset.status == "operational", 1), else_=0)).label("operational"),
            )
            .filter(base_filter(Asset))
            .first()
        )

        total_assets = asset_stats.total or 0
        operational_assets = asset_stats.operational or 0

        # Optimized: Single query for workflow stats
        workflow_stats = (
            db.query(
                func.count(Workflow.id).label("total"),
                func.sum(
                    case((Workflow.status == WorkflowStatusEnum.IN_PROGRESS, 1), else_=0)
                ).label("active"),
            )
            .filter(base_filter(Workflow))
            .first()
        )

        total_workflows = workflow_stats.total or 0
        active_workflows = workflow_stats.active or 0

        # Fixed: Compliance statistics query
        overdue_compliance = (
            db.query(func.count(ComplianceRecord.id))
            .filter(
                and_(
                    ComplianceRecord.tenant_id == tenant_id,
                    ComplianceRecord.status != ComplianceStatusEnum.COMPLETED,
                    ComplianceRecord.due_date < datetime.utcnow(),
                    ComplianceRecord.deleted_at.is_(None),
                )
            )
            .scalar()
            or 0
        )

        # Optimized: Single query for document stats
        doc_stats = (
            db.query(
                func.count(Document.id).label("total"),
                func.sum(
                    case(
                        (
                            and_(
                                Document.expiry_date.isnot(None),
                                Document.expiry_date > datetime.utcnow(),
                                Document.expiry_date <= datetime.utcnow() + timedelta(days=30),
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("expiring_soon"),
            )
            .filter(base_filter(Document))
            .first()
        )

        total_documents = doc_stats.total or 0
        expiring_documents = doc_stats.expiring_soon or 0

        return {
            "plants": {
                "total": total_plants,
                "active": active_plants,
                "total_capacity_kw": float(total_capacity),
            },
            "cer": {
                "total": total_cer,
                "active": active_cer,
            },
            "assets": {
                "total": total_assets,
                "operational": operational_assets,
            },
            "workflows": {
                "total": total_workflows,
                "active": active_workflows,
            },
            "compliance": {
                "overdue": overdue_compliance,
            },
            "documents": {
                "total": total_documents,
                "expiring_soon": expiring_documents,
            },
        }

    @staticmethod
    def get_recent_activity(db: Session, tenant_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity across all modules"""
        activities = []

        # Recent plants
        recent_plants = (
            db.query(Plant)
            .filter(and_(Plant.tenant_id == tenant_id, Plant.deleted_at.is_(None)))
            .order_by(Plant.created_at.desc())
            .limit(limit)
            .all()
        )

        for plant in recent_plants:
            activities.append(
                {
                    "type": "plant",
                    "id": plant.id,
                    "name": plant.name,
                    "action": "created",
                    "date": plant.created_at.isoformat() if plant.created_at else None,
                }
            )

        # Recent workflows
        recent_workflows = (
            db.query(Workflow)
            .filter(and_(Workflow.tenant_id == tenant_id, Workflow.deleted_at.is_(None)))
            .order_by(Workflow.created_at.desc())
            .limit(limit)
            .all()
        )

        for workflow in recent_workflows:
            activities.append(
                {
                    "type": "workflow",
                    "id": workflow.id,
                    "name": workflow.name,
                    "action": "created",
                    "date": workflow.created_at.isoformat() if workflow.created_at else None,
                }
            )

        # Sort by date and return top N
        activities.sort(key=lambda x: x["date"] or "", reverse=True)
        return activities[:limit]


# Export service instance
dashboard_service = DashboardService()
