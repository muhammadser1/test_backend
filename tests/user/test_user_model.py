"""
Comprehensive tests for User model
Tests: Business logic, data conversion, database operations
"""
import pytest
from datetime import datetime
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash, verify_password


class TestUserModelCreation:
    """Test User model instantiation"""
    
    def test_create_user_with_required_fields(self):
        """Test creating user with only required fields"""
        user = User(
            username="testuser",
            hashed_password="hashed_password"
        )
        
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password"
        assert user.role == UserRole.TEACHER  # Default
        assert user.status == UserStatus.ACTIVE  # Default
        assert user._id is not None  # Auto-generated UUID
        assert user.created_at is not None
        
    def test_create_user_with_all_fields(self):
        """Test creating user with all fields"""
        now = datetime.utcnow()
        user = User(
            username="fulluser",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            birthdate=datetime(1990, 1, 1),
            _id="custom-id",
            last_login=now,
            created_at=now,
            updated_at=now
        )
        
        assert user.username == "fulluser"
        assert user.role == UserRole.ADMIN
        assert user.email == "user@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.phone == "+1234567890"
        assert user._id == "custom-id"
        
    def test_user_id_auto_generation(self):
        """Test that user ID is auto-generated if not provided"""
        user1 = User(username="user1", hashed_password="hash1")
        user2 = User(username="user2", hashed_password="hash2")
        
        assert user1._id is not None
        assert user2._id is not None
        assert user1._id != user2._id  # Each user gets unique ID


class TestUserBusinessLogic:
    """Test User model business logic methods"""
    
    def test_is_active_returns_true_for_active_user(self):
        """Test is_active() for active user"""
        user = User(
            username="active",
            hashed_password="hash",
            status=UserStatus.ACTIVE
        )
        assert user.is_active() is True
        
    def test_is_active_returns_false_for_inactive_user(self):
        """Test is_active() for inactive user"""
        user = User(
            username="inactive",
            hashed_password="hash",
            status=UserStatus.INACTIVE
        )
        assert user.is_active() is False
        
    def test_is_active_returns_false_for_suspended_user(self):
        """Test is_active() for suspended user"""
        user = User(
            username="suspended",
            hashed_password="hash",
            status=UserStatus.SUSPENDED
        )
        assert user.is_active() is False
        
    def test_is_admin_returns_true_for_admin(self):
        """Test is_admin() for admin user"""
        user = User(
            username="admin",
            hashed_password="hash",
            role=UserRole.ADMIN
        )
        assert user.is_admin() is True
        
    def test_is_admin_returns_false_for_teacher(self):
        """Test is_admin() for teacher user"""
        user = User(
            username="teacher",
            hashed_password="hash",
            role=UserRole.TEACHER
        )
        assert user.is_admin() is False
        
    def test_is_teacher_returns_true_for_teacher(self):
        """Test is_teacher() for teacher user"""
        user = User(
            username="teacher",
            hashed_password="hash",
            role=UserRole.TEACHER
        )
        assert user.is_teacher() is True
        
    def test_is_teacher_returns_false_for_admin(self):
        """Test is_teacher() for admin user"""
        user = User(
            username="admin",
            hashed_password="hash",
            role=UserRole.ADMIN
        )
        assert user.is_teacher() is False
        
    def test_get_full_name_with_both_names(self):
        """Test get_full_name() with first and last name"""
        user = User(
            username="johndoe",
            hashed_password="hash",
            first_name="John",
            last_name="Doe"
        )
        assert user.get_full_name() == "John Doe"
        
    def test_get_full_name_with_only_first_name(self):
        """Test get_full_name() with only first name"""
        user = User(
            username="john",
            hashed_password="hash",
            first_name="John"
        )
        assert user.get_full_name() == "John"
        
    def test_get_full_name_with_only_last_name(self):
        """Test get_full_name() with only last name"""
        user = User(
            username="doe",
            hashed_password="hash",
            last_name="Doe"
        )
        assert user.get_full_name() == "Doe"
        
    def test_get_full_name_fallback_to_username(self):
        """Test get_full_name() fallback to username when no names"""
        user = User(
            username="johndoe",
            hashed_password="hash"
        )
        assert user.get_full_name() == "johndoe"
        
    def test_update_last_login(self):
        """Test update_last_login() sets current timestamp"""
        user = User(username="test", hashed_password="hash")
        
        assert user.last_login is None
        
        before = datetime.utcnow()
        user.update_last_login()
        after = datetime.utcnow()
        
        assert user.last_login is not None
        assert before <= user.last_login <= after


class TestUserDataConversion:
    """Test User model data conversion methods"""
    
    def test_to_dict_converts_all_fields(self):
        """Test to_dict() includes all user fields"""
        user = User(
            username="testuser",
            hashed_password="hashed",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone="+123456",
            birthdate=datetime(1990, 1, 1)
        )
        
        data = user.to_dict()
        
        assert data["_id"] == user._id
        assert data["username"] == "testuser"
        assert data["hashed_password"] == "hashed"
        assert data["role"] == "admin"  # Enum converted to value
        assert data["status"] == "active"  # Enum converted to value
        assert data["email"] == "test@example.com"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"
        assert data["phone"] == "+123456"
        assert data["birthdate"] == datetime(1990, 1, 1)
        assert "created_at" in data
        
    def test_to_dict_handles_enum_conversion(self):
        """Test to_dict() properly converts enums to strings"""
        user = User(
            username="test",
            hashed_password="hash",
            role=UserRole.TEACHER,
            status=UserStatus.INACTIVE
        )
        
        data = user.to_dict()
        
        assert data["role"] == "teacher"
        assert data["status"] == "inactive"
        assert isinstance(data["role"], str)
        assert isinstance(data["status"], str)
        
    def test_from_dict_creates_user_from_database_doc(self):
        """Test from_dict() recreates User from database document"""
        doc = {
            "_id": "test-id",
            "username": "testuser",
            "hashed_password": "hashed",
            "role": "admin",
            "status": "active",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+123",
            "birthdate": datetime(1990, 1, 1),
            "last_login": datetime(2024, 1, 1),
            "created_at": datetime(2023, 1, 1),
            "updated_at": datetime(2024, 1, 1)
        }
        
        user = User.from_dict(doc)
        
        assert user._id == "test-id"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed"
        assert user.role == UserRole.ADMIN
        assert user.status == UserStatus.ACTIVE
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        
    def test_from_dict_handles_missing_optional_fields(self):
        """Test from_dict() with minimal document"""
        doc = {
            "username": "minimal",
            "hashed_password": "hash"
        }
        
        user = User.from_dict(doc)
        
        assert user.username == "minimal"
        assert user.hashed_password == "hash"
        assert user.role == UserRole.TEACHER  # Default
        assert user.status == UserStatus.ACTIVE  # Default
        assert user.email is None
        
    def test_roundtrip_conversion(self):
        """Test User -> dict -> User maintains data"""
        original = User(
            username="roundtrip",
            hashed_password="hash",
            role=UserRole.ADMIN,
            email="test@test.com",
            first_name="Round",
            last_name="Trip"
        )
        
        data = original.to_dict()
        recreated = User.from_dict(data)
        
        assert recreated.username == original.username
        assert recreated.hashed_password == original.hashed_password
        assert recreated.role == original.role
        assert recreated.email == original.email
        assert recreated.first_name == original.first_name


class TestUserDatabaseMethods:
    """Test User model database interaction methods"""
    
    def test_find_by_username_returns_user_when_exists(self, mock_db):
        """Test find_by_username() finds existing user"""
        # Insert user
        user = User(username="findme", hashed_password="hash")
        mock_db["users"].insert_one(user.to_dict())
        
        # Find user
        found = User.find_by_username("findme", mock_db["users"])
        
        assert found is not None
        assert found.username == "findme"
        assert found._id == user._id
        
    def test_find_by_username_returns_none_when_not_exists(self, mock_db):
        """Test find_by_username() returns None for non-existent user"""
        found = User.find_by_username("nonexistent", mock_db["users"])
        assert found is None
        
    def test_find_by_email_returns_user_when_exists(self, mock_db):
        """Test find_by_email() finds existing user"""
        user = User(
            username="emailtest",
            hashed_password="hash",
            email="find@example.com"
        )
        mock_db["users"].insert_one(user.to_dict())
        
        found = User.find_by_email("find@example.com", mock_db["users"])
        
        assert found is not None
        assert found.email == "find@example.com"
        
    def test_find_by_email_returns_none_when_not_exists(self, mock_db):
        """Test find_by_email() returns None for non-existent email"""
        found = User.find_by_email("none@example.com", mock_db["users"])
        assert found is None
        
    def test_find_by_id_returns_user_when_exists(self, mock_db):
        """Test find_by_id() finds existing user"""
        user = User(username="idtest", hashed_password="hash")
        mock_db["users"].insert_one(user.to_dict())
        
        found = User.find_by_id(user._id, mock_db["users"])
        
        assert found is not None
        assert found._id == user._id
        assert found.username == "idtest"
        
    def test_find_by_id_returns_none_when_not_exists(self, mock_db):
        """Test find_by_id() returns None for non-existent ID"""
        found = User.find_by_id("nonexistent-id", mock_db["users"])
        assert found is None
        
    def test_username_exists_returns_true_when_exists(self, mock_db):
        """Test username_exists() returns True for existing username"""
        user = User(username="exists", hashed_password="hash")
        mock_db["users"].insert_one(user.to_dict())
        
        assert User.username_exists("exists", mock_db["users"]) is True
        
    def test_username_exists_returns_false_when_not_exists(self, mock_db):
        """Test username_exists() returns False for non-existent username"""
        assert User.username_exists("notexists", mock_db["users"]) is False
        
    def test_email_exists_returns_true_when_exists(self, mock_db):
        """Test email_exists() returns True for existing email"""
        user = User(
            username="test",
            hashed_password="hash",
            email="exists@example.com"
        )
        mock_db["users"].insert_one(user.to_dict())
        
        assert User.email_exists("exists@example.com", mock_db["users"]) is True
        
    def test_email_exists_returns_false_when_not_exists(self, mock_db):
        """Test email_exists() returns False for non-existent email"""
        assert User.email_exists("none@example.com", mock_db["users"]) is False
        
    def test_save_inserts_user_into_database(self, mock_db):
        """Test save() inserts user document into database"""
        user = User(username="savetest", hashed_password="hash")
        
        # Database should be empty
        assert mock_db["users"].count_documents({}) == 0
        
        # Save user
        user.save(mock_db["users"])
        
        # User should be in database
        assert mock_db["users"].count_documents({}) == 1
        found = mock_db["users"].find_one({"username": "savetest"})
        assert found is not None
        assert found["username"] == "savetest"
        
    def test_update_in_db_updates_user_fields(self, mock_db):
        """Test update_in_db() updates user in database"""
        user = User(
            username="updatetest",
            hashed_password="hash",
            email="old@example.com"
        )
        mock_db["users"].insert_one(user.to_dict())
        
        # Update user
        update_data = {"email": "new@example.com", "first_name": "Updated"}
        user.update_in_db(mock_db["users"], update_data)
        
        # Check database
        found = mock_db["users"].find_one({"_id": user._id})
        assert found["email"] == "new@example.com"
        assert found["first_name"] == "Updated"
        assert found["updated_at"] is not None
        
    def test_update_in_db_sets_updated_at_timestamp(self, mock_db):
        """Test update_in_db() automatically sets updated_at"""
        user = User(username="timestamp", hashed_password="hash")
        mock_db["users"].insert_one(user.to_dict())
        
        # Initially updated_at should be None
        found_before = mock_db["users"].find_one({"_id": user._id})
        assert found_before.get("updated_at") is None
        
        # Update user
        user.update_in_db(mock_db["users"], {"email": "new@test.com"})
        
        # After update, updated_at should be set
        found_after = mock_db["users"].find_one({"_id": user._id})
        updated_at = found_after["updated_at"]
        
        assert updated_at is not None
        assert isinstance(updated_at, datetime)


class TestUserRepr:
    """Test User model string representation"""
    
    def test_repr_shows_user_info(self):
        """Test __repr__() shows user ID, username, and role"""
        user = User(
            username="reprtest",
            hashed_password="hash",
            role=UserRole.ADMIN,
            _id="test-id-123"
        )
        
        repr_str = repr(user)
        
        assert "test-id-123" in repr_str
        assert "reprtest" in repr_str
        assert "admin" in repr_str.lower() or "ADMIN" in repr_str

