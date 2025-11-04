"""
Document models
Consolidated from Kronos EAM
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum

from app.models.base import BaseModel


class DocumentTypeEnum(str, enum.Enum):
    """Document types"""
    CERTIFICATE = "Certificate"
    PERMIT = "Permit"
    CONTRACT = "Contract"
    REPORT = "Report"
    INVOICE = "Invoice"
    LICENSE = "License"
    OTHER = "Other"


class DocumentStatusEnum(str, enum.Enum):
    """Document status"""
    DRAFT = "Draft"
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    EXPIRED = "Expired"


class Document(BaseModel):
    """Document model"""
    __tablename__ = "documents"
    
    # Basic info
    name = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(DocumentTypeEnum), nullable=False)
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.DRAFT)
    
    # File info
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer)  # in bytes
    mime_type = Column(String(100))
    
    # Entity relationships (can be linked to Plant, CER, or Compliance)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    cer_id = Column(Integer, ForeignKey("cer_configuration.id"), nullable=True)
    compliance_record_id = Column(Integer, ForeignKey("compliance_records.id"), nullable=True)
    
    # Dates
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    upload_date = Column(DateTime)
    
    # Metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word conflict)
    document_metadata = Column(JSON, default=dict)
    tags = Column(JSON, default=list)
    
    # Versioning
    version = Column(Integer, default=1)
    parent_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    
    # Relationships
    plant = relationship("Plant", back_populates="documents")
    cer = relationship("CER", back_populates="documents")
    compliance_record = relationship("ComplianceRecord", back_populates="documents")
    parent = relationship("Document", remote_side="Document.id", backref="versions")
    
    def __repr__(self):
        return f"<Document {self.name} ({self.type})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        from datetime import datetime
        return datetime.utcnow() > self.expiry_date
    
    @property
    def days_until_expiry(self) -> int:
        """Get days until expiry"""
        if not self.expiry_date:
            return None
        from datetime import datetime
        delta = self.expiry_date - datetime.utcnow()
        return delta.days

