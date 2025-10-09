from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.base import BaseResponse

class APIKey(BaseModel):
    """API Key model"""
    key: str
    name: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    scopes: List[str] = []

class APIKeyList(BaseModel):
    """API Key list model"""
    keys: List[APIKey] = []

class APIKeyResponse(BaseResponse):
    """API Key response model"""
    data: APIKeyList