"""
Workflow endpoints - Aggregated router combining workflow sub-modules
Split from monolithic workflows.py (561 lines) into 3 focused modules

Modules:
- helpers.py: Serialization helpers (2 functions)
- crud.py: Workflow CRUD operations (5 endpoints)
- templates.py: Template management (6 endpoints)
"""

from fastapi import APIRouter

from . import crud, templates

# Create main workflow router
router = APIRouter()

# Include sub-module routers
router.include_router(crud.router, tags=["workflows"])
router.include_router(templates.router, tags=["workflow-templates"])

__all__ = ["router"]
