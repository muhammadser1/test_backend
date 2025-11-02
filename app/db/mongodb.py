from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.core.config import config
import logging

# Configure logging
logger = logging.getLogger(__name__)


class MongoDatabase:
    """
    Handles MongoDB connections and collections.
    """

    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.students_collection = None
        self.lessons_collection = None
        self.payments_collection = None
        self.pricing_collection = None

    def check_mongo_connection(self):
        """
        Checks the MongoDB connection using the configured URI.
        """
        if not config.MONGO_CLUSTER_URL:
            raise KeyError("MongoDB URI is not set/loaded correctly.")

        try:
            client = MongoClient(
                config.MONGO_CLUSTER_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully!")
            return client
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            raise Exception(f"MongoDB connection failed: {str(e)}")

    def connect(self):
        """
        Initialize MongoDB connection and collections
        """
        try:
            self.client = self.check_mongo_connection()
            self.db = self.client[config.MONGO_DATABASE]
            
            # Initialize collections
            self.users_collection = self.db["users"]
            self.students_collection = self.db["students"]
            self.lessons_collection = self.db["lessons"]
            self.payments_collection = self.db["payments"]
            self.pricing_collection = self.db["pricing"]
            
            logger.info(f"✅ Connected to database: {config.MONGO_DATABASE}")
            logger.info(f"📚 Collections initialized: users, students, lessons, payments, pricing")
            
            # Create indexes
            self.create_indexes()
            
            return self
            
        except Exception as e:
            logger.error(f"❌ Error during MongoDB initialization: {str(e)}")
            raise

    def create_indexes(self):
        """
        Create indexes for collections
        """
        try:
            logger.info("🔍 Creating indexes...")
            
            # Users collection indexes
            self.users_collection.create_index("username", unique=True)
            self.users_collection.create_index("email")
            self.users_collection.create_index("role")
            self.users_collection.create_index("status")
            
            # Students collection indexes
            self.students_collection.create_index("full_name")
            self.students_collection.create_index("email")
            self.students_collection.create_index("is_active")
            
            # Lessons collection indexes
            self.lessons_collection.create_index("teacher_id")
            self.lessons_collection.create_index("status")
            self.lessons_collection.create_index("lesson_type")
            self.lessons_collection.create_index("scheduled_date")
            self.lessons_collection.create_index("subject")
            
            # Payments collection indexes
            self.payments_collection.create_index("student_name")
            self.payments_collection.create_index("payment_date")
            self.payments_collection.create_index("lesson_id")
            
            # Pricing collection indexes
            self.pricing_collection.create_index("subject", unique=True)
            self.pricing_collection.create_index("is_active")
            
            logger.info("✅ Indexes created successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Error creating indexes (may already exist): {str(e)}")

    def close(self):
        """
        Close MongoDB connection
        """
        if self.client:
            self.client.close()
            logger.info("❌ Closed MongoDB connection")

    def list_collections(self):
        """
        List all collections in the database
        """
        try:
            collections = self.db.list_collection_names()
            logger.info(f"📚 Existing collections: {collections}")
            return collections
        except Exception as e:
            logger.error(f"❌ Error listing collections: {str(e)}")
            return []


# Global database instance
mongo_db = MongoDatabase()


def connect_to_mongo():
    """
    Connect to MongoDB (sync version for startup)
    """
    global mongo_db
    mongo_db.connect()
    return mongo_db


def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global mongo_db
    mongo_db.close()


def get_database():
    """
    Get database instance
    """
    return mongo_db.db


def get_users_collection():
    """
    Get users collection
    """
    return mongo_db.users_collection


def get_lessons_collection():
    """
    Get lessons collection
    """
    return mongo_db.lessons_collection


def get_payments_collection():
    """
    Get payments collection
    """
    return mongo_db.payments_collection

