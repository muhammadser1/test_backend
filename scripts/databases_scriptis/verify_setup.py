"""
Setup Verification Script
Verifies that your system is properly configured and ready to run
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_env_file():
    """Check if .env file exists"""
    env_path = project_root / '.env'
    if env_path.exists():
        logger.info("✅ .env file found")
        return True
    else:
        logger.error("❌ .env file not found")
        logger.error("   Run: cp env.example .env (or Copy-Item on Windows)")
        return False


def check_env_variables():
    """Check if required environment variables are set"""
    from app.core.config import config
    
    issues = []
    
    if not config.MONGO_CLUSTER_URL or "username:password" in config.MONGO_CLUSTER_URL:
        issues.append("MONGO_CLUSTER_URL not configured properly")
    
    if not config.JWT_SECRET_KEY or "change-this" in config.JWT_SECRET_KEY:
        issues.append("SECRET_KEY needs to be changed")
    
    if issues:
        logger.error("❌ Environment variables not configured:")
        for issue in issues:
            logger.error(f"   - {issue}")
        return False
    else:
        logger.info("✅ Environment variables configured")
        return True


def check_database_connection():
    """Check database connection"""
    try:
        from pymongo import MongoClient
        from app.core.config import config
        
        client = MongoClient(
            config.MONGO_CLUSTER_URL,
            serverSelectionTimeoutMS=5000
        )
        
        client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")
        
        # Check if collections exist
        db = client[config.MONGO_DATABASE]
        collections = db.list_collection_names()
        
        if 'users' in collections and 'lessons' in collections:
            logger.info("✅ Database collections initialized")
            
            # Count documents
            user_count = db.users.count_documents({})
            lesson_count = db.lessons.count_documents({})
            
            logger.info(f"   - Users: {user_count}")
            logger.info(f"   - Lessons: {lesson_count}")
            
            if user_count == 0:
                logger.warning("⚠️  No users found. Run: python scripts/databases_scriptis/setup_database.py")
        else:
            logger.warning("⚠️  Collections not initialized. Run: python scripts/databases_scriptis/setup_database.py")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'motor',
        'beanie',
        'pydantic',
        'python_jose',
        'passlib',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"❌ Missing packages: {', '.join(missing)}")
        logger.error("   Run: pip install -r requirements.txt")
        return False
    else:
        logger.info("✅ All required packages installed")
        return True


def check_project_structure():
    """Check if project structure is intact"""
    required_dirs = [
        'app',
        'app/api',
        'app/core',
        'app/db',
        'app/models',
        'app/schemas',
        'app/services',
        'scripts',
    ]
    
    required_files = [
        'app/main.py',
        'app/db/mongodb.py',
        'app/models/user.py',
        'app/models/lesson.py',
        'requirements.txt',
    ]
    
    missing_dirs = [d for d in required_dirs if not (project_root / d).exists()]
    missing_files = [f for f in required_files if not (project_root / f).exists()]
    
    if missing_dirs or missing_files:
        logger.error("❌ Project structure incomplete:")
        for d in missing_dirs:
            logger.error(f"   Missing directory: {d}")
        for f in missing_files:
            logger.error(f"   Missing file: {f}")
        return False
    else:
        logger.info("✅ Project structure intact")
        return True


def verify_setup():
    """Main verification function"""
    logger.info("="*60)
    logger.info("Setup Verification for General Institute System")
    logger.info("="*60)
    logger.info("")
    
    checks = []
    
    # Check 1: Project structure
    logger.info("1️⃣  Checking project structure...")
    checks.append(check_project_structure())
    logger.info("")
    
    # Check 2: Dependencies
    logger.info("2️⃣  Checking dependencies...")
    checks.append(check_dependencies())
    logger.info("")
    
    # Check 3: Environment file
    logger.info("3️⃣  Checking environment file...")
    checks.append(check_env_file())
    logger.info("")
    
    # Check 4: Environment variables
    logger.info("4️⃣  Checking environment variables...")
    checks.append(check_env_variables())
    logger.info("")
    
    # Check 5: Database connection
    logger.info("5️⃣  Checking database connection...")
    checks.append(check_database_connection())
    logger.info("")
    
    # Summary
    logger.info("="*60)
    logger.info("VERIFICATION SUMMARY")
    logger.info("="*60)
    
    passed = sum(checks)
    total = len(checks)
    
    logger.info(f"Checks passed: {passed}/{total}")
    logger.info("")
    
    if all(checks):
        logger.info("🎉 All checks passed! Your system is ready to run.")
        logger.info("")
        logger.info("Start the server with:")
        logger.info("   uvicorn app.main:app --reload")
        logger.info("")
        logger.info("Then visit:")
        logger.info("   - API Docs: http://localhost:8000/docs")
        logger.info("   - Health Check: http://localhost:8000/health")
        logger.info("")
        return True
    else:
        logger.error("⚠️  Some checks failed. Please fix the issues above.")
        logger.info("")
        logger.info("Quick fixes:")
        logger.info("   1. Install dependencies: pip install -r requirements.txt")
        logger.info("   2. Create .env file: cp env.example .env")
        logger.info("   3. Configure .env with your MongoDB credentials")
        logger.info("   4. Test connection: python scripts/databases_scriptis/test_connection.py")
        logger.info("   5. Initialize database: python scripts/databases_scriptis/setup_database.py")
        logger.info("")
        return False


if __name__ == "__main__":
    success = verify_setup()
    sys.exit(0 if success else 1)

