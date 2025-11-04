"""
Document endpoints
Consolidated from Kronos EAM
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.core.security import get_current_active_user, TokenData
from app.core.config import settings
from app.services.document_service import document_service

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    plant_id: Optional[int] = Query(None),
    cer_id: Optional[int] = Query(None),
    compliance_record_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List documents"""
    from app.models.plant import Plant
    from app.models.cer import CER
    from datetime import datetime
    
    documents = document_service.list_documents(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        plant_id=plant_id,
        cer_id=cer_id,
        compliance_record_id=compliance_record_id,
        type=type,
        status=status
    )
    
    # Enrich documents with related entity information
    result = []
    for doc in documents:
        doc_dict = {
            "id": doc.id,
            "name": doc.name,
            "description": doc.description,
            "type": doc.type.value if hasattr(doc.type, 'value') else str(doc.type),
            "status": doc.status.value if hasattr(doc.status, 'value') else str(doc.status),
            "file_name": doc.file_name,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "plant_id": doc.plant_id,
            "cer_id": doc.cer_id,
            "compliance_record_id": doc.compliance_record_id,
            "issue_date": doc.issue_date.isoformat() if doc.issue_date else None,
            "expiry_date": doc.expiry_date.isoformat() if doc.expiry_date else None,
            "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
            "tags": doc.tags or [],
            "version": doc.version,
        }
        
        # Add plant name if linked
        if doc.plant_id:
            plant = db.query(Plant).filter(Plant.id == doc.plant_id).first()
            if plant:
                doc_dict["plant_name"] = plant.name
        
        # Add CER name if linked
        if doc.cer_id:
            cer = db.query(CER).filter(CER.id == doc.cer_id).first()
            if cer:
                doc_dict["cer_name"] = cer.name
        
        # Calculate expiry status
        if doc.expiry_date:
            delta = doc.expiry_date - datetime.utcnow()
            doc_dict["days_until_expiry"] = delta.days
            doc_dict["is_expired"] = delta.days < 0
        
        result.append(doc_dict)
    
    return result


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document details"""
    document = document_service.get_document(db, document_id, current_user.tenant_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document(
    file: UploadFile = File(...),
    name: str = Query(...),
    plant_id: Optional[int] = Query(None),
    cer_id: Optional[int] = Query(None),
    compliance_record_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    issue_date: Optional[str] = Query(None),
    expiry_date: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and create document"""
    try:
        from datetime import datetime
        
        # Save file
        upload_dir = os.path.join(settings.UPLOAD_DIR, current_user.tenant_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Parse dates if provided
        parsed_issue_date = None
        parsed_expiry_date = None
        if issue_date:
            try:
                parsed_issue_date = datetime.fromisoformat(issue_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    parsed_issue_date = datetime.strptime(issue_date, '%Y-%m-%d')
                except ValueError:
                    pass
        
        if expiry_date:
            try:
                parsed_expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            except ValueError:
                try:
                    parsed_expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')
                except ValueError:
                    pass
        
        document_data = {
            "name": name,
            "description": description,
            "type": type or "Other",
            "file_name": file.filename,
            "mime_type": file.content_type,
            "plant_id": plant_id,
            "cer_id": cer_id,
            "compliance_record_id": compliance_record_id,
            "issue_date": parsed_issue_date,
            "expiry_date": parsed_expiry_date,
        }
        
        document = document_service.create_document(
            db=db,
            document_data=document_data,
            tenant_id=current_user.tenant_id,
            user_id=int(current_user.sub),
            file_path=file_path
        )
        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")


@router.put("/{document_id}", response_model=dict)
async def update_document(
    document_id: int,
    update_data: dict,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update document"""
    from datetime import datetime
    
    # Parse dates if provided as strings
    if 'issue_date' in update_data and isinstance(update_data['issue_date'], str):
        try:
            update_data['issue_date'] = datetime.fromisoformat(update_data['issue_date'].replace('Z', '+00:00'))
        except ValueError:
            try:
                update_data['issue_date'] = datetime.strptime(update_data['issue_date'], '%Y-%m-%d')
            except ValueError:
                update_data['issue_date'] = None
    
    if 'expiry_date' in update_data and isinstance(update_data['expiry_date'], str):
        try:
            update_data['expiry_date'] = datetime.fromisoformat(update_data['expiry_date'].replace('Z', '+00:00'))
        except ValueError:
            try:
                update_data['expiry_date'] = datetime.strptime(update_data['expiry_date'], '%Y-%m-%d')
            except ValueError:
                update_data['expiry_date'] = None
    
    document = document_service.update_document(
        db=db,
        document_id=document_id,
        update_data=update_data,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub)
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download document file"""
    document = document_service.get_document(db, document_id, current_user.tenant_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        document.file_path,
        media_type=document.mime_type or 'application/octet-stream',
        filename=document.file_name
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete document"""
    success = document_service.delete_document(
        db=db,
        document_id=document_id,
        tenant_id=current_user.tenant_id,
        user_id=int(current_user.sub)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return None

