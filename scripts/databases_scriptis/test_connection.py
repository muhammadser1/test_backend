"""
Test MongoDB Connection Script
Run this script to test if your MongoDB connection is working
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pymongo import MongoClient
from app.core.config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """
    Test MongoDB connection
    """
    try:
        logger.info("="*60)
        logger.info("Testing MongoDB Connection")
        logger.info("="*60)
        logger.info(f"\n📊 Database: {config.MONGO_DATABASE}")
        logger.info(f"🔗 Cluster URL: {config.MONGO_CLUSTER_URL[:50]}...")
        
        # Create client
        client = MongoClient(
            config.MONGO_CLUSTER_URL,
            serverSelectionTimeoutMS=5000
        )
        
        # Test connection
        logger.info("\n🔍 Attempting to connect...")
        client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB!")
        
        # Get database
        db = client[config.MONGO_DATABASE]
        
        # List collections
        collections = db.list_collection_names()
        logger.info(f"\n📚 Existing collections: {collections if collections else 'None (database is empty)'}")
        
        # Get server info
        server_info = client.server_info()
        logger.info(f"\n📋 MongoDB Version: {server_info.get('version')}")
        
        # Close connection
        client.close()
        
        logger.info("\n" + "="*60)
        logger.info("✅ Connection test completed successfully!")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Connection test failed: {str(e)}")
        logger.error("\n💡 Please check:")
        logger.error("   1. Your MongoDB cluster URL in .env file")
        logger.error("   2. Your MongoDB credentials")
        logger.error("   3. Network connectivity")
        logger.error("   4. IP whitelist in MongoDB Atlas (if using Atlas)")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

