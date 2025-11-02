"""
Setup Database Script
Run this script to initialize your MongoDB database and create collections
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.utils.db_init import initialize_database


if __name__ == "__main__":
    print("="*60)
    print("MongoDB Database Setup")
    print("="*60)
    print()
    
    initialize_database()

