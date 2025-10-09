"""
Base schema models for AIRMS+
"""
from datetime import datetime
from typing import Optional, Any, Dict, Generic, TypeVar
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    """Base schema model for common fields"""
    id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class BaseResponse(BaseSchema):
    """Base response model for all API endpoints"""
    success: bool = True
    message: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)

DataT = TypeVar('DataT')

class Response(BaseResponse, Generic[DataT]):
    """Generic response model with typed data"""
    data: Optional[DataT] = None