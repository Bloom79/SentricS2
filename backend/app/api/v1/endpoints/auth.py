"""
Authentication endpoints
Consolidated from Kronos EAM
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    TokenData,
)
from app.core.rate_limiter import limiter, get_rate_limit
from app.schemas.auth import Token, UserResponse
from app.core.config import settings
from datetime import timedelta

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit(get_rate_limit("auth"))
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint - Rate limited to prevent brute force attacks"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token with user data
    token_data = {
        "sub": str(user.id),
        "tenant_id": user.tenant_id,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "permissions": user.permissions or [],
    }
    
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "tenant_id": user.tenant_id,
            "permissions": user.permissions or [],
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    from app.models.user import User
    user = db.query(User).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    request: Request,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    language: Optional[str] = None,
    timezone: Optional[str] = None,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    from app.models.user import User
    from app.core.audit import log_audit_event

    user = db.query(User).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Store old values for audit
    old_values = {
        "name": user.name,
        "phone": user.phone,
        "language": user.language,
        "timezone": user.timezone
    }

    # Update fields
    if name is not None:
        user.name = name
    if phone is not None:
        user.phone = phone
    if language is not None:
        user.language = language
    if timezone is not None:
        user.timezone = timezone

    try:
        db.commit()
        db.refresh(user)

        # Log audit event
        new_values = {
            "name": user.name,
            "phone": user.phone,
            "language": user.language,
            "timezone": user.timezone
        }
        log_audit_event(
            db=db,
            request=request,
            action="USER_UPDATED",
            resource_type="user",
            resource_id=user.id,
            resource_name=user.email,
            description=f"User {user.email} updated their profile",
            old_values=old_values,
            new_values=new_values
        )

        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str,
    new_password: str,
    current_user: TokenData = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    from app.models.user import User
    from app.core.audit import log_audit_event

    user = db.query(User).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not user.verify_password(current_password):
        # Log failed attempt
        log_audit_event(
            db=db,
            request=request,
            action="PASSWORD_CHANGED",
            resource_type="user",
            resource_id=user.id,
            resource_name=user.email,
            description=f"Failed password change attempt for {user.email}",
            severity="WARNING"
        )
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Set new password (this will trigger validation)
    try:
        user.password = new_password
        db.commit()

        # Log successful password change
        log_audit_event(
            db=db,
            request=request,
            action="PASSWORD_CHANGED",
            resource_type="user",
            resource_id=user.id,
            resource_name=user.email,
            description=f"Password changed successfully for {user.email}"
        )

        return {"message": "Password changed successfully"}
    except ValueError as e:
        # Password validation failed
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")
