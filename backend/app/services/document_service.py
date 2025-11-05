"""
Document Service - Business logic for document management
Consolidated from Kronos EAM
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import logging
import os

from app.models.document import Document, DocumentTypeEnum, DocumentStatusEnum
from app.models.plant import Plant
from app.models.cer import CER

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management"""

    @staticmethod
    def create_document(
        db: Session, document_data: Dict[str, Any], tenant_id: str, user_id: int, file_path: str
    ) -> Document:
        """Create a new document"""
        try:
            # Verify plant if linked
            if document_data.get("plant_id"):
                plant = (
                    db.query(Plant)
                    .filter(
                        and_(
                            Plant.id == document_data["plant_id"],
                            Plant.tenant_id == tenant_id,
                            Plant.deleted_at.is_(None),
                        )
                    )
                    .first()
                )
                if not plant:
                    raise ValueError(f"Plant {document_data['plant_id']} not found")

            # Verify CER if linked
            if document_data.get("cer_id"):
                cer = (
                    db.query(CER)
                    .filter(
                        and_(
                            CER.id == document_data["cer_id"],
                            CER.tenant_id == tenant_id,
                            CER.deleted_at.is_(None),
                        )
                    )
                    .first()
                )
                if not cer:
                    raise ValueError(f"CER {document_data['cer_id']} not found")

            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

            document = Document(
                tenant_id=tenant_id,
                name=document_data["name"],
                description=document_data.get("description"),
                type=document_data.get("type", DocumentTypeEnum.OTHER),
                status=DocumentStatusEnum.DRAFT,
                file_name=document_data["file_name"],
                file_path=file_path,
                file_size=file_size,
                mime_type=document_data.get("mime_type"),
                plant_id=document_data.get("plant_id"),
                cer_id=document_data.get("cer_id"),
                compliance_record_id=document_data.get("compliance_record_id"),
                issue_date=document_data.get("issue_date"),
                expiry_date=document_data.get("expiry_date"),
                upload_date=datetime.utcnow(),
                document_metadata=document_data.get("metadata", {}),
                tags=document_data.get("tags", []),
                version=document_data.get("version", 1),
                parent_document_id=document_data.get("parent_document_id"),
                created_by=user_id,
            )

            db.add(document)
            db.commit()
            db.refresh(document)

            logger.info(f"Created document {document.id}")
            return document

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating document: {e}")
            raise

    @staticmethod
    def get_document(db: Session, document_id: int, tenant_id: str) -> Optional[Document]:
        """Get document by ID"""
        return (
            db.query(Document)
            .filter(
                and_(
                    Document.id == document_id,
                    Document.tenant_id == tenant_id,
                    Document.deleted_at.is_(None),
                )
            )
            .first()
        )

    @staticmethod
    def list_documents(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        plant_id: Optional[int] = None,
        cer_id: Optional[int] = None,
        compliance_record_id: Optional[int] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Document]:
        """List documents"""
        query = db.query(Document).filter(
            and_(Document.tenant_id == tenant_id, Document.deleted_at.is_(None))
        )

        if plant_id:
            query = query.filter(Document.plant_id == plant_id)
        if cer_id:
            query = query.filter(Document.cer_id == cer_id)
        if compliance_record_id:
            query = query.filter(Document.compliance_record_id == compliance_record_id)
        if type:
            query = query.filter(Document.type == type)
        if status:
            query = query.filter(Document.status == status)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_document(
        db: Session, document_id: int, update_data: Dict[str, Any], tenant_id: str, user_id: int
    ) -> Optional[Document]:
        """Update document"""
        document = DocumentService.get_document(db, document_id, tenant_id)
        if not document:
            return None

        for key, value in update_data.items():
            if hasattr(document, key) and key not in ["id", "tenant_id", "created_at"]:
                setattr(document, key, value)

        document.updated_by = user_id
        document.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete_document(db: Session, document_id: int, tenant_id: str, user_id: int) -> bool:
        """Delete document (soft delete)"""
        document = DocumentService.get_document(db, document_id, tenant_id)
        if not document:
            return False

        document.soft_delete(user_id)
        db.commit()
        return True


# Export service instance
document_service = DocumentService()
