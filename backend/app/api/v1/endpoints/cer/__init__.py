"""
CER endpoints - Aggregated router combining all CER sub-modules
Split from monolithic cer.py (1,141 lines) into 6 focused modules

Modules:
- crud.py: CER CRUD operations (5 endpoints)
- members.py: Member management (6 endpoints)
- participation.py: Participation requests (6 endpoints)
- compliance.py: Compliance tracking (3 endpoints)
- documents.py: Document management (6 endpoints)
- plants.py: Plant linking (3 endpoints)
"""

from fastapi import APIRouter

from . import crud, members

# Create main CER router
router = APIRouter()

# Include sub-module routers
router.include_router(crud.router, tags=["cer-crud"])
router.include_router(members.router, tags=["cer-members"])

# Note: Remaining modules (participation, compliance, documents, plants)
# will be added as they are created

__all__ = ["router"]
