"""
Workflow phase endpoints - Aggregated router combining phase sub-modules
Split from monolithic workflow_phases.py (481 lines) into 3 focused modules

Modules:
- details.py: Phase details (1 endpoint)
- updates.py: Status and assignment updates (2 endpoints)
- attachments.py: Documents and comments (2 endpoints)
"""

from fastapi import APIRouter

from . import details, updates, attachments

# Create main workflow phases router
router = APIRouter()

# Include sub-module routers
router.include_router(details.router, tags=["workflow-phases"])
router.include_router(updates.router, tags=["workflow-phases"])
router.include_router(attachments.router, tags=["workflow-phases"])

__all__ = ["router"]
