"""
Pytest configuration and shared fixtures
"""
import pytest
from fastapi.testclient import TestClient
from mongomock import MongoClient as MockMongoClient
from datetime import datetime
from app.main import app
from app.db import mongo_db
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash


@pytest.fixture(scope="function")
def mock_db():
    """
    Mock MongoDB database for testing
    """
    client = MockMongoClient()
    db = client["test_db"]
    
    # Create collections
    users_collection = db["users"]
    students_collection = db["students"]
    lessons_collection = db["lessons"]
    payments_collection = db["payments"]
    pricing_collection = db["pricing"]
    
    yield {
        "db": db,
        "users": users_collection,
        "students": students_collection,
        "lessons": lessons_collection,
        "payments": payments_collection,
        "pricing": pricing_collection
    }
    
    # Cleanup
    client.close()


@pytest.fixture(scope="function")
def client():
    """
    FastAPI test client
    """
    return TestClient(app)


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing
    """
    return {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
        "role": UserRole.TEACHER,
        "status": UserStatus.ACTIVE
    }


@pytest.fixture
def create_test_user(mock_db):
    """
    Factory fixture to create test users
    """
    def _create_user(**kwargs):
        # Default values
        user_data = {
            "username": "testuser",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.TEACHER,
            "status": UserStatus.ACTIVE,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
        }
        # Override with provided kwargs
        user_data.update(kwargs)
        
        user = User(**user_data)
        mock_db["users"].insert_one(user.to_dict())
        return user
    
    return _create_user


@pytest.fixture
def admin_user(create_test_user):
    """
    Create an admin user for testing
    """
    return create_test_user(
        username="admin",
        email="admin@example.com",
        role=UserRole.ADMIN,
        first_name="Admin",
        last_name="User"
    )


@pytest.fixture
def teacher_user(create_test_user):
    """
    Create a teacher user for testing
    """
    return create_test_user(
        username="teacher",
        email="teacher@example.com",
        role=UserRole.TEACHER,
        first_name="Teacher",
        last_name="User"
    )


@pytest.fixture
def inactive_user(create_test_user):
    """
    Create an inactive user for testing
    """
    return create_test_user(
        username="inactive",
        email="inactive@example.com",
        status=UserStatus.INACTIVE
    )
