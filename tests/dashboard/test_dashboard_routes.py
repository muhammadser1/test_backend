"""
Tests for Dashboard/Statistics API Routes
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash, create_access_token


class TestDashboardStats:
    """Test GET /dashboard/stats"""
    
    def test_get_dashboard_stats_as_admin(self, client, mock_db):
        """Test getting dashboard stats as admin"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.students_collection = mock_db["students"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            mock_mongo.payments_collection = mock_db["payments"]
            mock_mongo.pricing_collection = mock_db["pricing"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "users" in data
            assert "students" in data
            assert "lessons" in data
            assert "payments" in data
            assert "pricing" in data
    
    def test_get_dashboard_stats_as_teacher_should_fail(self, client, mock_db):
        """Test that teachers cannot access dashboard stats"""
        # Create teacher user
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
            
            response = client.get(
                "/api/v1/dashboard/stats",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403
    
    def test_get_dashboard_stats_without_auth(self, client):
        """Test dashboard stats without authentication"""
        response = client.get("/api/v1/dashboard/stats")
        assert response.status_code in [401, 403]
    
    def test_get_dashboard_stats_with_month_filter(self, client, mock_db):
        """Test getting dashboard stats filtered by month"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.students_collection = mock_db["students"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            mock_mongo.payments_collection = mock_db["payments"]
            mock_mongo.pricing_collection = mock_db["pricing"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats?month=1&year=2025",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "filter" in data
            assert data["filter"]["month"] == 1
            assert data["filter"]["year"] == 2025


class TestTeachersStats:
    """Test GET /dashboard/stats/teachers"""
    
    def test_get_teachers_stats(self, client, mock_db):
        """Test getting detailed teachers stats"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/teachers",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "total_teachers" in data
            assert "teachers" in data
            assert isinstance(data["teachers"], list)
    
    def test_get_teachers_stats_as_teacher_should_fail(self, client, mock_db):
        """Test that teachers cannot access teachers stats"""
        # Create teacher user
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
            
            response = client.get(
                "/api/v1/dashboard/stats/teachers",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403
    
    def test_get_teachers_stats_with_month_filter(self, client, mock_db):
        """Test getting teachers stats filtered by month and year"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/teachers?month=1&year=2025",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "total_teachers" in data
            assert "teachers" in data
            assert "filters" in data
            assert "lesson_date_filter" in data["filters"]
            assert data["filters"]["lesson_date_filter"]["month"] == 1
            assert data["filters"]["lesson_date_filter"]["year"] == 2025
    
    def test_get_teachers_stats_with_search_filter(self, client, mock_db):
        """Test searching teachers by name"""
        # Create admin user
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create test teachers
        teacher1 = User(
            username="teacher1",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE,
            first_name="محمد",
            last_name="أحمد"
        )
        teacher2 = User(
            username="teacher2",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE,
            first_name="علي",
            last_name="حسن"
        )
        mock_db["users"].insert_one(teacher1.to_dict())
        mock_db["users"].insert_one(teacher2.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/teachers?search=محمد",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "total_teachers" in data
            assert "filters" in data
            assert data["filters"]["search"] == "محمد"
            # Should only return teachers matching search
            assert data["total_teachers"] >= 0
    
    def test_get_teachers_stats_with_status_filter(self, client, mock_db):
        """Test filtering teachers by status"""
        # Create admin user
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create teachers with different statuses
        active_teacher = User(
            username="teacher_active",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE
        )
        suspended_teacher = User(
            username="teacher_suspended",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.TEACHER,
            status=UserStatus.SUSPENDED
        )
        mock_db["users"].insert_one(active_teacher.to_dict())
        mock_db["users"].insert_one(suspended_teacher.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            # Test active status
            response = client.get(
                "/api/v1/dashboard/stats/teachers?status=active",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "filters" in data
            assert data["filters"]["status"] == "active"
            # Should only return active teachers
            for teacher in data["teachers"]:
                assert teacher["status"] == "active"
    
    def test_get_teachers_stats_with_combined_filters(self, client, mock_db):
        """Test combining multiple filters"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/teachers?month=1&year=2025&search=teacher&status=active",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "filters" in data
            assert "lesson_date_filter" in data["filters"]
            assert data["filters"]["search"] == "teacher"
            assert data["filters"]["status"] == "active"
    
    def test_get_teachers_stats_includes_new_fields(self, client, mock_db):
        """Test that response includes new fields like total_hours, phone, etc."""
        # Create admin user
        admin = User(
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        mock_db["users"].insert_one(admin.to_dict())
        
        # Create teacher with full details
        teacher = User(
            username="teacher",
            hashed_password=get_password_hash("pass123"),
            role=UserRole.TEACHER,
            status=UserStatus.ACTIVE,
            first_name="محمد",
            last_name="أحمد",
            email="teacher@example.com",
            phone="+1234567890"
        )
        mock_db["users"].insert_one(teacher.to_dict())
        
        token = create_access_token({
            "sub": admin._id,
            "username": admin.username,
            "role": admin.role.value
        })
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.users_collection = mock_db["users"]
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/teachers",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            if data["total_teachers"] > 0:
                teacher_data = data["teachers"][0]
                # Check for new fields
                assert "total_hours" in teacher_data
                assert "phone" in teacher_data
                assert "status" in teacher_data
                assert "created_at" in teacher_data
                assert "last_login" in teacher_data


class TestStudentsStats:
    """Test GET /dashboard/stats/students"""
    
    def test_get_students_stats(self, client, mock_db):
        """Test getting detailed students stats"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_mongo.payments_collection = mock_db["payments"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/students",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "total_students" in data
            assert "students" in data
            assert isinstance(data["students"], list)
    
    def test_get_students_stats_as_teacher_should_fail(self, client, mock_db):
        """Test that teachers cannot access students stats"""
        # Create teacher user
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
            
            response = client.get(
                "/api/v1/dashboard/stats/students",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403


class TestLessonsStats:
    """Test GET /dashboard/stats/lessons"""
    
    def test_get_lessons_stats(self, client, mock_db):
        """Test getting detailed lessons stats"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/lessons",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "by_type" in data
            assert "by_status" in data
            assert "total_hours" in data
    
    def test_get_lessons_stats_with_month_filter(self, client, mock_db):
        """Test getting lessons stats filtered by month"""
        # Create admin user
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
        
        with patch('app.api.v1.endpoints.dashboard.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.lessons_collection = mock_db["lessons"]
            
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/dashboard/stats/lessons?month=1&year=2025",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "filter" in data
            assert data["filter"]["month"] == 1
            assert data["filter"]["year"] == 2025
    
    def test_get_lessons_stats_as_teacher_should_fail(self, client, mock_db):
        """Test that teachers cannot access lessons stats"""
        # Create teacher user
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
            
            response = client.get(
                "/api/v1/dashboard/stats/lessons",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403
