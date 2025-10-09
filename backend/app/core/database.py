"""
🛡️ AIRMS+ MongoDB Database Layer
Comprehensive database operations for AI risk detection and misinformation analysis
"""

import asyncio
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from pymongo import IndexModel, ASCENDING, DESCENDING
from bson import ObjectId
from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

class PIISecurityManager:
    """Secure PII handling with SHA-256 hashing and salting"""
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt"""
        return secrets.token_hex(settings.PII_SALT_LENGTH)
    
    @staticmethod
    def hash_pii(value: str, salt: str) -> str:
        """Hash PII value with salt using SHA-256"""
        combined = f"{value}{salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def verify_pii(value: str, salt: str, hashed_value: str) -> bool:
        """Verify PII value against stored hash"""
        return PIISecurityManager.hash_pii(value, salt) == hashed_value

class MongoDB:
    """MongoDB connection and operations manager"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.connected = False
        
    async def connect(self) -> bool:
        """Connect to MongoDB and initialize database"""
        try:
            # Log connection attempt
            logger.info(f"🔄 Attempting to connect to MongoDB: {settings.MONGODB_URL}")
            logger.info(f"📁 Using database: {settings.MONGODB_DATABASE}")
            
            # Create MongoDB client
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                maxIdleTimeMS=settings.MONGODB_MAX_IDLE_TIME_MS,
                serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS
            )
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ Successfully pinged MongoDB server")
            
            # Get database
            self.database = self.client[settings.MONGODB_DATABASE]
            
            # Validate database connection and collections
            db_info = await self.database.command("dbStats")
            collections = await self.database.list_collection_names()
            
            logger.info(f"✅ MongoDB Connected Successfully:")
            logger.info(f"   - Database: {settings.MONGODB_DATABASE}")
            logger.info(f"   - Collections: {len(collections)}")
            logger.info(f"   - Size: {db_info.get('dataSize', 0) / 1024 / 1024:.2f} MB")
            
            if 'users' not in collections:
                logger.warning("⚠️ Users collection not found in database")
            else:
                users_count = await self.database.users.count_documents({})
                logger.info(f"� Users collection: {users_count} users")
            
            # Create indexes
            await self._create_indexes()
            
            self.connected = True
            logger.info(f"✅ Connected to MongoDB: {settings.MONGODB_DATABASE}")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("🔌 Disconnected from MongoDB")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check MongoDB health and return status"""
        try:
            if not self.connected or not self.client:
                return {"status": "disconnected", "error": "No connection"}
            
            # Ping database
            await self.client.admin.command('ping')
            
            # Get server info
            server_info = await self.client.server_info()
            
            # Get database stats
            stats = await self.database.command("dbStats")
            
            # Check users collection
            users_count = await self.database.users.count_documents({})
            logger.info(f"Found {users_count} users in database")
            
            # Test user lookup
            test_user = await self.database.users.find_one({"email": "admin@airms.com"})
            if test_user:
                logger.info("✅ Successfully found admin user")
            else:
                logger.warning("⚠️ Admin user not found in database")
            
            return {
                "status": "healthy",
                "server_version": server_info.get("version"),
                "database": settings.MONGODB_DATABASE,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0)
            }
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        try:
            # Users collection indexes
            await self.database.users.create_index("email", unique=True)
            await self.database.users.create_index("created_at")
            await self.database.users.create_index("is_active")
            
            # Risk cases collection indexes
            await self.database.risk_cases.create_index("case_id", unique=True)
            await self.database.risk_cases.create_index("user_id")
            await self.database.risk_cases.create_index("created_at")
            await self.database.risk_cases.create_index("risk_score")
            await self.database.risk_cases.create_index("severity")
            await self.database.risk_cases.create_index([("created_at", -1), ("risk_score", -1)])
            
            # PII data store indexes
            await self.database.pii_data_store.create_index("hashed_value", unique=True)
            await self.database.pii_data_store.create_index("pii_type")
            await self.database.pii_data_store.create_index("linked_case_id")
            await self.database.pii_data_store.create_index("created_at")
            
            # Misinformation cases indexes
            await self.database.misinformation_cases.create_index("case_id", unique=True)
            await self.database.misinformation_cases.create_index("user_id")
            await self.database.misinformation_cases.create_index("misinformation_type")
            await self.database.misinformation_cases.create_index("confidence_score")
            await self.database.misinformation_cases.create_index("created_at")
            
            # Analytics indexes
            await self.database.daily_analytics.create_index([("date", -1), ("metric_type", 1)])
            await self.database.system_metrics.create_index("timestamp")
            
            # Requests collection indexes
            request_indexes = [
                IndexModel([("requestId", ASCENDING)], unique=True),
                IndexModel([("userId", ASCENDING)]),
                IndexModel([("timestamp", DESCENDING)]),
                IndexModel([("risk_assessment.riskScore", DESCENDING)]),
                IndexModel([("mitigation.action", ASCENDING)])
            ]
            await self.database.requests.create_indexes(request_indexes)
            
            # Analytics collection indexes
            analytics_indexes = [
                IndexModel([("lastUpdated", DESCENDING)]),
                IndexModel([("timeframe", ASCENDING)])
            ]
            await self.database.analytics.create_indexes(analytics_indexes)
            
            logger.info("📊 Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

# Global MongoDB instance
mongodb = MongoDB()

class DatabaseOperations:
    """High-level database operations for AIRMS+"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.pii_manager = PIISecurityManager()
    
    # === USER OPERATIONS ===
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create a new user"""
        try:
            user_data["created_at"] = datetime.utcnow()
            user_data["updated_at"] = datetime.utcnow()
            user_data["is_active"] = True
            
            result = await self.db.users.insert_one(user_data)
            logger.info(f"👤 User created: {user_data.get('email')}")
            return str(result.inserted_id)
            
        except DuplicateKeyError:
            logger.warning(f"User already exists: {user_data.get('email')}")
            return None
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = await self.db.users.find_one({"email": email})
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    # === RISK CASE OPERATIONS ===
    
    async def create_risk_case(self, case_data: Dict[str, Any]) -> Optional[str]:
        """Create a new risk assessment case"""
        try:
            case_data["case_id"] = str(ObjectId())
            case_data["created_at"] = datetime.utcnow()
            
            # Handle PII data separately
            pii_detected = case_data.get("pii_detected", [])
            if pii_detected:
                # Store PII securely
                for pii_item in pii_detected:
                    await self._store_pii_securely(
                        pii_item["value"], 
                        pii_item["type"], 
                        case_data["case_id"]
                    )
                
                # Remove actual PII values from case data
                case_data["pii_detected"] = [
                    {k: v for k, v in item.items() if k != "value"} 
                    for item in pii_detected
                ]
            
            result = await self.db.risk_cases.insert_one(case_data)
            logger.info(f"🛡️ Risk case created: {case_data['case_id']}")
            return case_data["case_id"]
            
        except Exception as e:
            logger.error(f"Failed to create risk case: {e}")
            return None
    
    async def get_risk_cases(self, 
                           user_id: Optional[str] = None,
                           severity: Optional[str] = None,
                           limit: int = 100,
                           skip: int = 0) -> List[Dict[str, Any]]:
        """Get risk cases with optional filtering"""
        try:
            query = {}
            if user_id:
                query["user_id"] = user_id
            if severity:
                query["severity"] = severity
            
            cursor = self.db.risk_cases.find(query).sort("created_at", -1).skip(skip).limit(limit)
            cases = await cursor.to_list(length=limit)
            return cases
            
        except Exception as e:
            logger.error(f"Failed to get risk cases: {e}")
            return []
    
    async def get_risk_statistics(self) -> Dict[str, Any]:
        """Get comprehensive risk statistics"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_cases": {"$sum": 1},
                        "avg_risk_score": {"$avg": "$risk_score"},
                        "high_risk_cases": {
                            "$sum": {"$cond": [{"$gte": ["$risk_score", settings.HIGH_RISK_THRESHOLD]}, 1, 0]}
                        },
                        "medium_risk_cases": {
                            "$sum": {"$cond": [
                                {"$and": [
                                    {"$gte": ["$risk_score", settings.MEDIUM_RISK_THRESHOLD]},
                                    {"$lt": ["$risk_score", settings.HIGH_RISK_THRESHOLD]}
                                ]}, 1, 0
                            ]}
                        },
                        "low_risk_cases": {
                            "$sum": {"$cond": [{"$lt": ["$risk_score", settings.MEDIUM_RISK_THRESHOLD]}, 1, 0]}
                        }
                    }
                }
            ]
            
            result = await self.db.risk_cases.aggregate(pipeline).to_list(length=1)
            if result:
                stats = result[0]
                stats.pop("_id", None)
                return stats
            
            return {
                "total_cases": 0,
                "avg_risk_score": 0.0,
                "high_risk_cases": 0,
                "medium_risk_cases": 0,
                "low_risk_cases": 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get risk statistics: {e}")
            return {}
    
    # === PII OPERATIONS ===
    
    async def _store_pii_securely(self, pii_value: str, pii_type: str, case_id: str):
        """Store PII data securely with hashing"""
        try:
            salt = self.pii_manager.generate_salt()
            hashed_value = self.pii_manager.hash_pii(pii_value, salt)
            
            pii_data = {
                "pii_type": pii_type,
                "hashed_value": hashed_value,
                "salt": salt,
                "linked_case_id": case_id,
                "created_at": datetime.utcnow()
            }
            
            await self.db.pii_data_store.insert_one(pii_data)
            logger.info(f"🔒 PII stored securely: {pii_type}")
            
        except Exception as e:
            logger.error(f"Failed to store PII: {e}")
    
    async def check_pii_exists(self, pii_value: str, pii_type: str) -> bool:
        """Check if PII value exists in database (reverse lookup)"""
        try:
            if not settings.PII_ENABLE_REVERSE_LOOKUP:
                return False
            
            # Get all PII records of this type
            cursor = self.db.pii_data_store.find({"pii_type": pii_type})
            async for record in cursor:
                if self.pii_manager.verify_pii(pii_value, record["salt"], record["hashed_value"]):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to check PII: {e}")
            return False
    
    # === MISINFORMATION OPERATIONS ===
    
    async def create_misinformation_case(self, case_data: Dict[str, Any]) -> Optional[str]:
        """Create a misinformation detection case"""
        try:
            case_data["case_id"] = str(ObjectId())
            case_data["created_at"] = datetime.utcnow()
            
            result = await self.db.misinformation_cases.insert_one(case_data)
            logger.info(f"🚨 Misinformation case created: {case_data['case_id']}")
            return case_data["case_id"]
            
        except Exception as e:
            logger.error(f"Failed to create misinformation case: {e}")
            return None
    
    async def get_misinformation_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get misinformation trends over specified days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": {
                            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                            "type": "$misinformation_type"
                        },
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence_score"}
                    }
                },
                {"$sort": {"_id.date": 1}}
            ]
            
            results = await self.db.misinformation_cases.aggregate(pipeline).to_list(length=None)
            return results
            
        except Exception as e:
            logger.error(f"Failed to get misinformation trends: {e}")
            return []
    
    # === ANALYTICS OPERATIONS ===
    
    async def update_daily_analytics(self, date: datetime, metrics: Dict[str, Any]):
        """Update daily analytics metrics"""
        try:
            date_str = date.strftime("%Y-%m-%d")
            
            await self.db.daily_analytics.update_one(
                {"date": date_str},
                {
                    "$set": {
                        "date": date_str,
                        "updated_at": datetime.utcnow(),
                        **metrics
                    }
                },
                upsert=True
            )
            
            logger.info(f"📊 Daily analytics updated: {date_str}")
            
        except Exception as e:
            logger.error(f"Failed to update daily analytics: {e}")
    
    async def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for specified days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            start_date_str = start_date.strftime("%Y-%m-%d")
            
            # Get risk case analytics
            risk_pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": None,
                        "total_assessments": {"$sum": 1},
                        "avg_risk_score": {"$avg": "$risk_score"},
                        "bias_detections": {"$sum": {"$cond": ["$detected_bias", 1, 0]}},
                        "hallucination_detections": {"$sum": {"$cond": ["$hallucination_flag", 1, 0]}},
                        "pii_detections": {"$sum": {"$cond": [{"$gt": [{"$size": "$pii_detected"}, 0]}, 1, 0]}},
                        "adversarial_detections": {"$sum": {"$cond": ["$adversarial_flag", 1, 0]}}
                    }
                }
            ]
            
            risk_stats = await self.db.risk_cases.aggregate(risk_pipeline).to_list(length=1)
            risk_data = risk_stats[0] if risk_stats else {}
            risk_data.pop("_id", None)
            
            # Get misinformation analytics
            misinfo_pipeline = [
                {"$match": {"created_at": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": "$misinformation_type",
                        "count": {"$sum": 1},
                        "avg_confidence": {"$avg": "$confidence_score"}
                    }
                }
            ]
            
            misinfo_stats = await self.db.misinformation_cases.aggregate(misinfo_pipeline).to_list(length=None)
            
            return {
                "period_days": days,
                "risk_analytics": risk_data,
                "misinformation_analytics": misinfo_stats,
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {}
    
    # === SYSTEM METRICS ===
    
    async def record_system_metrics(self, metrics: Dict[str, Any]):
        """Record system performance metrics"""
        try:
            metrics["timestamp"] = datetime.utcnow()
            await self.db.system_metrics.insert_one(metrics)
            
        except Exception as e:
            logger.error(f"Failed to record system metrics: {e}")
    
    async def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time system statistics"""
        try:
            # Get recent metrics (last 5 minutes)
            recent_time = datetime.utcnow() - timedelta(minutes=5)
            
            # System metrics
            system_metrics = await self.db.system_metrics.find_one(
                {"timestamp": {"$gte": recent_time}},
                sort=[("timestamp", -1)]
            )
            
            # Recent risk cases
            recent_cases = await self.db.risk_cases.count_documents(
                {"created_at": {"$gte": recent_time}}
            )
            
            # Active users (last hour)
            hour_ago = datetime.utcnow() - timedelta(hours=1)
            active_users = await self.db.users.count_documents(
                {"last_active": {"$gte": hour_ago}}
            )
            
            return {
                "system_metrics": system_metrics or {},
                "recent_assessments": recent_cases,
                "active_users": active_users,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get real-time stats: {e}")
            return {}
    
    # === GENERIC DOCUMENT OPERATIONS ===
    
    async def create_document(self, collection: str, document: Dict[str, Any]) -> Optional[str]:
        """Create a document in any collection"""
        try:
            document["created_at"] = datetime.utcnow()
            result = await self.db[collection].insert_one(document)
            logger.info(f"📄 Document created in {collection}: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create document in {collection}: {e}")
            return None
    
    async def find_documents(self, collection: str, query: Dict[str, Any], limit: int = 100, sort: List[tuple] = None, skip: int = 0) -> List[Dict[str, Any]]:
        """Find documents in any collection"""
        try:
            cursor = self.db[collection].find(query)
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Failed to find documents in {collection}: {e}")
            return []
    
    async def find_document(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document in any collection"""
        try:
            document = await self.db[collection].find_one(query)
            return document
        except Exception as e:
            logger.error(f"Failed to find document in {collection}: {e}")
            return None
    
    async def update_document(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a document in any collection"""
        try:
            result = await self.db[collection].update_one(query, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document in {collection}: {e}")
            return False
    
    async def count_documents(self, collection: str, query: Dict[str, Any]) -> int:
        """Count documents in any collection"""
        try:
            count = await self.db[collection].count_documents(query)
            return count
        except Exception as e:
            logger.error(f"Failed to count documents in {collection}: {e}")
            return 0
    
    async def delete_document(self, collection: str, query: Dict[str, Any]) -> bool:
        """Delete a document from any collection"""
        try:
            result = await self.db[collection].delete_one(query)
            if result.deleted_count > 0:
                logger.info(f"📄 Document deleted from {collection}")
                return True
            else:
                logger.warning(f"No document found to delete in {collection}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete document from {collection}: {e}")
            return False

# Initialize database operations
async def get_database_operations() -> DatabaseOperations:
    """Get database operations instance"""
    if not mongodb.connected:
        await mongodb.connect()
    
    return DatabaseOperations(mongodb.database)

# Startup and shutdown events
async def startup_database():
    """Initialize database connection on startup"""
    success = await mongodb.connect()
    if not success:
        raise ConnectionFailure("Failed to connect to MongoDB")

async def shutdown_database():
    """Close database connection on shutdown"""
    await mongodb.disconnect()

# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency for getting database instance"""
    if not mongodb.connected:
        await mongodb.connect()
    return mongodb.database
