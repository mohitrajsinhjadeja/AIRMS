"""
Authentication schemas for AIRMS+
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from .base import BaseSchema, BaseResponse

class TokenData(BaseSchema):
    """Token data schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    scope: Optional[str] = None

class TokenResponse(BaseResponse):
    """Token response schema"""
    data: TokenData

class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)

class UserAuth(BaseSchema):
    """User authentication schema"""
    username: str
    email: EmailStr
    disabled: bool = False
    last_login: Optional[datetime] = None