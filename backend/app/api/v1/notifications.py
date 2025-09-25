"""
Notification API routes
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query

from app.core.auth import get_current_active_user
from app.models.user import UserInDB
from app.models.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationStats
)
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    category: Optional[str] = Query(default=None),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get notifications for the current user
    """
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=str(current_user.id),
            limit=limit,
            skip=skip,
            unread_only=unread_only,
            category=category
        )
        
        logger.info(f"✅ Retrieved {len(notifications)} notifications for user {current_user.email}")
        return notifications
        
    except Exception as e:
        logger.error(f"❌ Failed to get notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )


@router.get("/stats", response_model=NotificationStats)
@router.get("stats", response_model=NotificationStats)
async def get_notification_stats(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Get notification statistics for the current user
    """
    try:
        stats = await notification_service.get_stats(user_id=str(current_user.id))
        
        logger.info(f"✅ Retrieved notification stats for user {current_user.email}")
        return stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get notification stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification statistics"
        )


@router.post("/{notification_id}/read")
@router.post("{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Mark a notification as read
    """
    try:
        success = await notification_service.mark_as_read(
            notification_id=notification_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or access denied"
            )
        
        logger.info(f"✅ Notification {notification_id} marked as read by {current_user.email}")
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to mark notification as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )


@router.post("/read-all")
@router.post("read-all")
async def mark_all_notifications_as_read(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Mark all notifications as read for the current user
    """
    try:
        count = await notification_service.mark_all_as_read(user_id=str(current_user.id))
        
        logger.info(f"✅ Marked {count} notifications as read for {current_user.email}")
        return {"message": f"Marked {count} notifications as read"}
        
    except Exception as e:
        logger.error(f"❌ Failed to mark all notifications as read: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )


@router.delete("/{notification_id}")
@router.delete("{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Delete (archive) a notification
    """
    try:
        success = await notification_service.delete(
            notification_id=notification_id,
            user_id=str(current_user.id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found or access denied"
            )
        
        logger.info(f"✅ Notification {notification_id} deleted by {current_user.email}")
        return {"message": "Notification deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )


# Admin-only endpoints
@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Create a new notification (admin only for now)
    """
    try:
        # For now, allow any authenticated user to create notifications
        # In production, you might want to restrict this to admin users only
        
        created_notification = await notification_service.create(notification_data)
        
        if not created_notification:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create notification"
            )
        
        # Convert to response format
        response = NotificationResponse(
            id=str(created_notification.id),
            title=created_notification.title,
            message=created_notification.message,
            type=created_notification.type,
            category=created_notification.category,
            priority=created_notification.priority,
            action_url=created_notification.action_url,
            metadata=created_notification.metadata,
            read=created_notification.read,
            archived=created_notification.archived,
            created_at=created_notification.created_at,
            read_at=created_notification.read_at,
            time_ago="Just now"
        )
        
        logger.info(f"✅ Notification created by {current_user.email}: {notification_data.title}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )


@router.get("/system", response_model=List[NotificationResponse])
@router.get("system", response_model=List[NotificationResponse])
async def get_system_notifications(
    limit: int = Query(default=10, ge=1, le=50),
    skip: int = Query(default=0, ge=0)
):
    """
    Get system-wide notifications (public endpoint)
    """
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=None,  # System-wide notifications
            limit=limit,
            skip=skip,
            unread_only=False
        )
        
        logger.info(f"✅ Retrieved {len(notifications)} system notifications")
        return notifications
        
    except Exception as e:
        logger.error(f"❌ Failed to get system notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system notifications"
        )
