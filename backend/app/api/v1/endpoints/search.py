"""
Global Search API
Search across all modules (plants, CER, assets, workflows, documents, compliance)
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.models.plant import Plant
from app.models.cer import CER
from app.models.asset import Asset
from app.models.workflow import Workflow
from app.models.document import Document
from app.models.compliance import ComplianceRecord
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/global")
async def global_search(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results to return"),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Global search across all modules
    Returns unified results from plants, CERs, assets, workflows, documents, and compliance
    """
    try:
        results = []
        search_term = f"%{q}%"

        # Search Plants
        plants = db.query(Plant).filter(
            and_(
                Plant.tenant_id == current_user.tenant_id,
                Plant.deleted_at.is_(None),
                or_(
                    Plant.name.ilike(search_term),
                    Plant.code.ilike(search_term),
                    Plant.location.ilike(search_term)
                )
            )
        ).limit(limit // 6).all()

        for plant in plants:
            results.append({
                "id": plant.id,
                "type": "plant",
                "title": plant.name,
                "subtitle": f"{plant.code} • {plant.location or 'No location'}",
                "status": plant.status.value if hasattr(plant.status, 'value') else str(plant.status),
                "url": f"/plants/{plant.id}"
            })

        # Search CERs
        cers = db.query(CER).filter(
            and_(
                CER.tenant_id == current_user.tenant_id,
                CER.deleted_at.is_(None),
                or_(
                    CER.name.ilike(search_term),
                    CER.code.ilike(search_term),
                    CER.legal_name.ilike(search_term)
                )
            )
        ).limit(limit // 6).all()

        for cer in cers:
            results.append({
                "id": cer.id,
                "type": "cer",
                "title": cer.name,
                "subtitle": f"{cer.code} • {len(cer.members or [])} members",
                "status": cer.status.value if hasattr(cer.status, 'value') else str(cer.status),
                "url": f"/cer/{cer.id}"
            })

        # Search Assets
        assets = db.query(Asset).filter(
            and_(
                Asset.tenant_id == current_user.tenant_id,
                Asset.deleted_at.is_(None),
                or_(
                    Asset.name.ilike(search_term),
                    Asset.code.ilike(search_term),
                    Asset.manufacturer.ilike(search_term)
                )
            )
        ).limit(limit // 6).all()

        for asset in assets:
            results.append({
                "id": asset.id,
                "type": "asset",
                "title": asset.name,
                "subtitle": f"{asset.manufacturer or 'Unknown'} • {asset.model or ''}",
                "status": asset.status.value if hasattr(asset.status, 'value') else str(asset.status),
                "url": f"/assets/{asset.id}"
            })

        # Search Workflows
        workflows = db.query(Workflow).filter(
            and_(
                Workflow.tenant_id == current_user.tenant_id,
                Workflow.deleted_at.is_(None),
                or_(
                    Workflow.name.ilike(search_term),
                    Workflow.description.ilike(search_term)
                )
            )
        ).limit(limit // 6).all()

        for workflow in workflows:
            results.append({
                "id": workflow.id,
                "type": "workflow",
                "title": workflow.name,
                "subtitle": workflow.type or "Workflow",
                "status": workflow.status.value if hasattr(workflow.status, 'value') else str(workflow.status),
                "url": f"/workflows/{workflow.id}"
            })

        # Search Documents
        documents = db.query(Document).filter(
            and_(
                Document.tenant_id == current_user.tenant_id,
                Document.deleted_at.is_(None),
                or_(
                    Document.name.ilike(search_term),
                    Document.document_type.ilike(search_term)
                )
            )
        ).limit(limit // 6).all()

        for doc in documents:
            results.append({
                "id": doc.id,
                "type": "document",
                "title": doc.name,
                "subtitle": doc.document_type or "Document",
                "status": doc.status or "Active",
                "url": f"/documents/{doc.id}"
            })

        # Search Compliance
        compliance_records = db.query(ComplianceRecord).filter(
            and_(
                ComplianceRecord.tenant_id == current_user.tenant_id,
                ComplianceRecord.deleted_at.is_(None),
                or_(
                    ComplianceRecord.requirement_name.ilike(search_term),
                    ComplianceRecord.description.ilike(search_term)
                )
            )
        ).limit(limit // 6).all()

        for comp in compliance_records:
            results.append({
                "id": comp.id,
                "type": "compliance",
                "title": comp.requirement_name,
                "subtitle": f"{comp.authority or 'Unknown'} • Due {comp.due_date.strftime('%Y-%m-%d') if comp.due_date else 'N/A'}",
                "status": comp.status.value if hasattr(comp.status, 'value') else str(comp.status),
                "url": f"/compliance/{comp.id}"
            })

        # Limit total results
        results = results[:limit]

        return {
            "query": q,
            "total": len(results),
            "results": results
        }

    except Exception as e:
        logger.error(f"Global search error: {e}", exc_info=True)
        return {
            "query": q,
            "total": 0,
            "results": [],
            "error": "Search failed"
        }
