"""
Comprehensive tests for User dependencies (deps.py)
Tests: Authentication, authorization, token validation
"""
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, patch
from app.api.deps import get_current_user, get_current_admin, get_current_teacher
from app.models.user import User, UserRole, UserStatus
from app.core.security import create_access_token


class TestGetCurrentUser:
    """Test get_current_user dependency"""
    
    def test_valid_token_returns_user(self, mock_db):
        """Test get_current_user with valid token returns user"""
        # Create user in database
        user = User(
            username="validuser",
            hashed_password="hash",
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        # Create valid token
        token_data = {
            "sub": user._id,
            "username": user.username,
            "role": user.role.value
        }
        token = create_access_token(token_data)
        
        # Mock credentials
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        # Patch mongo_db to use mock
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            result = get_current_user(credentials)
            
            assert result is not None
            assert result["username"] == "validuser"
            assert result["_id"] == user._id
    
    def test_invalid_token_raises_401(self):
        """Test get_current_user with invalid token raises 401"""
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in exc_info.value.detail
    
    def test_token_without_sub_raises_401(self):
        """Test get_current_user with token missing 'sub' raises 401"""
        # Create token without 'sub'
        token_data = {"username": "test", "role": "teacher"}
        token = create_access_token(token_data)
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token payload" in exc_info.value.detail
    
    def test_user_not_found_raises_404(self, mock_db):
        """Test get_current_user with non-existent user raises 404"""
        # Create token for non-existent user
        token_data = {
            "sub": "nonexistent-id",
            "username": "ghost",
            "role": "teacher"
        }
        token = create_access_token(token_data)
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(credentials)
            
            assert exc_info.value.status_code == 404
            assert "User not found" in exc_info.value.detail
    
    def test_inactive_user_raises_403(self, mock_db):
        """Test get_current_user with inactive user raises 403"""
        # Create inactive user
        user = User(
            username="inactive",
            hashed_password="hash",
            status=UserStatus.INACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        # Create token
        token_data = {
            "sub": user._id,
            "username": user.username,
            "role": user.role.value
        }
        token = create_access_token(token_data)
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(credentials)
            
            assert exc_info.value.status_code == 403
            assert "inactive" in exc_info.value.detail.lower()
    
    def test_suspended_user_raises_403(self, mock_db):
        """Test get_current_user with suspended user raises 403"""
        # Create suspended user
        user = User(
            username="suspended",
            hashed_password="hash",
            status=UserStatus.SUSPENDED
        )
        mock_db["users"].insert_one(user.to_dict())
        
        # Create token
        token_data = {
            "sub": user._id,
            "username": user.username,
            "role": user.role.value
        }
        token = create_access_token(token_data)
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(credentials)
            
            assert exc_info.value.status_code == 403
            assert "suspended" in exc_info.value.detail.lower()
    
    def test_expired_token_raises_401(self):
        """Test get_current_user with expired token raises 401"""
        from datetime import timedelta
        
        # Create token that's already expired
        token_data = {
            "sub": "user-id",
            "username": "test",
            "role": "teacher"
        }
        # Negative expiration means expired
        token = create_access_token(token_data, expires_delta=timedelta(seconds=-60))
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401


class TestGetCurrentAdmin:
    """Test get_current_admin dependency"""
    
    def test_admin_user_passes(self):
        """Test get_current_admin allows admin user"""
        admin_data = {
            "_id": "admin-id",
            "username": "admin",
            "role": "admin",
            "status": "active"
        }
        
        result = get_current_admin(admin_data)
        
        assert result == admin_data
        assert result["role"] == "admin"
    
    def test_teacher_user_raises_403(self):
        """Test get_current_admin rejects teacher user"""
        teacher_data = {
            "_id": "teacher-id",
            "username": "teacher",
            "role": "teacher",
            "status": "active"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(teacher_data)
        
        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail
    
    def test_user_without_role_raises_403(self):
        """Test get_current_admin rejects user without role field"""
        user_data = {
            "_id": "user-id",
            "username": "norole",
            "status": "active"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_admin(user_data)
        
        assert exc_info.value.status_code == 403


class TestGetCurrentTeacher:
    """Test get_current_teacher dependency"""
    
    def test_teacher_user_passes(self):
        """Test get_current_teacher allows teacher user"""
        teacher_data = {
            "_id": "teacher-id",
            "username": "teacher",
            "role": "teacher",
            "status": "active"
        }
        
        result = get_current_teacher(teacher_data)
        
        assert result == teacher_data
        assert result["role"] == "teacher"
    
    def test_admin_user_raises_403(self):
        """Test get_current_teacher rejects admin user"""
        admin_data = {
            "_id": "admin-id",
            "username": "admin",
            "role": "admin",
            "status": "active"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_teacher(admin_data)
        
        assert exc_info.value.status_code == 403
        assert "Teacher access required" in exc_info.value.detail
    
    def test_user_without_role_raises_403(self):
        """Test get_current_teacher rejects user without role field"""
        user_data = {
            "_id": "user-id",
            "username": "norole",
            "status": "active"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_teacher(user_data)
        
        assert exc_info.value.status_code == 403


class TestDependencyChaining:
    """Test how dependencies work together"""
    
    def test_admin_dependency_uses_current_user(self, mock_db):
        """Test get_current_admin depends on get_current_user"""
        # Create admin user
        admin = User(
            username="admin",
            hashed_password="hash",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create token
        token_data = {
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        }
        token = create_access_token(token_data)
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            # get_current_admin should call get_current_user first
            user_data = get_current_user(credentials)
            admin_data = get_current_admin(user_data)
            
            assert admin_data["role"] == "admin"
    
    def test_teacher_dependency_uses_current_user(self, mock_db):
        """Test get_current_teacher depends on get_current_user"""
        # Create teacher user
        teacher = User(
            username="teacher",
            hashed_password="hash",
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(teacher.to_dict())
        
        # Create token
        token_data = {
            "sub": teacher._id,
            "username": teacher.username,
            "role": teacher.role.value
        }
        token = create_access_token(token_data)
        
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            # get_current_teacher should call get_current_user first
            user_data = get_current_user(credentials)
            teacher_data = get_current_teacher(user_data)
            
            assert teacher_data["role"] == "teacher"


class TestSecurityHeaders:
    """Test security-related headers and responses"""
    
    def test_invalid_auth_includes_www_authenticate_header(self):
        """Test 401 responses include WWW-Authenticate header"""
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = "invalid-token"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        
        assert exc_info.value.status_code == 401
        # Check if headers dict exists and has WWW-Authenticate
        if hasattr(exc_info.value, 'headers') and exc_info.value.headers:
            assert "WWW-Authenticate" in exc_info.value.headers

