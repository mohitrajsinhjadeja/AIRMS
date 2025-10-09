
"""
User service for MongoDB operations
"""

import logging
from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.database import mongodb
from app.core.auth import get_password_hash, verify_password
from app.models.user import UserCreate, UserUpdate, UserInDB, UserResponse

logger = logging.getLogger(__name__)

# In-memory storage for development mode
_dev_users = {}
_dev_user_counter = 1


class UserService:
    """User service for database operations"""
    
    def __init__(self):
        self.collection_name = "users"
    
    @property
    def collection(self):
        """Get users collection"""
        if not mongodb.connected:
            raise RuntimeError("Database not connected")
        return mongodb.database[self.collection_name]
    
    async def create(self, user_data: UserCreate) -> Optional[UserInDB]:
        """Create a new user"""
        try:
            # Development mode - use in-memory storage
            if not mongodb.connected:
                return await self._create_dev_user(user_data)
            
            # Production mode - use MongoDB
            # Hash the password
            password_hash = get_password_hash(user_data.password)
            
            # Prepare user document
            user_doc = {
                "email": user_data.email,
                "full_name": user_data.full_name,
                "role": user_data.role,
                "is_active": user_data.is_active,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None
            }
            
            # Insert user
            result = await self.collection.insert_one(user_doc)
            
            if result.inserted_id:
                # Retrieve the created user
                created_user = await self.collection.find_one({"_id": result.inserted_id})
                logger.info(f"✅ User created successfully: {user_data.email}")
                return UserInDB(**created_user)
            
            return None
            
        except DuplicateKeyError:
            logger.warning(f"⚠️ User with email {user_data.email} already exists")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to create user: {e}")
            return None
    
    async def _create_dev_user(self, user_data: UserCreate) -> Optional[UserInDB]:
        """Create user in development mode (in-memory)"""
        global _dev_user_counter
        
        # Check if user already exists
        for user in _dev_users.values():
            if user.email == user_data.email:
                logger.warning(f"⚠️ User with email {user_data.email} already exists (dev mode)")
                return None
        
        # Hash the password
        password_hash = get_password_hash(user_data.password)
        
        # Create user
        user_id = ObjectId()
        user = UserInDB(
            id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            is_active=user_data.is_active,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_login=None
        )
        
        _dev_users[str(user_id)] = user
        _dev_user_counter += 1
        
        logger.info(f"✅ User created successfully (dev mode): {user_data.email}")
        return user
    
    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        try:
            # Development mode
            if not mongodb.connected:
                return _dev_users.get(user_id)
            
            # Production mode
            if not ObjectId.is_valid(user_id):
                return None
            
            user_doc = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return UserInDB(**user_doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user by ID: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        try:
            # Development mode
            if not mongodb.connected:
                for user in _dev_users.values():
                    if user.email == email:
                        return user
                return None
            
            # Production mode
            user_doc = await self.collection.find_one({"email": email})
            if user_doc:
                return UserInDB(**user_doc)
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get user by email: {e}")
            return None
    
    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[UserInDB]:
        """Update user"""
        try:
            # Development mode
            if not mongodb.connected:
                user = _dev_users.get(user_id)
                if user:
                    # Update fields
                    for field, value in user_data.dict(exclude_unset=True).items():
                        if value is not None:
                            setattr(user, field, value)
                    user.updated_at = datetime.utcnow()
                    return user
                return None
            
            # Production mode
            if not ObjectId.is_valid(user_id):
                return None
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow()
            }
            
            # Add fields that are not None
            for field, value in user_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_data[field] = value
            
            # Update user
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Return updated user
                return await self.get_by_id(user_id)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to update user: {e}")
            return None
    
    async def delete(self, user_id: str) -> bool:
        """Delete user"""
        try:
            # Development mode
            if not mongodb.connected:
                if user_id in _dev_users:
                    del _dev_users[user_id]
                    return True
                return False
            
            # Production mode
            if not ObjectId.is_valid(user_id):
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to delete user: {e}")
            return False
    
    async def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        try:
            logger.info(f"🔐 Attempting to authenticate user: {email}")
            
            user = await self.get_by_email(email)
            if not user:
                logger.warning(f"⚠️ User not found: {email}")
                return None
            
            logger.info(f"🔍 User found: {email}, checking password...")
            
            if not verify_password(password, user.password_hash):
                logger.warning(f"⚠️ Password verification failed for user: {email}")
                return None
            
            logger.info(f"✅ Password verified for user: {email}")
            
            # Update last login
            if mongodb.connected:
                await self.collection.update_one(
                    {"_id": user.id},
                    {"$set": {"last_login": datetime.utcnow()}}
                )
            else:
                # Development mode
                user.last_login = datetime.utcnow()
            
            logger.info(f"✅ User authenticated successfully: {email}")
            return user
            
        except Exception as e:
            logger.error(f"❌ Failed to authenticate user: {e}")
            return None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users (admin only)"""
        try:
            # Development mode
            if not mongodb.connected:
                users = []
                for user in list(_dev_users.values())[skip:skip+limit]:
                    users.append(UserResponse(
                        id=str(user.id),
                        email=user.email,
                        full_name=user.full_name,
                        role=user.role,
                        is_active=user.is_active,
                        created_at=user.created_at,
                        updated_at=user.updated_at,
                        last_login=user.last_login
                    ))
                return users
            
            # Production mode
            cursor = self.collection.find().skip(skip).limit(limit).sort("created_at", -1)
            users = []
            
            async for user_doc in cursor:
                user = UserInDB(**user_doc)
                users.append(UserResponse(
                    id=str(user.id),
                    email=user.email,
                    full_name=user.full_name,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                ))
            
            return users
            
        except Exception as e:
            logger.error(f"❌ Failed to get all users: {e}")
            return []
    
    async def count(self) -> int:
        """Count total users"""
        try:
            # Development mode
            if not mongodb.connected:
                return len(_dev_users)
            
            # Production mode
            return await self.collection.count_documents({})
        except Exception as e:
            logger.error(f"❌ Failed to count users: {e}")
            return 0
    
    async def count_active(self) -> int:
        """Count active users"""
        try:
            # Development mode
            if not mongodb.connected:
                return sum(1 for user in _dev_users.values() if user.is_active)
            
            # Production mode
            return await self.collection.count_documents({"is_active": True})
        except Exception as e:
            logger.error(f"❌ Failed to count active users: {e}")
            return 0


# Global user service instance
user_service = UserService()
