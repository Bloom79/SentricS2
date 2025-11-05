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

from . import crud, members, participation, compliance, documents, plants

# Create main CER router
router = APIRouter()

# Include sub-module routers
router.include_router(crud.router, tags=["cer-crud"])
router.include_router(members.router, tags=["cer-members"])
router.include_router(participation.router, tags=["cer-participation"])
router.include_router(compliance.router, tags=["cer-compliance"])
router.include_router(documents.router, tags=["cer-documents"])
router.include_router(plants.router, tags=["cer-plants"])

__all__ = ["router"]
