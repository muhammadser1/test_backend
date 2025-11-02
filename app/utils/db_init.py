"""
Database Initialization Script
This script initializes the MongoDB database, creates collections,
and optionally creates an initial admin user.
"""
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.config import config
from app.core.security import get_password_hash
from app.db.mongodb import connect_to_mongo, close_mongo_connection, mongo_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user():
    """
    Create the initial admin user if it doesn't exist
    """
    try:
        users_collection = mongo_db.users_collection
        
        # Check if admin already exists
        admin = users_collection.find_one({"username": "mhmdd400"})
        
        if admin:
            logger.info("✓ Admin user already exists")
            return admin
        
        # Create admin user
        import uuid
        admin_password = "mhmdd400"
        hashed_password = get_password_hash(admin_password)
        
        admin_user = {
            "_id": str(uuid.uuid4()),
            "username": "mhmdd400",  # Fixed: was "admin", should be "mhmdd400"
            "hashed_password": hashed_password,  # Fixed: was "password", should be "hashed_password"
            "role": "admin",
            "status": "active",
            "email": "admin@institute.com",
            "first_name": "System",
            "last_name": "Administrator",
            "phone": None,
            "last_login": None,
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        users_collection.insert_one(admin_user)
        logger.info("✅ Created admin user successfully")
        logger.info(f"   Username: mhmdd400")
        logger.info(f"   Password: {admin_password}")
        logger.info("   ⚠️  IMPORTANT: Change the admin password after first login!")
        
        
        return admin_user
        
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {str(e)}")
        raise


def create_sample_teacher():
    """
    Create a sample teacher user for testing
    """
    try:
        users_collection = mongo_db.users_collection
        
        # Check if teacher already exists
        teacher = users_collection.find_one({"username": "teacher1"})
        
        if teacher:
            logger.info("✓ Sample teacher already exists")
            return teacher
        
        # Create teacher user
        import uuid
        teacher_password = "teacher123"
        hashed_password = get_password_hash(teacher_password)
        
        teacher_user = {
            "_id": str(uuid.uuid4()),
            "username": "teacher1",
            "hashed_password": hashed_password,  # Fixed: was "password", should be "hashed_password"
            "role": "teacher",
            "status": "active",
            "email": "teacher1@institute.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "last_login": None,
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        users_collection.insert_one(teacher_user)
        logger.info("✅ Created sample teacher user successfully")
        logger.info(f"   Username: teacher1")
        logger.info(f"   Password: {teacher_password}")
        
        return teacher_user
        
    except Exception as e:
        logger.error(f"❌ Error creating teacher user: {str(e)}")
        raise


def initialize_database():
    """
    Main function to initialize the database
    """
    try:
        logger.info("🚀 Starting database initialization...")
        logger.info(f"📊 Database: {config.MONGO_DATABASE}")
        
        # Connect to MongoDB
        connect_to_mongo()
        
        # Create initial users
        logger.info("\n👥 Creating initial users...")
        create_admin_user()
        create_sample_teacher()
        
        # Display summary
        logger.info("\n" + "="*60)
        logger.info("📊 DATABASE INITIALIZATION SUMMARY")
        logger.info("="*60)
        
        # Count documents
        user_count = mongo_db.users_collection.count_documents({})
        lesson_count = mongo_db.lessons_collection.count_documents({})
        payment_count = mongo_db.payments_collection.count_documents({})
        
        logger.info(f"👥 Total users: {user_count}")
        logger.info(f"📚 Total lessons: {lesson_count}")
        logger.info(f"💰 Total payments: {payment_count}")
        
        # List users
        users = mongo_db.users_collection.find({})
        logger.info("\n📋 Users in database:")
        for user in users:
            logger.info(f"   - {user['username']} ({user['role']}) - {user.get('email', 'N/A')}")
        
        logger.info("\n" + "="*60)
        logger.info("✅ Database initialization completed successfully!")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"\n❌ Database initialization failed: {str(e)}")
        raise
    finally:
        close_mongo_connection()


def reset_database():
    """
    Reset the database by dropping all collections
    WARNING: This will delete all data!
    """
    try:
        logger.warning("⚠️  WARNING: This will delete ALL data in the database!")
        confirmation = input("Type 'yes' to confirm: ")
        
        if confirmation.lower() != 'yes':
            logger.info("❌ Database reset cancelled")
            return
        
        connect_to_mongo()
        
        # Drop all collections
        collections = mongo_db.db.list_collection_names()
        
        for collection in collections:
            mongo_db.db.drop_collection(collection)
            logger.info(f"🗑️  Dropped collection: {collection}")
        
        logger.info("🗑️  All collections dropped: users, lessons, payments")
        
        logger.info("✅ Database reset completed")
        
        close_mongo_connection()
        
    except Exception as e:
        logger.error(f"❌ Error resetting database: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_database()
    else:
        initialize_database()

