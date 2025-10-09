"""
Notification data models for MongoDB
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from bson import ObjectId


class NotificationBase(BaseModel):
    """Base notification model"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    type: Literal["info", "success", "warning", "error"] = "info"
    category: Optional[str] = Field(None, max_length=50)  # e.g., "security", "api", "system"
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    action_url: Optional[str] = None  # URL to navigate to when clicked
    metadata: Optional[dict] = None  # Additional data


class NotificationCreate(NotificationBase):
    """Create notification model"""
    user_id: Optional[str] = None  # If None, it's a system-wide notification
    

class NotificationUpdate(BaseModel):
    """Update notification model"""
    read: Optional[bool] = None
    archived: Optional[bool] = None


class NotificationInDB(NotificationBase):
    """Notification model as stored in database"""
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    user_id: Optional[ObjectId] = None  # If None, it's a system-wide notification
    read: bool = False
    archived: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class NotificationResponse(BaseModel):
    """Notification response model"""
    id: str
    title: str
    message: str
    type: str
    category: Optional[str] = None
    priority: str
    action_url: Optional[str] = None
    metadata: Optional[dict] = None
    read: bool
    archived: bool
    created_at: datetime
    read_at: Optional[datetime] = None
    time_ago: str  # Human readable time like "2 min ago"


class NotificationStats(BaseModel):
    """Notification statistics"""
    total: int
    unread: int
    by_type: dict  # {"info": 5, "warning": 2, etc.}
    by_priority: dict  # {"low": 3, "medium": 4, etc.}
