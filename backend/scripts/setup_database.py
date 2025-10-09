"""
🗄️ Database Setup Script for AIRMS
Initialize MongoDB collections and indexes for optimal performance
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from db.models import DATABASE_INDEXES, COLLECTIONS
from core.config.settings import get_settings

logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Database initialization and setup utilities"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.settings.MONGODB_URL)
            self.db = self.client[self.settings.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def create_collections(self):
        """Create collections if they don't exist"""
        logger.info("Creating collections...")
        
        existing_collections = await self.db.list_collection_names()
        
        for collection_name, model_class in COLLECTIONS.items():
            if collection_name not in existing_collections:
                await self.db.create_collection(collection_name)
                logger.info(f"✅ Created collection: {collection_name}")
            else:
                logger.info(f"📋 Collection already exists: {collection_name}")
    
    async def create_indexes(self):
        """Create database indexes for performance optimization"""
        logger.info("Creating database indexes...")
        
        for collection_name, indexes in DATABASE_INDEXES.items():
            collection = self.db[collection_name]
            
            try:
                # Get existing indexes
                existing_indexes = await collection.list_indexes().to_list(length=None)
                existing_index_keys = [
                    tuple(sorted(idx.get('key', {}).items())) 
                    for idx in existing_indexes
                ]
                
                for index_spec in indexes:
                    # Convert index specification to tuple for comparison
                    if isinstance(index_spec[0], tuple):
                        index_key = tuple(sorted(index_spec))
                    else:
                        index_key = tuple(index_spec)
                    
                    if index_key not in existing_index_keys:
                        await collection.create_index(index_spec)
                        logger.info(f"✅ Created index on {collection_name}: {index_spec}")
                    else:
                        logger.info(f"📋 Index already exists on {collection_name}: {index_spec}")
                        
            except Exception as e:
                logger.error(f"❌ Failed to create indexes for {collection_name}: {e}")
    
    async def setup_security_collections(self):
        """Setup security-specific collections and configurations"""
        logger.info("Setting up security collections...")
        
        # Create capped collections for high-volume security logs
        security_collections = {
            'rate_limit_logs': {
                'capped': True,
                'size': 100 * 1024 * 1024,  # 100MB
                'max': 1000000  # 1M documents
            },
            'security_audit_logs': {
                'capped': True,
                'size': 500 * 1024 * 1024,  # 500MB
                'max': 5000000  # 5M documents
            }
        }
        
        existing_collections = await self.db.list_collection_names()
        
        for collection_name, config in security_collections.items():
            if collection_name not in existing_collections:
                await self.db.create_collection(
                    collection_name,
                    capped=config['capped'],
                    size=config['size'],
                    max=config['max']
                )
                logger.info(f"✅ Created capped collection: {collection_name}")
    
    async def create_sample_data(self):
        """Create sample data for testing (optional)"""
        logger.info("Creating sample data...")
        
        # Sample risk statistics
        sample_stats = {
            "date": "2025-01-01T00:00:00Z",
            "total_requests": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "risk_distribution": {
                "minimal": 0,
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            },
            "category_distribution": {
                "pii": 0,
                "misinformation": 0,
                "bias": 0,
                "hallucination": 0,
                "adversarial": 0
            },
            "avg_processing_time_ms": 0,
            "max_processing_time_ms": 0,
            "min_processing_time_ms": 0,
            "security_incidents": 0,
            "rate_limit_violations": 0,
            "blocked_requests": 0
        }
        
        # Check if sample data already exists
        existing_stats = await self.db.risk_statistics.find_one({"date": sample_stats["date"]})
        if not existing_stats:
            await self.db.risk_statistics.insert_one(sample_stats)
            logger.info("✅ Created sample risk statistics")
    
    async def verify_setup(self):
        """Verify database setup is correct"""
        logger.info("Verifying database setup...")
        
        # Check collections
        collections = await self.db.list_collection_names()
        expected_collections = set(COLLECTIONS.keys())
        missing_collections = expected_collections - set(collections)
        
        if missing_collections:
            logger.warning(f"⚠️ Missing collections: {missing_collections}")
        else:
            logger.info("✅ All required collections exist")
        
        # Check indexes
        for collection_name in COLLECTIONS.keys():
            if collection_name in collections:
                collection = self.db[collection_name]
                indexes = await collection.list_indexes().to_list(length=None)
                logger.info(f"📋 {collection_name}: {len(indexes)} indexes")
        
        # Test basic operations
        try:
            # Test insert and find
            test_doc = {"test": True, "timestamp": "2025-01-01T00:00:00Z"}
            result = await self.db.test_collection.insert_one(test_doc)
            found_doc = await self.db.test_collection.find_one({"_id": result.inserted_id})
            
            if found_doc:
                await self.db.test_collection.delete_one({"_id": result.inserted_id})
                logger.info("✅ Database operations test passed")
            else:
                logger.error("❌ Database operations test failed")
                
        except Exception as e:
            logger.error(f"❌ Database operations test failed: {e}")
    
    async def cleanup_test_data(self):
        """Clean up any test collections"""
        try:
            await self.db.drop_collection("test_collection")
        except:
            pass
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("👋 Database connection closed")

async def main():
    """Main setup function"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    setup = DatabaseSetup()
    
    try:
        logger.info("🚀 Starting AIRMS database setup...")
        
        # Connect to database
        await setup.connect()
        
        # Create collections
        await setup.create_collections()
        
        # Create indexes
        await setup.create_indexes()
        
        # Setup security collections
        await setup.setup_security_collections()
        
        # Create sample data
        await setup.create_sample_data()
        
        # Verify setup
        await setup.verify_setup()
        
        # Cleanup
        await setup.cleanup_test_data()
        
        logger.info("🎉 Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"💥 Database setup failed: {e}")
        raise
    finally:
        await setup.close()

if __name__ == "__main__":
    asyncio.run(main())
