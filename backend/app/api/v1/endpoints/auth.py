"""
Authentication endpoints
Consolidated from Kronos EAM
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    TokenData,
)
from app.schemas.auth import Token, UserResponse
from app.core.config import settings
from datetime import timedelta

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint"""
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
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        "permissions": user.permissions or [],
    }

    access_token = create_access_token(
        data=token_data, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "tenant_id": user.tenant_id,
            "permissions": user.permissions or [],
        },
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Get current user information"""
    from app.models.user import User

    user = db.query(User).filter(User.id == int(current_user.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
