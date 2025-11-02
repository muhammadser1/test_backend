"""
Tests for the detailed teachers statistics endpoint.
Tests the GET /dashboard/stats/teachers-detailed endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from bson import ObjectId
from app.main import app
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash, create_access_token
from unittest.mock import patch

client = TestClient(app)


class TestTeachersDetailedStats:
    """Test cases for the detailed teachers statistics endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self, mock_db):
        """Setup test data and cleanup after each test."""
        # Store mock_db for use in tests
        self.mock_db = mock_db
        
        # Clean up before test
        self.mock_db["users"].delete_many({})
        self.mock_db["lessons"].delete_many({})
        
        # Create test admin user
        admin = User(
            username="admin_test",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            email="admin@test.com",
            first_name="Admin",
            last_name="User"
        )
        self.mock_db["users"].insert_one(admin.to_dict())
        
        # Create authentication token
        self.admin_token = create_access_token({
            "sub": str(admin._id),
            "username": admin.username,
            "role": admin.role.value
        })
        
        # Create test teachers
        self.teacher1_id = ObjectId()
        self.teacher2_id = ObjectId()
        self.teacher3_id = ObjectId()
        
        teachers = [
            {
                "_id": self.teacher1_id,
                "username": "teacher1",
                "email": "teacher1@test.com",
                "first_name": "أحمد",
                "last_name": "محمد علي",
                "role": "teacher",
                "status": "active",
                "password_hash": "hashed_password",
                "created_at": datetime.utcnow()
            },
            {
                "_id": self.teacher2_id,
                "username": "teacher2",
                "email": "teacher2@test.com",
                "first_name": "فاطمة",
                "last_name": "حسن",
                "role": "teacher",
                "status": "active",
                "password_hash": "hashed_password",
                "created_at": datetime.utcnow()
            },
            {
                "_id": self.teacher3_id,
                "username": "teacher3",
                "email": "teacher3@test.com",
                "first_name": "محمد",
                "last_name": "عبد الرحمن",
                "role": "teacher",
                "status": "suspended",
                "password_hash": "hashed_password",
                "created_at": datetime.utcnow()
            }
        ]
        self.mock_db["users"].insert_many(teachers)
        
        # Create test lessons
        now = datetime.utcnow()
        lessons = [
            # Teacher 1 lessons
            {
                "_id": ObjectId(),
                "teacher_id": str(self.teacher1_id),
                "subject": "Math",
                "education_level": "elementary",
                "lesson_type": "individual",
                "duration_minutes": 60,  # 1 hour
                "status": "completed",
                "scheduled_date": now - timedelta(days=1),
                "students": [{"student_name": "Student 1"}]
            },
            {
                "_id": ObjectId(),
                "teacher_id": str(self.teacher1_id),
                "subject": "Arabic",
                "education_level": "secondary",
                "lesson_type": "individual",
                "duration_minutes": 90,  # 1.5 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=2),
                "students": [{"student_name": "Student 2"}]
            },
            {
                "_id": ObjectId(),
                "teacher_id": str(self.teacher1_id),
                "subject": "Science",
                "education_level": "middle",
                "lesson_type": "group",
                "duration_minutes": 120,  # 2 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=3),
                "students": [{"student_name": "Student 3"}, {"student_name": "Student 4"}]
            },
            # Teacher 2 lessons
            {
                "_id": ObjectId(),
                "teacher_id": str(self.teacher2_id),
                "subject": "English",
                "education_level": "elementary",
                "lesson_type": "individual",
                "duration_minutes": 45,  # 0.75 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=1),
                "students": [{"student_name": "Student 5"}]
            },
            {
                "_id": ObjectId(),
                "teacher_id": str(self.teacher2_id),
                "subject": "History",
                "education_level": "secondary",
                "lesson_type": "group",
                "duration_minutes": 90,  # 1.5 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=2),
                "students": [{"student_name": "Student 6"}, {"student_name": "Student 7"}]
            },
            # Teacher 3 lessons (suspended teacher)
            {
                "_id": ObjectId(),
                "teacher_id": str(self.teacher3_id),
                "subject": "Physics",
                "education_level": "secondary",
                "lesson_type": "individual",
                "duration_minutes": 60,
                "status": "completed",
                "scheduled_date": now - timedelta(days=1),
                "students": [{"student_name": "Student 8"}]
            }
        ]
        self.mock_db["lessons"].insert_many(lessons)
        
        yield
        
        # Cleanup after test
        self.mock_db["users"].delete_many({})
        self.mock_db["lessons"].delete_many({})

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_success(self, mock_deps, mock_mongo_db):
        """Test successful retrieval of detailed teacher statistics."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "total_teachers" in data
        assert "teachers" in data
        assert isinstance(data["teachers"], list)
        
        # Should return 2 active teachers (teacher3 is suspended)
        assert data["total_teachers"] == 2
        assert len(data["teachers"]) == 2
        
        # Check teacher data structure
        for teacher in data["teachers"]:
            assert "teacher_id" in teacher
            assert "teacher_name" in teacher
            assert "total_individual_hours" in teacher
            assert "total_group_hours" in teacher
            assert "individual_hours_by_level" in teacher
            assert "group_hours_by_level" in teacher
            
            # Check education level breakdown structure
            individual_levels = teacher["individual_hours_by_level"]
            group_levels = teacher["group_hours_by_level"]
            
            assert "elementary" in individual_levels
            assert "middle" in individual_levels
            assert "secondary" in individual_levels
            assert "elementary" in group_levels
            assert "middle" in group_levels
            assert "secondary" in group_levels
            
            # All values should be numbers
            for level in ["elementary", "middle", "secondary"]:
                assert isinstance(individual_levels[level], (int, float))
                assert isinstance(group_levels[level], (int, float))

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_with_status_filter(self, mock_deps, mock_mongo_db):
        """Test filtering teachers by status."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Test active teachers only (default)
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?status=active",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_teachers"] == 2
        
        # Test suspended teachers
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?status=suspended",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_teachers"] == 1
        assert data["teachers"][0]["teacher_name"] == "محمد عبد الرحمن"

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_with_search(self, mock_deps, mock_mongo_db):
        """Test searching teachers by name."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Search by first name
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?search=أحمد",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_teachers"] == 1
        assert "أحمد" in data["teachers"][0]["teacher_name"]
        
        # Search by last name
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?search=حسن",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_teachers"] == 1
        assert "حسن" in data["teachers"][0]["teacher_name"]

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_with_date_filter(self, mock_deps, mock_mongo_db):
        """Test filtering lessons by date range."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        now = datetime.utcnow()
        current_year = now.year
        current_month = now.month
        
        # Test with month and year filter
        response = client.get(
            f"/api/v1/dashboard/stats/teachers-detailed?month={current_month}&year={current_year}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return teachers but with potentially different hour counts
        # depending on when the test runs
        assert "total_teachers" in data
        assert "teachers" in data

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_hours_calculation(self, mock_deps, mock_mongo_db):
        """Test that hours are calculated correctly."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find teacher1 (أحمد محمد علي)
        teacher1 = None
        for teacher in data["teachers"]:
            if "أحمد" in teacher["teacher_name"]:
                teacher1 = teacher
                break
        
        assert teacher1 is not None
        
        # Teacher1 should have:
        # - Individual: 1 hour (elementary) + 1.5 hours (secondary) = 2.5 hours
        # - Group: 2 hours (middle)
        assert teacher1["total_individual_hours"] == 2.5
        assert teacher1["total_group_hours"] == 2.0
        
        # Check individual hours by level
        individual_levels = teacher1["individual_hours_by_level"]
        assert individual_levels["elementary"] == 1.0
        assert individual_levels["secondary"] == 1.5
        assert individual_levels["middle"] == 0.0
        
        # Check group hours by level
        group_levels = teacher1["group_hours_by_level"]
        assert group_levels["middle"] == 2.0
        assert group_levels["elementary"] == 0.0
        assert group_levels["secondary"] == 0.0

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_unauthorized(self, mock_deps, mock_mongo_db):
        """Test that unauthorized users cannot access the endpoint."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Test without authentication token
        response = client.get("/api/v1/dashboard/stats/teachers-detailed")
        assert response.status_code == 403  # Forbidden (no admin role)

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_empty_result(self, mock_deps, mock_mongo_db):
        """Test endpoint behavior when no teachers match filters."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Search for non-existent teacher
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?search=nonexistent",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_teachers"] == 0
        assert data["teachers"] == []

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_education_level_normalization(self, mock_deps, mock_mongo_db):
        """Test that education levels are normalized correctly."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Add a lesson with "primary" level (should be normalized to "elementary")
        lesson_with_primary = {
            "_id": ObjectId(),
            "teacher_id": str(self.teacher1_id),
            "subject": "Art",
            "education_level": "primary",  # This should be normalized to "elementary"
            "lesson_type": "individual",
            "duration_minutes": 30,  # 0.5 hours
            "status": "completed",
            "scheduled_date": datetime.utcnow(),
            "students": [{"student_name": "Student 9"}]
        }
        self.mock_db["lessons"].insert_one(lesson_with_primary)
        
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find teacher1 and check that primary was normalized to elementary
        teacher1 = None
        for teacher in data["teachers"]:
            if "أحمد" in teacher["teacher_name"]:
                teacher1 = teacher
                break
        
        assert teacher1 is not None
        # Should now have 1.5 hours elementary (1 + 0.5)
        assert teacher1["individual_hours_by_level"]["elementary"] == 1.5

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_teachers_sorted_by_total_hours(self, mock_deps, mock_mongo_db):
        """Test that teachers are sorted by total hours in descending order."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        teachers = data["teachers"]
        if len(teachers) >= 2:
            # Check that teachers are sorted by total hours (individual + group)
            for i in range(len(teachers) - 1):
                current_total = teachers[i]["total_individual_hours"] + teachers[i]["total_group_hours"]
                next_total = teachers[i + 1]["total_individual_hours"] + teachers[i + 1]["total_group_hours"]
                assert current_total >= next_total

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_teachers_detailed_stats_invalid_month_year(self, mock_deps, mock_mongo_db):
        """Test validation of month and year parameters."""
        # Configure the mocks
        mock_mongo_db.users_collection = self.mock_db["users"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Test invalid month
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?month=13",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test invalid year
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?year=1999",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test valid parameters
        response = client.get(
            "/api/v1/dashboard/stats/teachers-detailed?month=12&year=2024",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
