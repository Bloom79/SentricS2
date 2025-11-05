"""
Asset endpoints - Aggregated router combining asset sub-modules
Split from monolithic assets.py (411 lines) into 5 focused modules

Modules:
- helpers.py: Helper functions (1 function)
- types.py: Asset type management (2 endpoints)
- crud.py: Asset CRUD operations (5 endpoints)
- strings.py: String configuration (6 endpoints)
- bulk.py: Bulk import operations (2 endpoints)
"""

from fastapi import APIRouter

from . import types, crud, strings, bulk

# Create main assets router
router = APIRouter()

# Include sub-module routers
router.include_router(types.router, tags=["assets"])
router.include_router(crud.router, tags=["assets"])
router.include_router(strings.router, tags=["assets-strings"])
router.include_router(bulk.router, tags=["assets-bulk"])

__all__ = ["router"]
