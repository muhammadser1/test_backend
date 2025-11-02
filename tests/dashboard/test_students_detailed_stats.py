"""
Tests for the detailed students statistics endpoint.
Tests the GET /dashboard/stats/students-detailed endpoint.
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


class TestStudentsDetailedStats:
    """Test cases for the detailed students statistics endpoint."""

    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self, mock_db):
        """Setup test data and cleanup after each test."""
        # Store mock_db for use in tests
        self.mock_db = mock_db
        
        # Clean up before test
        self.mock_db["users"].delete_many({})
        self.mock_db["students"].delete_many({})
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
        
        # Create test students
        self.student1_id = ObjectId()
        self.student2_id = ObjectId()
        self.student3_id = ObjectId()
        self.student4_id = ObjectId()
        
        students = [
            {
                "_id": self.student1_id,
                "full_name": "نادر حنيني",
                "email": "nader@test.com",
                "phone": "+1234567890",
                "education_level": "elementary",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "_id": self.student2_id,
                "full_name": "مهدي مسلم",
                "email": "mahdi@test.com",
                "phone": "+1234567891",
                "education_level": "elementary",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "_id": self.student3_id,
                "full_name": "مايا برقاوي",
                "email": "maya@test.com",
                "phone": "+1234567892",
                "education_level": "secondary",
                "is_active": True,
                "created_at": datetime.utcnow()
            },
            {
                "_id": self.student4_id,
                "full_name": "ادم قص",
                "email": "adam@test.com",
                "phone": "+1234567893",
                "education_level": "middle",
                "is_active": False,  # Inactive student
                "created_at": datetime.utcnow()
            }
        ]
        self.mock_db["students"].insert_many(students)
        
        # Create test lessons
        now = datetime.utcnow()
        lessons = [
            # Student 1 lessons (نادر حنيني)
            {
                "_id": ObjectId(),
                "teacher_id": "teacher1",
                "subject": "Math",
                "education_level": "elementary",
                "lesson_type": "individual",
                "duration_minutes": 60,  # 1 hour
                "status": "completed",
                "scheduled_date": now - timedelta(days=1),
                "students": [{"student_name": "نادر حنيني", "student_id": str(self.student1_id)}]
            },
            {
                "_id": ObjectId(),
                "teacher_id": "teacher1",
                "subject": "Arabic",
                "education_level": "elementary",
                "lesson_type": "individual",
                "duration_minutes": 180,  # 3 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=2),
                "students": [{"student_name": "نادر حنيني", "student_id": str(self.student1_id)}]
            },
            # Student 2 lessons (مهدي مسلم)
            {
                "_id": ObjectId(),
                "teacher_id": "teacher2",
                "subject": "Science",
                "education_level": "elementary",
                "lesson_type": "individual",
                "duration_minutes": 210,  # 3.5 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=1),
                "students": [{"student_name": "مهدي مسلم", "student_id": str(self.student2_id)}]
            },
            # Student 3 lessons (مايا برقاوي)
            {
                "_id": ObjectId(),
                "teacher_id": "teacher3",
                "subject": "English",
                "education_level": "secondary",
                "lesson_type": "individual",
                "duration_minutes": 120,  # 2 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=1),
                "students": [{"student_name": "مايا برقاوي", "student_id": str(self.student3_id)}]
            },
            {
                "_id": ObjectId(),
                "teacher_id": "teacher3",
                "subject": "History",
                "education_level": "secondary",
                "lesson_type": "group",
                "duration_minutes": 90,  # 1.5 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=2),
                "students": [
                    {"student_name": "مايا برقاوي", "student_id": str(self.student3_id)},
                    {"student_name": "Another Student", "student_id": "other_id"}
                ]
            },
            # Student 4 lessons (ادم قص) - inactive student
            {
                "_id": ObjectId(),
                "teacher_id": "teacher4",
                "subject": "Physics",
                "education_level": "middle",
                "lesson_type": "individual",
                "duration_minutes": 240,  # 4 hours
                "status": "completed",
                "scheduled_date": now - timedelta(days=1),
                "students": [{"student_name": "ادم قص", "student_id": str(self.student4_id)}]
            }
        ]
        self.mock_db["lessons"].insert_many(lessons)
        
        yield
        
        # Cleanup after test
        self.mock_db["users"].delete_many({})
        self.mock_db["students"].delete_many({})
        self.mock_db["lessons"].delete_many({})

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_success(self, mock_deps, mock_mongo_db):
        """Test successful retrieval of detailed student statistics."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "total_students" in data
        assert "students" in data
        assert isinstance(data["students"], list)
        
        # Should return 3 active students (student4 is inactive)
        assert data["total_students"] == 3
        assert len(data["students"]) == 3
        
        # Check student data structure
        for student in data["students"]:
            assert "student_id" in student
            assert "student_name" in student
            assert "individual_hours" in student
            assert "group_hours" in student
            assert "total_hours" in student
            assert "education_level" in student
            
            # All values should be numbers
            assert isinstance(student["individual_hours"], (int, float))
            assert isinstance(student["group_hours"], (int, float))
            assert isinstance(student["total_hours"], (int, float))
            assert isinstance(student["education_level"], str)

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_with_education_level_filter(self, mock_deps, mock_mongo_db):
        """Test filtering students by education level."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Test elementary students only
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?education_level=elementary",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 2
        for student in data["students"]:
            assert student["education_level"] == "elementary"
        
        # Test secondary students only
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?education_level=secondary",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 1
        assert data["students"][0]["education_level"] == "secondary"

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_with_search(self, mock_deps, mock_mongo_db):
        """Test searching students by name."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Search by first name
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?search=نادر",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 1
        assert "نادر" in data["students"][0]["student_name"]
        
        # Search by last name
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?search=برقاوي",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 1
        assert "برقاوي" in data["students"][0]["student_name"]

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_with_active_filter(self, mock_deps, mock_mongo_db):
        """Test filtering students by active status."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Test active students only (default)
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?is_active=true",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 3
        
        # Test inactive students
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?is_active=false",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 1
        assert data["students"][0]["student_name"] == "ادم قص"

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_with_date_filter(self, mock_deps, mock_mongo_db):
        """Test filtering lessons by date range."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        now = datetime.utcnow()
        current_year = now.year
        current_month = now.month
        
        # Test with month and year filter
        response = client.get(
            f"/api/v1/dashboard/stats/students-detailed?month={current_month}&year={current_year}",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return students but with potentially different hour counts
        # depending on when the test runs
        assert "total_students" in data
        assert "students" in data

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_hours_calculation(self, mock_deps, mock_mongo_db):
        """Test that hours are calculated correctly."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find student1 (نادر حنيني)
        student1 = None
        for student in data["students"]:
            if "نادر" in student["student_name"]:
                student1 = student
                break
        
        assert student1 is not None
        
        # Student1 should have:
        # - Individual: 1 hour + 3 hours = 4 hours
        # - Group: 0 hours
        # - Total: 4 hours
        assert student1["individual_hours"] == 4.0
        assert student1["group_hours"] == 0.0
        assert student1["total_hours"] == 4.0
        assert student1["education_level"] == "elementary"
        
        # Find student3 (مايا برقاوي)
        student3 = None
        for student in data["students"]:
            if "مايا" in student["student_name"]:
                student3 = student
                break
        
        assert student3 is not None
        
        # Student3 should have:
        # - Individual: 2 hours
        # - Group: 1.5 hours
        # - Total: 3.5 hours
        assert student3["individual_hours"] == 2.0
        assert student3["group_hours"] == 1.5
        assert student3["total_hours"] == 3.5
        assert student3["education_level"] == "secondary"

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_unauthorized(self, mock_deps, mock_mongo_db):
        """Test that unauthorized users cannot access the endpoint."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Test without authentication token
        response = client.get("/api/v1/dashboard/stats/students-detailed")
        assert response.status_code == 403  # Forbidden (no admin role)

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_empty_result(self, mock_deps, mock_mongo_db):
        """Test endpoint behavior when no students match filters."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Search for non-existent student
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?search=nonexistent",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_students"] == 0
        assert data["students"] == []

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_education_level_normalization(self, mock_deps, mock_mongo_db):
        """Test that education levels are normalized correctly."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Add a student with "primary" level (should be normalized to "elementary")
        student_with_primary = {
            "_id": ObjectId(),
            "full_name": "Test Primary Student",
            "email": "primary@test.com",
            "phone": "+1234567899",
            "education_level": "primary",  # This should be normalized to "elementary"
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        self.mock_db["students"].insert_one(student_with_primary)
        
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find the primary student and check that it was normalized to elementary
        primary_student = None
        for student in data["students"]:
            if student["student_name"] == "Test Primary Student":
                primary_student = student
                break
        
        assert primary_student is not None
        assert primary_student["education_level"] == "elementary"

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_students_sorted_by_total_hours(self, mock_deps, mock_mongo_db):
        """Test that students are sorted by total hours in descending order."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        students = data["students"]
        if len(students) >= 2:
            # Check that students are sorted by total hours
            for i in range(len(students) - 1):
                assert students[i]["total_hours"] >= students[i + 1]["total_hours"]

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_invalid_month_year(self, mock_deps, mock_mongo_db):
        """Test validation of month and year parameters."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Test invalid month
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?month=13",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test invalid year
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?year=1999",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test valid parameters
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed?month=12&year=2024",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200

    @patch('app.api.v1.endpoints.dashboard.mongo_db')
    @patch('app.api.deps.mongo_db')
    def test_get_students_detailed_stats_only_approved_completed_lessons(self, mock_deps, mock_mongo_db):
        """Test that only approved and completed lessons are counted."""
        # Configure the mocks
        mock_mongo_db.students_collection = self.mock_db["students"]
        mock_mongo_db.lessons_collection = self.mock_db["lessons"]
        mock_deps.users_collection = self.mock_db["users"]
        
        # Add a pending lesson for student1
        pending_lesson = {
            "_id": ObjectId(),
            "teacher_id": "teacher1",
            "subject": "Math",
            "education_level": "elementary",
            "lesson_type": "individual",
            "duration_minutes": 60,  # 1 hour
            "status": "pending",  # This should not be counted
            "scheduled_date": datetime.utcnow(),
            "students": [{"student_name": "نادر حنيني", "student_id": str(self.student1_id)}]
        }
        self.mock_db["lessons"].insert_one(pending_lesson)
        
        response = client.get(
            "/api/v1/dashboard/stats/students-detailed",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Find student1 and verify the pending lesson was not counted
        student1 = None
        for student in data["students"]:
            if "نادر" in student["student_name"]:
                student1 = student
                break
        
        assert student1 is not None
        # Should still be 4 hours (not 5) because pending lesson is not counted
        assert student1["individual_hours"] == 4.0
        assert student1["total_hours"] == 4.0
