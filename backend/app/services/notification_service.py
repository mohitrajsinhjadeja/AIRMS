"""
Notification service for MongoDB operations
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import mongodb
from app.models.notification import (
    NotificationCreate, 
    NotificationUpdate, 
    NotificationInDB, 
    NotificationResponse,
    NotificationStats
)

logger = logging.getLogger(__name__)


def format_time_ago(created_at: datetime) -> str:
    """Format datetime to human readable time ago"""
    now = datetime.utcnow()
    diff = now - created_at
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    
    minutes = diff.seconds // 60
    if minutes > 0:
        return f"{minutes} min ago"
    
    return "Just now"


class NotificationService:
    """Notification service for database operations"""
    
    def __init__(self):
        self.collection_name = "notifications"
    
    @property
    def collection(self):
        """Get notifications collection"""
        if not mongodb.connected:
            raise RuntimeError("Database not connected")
        return mongodb.database[self.collection_name]
    
    async def create(self, notification_data: NotificationCreate) -> Optional[NotificationInDB]:
        """Create a new notification"""
        try:
            if not mongodb.connected:
                logger.warning("⚠️ Database not connected, cannot create notification")
                return None
            
            # Prepare notification document
            notification_doc = {
                "title": notification_data.title,
                "message": notification_data.message,
                "type": notification_data.type,
                "category": notification_data.category,
                "priority": notification_data.priority,
                "action_url": notification_data.action_url,
                "metadata": notification_data.metadata,
                "user_id": ObjectId(notification_data.user_id) if notification_data.user_id else None,
                "read": False,
                "archived": False,
                "created_at": datetime.utcnow(),
                "read_at": None
            }
            
            # Insert notification
            result = await self.collection.insert_one(notification_doc)
            
            if result.inserted_id:
                # Retrieve the created notification
                created_notification = await self.collection.find_one({"_id": result.inserted_id})
                logger.info(f"✅ Notification created: {notification_data.title}")
                return NotificationInDB(**created_notification)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to create notification: {e}")
            return None
    
    async def get_by_id(self, notification_id: str) -> Optional[NotificationInDB]:
        """Get notification by ID"""
        try:
            if not mongodb.connected or not ObjectId.is_valid(notification_id):
                return None
            
            notification_doc = await self.collection.find_one({"_id": ObjectId(notification_id)})
            if notification_doc:
                return NotificationInDB(**notification_doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get notification by ID: {e}")
            return None
    
    async def get_user_notifications(
        self, 
        user_id: Optional[str] = None, 
        limit: int = 50, 
        skip: int = 0,
        unread_only: bool = False,
        category: Optional[str] = None
    ) -> List[NotificationResponse]:
        """Get notifications for a user (or system-wide if user_id is None)"""
        try:
            if not mongodb.connected:
                return []
            
            # Build query
            query = {}
            
            if user_id:
                # User-specific notifications OR system-wide notifications
                query["$or"] = [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": None}
                ]
            else:
                # Only system-wide notifications
                query["user_id"] = None
            
            if unread_only:
                query["read"] = False
            
            if category:
                query["category"] = category
            
            # Don't show archived notifications by default
            query["archived"] = False
            
            # Get notifications
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            notifications = []
            
            async for notification_doc in cursor:
                notification = NotificationInDB(**notification_doc)
                notifications.append(NotificationResponse(
                    id=str(notification.id),
                    title=notification.title,
                    message=notification.message,
                    type=notification.type,
                    category=notification.category,
                    priority=notification.priority,
                    action_url=notification.action_url,
                    metadata=notification.metadata,
                    read=notification.read,
                    archived=notification.archived,
                    created_at=notification.created_at,
                    read_at=notification.read_at,
                    time_ago=format_time_ago(notification.created_at)
                ))
            
            return notifications
            
        except Exception as e:
            logger.error(f"❌ Failed to get user notifications: {e}")
            return []
    
    async def mark_as_read(self, notification_id: str, user_id: Optional[str] = None) -> bool:
        """Mark notification as read"""
        try:
            if not mongodb.connected or not ObjectId.is_valid(notification_id):
                return False
            
            # Build query to ensure user can only mark their own notifications as read
            query = {"_id": ObjectId(notification_id)}
            if user_id:
                query["$or"] = [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": None}  # System-wide notifications
                ]
            
            result = await self.collection.update_one(
                query,
                {
                    "$set": {
                        "read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to mark notification as read: {e}")
            return False
    
    async def mark_all_as_read(self, user_id: Optional[str] = None) -> int:
        """Mark all notifications as read for a user"""
        try:
            if not mongodb.connected:
                return 0
            
            # Build query
            query = {"read": False}
            if user_id:
                query["$or"] = [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": None}  # System-wide notifications
                ]
            else:
                query["user_id"] = None
            
            result = await self.collection.update_many(
                query,
                {
                    "$set": {
                        "read": True,
                        "read_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"❌ Failed to mark all notifications as read: {e}")
            return 0
    
    async def delete(self, notification_id: str, user_id: Optional[str] = None) -> bool:
        """Delete notification (or mark as archived)"""
        try:
            if not mongodb.connected or not ObjectId.is_valid(notification_id):
                return False
            
            # Build query to ensure user can only delete their own notifications
            query = {"_id": ObjectId(notification_id)}
            if user_id:
                query["$or"] = [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": None}  # System-wide notifications
                ]
            
            # Archive instead of delete to maintain audit trail
            result = await self.collection.update_one(
                query,
                {"$set": {"archived": True}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to delete notification: {e}")
            return False
    
    async def get_stats(self, user_id: Optional[str] = None) -> NotificationStats:
        """Get notification statistics"""
        try:
            if not mongodb.connected:
                return NotificationStats(total=0, unread=0, by_type={}, by_priority={})
            
            # Build query
            query = {"archived": False}
            if user_id:
                query["$or"] = [
                    {"user_id": ObjectId(user_id)},
                    {"user_id": None}  # System-wide notifications
                ]
            else:
                query["user_id"] = None
            
            # Get total count
            total = await self.collection.count_documents(query)
            
            # Get unread count
            unread_query = {**query, "read": False}
            unread = await self.collection.count_documents(unread_query)
            
            # Get counts by type and priority
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": {"type": "$type", "priority": "$priority"},
                    "count": {"$sum": 1}
                }}
            ]
            
            by_type = {}
            by_priority = {}
            
            async for result in self.collection.aggregate(pipeline):
                type_name = result["_id"]["type"]
                priority_name = result["_id"]["priority"]
                count = result["count"]
                
                by_type[type_name] = by_type.get(type_name, 0) + count
                by_priority[priority_name] = by_priority.get(priority_name, 0) + count
            
            return NotificationStats(
                total=total,
                unread=unread,
                by_type=by_type,
                by_priority=by_priority
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get notification stats: {e}")
            return NotificationStats(total=0, unread=0, by_type={}, by_priority={})
    
    async def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Clean up old archived notifications"""
        try:
            if not mongodb.connected:
                return 0
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = await self.collection.delete_many({
                "archived": True,
                "created_at": {"$lt": cutoff_date}
            })
            
            logger.info(f"✅ Cleaned up {result.deleted_count} old notifications")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old notifications: {e}")
            return 0


# Global notification service instance
notification_service = NotificationService()
