"""
Services module
"""

from app.services.plant_service import plant_service, PlantService
from app.services.cer_service import cer_service, CERService
from app.services.asset_service import asset_service, AssetService
from app.services.workflow_service import workflow_service, WorkflowService
from app.services.document_service import document_service, DocumentService
from app.services.compliance_service import compliance_service, ComplianceService
from app.services.dashboard_service import dashboard_service, DashboardService

__all__ = [
    "plant_service",
    "PlantService",
    "cer_service",
    "CERService",
    "asset_service",
    "AssetService",
    "workflow_service",
    "WorkflowService",
    "document_service",
    "DocumentService",
    "compliance_service",
    "ComplianceService",
    "dashboard_service",
    "DashboardService",
]

