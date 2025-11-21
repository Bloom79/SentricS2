"""
API Router - Consolidated endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    plants,
    cer,
    cer_energy,
    assets,
    workflows,
    workflow_phases,
    documents,
    compliance,
    dashboard,
    energy,
    billing,
    search,
    maintenance,
    plant_performance,
    italian_cer,
)
from app.api.v1 import sites
from app.core.config import settings

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Development endpoints (only in development mode)
# Always register the router, but endpoints check ENVIRONMENT at runtime
try:
    from app.api.v1.endpoints import dev
    api_router.include_router(dev.router, prefix="/dev", tags=["development"])
except ImportError:
    pass  # Dev module might not exist

# Sites (must be before plants as sites contain plants)
api_router.include_router(sites.router, tags=["sites"])

# Plants
api_router.include_router(plants.router, prefix="/plants", tags=["plants"])
api_router.include_router(plant_performance.router, prefix="/plants", tags=["plant-performance"])

# CER (Renewable Energy Communities)
api_router.include_router(cer.router, prefix="/cer", tags=["cer"])

# CER Energy Sharing (NEW - Core CER Business Logic)
api_router.include_router(cer_energy.router, tags=["cer-energy"])

# Italian CER Regulatory Services (GSE, Terna, Tax, Compliance)
api_router.include_router(italian_cer.router, prefix="/cer/italian", tags=["italian-cer"])

# Energy (CER Energy Sharing)
api_router.include_router(energy.router, tags=["energy"])

# Billing (CER Billing & Financial)
api_router.include_router(billing.router, tags=["billing"])

# Assets
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])

# Workflows
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(workflow_phases.router, prefix="/workflows", tags=["workflow-phases"])

# Documents
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# Compliance
api_router.include_router(compliance.router, prefix="/compliance", tags=["compliance"])

# Dashboard
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

# Search (Global Search)
api_router.include_router(search.router, prefix="/search", tags=["search"])

# Maintenance
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])

