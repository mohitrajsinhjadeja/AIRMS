#!/usr/bin/env python3
"""
Seed sample notifications for testing
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import mongodb
from app.services.notification_service import notification_service
from app.services.user_service import user_service
from app.models.notification import NotificationCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_notifications():
    """Seed sample notifications"""
    
    print("🔔 Seeding Sample Notifications")
    print("=" * 40)
    
    # Connect to MongoDB
    print("📡 Connecting to MongoDB...")
    await mongodb.connect()
    
    if not mongodb.is_connected:
        print("❌ MongoDB connection failed!")
        return
    
    print("✅ MongoDB connected successfully")
    
    # Get a user to assign some notifications to
    admin_user = await user_service.get_by_email("admin@airms.com")
    user_id = str(admin_user.id) if admin_user else None
    
    # Sample notifications to create
    sample_notifications = [
        # System-wide notifications (no user_id)
        NotificationCreate(
            title="System Alert",
            message="High risk activity detected",
            type="warning",
            category="security",
            priority="high",
            user_id=None  # System-wide
        ),
        NotificationCreate(
            title="API Key Created",
            message="API key created successfully",
            type="success",
            category="api",
            priority="medium",
            user_id=None  # System-wide
        ),
        NotificationCreate(
            title="Monthly Report",
            message="Monthly usage report available",
            type="info",
            category="system",
            priority="low",
            action_url="/dashboard/analytics",
            user_id=None  # System-wide
        ),
        
        # User-specific notifications (if user exists)
        NotificationCreate(
            title="Welcome to AIRMS",
            message="Your account has been set up successfully",
            type="success",
            category="account",
            priority="medium",
            user_id=user_id
        ),
        NotificationCreate(
            title="Security Alert",
            message="Unusual login activity detected from new location",
            type="warning",
            category="security",
            priority="high",
            action_url="/dashboard/settings",
            user_id=user_id
        ),
        NotificationCreate(
            title="Risk Assessment Complete",
            message="Your latest risk assessment has been completed with a score of 7.2",
            type="info",
            category="risk",
            priority="medium",
            action_url="/dashboard/risk",
            user_id=user_id
        ),
        NotificationCreate(
            title="System Maintenance",
            message="Scheduled maintenance will occur tonight at 2 AM UTC",
            type="info",
            category="system",
            priority="low",
            user_id=user_id
        ),
        NotificationCreate(
            title="Critical Error",
            message="Database connection failed - immediate attention required",
            type="error",
            category="system",
            priority="critical",
            user_id=user_id
        )
    ]
    
    created_count = 0
    
    for notification_data in sample_notifications:
        try:
            created_notification = await notification_service.create(notification_data)
            if created_notification:
                created_count += 1
                print(f"✅ Created: {notification_data.title}")
            else:
                print(f"❌ Failed to create: {notification_data.title}")
        except Exception as e:
            print(f"❌ Error creating {notification_data.title}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Created {created_count} notifications")
    
    # Show current notification stats
    try:
        stats = await notification_service.get_stats()
        print(f"   Total notifications: {stats.total}")
        print(f"   Unread notifications: {stats.unread}")
        print(f"   By type: {stats.by_type}")
        print(f"   By priority: {stats.by_priority}")
        
        if user_id:
            user_stats = await notification_service.get_stats(user_id=user_id)
            print(f"\n👤 User-specific stats:")
            print(f"   Total: {user_stats.total}")
            print(f"   Unread: {user_stats.unread}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    
    print("\n🎉 Notification seeding complete!")
    print("💡 You can now see real notifications in the frontend topbar")
    
    # Disconnect
    await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(seed_notifications())
