"""
Authentication schemas
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class Token(BaseModel):
    """Token response"""

    access_token: str
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """User response schema"""

    id: int
    email: str
    name: str
    role: str
    status: str
    tenant_id: str

    class Config:
        from_attributes = True
