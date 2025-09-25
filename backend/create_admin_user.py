#!/usr/bin/env python3
"""
Create the missing admin user mohitrajjadeja4+admin@gmail.com
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import mongodb
from app.services.user_service import user_service
from app.models.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user():
    """Create the missing admin user"""
    
    print("🔧 Creating Admin User: mohitrajjadeja4+admin@gmail.com")
    print("=" * 60)
    
    # Connect to MongoDB
    print("📡 Connecting to MongoDB...")
    await mongodb.connect()
    
    if not mongodb.is_connected:
        print("❌ MongoDB connection failed!")
        print("💡 Make sure MongoDB is running and accessible")
        return
    
    print("✅ MongoDB connected successfully")
    
    # Check if user already exists
    admin_email = "mohitrajjadeja4+admin@gmail.com"
    existing_user = await user_service.get_by_email(admin_email)
    
    if existing_user:
        print(f"✅ User already exists: {admin_email}")
        print(f"   Role: {existing_user.role}")
        print(f"   Active: {existing_user.is_active}")
        
        # Update to admin role if not already
        if existing_user.role != "admin":
            from app.models.user import UserUpdate
            update_data = UserUpdate(role="admin")
            updated_user = await user_service.update(str(existing_user.id), update_data)
            if updated_user:
                print("✅ User role updated to admin")
            else:
                print("❌ Failed to update user role")
    else:
        print(f"❌ User not found: {admin_email}")
        print("Creating new admin user...")
        
        # Get password from user
        password = input("Enter password for the admin user: ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long")
            return
        
        # Create admin user
        admin_data = UserCreate(
            email=admin_email,
            password=password,
            full_name="Admin User",
            role="admin"
        )
        
        try:
            created_user = await user_service.create(admin_data)
            if created_user:
                print("✅ Admin user created successfully!")
                print(f"   Email: {admin_email}")
                print(f"   Password: {password}")
                print(f"   Role: admin")
                print(f"   ID: {created_user.id}")
            else:
                print("❌ Failed to create admin user")
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
    
    print("\n📊 Current user statistics:")
    total_users = await user_service.count()
    active_users = await user_service.count_active()
    print(f"   Total users: {total_users}")
    print(f"   Active users: {active_users}")
    
    print(f"\n🎉 Admin user setup complete!")
    print(f"You can now login with: {admin_email}")
    
    # Disconnect
    await mongodb.disconnect()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
