"""
Comprehensive tests for Admin routes/endpoints
Tests: User management, earnings, birthdays, pricing
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash, create_access_token


class TestAdminCreateUser:
    """Test POST /api/v1/admin/users - Admin creates users"""
    
    def test_admin_creates_teacher_successfully(self, client, mock_db):
        """Test admin can create a new teacher"""
        # Create admin user
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create admin token
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "newteacher",
                    "password": "password123",
                    "role": "teacher",
                    "email": "teacher@example.com",
                    "first_name": "New",
                    "last_name": "Teacher"
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["username"] == "newteacher"
            assert data["role"] == "teacher"
            assert data["status"] == "active"
            
            # Verify user was created in database
            created_user = mock_db["users"].find_one({"username": "newteacher"})
            assert created_user is not None
    
    def test_admin_creates_another_admin_successfully(self, client, mock_db):
        """Test admin can create another admin user"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "newadmin",
                    "password": "password123",
                    "role": "admin",
                    "email": "newadmin@example.com"  # Email required for admin
                }
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["role"] == "admin"
    
    def test_create_admin_without_email_fails(self, client, mock_db):
        """Test creating admin without email returns 400"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "newadmin",
                    "password": "password123",
                    "role": "admin"
                    # Missing email!
                }
            )
            
            assert response.status_code == 400
            assert "Email is required for admin users" in response.json()["detail"]
    
    def test_create_user_with_duplicate_username_fails(self, client, mock_db):
        """Test creating user with existing username fails"""
        # Create admin
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create existing user
        existing = User(
            username="existing",
            hashed_password="hash",
            email="existing@example.com"
        )
        mock_db["users"].insert_one(existing.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "existing",  # Duplicate
                    "password": "password123",
                    "role": "teacher"
                }
            )
            
            assert response.status_code == 400
            assert "Username already exists" in response.json()["detail"]
    
    def test_create_user_with_duplicate_email_fails(self, client, mock_db):
        """Test creating user with existing email fails"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create existing user
        existing = User(
            username="existing",
            hashed_password="hash",
            email="duplicate@example.com"
        )
        mock_db["users"].insert_one(existing.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "newuser",
                    "password": "password123",
                    "role": "teacher",
                    "email": "duplicate@example.com"  # Duplicate
                }
            )
            
            assert response.status_code == 400
            assert "Email already exists" in response.json()["detail"]
    
    def test_teacher_cannot_create_user(self, client, mock_db):
        """Test teacher cannot access create user endpoint"""
        teacher = User(
            username="teacher",
            hashed_password=get_password_hash("teacher123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(teacher.to_dict())
        
        token = create_access_token({
            "sub": teacher._id,
            "username": teacher.username,
            "role": teacher.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "newuser",
                    "password": "password123",
                    "role": "teacher"
                }
            )
            
            assert response.status_code == 403
            assert "Admin access required" in response.json()["detail"]


class TestAdminGetAllUsers:
    """Test GET /api/v1/admin/users - Get all users"""
    
    def test_admin_gets_all_users(self, client, mock_db):
        """Test admin can retrieve all users"""
        # Create admin
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create multiple users
        user1 = User(username="user1", hashed_password="hash", role=UserRole.TEACHER)
        user2 = User(username="user2", hashed_password="hash", role=UserRole.ADMIN)
        mock_db["users"].insert_one(user1.to_dict())
        mock_db["users"].insert_one(user2.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            users = response.json()
            assert len(users) >= 2  # At least user1 and user2
    
    def test_admin_filters_users_by_role(self, client, mock_db):
        """Test admin can filter users by role"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create users with different roles
        teacher1 = User(username="teacher1", hashed_password="hash", role=UserRole.TEACHER)
        teacher2 = User(username="teacher2", hashed_password="hash", role=UserRole.TEACHER)
        admin2 = User(username="admin2", hashed_password="hash", role=UserRole.ADMIN)
        mock_db["users"].insert_one(teacher1.to_dict())
        mock_db["users"].insert_one(teacher2.to_dict())
        mock_db["users"].insert_one(admin2.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            # Filter by teacher
            response = client.get(
                "/api/v1/admin/users?role=teacher",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            users = response.json()
            assert all(u["role"] == "teacher" for u in users)
    
    def test_admin_filters_users_by_status(self, client, mock_db):
        """Test admin can filter users by status"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create users with different statuses
        active = User(username="active", hashed_password="hash", status=UserStatus.ACTIVE)
        inactive = User(username="inactive", hashed_password="hash", status=UserStatus.INACTIVE)
        mock_db["users"].insert_one(active.to_dict())
        mock_db["users"].insert_one(inactive.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            # Filter by active
            response = client.get(
                "/api/v1/admin/users?status=active",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            users = response.json()
            assert all(u["status"] == "active" for u in users)
    
    def test_admin_uses_pagination(self, client, mock_db):
        """Test admin can paginate users list"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create 15 users
        for i in range(15):
            user = User(username=f"user{i}", hashed_password="hash")
            mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            # Get first page
            response = client.get(
                "/api/v1/admin/users?skip=0&limit=5",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            users = response.json()
            assert len(users) == 5


class TestAdminGetUser:
    """Test GET /api/v1/admin/users/{user_id} - Get specific user"""
    
    def test_admin_gets_user_by_id(self, client, mock_db):
        """Test admin can get specific user by ID"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create target user
        target_user = User(
            username="targetuser",
            hashed_password="hash",
            email="target@example.com",
            first_name="Target",
            last_name="User"
        )
        mock_db["users"].insert_one(target_user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                f"/api/v1/admin/users/{target_user._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "targetuser"
            assert data["email"] == "target@example.com"
    
    def test_admin_get_nonexistent_user_returns_404(self, client, mock_db):
        """Test getting non-existent user returns 404"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/admin/users/nonexistent-id",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]
    
    def test_teacher_cannot_get_user(self, client, mock_db):
        """Test teacher cannot access get user endpoint"""
        teacher = User(
            username="teacher",
            hashed_password=get_password_hash("teacher123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(teacher.to_dict())
        
        target = User(username="target", hashed_password="hash")
        mock_db["users"].insert_one(target.to_dict())
        
        token = create_access_token({
            "sub": teacher._id,
            "username": teacher.username,
            "role": teacher.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                f"/api/v1/admin/users/{target._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403
            assert "Admin access required" in response.json()["detail"]


class TestAdminUpdateUser:
    """Test PUT /api/v1/admin/users/{user_id} - Update user"""
    
    def test_admin_updates_user_successfully(self, client, mock_db):
        """Test admin can update user information"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create user to update
        user = User(
            username="oldusername",
            hashed_password="hash",
            email="old@example.com",
            first_name="Old"
        )
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.put(
                f"/api/v1/admin/users/{user._id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "email": "new@example.com",
                    "first_name": "Updated"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "new@example.com"
            assert data["first_name"] == "Updated"
            
            # Verify database was updated
            updated = mock_db["users"].find_one({"_id": user._id})
            assert updated["email"] == "new@example.com"
    
    def test_admin_updates_user_status(self, client, mock_db):
        """Test admin can change user status"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user = User(username="user", hashed_password="hash", status=UserStatus.ACTIVE)
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.put(
                f"/api/v1/admin/users/{user._id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "status": "suspended"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "suspended"
    
    def test_admin_updates_user_role(self, client, mock_db):
        """Test admin can change user role"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user = User(username="user", hashed_password="hash", role=UserRole.TEACHER)
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.put(
                f"/api/v1/admin/users/{user._id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "role": "admin"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["role"] == "admin"
    
    def test_update_to_duplicate_username_fails(self, client, mock_db):
        """Test updating username to existing one fails"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user1 = User(username="user1", hashed_password="hash")
        user2 = User(username="existing", hashed_password="hash")
        mock_db["users"].insert_one(user1.to_dict())
        mock_db["users"].insert_one(user2.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.put(
                f"/api/v1/admin/users/{user1._id}",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "existing"  # Duplicate
                }
            )
            
            assert response.status_code == 400
            assert "Username already exists" in response.json()["detail"]
    
    def test_update_nonexistent_user_returns_404(self, client, mock_db):
        """Test updating non-existent user returns 404"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.put(
                "/api/v1/admin/users/nonexistent-id",
                headers={"Authorization": f"Bearer {token}"},
                json={"first_name": "New"}
            )
            
            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]


class TestAdminDeactivateUser:
    """Test DELETE /api/v1/admin/users/{user_id} - Deactivate user (soft delete)"""
    
    def test_admin_deactivates_user_successfully(self, client, mock_db):
        """Test admin can deactivate (soft delete) a user"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user = User(
            username="tobedeactivated",
            hashed_password="hash",
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.delete(
                f"/api/v1/admin/users/{user._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "deactivated successfully" in data["message"]
            assert data["status"] == "inactive"
            
            # Verify user still exists but is inactive
            deactivated = mock_db["users"].find_one({"_id": user._id})
            assert deactivated is not None  # Not deleted
            assert deactivated["status"] == "inactive"
    
    def test_deactivate_already_inactive_user_fails(self, client, mock_db):
        """Test deactivating already inactive user returns 400"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user = User(
            username="alreadyinactive",
            hashed_password="hash",
            status=UserStatus.INACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.delete(
                f"/api/v1/admin/users/{user._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 400
            assert "already inactive" in response.json()["detail"]
    
    def test_deactivate_nonexistent_user_returns_404(self, client, mock_db):
        """Test deactivating non-existent user returns 404"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.delete(
                "/api/v1/admin/users/nonexistent-id",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 404
    
    def test_soft_delete_preserves_user_data(self, client, mock_db):
        """Test soft delete doesn't actually remove user from database"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user = User(
            username="preserve",
            hashed_password="hash",
            email="preserve@example.com",
            first_name="Preserve",
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.delete(
                f"/api/v1/admin/users/{user._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            
            # User still exists with all data
            preserved = mock_db["users"].find_one({"_id": user._id})
            assert preserved is not None
            assert preserved["username"] == "preserve"
            assert preserved["email"] == "preserve@example.com"
            assert preserved["first_name"] == "Preserve"
            assert preserved["status"] == "inactive"


class TestAdminResetPassword:
    """Test POST /api/v1/admin/users/{user_id}/reset-password - Reset password"""
    
    def test_admin_resets_user_password_successfully(self, client, mock_db):
        """Test admin can reset user password"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user = User(
            username="user",
            hashed_password=get_password_hash("oldpassword")
        )
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                f"/api/v1/admin/users/{user._id}/reset-password",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "new_password": "newpassword123"
                }
            )
            
            assert response.status_code == 200
            assert "Password reset successfully" in response.json()["message"]
            
            # Verify password was changed
            updated_user = mock_db["users"].find_one({"_id": user._id})
            assert updated_user["hashed_password"] != user.hashed_password
    
    def test_reset_password_with_short_password_fails(self, client, mock_db):
        """Test resetting password with <6 chars fails"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        user = User(username="user", hashed_password="hash")
        mock_db["users"].insert_one(user.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                f"/api/v1/admin/users/{user._id}/reset-password",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "new_password": "12345"  # Too short
                }
            )
            
            assert response.status_code == 422
    
    def test_reset_password_for_nonexistent_user_fails(self, client, mock_db):
        """Test resetting password for non-existent user returns 404"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/admin/users/nonexistent-id/reset-password",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "new_password": "newpassword123"
                }
            )
            
            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]


# class TestAdminSubjectPrices:
#     """Test GET /api/v1/admin/subject-prices - Get subject pricing"""
    
#     def test_admin_gets_subject_prices(self, client, mock_db):
#         """Test admin can get all subject prices"""
#         admin = User(
#             username="admin",
#             hashed_password=get_password_hash("admin123"),
#             role=UserRole.ADMIN,
#             status=UserStatus.ACTIVE
#         )
#         mock_db["users"].insert_one(admin.to_dict())
        
#         token = create_access_token({
#             "sub": admin._id,
#             "username": admin.username,
#             "role": admin.role.value
#         })
        
#         with patch('app.api.deps.mongo_db') as mock_deps, \
#              patch('app.core.pricing.mongo_db') as mock_pricing_db:
#             mock_deps.users_collection = mock_db["users"]
#             mock_pricing_db.pricing_collection = mock_db["pricing"]
            
#             response = client.get(
#                 "/api/v1/admin/subject-prices",
#                 headers={"Authorization": f"Bearer {token}"}
#             )
            
#             assert response.status_code == 200
#             data = response.json()
#             assert "prices" in data
#             assert "default_individual_price" in data
#             assert "default_group_price" in data
#             assert isinstance(data["prices"], list)
    
#     def test_teacher_cannot_get_subject_prices(self, client, mock_db):
#         """Test teacher cannot access subject prices endpoint"""
#         teacher = User(
#             username="teacher",
#             hashed_password=get_password_hash("teacher123"),
#             role=UserRole.TEACHER,
#             status=UserStatus.ACTIVE
#         )
#         mock_db["users"].insert_one(teacher.to_dict())
        
#         token = create_access_token({
#             "sub": teacher._id,
#             "username": teacher.username,
#             "role": teacher.role.value
#         })
        
#         with patch('app.api.deps.mongo_db') as mock_deps:
#             mock_deps.users_collection = mock_db["users"]
            
#             response = client.get(
#                 "/api/v1/admin/subject-prices",
#                 headers={"Authorization": f"Bearer {token}"}
#             )
            
#             assert response.status_code == 403


# class TestAdminTeacherEarnings:
#     """Test GET /api/v1/admin/teacher-earnings/{teacher_id} - Get teacher earnings"""
    
#     def test_admin_gets_teacher_earnings(self, client, mock_db):
#         """Test admin can get teacher earnings breakdown"""
#         admin = User(
#             username="admin",
#             hashed_password=get_password_hash("admin123"),
#             role=UserRole.ADMIN,
#             status=UserStatus.ACTIVE
#         )
#         mock_db["users"].insert_one(admin.to_dict())
        
#         teacher = User(
#             username="teacher",
#             hashed_password="hash",
#             role=UserRole.TEACHER,
#             first_name="Test",
#             last_name="Teacher"
#         )
#         mock_db["users"].insert_one(teacher.to_dict())
        
#         # Create some lessons for the teacher
#         lesson1 = {
#             "_id": "lesson1",
#             "teacher_id": teacher._id,
#             "subject": "Math",
#             "lesson_type": "individual",
#             "duration_minutes": 60,
#             "status": "completed",
#             "scheduled_date": datetime(2024, 1, 15)
#         }
#         lesson2 = {
#             "_id": "lesson2",
#             "teacher_id": teacher._id,
#             "subject": "Physics",
#             "lesson_type": "group",
#             "duration_minutes": 90,
#             "status": "completed",
#             "scheduled_date": datetime(2024, 1, 20)
#         }
#         mock_db["lessons"].insert_one(lesson1)
#         mock_db["lessons"].insert_one(lesson2)
        
#         token = create_access_token({
#             "sub": admin._id,
#             "username": admin.username,
#             "role": admin.role.value
#         })
        
#         with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
#              patch('app.api.deps.mongo_db') as mock_deps, \
#              patch('app.core.pricing.mongo_db') as mock_pricing_db:
#             mock_mongo.users_collection = mock_db["users"]
#             mock_mongo.lessons_collection = mock_db["lessons"]
#             mock_deps.users_collection = mock_db["users"]
#             mock_pricing_db.pricing_collection = mock_db["pricing"]
            
#             response = client.get(
#                 f"/api/v1/admin/teacher-earnings/{teacher._id}",
#                 headers={"Authorization": f"Bearer {token}"}
#             )
            
#             assert response.status_code == 200
#             data = response.json()
#             assert data["teacher_id"] == teacher._id
#             assert data["teacher_name"] == "Test Teacher"
#             assert data["total_lessons"] == 2
#             assert data["total_hours"] == 2.5  # 60 + 90 minutes = 150 min = 2.5 hours
#             assert len(data["by_subject"]) >= 1
    
    # def test_teacher_earnings_with_month_filter(self, client, mock_db):
    #     """Test filtering teacher earnings by month"""
    #     admin = User(
    #         username="admin",
    #         hashed_password=get_password_hash("admin123"),
    #         role=UserRole.ADMIN,
    #         status=UserStatus.ACTIVE
    #     )
    #     mock_db["users"].insert_one(admin.to_dict())
        
    #     teacher = User(
    #         username="teacher",
    #         hashed_password="hash",
    #         role=UserRole.TEACHER,
    #         first_name="Test",
    #         last_name="Teacher"
    #     )
    #     mock_db["users"].insert_one(teacher.to_dict())
        
    #     # Create lessons in different months
    #     lesson_jan = {
    #         "_id": "lesson_jan",
    #         "teacher_id": teacher._id,
    #         "subject": "Math",
    #         "lesson_type": "individual",
    #         "duration_minutes": 60,
    #         "status": "completed",
    #         "scheduled_date": datetime(2024, 1, 15)
    #     }
    #     lesson_feb = {
    #         "_id": "lesson_feb",
    #         "teacher_id": teacher._id,
    #         "subject": "Math",
    #         "lesson_type": "individual",
    #         "duration_minutes": 60,
    #         "status": "completed",
    #         "scheduled_date": datetime(2024, 2, 15)
    #     }
    #     mock_db["lessons"].insert_one(lesson_jan)
    #     mock_db["lessons"].insert_one(lesson_feb)
        
    #     token = create_access_token({
    #         "sub": admin._id,
    #         "username": admin.username,
    #         "role": admin.role.value
    #     })
        
    #     with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
    #          patch('app.api.deps.mongo_db') as mock_deps, \
    #          patch('app.core.pricing.mongo_db') as mock_pricing_db:
    #         mock_mongo.users_collection = mock_db["users"]
    #         mock_mongo.lessons_collection = mock_db["lessons"]
    #         mock_deps.users_collection = mock_db["users"]
    #         mock_pricing_db.pricing_collection = mock_db["pricing"]
            
    #         # Filter by January
    #         response = client.get(
    #             f"/api/v1/admin/teacher-earnings/{teacher._id}?month=1&year=2024",
    #             headers={"Authorization": f"Bearer {token}"}
    #         )
            
    #         assert response.status_code == 200
    #         data = response.json()
    #         assert data["month"] == 1
    #         assert data["year"] == 2024
    #         assert data["total_lessons"] == 1  # Only January lesson
    
    # def test_earnings_for_non_teacher_fails(self, client, mock_db):
    #     """Test getting earnings for non-teacher user fails"""
    #     admin = User(
    #         username="admin",
    #         hashed_password=get_password_hash("admin123"),
    #         role=UserRole.ADMIN,
    #         status=UserStatus.ACTIVE
    #     )
    #     mock_db["users"].insert_one(admin.to_dict())
        
    #     # Create another admin (not teacher)
    #     admin2 = User(
    #         username="admin2",
    #         hashed_password="hash",
    #         role=UserRole.ADMIN
    #     )
    #     mock_db["users"].insert_one(admin2.to_dict())
        
    #     token = create_access_token({
    #         "sub": admin._id,
    #         "username": admin.username,
    #         "role": admin.role.value
    #     })
        
    #     with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
    #          patch('app.api.deps.mongo_db') as mock_deps:
    #         mock_mongo.users_collection = mock_db["users"]
    #         mock_mongo.lessons_collection = mock_db["lessons"]
    #         mock_deps.users_collection = mock_db["users"]
            
    #         response = client.get(
    #             f"/api/v1/admin/teacher-earnings/{admin2._id}",
    #             headers={"Authorization": f"Bearer {token}"}
    #         )
            
    #         assert response.status_code == 400
    #         assert "not a teacher" in response.json()["detail"]
    
    # def test_earnings_for_nonexistent_teacher_fails(self, client, mock_db):
    #     """Test getting earnings for non-existent teacher returns 404"""
    #     admin = User(
    #         username="admin",
    #         hashed_password=get_password_hash("admin123"),
    #         role=UserRole.ADMIN,
    #         status=UserStatus.ACTIVE
    #     )
    #     mock_db["users"].insert_one(admin.to_dict())
        
    #     token = create_access_token({
    #         "sub": admin._id,
    #         "username": admin.username,
    #         "role": admin.role.value
    #     })
        
    #     with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
    #          patch('app.api.deps.mongo_db') as mock_deps:
    #         mock_mongo.users_collection = mock_db["users"]
    #         mock_mongo.lessons_collection = mock_db["lessons"]
    #         mock_deps.users_collection = mock_db["users"]
            
    #         response = client.get(
    #             "/api/v1/admin/teacher-earnings/nonexistent-id",
    #             headers={"Authorization": f"Bearer {token}"}
    #         )
            
    #         assert response.status_code == 404
    #         assert "Teacher not found" in response.json()["detail"]
    
    # def test_earnings_excludes_cancelled_lessons(self, client, mock_db):
    #     """Test earnings calculation excludes cancelled lessons"""
    #     admin = User(
    #         username="admin",
    #         hashed_password=get_password_hash("admin123"),
    #         role=UserRole.ADMIN,
    #         status=UserStatus.ACTIVE
    #     )
    #     mock_db["users"].insert_one(admin.to_dict())
        
    #     teacher = User(
    #         username="teacher",
    #         hashed_password="hash",
    #         role=UserRole.TEACHER,
    #         first_name="Test",
    #         last_name="Teacher"
    #     )
    #     mock_db["users"].insert_one(teacher.to_dict())
        
    #     # Create completed and cancelled lessons
    #     completed = {
    #         "_id": "completed",
    #         "teacher_id": teacher._id,
    #         "subject": "Math",
    #         "lesson_type": "individual",
    #         "duration_minutes": 60,
    #         "status": "completed",
    #         "scheduled_date": datetime(2024, 1, 15)
    #     }
    #     cancelled = {
    #         "_id": "cancelled",
    #         "teacher_id": teacher._id,
    #         "subject": "Math",
    #         "lesson_type": "individual",
    #         "duration_minutes": 60,
    #         "status": "cancelled",
    #         "scheduled_date": datetime(2024, 1, 16)
    #     }
    #     mock_db["lessons"].insert_one(completed)
    #     mock_db["lessons"].insert_one(cancelled)
        
    #     token = create_access_token({
    #         "sub": admin._id,
    #         "username": admin.username,
    #         "role": admin.role.value
    #     })
        
    #     with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
    #          patch('app.api.deps.mongo_db') as mock_deps, \
    #          patch('app.core.pricing.mongo_db') as mock_pricing_db:
    #         mock_mongo.users_collection = mock_db["users"]
    #         mock_mongo.lessons_collection = mock_db["lessons"]
    #         mock_deps.users_collection = mock_db["users"]
    #         mock_pricing_db.pricing_collection = mock_db["pricing"]
            
    #         response = client.get(
    #             f"/api/v1/admin/teacher-earnings/{teacher._id}",
    #             headers={"Authorization": f"Bearer {token}"}
    #         )
            
    #         assert response.status_code == 200
    #         data = response.json()
    #         assert data["total_lessons"] == 1  # Only completed, not cancelled


class TestAdminAuthorization:
    """Test admin-only access control"""
    
    def test_all_admin_endpoints_require_authentication(self, client):
        """Test all admin endpoints require authentication token"""
        endpoints = [
            ("post", "/api/v1/admin/users", {"username": "test", "password": "test", "role": "teacher"}),
            ("get", "/api/v1/admin/users", None),
            ("get", "/api/v1/admin/users/some-id", None),
            ("put", "/api/v1/admin/users/some-id", {"first_name": "Test"}),
            ("delete", "/api/v1/admin/users/some-id", None),
            ("post", "/api/v1/admin/users/some-id/reset-password", {"new_password": "newpass123"}),
        ]
        
        for method, url, json_data in endpoints:
            if method == "get":
                response = client.get(url)
            elif method == "post":
                response = client.post(url, json=json_data)
            elif method == "put":
                response = client.put(url, json=json_data)
            elif method == "delete":
                response = client.delete(url)
            
            assert response.status_code == 403, f"Endpoint {method.upper()} {url} should require auth"
    
    def test_teacher_cannot_access_any_admin_endpoint(self, client, mock_db):
        """Test teacher is blocked from all admin endpoints"""
        teacher = User(
            username="teacher",
            hashed_password=get_password_hash("teacher123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(teacher.to_dict())
        
        token = create_access_token({
            "sub": teacher._id,
            "username": teacher.username,
            "role": teacher.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Try accessing admin endpoints as teacher
            endpoints = [
                ("post", "/api/v1/admin/users", {"username": "test", "password": "test", "role": "teacher"}),
                ("get", "/api/v1/admin/users", None),
            ]
            
            for method, url, json_data in endpoints:
                if method == "get":
                    response = client.get(url, headers={"Authorization": f"Bearer {token}"})
                elif method == "post":
                    response = client.post(url, headers={"Authorization": f"Bearer {token}"}, json=json_data)
                
                assert response.status_code == 403, f"Teacher should be blocked from {method.upper()} {url}"
                assert "Admin access required" in response.json()["detail"]


class TestAdminEndpointValidation:
    """Test input validation for admin endpoints"""
    
    def test_create_user_without_required_fields_fails(self, client, mock_db):
        """Test creating user without required fields fails validation"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            # Missing username
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={"password": "password123", "role": "teacher"}
            )
            assert response.status_code == 422
            
            # Missing password
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={"username": "test", "role": "teacher"}
            )
            assert response.status_code == 422
            
            # Missing role
            response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={"username": "test", "password": "password123"}
            )
            assert response.status_code == 422
    
    def test_pagination_limits_work_correctly(self, client, mock_db):
        """Test pagination parameters work correctly"""
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            # Limit too high (>100)
            response = client.get(
                "/api/v1/admin/users?limit=101",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 422
            
            # Negative skip
            response = client.get(
                "/api/v1/admin/users?skip=-1",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 422


class TestAdminIntegration:
    """Test complete admin workflows"""
    
    def test_complete_user_lifecycle(self, client, mock_db):
        """Test complete user management flow: create → update → deactivate"""
        # Create admin
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.admin.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            # 1. Create user
            create_response = client.post(
                "/api/v1/admin/users",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "username": "lifecycle",
                    "password": "password123",
                    "role": "teacher",
                    "email": "lifecycle@example.com"
                }
            )
            assert create_response.status_code == 201
            user_id = create_response.json()["id"]
            
            # 2. Get user
            get_response = client.get(
                f"/api/v1/admin/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert get_response.status_code == 200
            assert get_response.json()["username"] == "lifecycle"
            
            # 3. Update user
            update_response = client.put(
                f"/api/v1/admin/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"},
                json={"first_name": "Updated"}
            )
            assert update_response.status_code == 200
            assert update_response.json()["first_name"] == "Updated"
            
            # 4. Deactivate user
            delete_response = client.delete(
                f"/api/v1/admin/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert delete_response.status_code == 200
            assert "deactivated" in delete_response.json()["message"]
            
            # 5. Verify user still exists but is inactive
            final_user = mock_db["users"].find_one({"_id": user_id})
            assert final_user is not None
            assert final_user["status"] == "inactive"

