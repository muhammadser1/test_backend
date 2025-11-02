"""
Comprehensive tests for User routes/endpoints
Tests: Login, Logout, Get Profile
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash, create_access_token, verify_password


class TestLoginEndpoint:
    """Test POST /api/v1/user/login"""
    
    def test_successful_login_with_valid_credentials(self, client, mock_db):
        """Test login with correct username and password"""
        # Create user
        password = "password123"
        user = User(
            username="testuser",
            hashed_password=get_password_hash(password),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE,
            email="test@example.com"
        )
        mock_db["users"].insert_one(user.to_dict())
        
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post("/api/v1/user/login", json={
                "username": "testuser",
                "password": password
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Check response structure
            assert "access_token" in data
            assert "token_type" in data
            assert "user" in data
            
            # Check token type
            assert data["token_type"] == "bearer"
            
            # Check user info
            user_info = data["user"]
            assert user_info["username"] == "testuser"
            assert user_info["role"] == "teacher"
            assert user_info["status"] == "active"
            assert "last_login" in user_info
    
    def test_login_updates_last_login_timestamp(self, client, mock_db):
        """Test login updates user's last_login field"""
        password = "password123"
        user = User(
            username="logintest",
            hashed_password=get_password_hash(password),
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        # Last login should be None initially
        user_doc = mock_db["users"].find_one({"username": "logintest"})
        assert user_doc.get("last_login") is None
        
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post("/api/v1/user/login", json={
                "username": "logintest",
                "password": password
            })
            
            assert response.status_code == 200
            
            # Last login should be updated
            user_doc = mock_db["users"].find_one({"username": "logintest"})
            assert user_doc.get("last_login") is not None
    
    def test_login_with_wrong_password_returns_401(self, client, mock_db):
        """Test login with incorrect password fails"""
        user = User(
            username="testuser",
            hashed_password=get_password_hash("correct_password"),
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post("/api/v1/user/login", json={
                "username": "testuser",
                "password": "wrong_password"
            })
            
            assert response.status_code == 401
            assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_with_nonexistent_username_returns_401(self, client, mock_db):
        """Test login with username that doesn't exist"""
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post("/api/v1/user/login", json={
                "username": "nonexistent",
                "password": "somepassword"
            })
            
            assert response.status_code == 401
            assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_with_inactive_user_returns_403(self, client, mock_db):
        """Test login with inactive account fails"""
        password = "password123"
        user = User(
            username="inactive",
            hashed_password=get_password_hash(password),
            status=UserStatus.INACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post("/api/v1/user/login", json={
                "username": "inactive",
                "password": password
            })
            
            assert response.status_code == 403
            assert "inactive" in response.json()["detail"].lower()
    
    def test_login_with_suspended_user_returns_403(self, client, mock_db):
        """Test login with suspended account fails"""
        password = "password123"
        user = User(
            username="suspended",
            hashed_password=get_password_hash(password),
            status=UserStatus.SUSPENDED
        )
        mock_db["users"].insert_one(user.to_dict())
        
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post("/api/v1/user/login", json={
                "username": "suspended",
                "password": password
            })
            
            assert response.status_code == 403
            assert "suspended" in response.json()["detail"].lower()
    
    def test_login_with_missing_username_returns_422(self, client):
        """Test login without username fails validation"""
        response = client.post("/api/v1/user/login", json={
            "password": "password123"
        })
        
        assert response.status_code == 422
    
    def test_login_with_missing_password_returns_422(self, client):
        """Test login without password fails validation"""
        response = client.post("/api/v1/user/login", json={
            "username": "testuser"
        })
        
        assert response.status_code == 422
    
    def test_login_with_short_password_returns_422(self, client):
        """Test login with password shorter than 6 chars fails"""
        response = client.post("/api/v1/user/login", json={
            "username": "testuser",
            "password": "12345"  # Too short
        })
        
        assert response.status_code == 422
    
    def test_login_with_admin_user(self, client, mock_db):
        """Test admin can login successfully"""
        password = "adminpass"
        admin = User(
            username="admin",
            hashed_password=get_password_hash(password),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post("/api/v1/user/login", json={
                "username": "admin",
                "password": password
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["role"] == "admin"


class TestLogoutEndpoint:
    """Test POST /api/v1/user/logout"""
    
    def test_logout_with_valid_token_returns_success(self, client, mock_db):
        """Test logout with valid authentication token"""
        # Create user
        user = User(
            username="logouttest",
            hashed_password="hash",
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        # Create token
        token_data = {
            "sub": user._id,
            "username": user.username,
            "role": user.role.value
        }
        token = create_access_token(token_data)
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/user/logout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "logged out" in data["message"].lower()
    
    def test_logout_without_token_returns_403(self, client):
        """Test logout without authentication token fails"""
        response = client.post("/api/v1/user/logout")
        
        assert response.status_code == 403
    
    def test_logout_with_invalid_token_returns_401(self, client):
        """Test logout with invalid token fails"""
        response = client.post(
            "/api/v1/user/logout",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401


class TestGetMeEndpoint:
    """Test GET /api/v1/user/me"""
    
    def test_get_me_returns_full_user_profile(self, client, mock_db):
        """Test /me endpoint returns complete user information"""
        user = User(
            username="profiletest",
            hashed_password="hash",
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE,
            email="profile@example.com",
            first_name="Profile",
            last_name="Test",
            phone="+1234567890"
        )
        mock_db["users"].insert_one(user.to_dict())
        
        # Create token
        token_data = {
            "sub": user._id,
            "username": user.username,
            "role": user.role.value
        }
        token = create_access_token(token_data)
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/user/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["username"] == "profiletest"
            assert data["email"] == "profile@example.com"
            assert data["first_name"] == "Profile"
            assert data["last_name"] == "Test"
            assert data["phone"] == "+1234567890"
            assert data["role"] == "teacher"
            assert data["status"] == "active"
            assert "id" in data
            assert "created_at" in data
    
    def test_get_me_without_token_returns_403(self, client):
        """Test /me endpoint without token fails"""
        response = client.get("/api/v1/user/me")
        
        assert response.status_code == 403
    
    def test_get_me_with_invalid_token_returns_401(self, client):
        """Test /me endpoint with invalid token fails"""
        response = client.get(
            "/api/v1/user/me",
            headers={"Authorization": "Bearer invalid.token"}
        )
        
        assert response.status_code == 401
    
    def test_get_me_with_admin_user(self, client, mock_db):
        """Test /me endpoint works for admin users"""
        admin = User(
            username="admin",
            hashed_password="hash",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token_data = {
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        }
        token = create_access_token(token_data)
        
        with patch('app.api.deps.mongo_db') as mock_mongo:
            mock_mongo.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/user/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "admin"


# class TestTeacherSignupEndpoint:
#     """Test POST /api/v1/user/teacher/signup"""
#     
#     def test_successful_teacher_signup(self, client, mock_db):
#         """Test teacher can self-register successfully"""
#         with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
#             mock_mongo.users_collection = mock_db["users"]
#             
#             response = client.post("/api/v1/user/teacher/signup", json={
#                 "username": "newteacher",
#                 "password": "password123",
#                 "email": "teacher@example.com",
#                 "first_name": "New",
#                 "last_name": "Teacher",
#                 "phone": "+1234567890"
#             })
#             
#             assert response.status_code == 201
#             data = response.json()
#             
#             # Check response
#             assert data["username"] == "newteacher"
#             assert data["email"] == "teacher@example.com"
#             assert data["first_name"] == "New"
#             assert data["last_name"] == "Teacher"
#             assert data["role"] == "teacher"  # Always teacher
#             assert data["status"] == "active"  # Active by default
#             
#             # Check user was saved to database
#             user_doc = mock_db["users"].find_one({"username": "newteacher"})
#             assert user_doc is not None
#             assert user_doc["email"] == "teacher@example.com"
#     
#     def test_signup_hashes_password(self, client, mock_db):
#         """Test signup doesn't store plain text password"""
#         with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
#             mock_mongo.users_collection = mock_db["users"]
#             
#             response = client.post("/api/v1/user/teacher/signup", json={
#                 "username": "hashtest",
#                 "password": "mypassword",
#                 "email": "hash@example.com",
#                 "first_name": "Hash",
#                 "last_name": "Test"
#             })
#             
#             assert response.status_code == 201
#             
#             # Check password is hashed
#             user_doc = mock_db["users"].find_one({"username": "hashtest"})
#             assert user_doc["hashed_password"] != "mypassword"
#             assert verify_password("mypassword", user_doc["hashed_password"])
#     
#     def test_signup_with_duplicate_username_returns_400(self, client, mock_db):
#         """Test signup with existing username fails"""
#         # Create existing user
#         existing = User(
#             username="existing",
#             hashed_password="hash",
#             email="existing@example.com"
#         )
#         mock_db["users"].insert_one(existing.to_dict())
#         
#         with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
#             mock_mongo.users_collection = mock_db["users"]
#             
#             response = client.post("/api/v1/user/teacher/signup", json={
#                 "username": "existing",  # Duplicate
#                 "password": "password123",
#                 "email": "new@example.com",
#                 "first_name": "New",
#                 "last_name": "User"
#             })
#             
#             assert response.status_code == 400
#             assert "Username already exists" in response.json()["detail"]
#     
#     def test_signup_with_duplicate_email_returns_400(self, client, mock_db):
#         """Test signup with existing email fails"""
#         # Create existing user
#         existing = User(
#             username="existing",
#             hashed_password="hash",
#             email="duplicate@example.com"
#         )
#         mock_db["users"].insert_one(existing.to_dict())
#         
#         with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
#             mock_mongo.users_collection = mock_db["users"]
#             
#             response = client.post("/api/v1/user/teacher/signup", json={
#                 "username": "newuser",
#                 "password": "password123",
#                 "email": "duplicate@example.com",  # Duplicate
#                 "first_name": "New",
#                 "last_name": "User"
#             })
#             
#             assert response.status_code == 400
#             assert "Email already exists" in response.json()["detail"]
#     
#     def test_signup_without_required_fields_returns_422(self, client):
#         """Test signup without required fields fails validation"""
#         # Missing email
#         response = client.post("/api/v1/user/teacher/signup", json={
#             "username": "test",
#             "password": "password123",
#             "first_name": "Test",
#             "last_name": "User"
#         })
#         assert response.status_code == 422
#         
#         # Missing first_name
#         response = client.post("/api/v1/user/teacher/signup", json={
#             "username": "test",
#             "password": "password123",
#             "email": "test@example.com",
#             "last_name": "User"
#         })
#         assert response.status_code == 422
#         
#         # Missing last_name
#         response = client.post("/api/v1/user/teacher/signup", json={
#             "username": "test",
#             "password": "password123",
#             "email": "test@example.com",
#             "first_name": "Test"
#         })
#         assert response.status_code == 422
#     
#     def test_signup_with_invalid_email_returns_422(self, client):
#         """Test signup with invalid email format fails"""
#         response = client.post("/api/v1/user/teacher/signup", json={
#             "username": "test",
#             "password": "password123",
#             "email": "not-an-email",  # Invalid
#             "first_name": "Test",
#             "last_name": "User"
#         })
#         
#         assert response.status_code == 422
#     
#     def test_signup_with_short_password_returns_422(self, client):
#         """Test signup with password < 6 chars fails"""
#         response = client.post("/api/v1/user/teacher/signup", json={
#             "username": "test",
#             "password": "12345",  # Too short
#             "email": "test@example.com",
#             "first_name": "Test",
#             "last_name": "User"
#         })
#         
#         assert response.status_code == 422
#     
#     def test_signup_with_short_username_returns_422(self, client):
#         """Test signup with username < 3 chars fails"""
#         response = client.post("/api/v1/user/teacher/signup", json={
#             "username": "ab",  # Too short
#             "password": "password123",
#             "email": "test@example.com",
#             "first_name": "Test",
#             "last_name": "User"
#         })
#         
#         assert response.status_code == 422
#     
#     def test_signup_role_is_always_teacher(self, client, mock_db):
#         """Test signup always creates teacher role, never admin"""
#         with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
#             mock_mongo.users_collection = mock_db["users"]
#             
#             response = client.post("/api/v1/user/teacher/signup", json={
#                 "username": "roletest",
#                 "password": "password123",
#                 "email": "role@example.com",
#                 "first_name": "Role",
#                 "last_name": "Test"
#             })
#             
#             assert response.status_code == 201
#             
#             # Verify role is teacher in database
#             user_doc = mock_db["users"].find_one({"username": "roletest"})
#             assert user_doc["role"] == "teacher"
#     
#     def test_signup_with_optional_phone(self, client, mock_db):
#         """Test signup works with optional phone number"""
#         with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
#             mock_mongo.users_collection = mock_db["users"]
#             
#             response = client.post("/api/v1/user/teacher/signup", json={
#                 "username": "phonetest",
#                 "password": "password123",
#                 "email": "phone@example.com",
#                 "first_name": "Phone",
#                 "last_name": "Test",
#                 "phone": "+9876543210"
#             })
#             
#             assert response.status_code == 201
#             data = response.json()
#             assert data["phone"] == "+9876543210"
#     
#     def test_signup_without_optional_phone(self, client, mock_db):
#         """Test signup works without phone number"""
#         with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
#             mock_mongo.users_collection = mock_db["users"]
#             
#             response = client.post("/api/v1/user/teacher/signup", json={
#                 "username": "nophone",
#                 "password": "password123",
#                 "email": "nophone@example.com",
#                 "first_name": "No",
#                 "last_name": "Phone"
#             })
#             
#             assert response.status_code == 201
#             data = response.json()
#             assert data["phone"] is None


class TestEndpointIntegration:
    """Test full user flow integration"""
    
    # def test_signup_then_login_flow(self, client, mock_db):
    #     """Test complete flow: signup -> login"""
    #     with patch('app.api.v1.endpoints.user.mongo_db') as mock_mongo:
    #         mock_mongo.users_collection = mock_db["users"]
    #         
    #         # 1. Signup
    #         signup_response = client.post("/api/v1/user/teacher/signup", json={
    #             "username": "flowtest",
    #             "password": "password123",
    #             "email": "flow@example.com",
    #             "first_name": "Flow",
    #             "last_name": "Test"
    #         })
    #         assert signup_response.status_code == 201
    #         
    #         # 2. Login with same credentials
    #         login_response = client.post("/api/v1/user/login", json={
    #             "username": "flowtest",
    #             "password": "password123"
    #         })
    #         assert login_response.status_code == 200
    #         
    #         # Get token
    #         token = login_response.json()["access_token"]
    #         
    #         # 3. Get profile with token
    #         with patch('app.api.deps.mongo_db') as mock_deps:
    #             mock_deps.users_collection = mock_db["users"]
    #             
    #             me_response = client.get(
    #                 "/api/v1/user/me",
    #                 headers={"Authorization": f"Bearer {token}"}
    #             )
    #             
    #             assert me_response.status_code == 200
    #             profile = me_response.json()
    #             assert profile["username"] == "flowtest"
    #             assert profile["email"] == "flow@example.com"

