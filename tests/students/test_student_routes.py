"""
Tests for Student API Routes
"""
import pytest
from datetime import datetime
from unittest.mock import patch
from app.models.user import User, UserRole, UserStatus
from app.models.student import Student
from app.core.security import get_password_hash, create_access_token


class TestStudentCreate:
    """Test POST /students/"""
    
    def test_create_student_as_admin(self, client, mock_db):
        """Test creating a student as admin"""
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
        
        sample_student_data = {
            "full_name": "محمد أحمد علي",
            "email": "mohammed@example.com",
            "phone": "+1234567890",
            "birthdate": "2010-05-15T00:00:00",
            "notes": "Test student"
        }
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/students/",
                json=sample_student_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["full_name"] == "محمد أحمد علي"
            assert data["email"] == "mohammed@example.com"
            assert data["is_active"] is True
            assert "id" in data
    
    def test_create_student_as_teacher_should_fail(self, client, mock_db):
        """Test that teachers cannot create students"""
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
        
        sample_student_data = {
            "full_name": "محمد أحمد علي",
            "email": "mohammed@example.com"
        }
        
        with patch('app.api.deps.mongo_db') as mock_deps:
            mock_deps.users_collection = mock_db["users"]
            
            response = client.post(
                "/api/v1/students/",
                json=sample_student_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 403


class TestStudentGet:
    """Test GET /students/"""
    
    def test_get_all_students_as_admin(self, client, mock_db):
        """Test getting all students as admin"""
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
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/students/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "students" in data
    
    def test_get_all_students_as_teacher(self, client, mock_db):
        """Test that teachers can view students"""
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
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/students/",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "students" in data


class TestStudentSearch:
    """Test GET /students/search"""
    
    def test_search_students(self, client, mock_db):
        """Test searching students by name"""
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
        
        # Create a student
        student = Student(
            full_name="محمد أحمد علي",
            email="mohammed@example.com",
            is_active=True
        )
        mock_db["students"].insert_one(student.to_dict())
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            # Search for the student
            response = client.get(
                "/api/v1/students/search?name=محمد",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] >= 1
            assert any("محمد" in student["full_name"] for student in data["students"])


class TestStudentGetById:
    """Test GET /students/{student_id}"""
    
    def test_get_student_by_id(self, client, mock_db):
        """Test getting a student by ID"""
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
        
        # Create a student
        student = Student(
            full_name="محمد أحمد علي",
            email="mohammed@example.com",
            is_active=True
        )
        mock_db["students"].insert_one(student.to_dict())
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            # Get the student
            response = client.get(
                f"/api/v1/students/{student._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == student._id
            assert data["full_name"] == "محمد أحمد علي"
    
    def test_get_nonexistent_student(self, client, mock_db):
        """Test getting a student that doesn't exist"""
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
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.get(
                "/api/v1/students/nonexistent-id",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 404


class TestStudentUpdate:
    """Test PUT /students/{student_id}"""
    
    def test_update_student(self, client, mock_db):
        """Test updating a student"""
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
        
        # Create a student
        student = Student(
            full_name="محمد أحمد علي",
            email="mohammed@example.com",
            is_active=True
        )
        mock_db["students"].insert_one(student.to_dict())
        
        update_data = {
            "full_name": "أحمد محمد علي",
            "phone": "+9876543210"
        }
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            response = client.put(
                f"/api/v1/students/{student._id}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["full_name"] == "أحمد محمد علي"
            assert data["phone"] == "+9876543210"


class TestStudentDelete:
    """Test DELETE /students/{student_id}"""
    
    def test_delete_student(self, client, mock_db):
        """Test deleting a student (soft delete)"""
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
        
        # Create a student
        student = Student(
            full_name="محمد أحمد علي",
            email="mohammed@example.com",
            is_active=True
        )
        mock_db["students"].insert_one(student.to_dict())
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            # Delete the student
            response = client.delete(
                f"/api/v1/students/{student._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 204
            
            # Verify student is marked as inactive
            get_response = client.get(
                f"/api/v1/students/{student._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert get_response.json()["is_active"] is False


class TestStudentEdgeCases:
    """Test edge cases for student operations"""
    
    def test_create_student_with_duplicate_email(self, client, mock_db):
        """Test creating a student with duplicate email"""
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
        
        # Create first student
        student = Student(
            full_name="محمد أحمد علي",
            email="mohammed@example.com",
            is_active=True
        )
        mock_db["students"].insert_one(student.to_dict())
        
        sample_student_data = {
            "full_name": "أحمد محمد علي",
            "email": "mohammed@example.com"
        }
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            # Try to create another student with same email
            response = client.post(
                "/api/v1/students/",
                json=sample_student_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 400
            assert "already exists" in response.json()["detail"]
    
    def test_get_students_include_inactive(self, client, mock_db):
        """Test getting students including inactive ones"""
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
        
        # Create a student
        student = Student(
            full_name="محمد أحمد علي",
            email="mohammed@example.com",
            is_active=True
        )
        mock_db["students"].insert_one(student.to_dict())
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            # Delete the student
            client.delete(
                f"/api/v1/students/{student._id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Get all students without inactive
            response = client.get(
                "/api/v1/students/",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert student._id not in [s["id"] for s in response.json()["students"]]
            
            # Get all students with inactive
            response = client.get(
                "/api/v1/students/?include_inactive=true",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert student._id in [s["id"] for s in response.json()["students"]]
    
    def test_search_students_case_insensitive(self, client, mock_db):
        """Test that student search is case-insensitive"""
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
        
        # Create a student with Arabic name
        student = Student(
            full_name="محمد أحمد علي",
            email="mohammed@example.com",
            is_active=True
        )
        mock_db["students"].insert_one(student.to_dict())
        
        with patch('app.api.v1.endpoints.students.mongo_db') as mock_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            mock_mongo.students_collection = mock_db["students"]
            mock_deps.users_collection = mock_db["users"]
            
            # Search with different case
            response = client.get(
                "/api/v1/students/search?name=محمد",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            assert response.json()["total"] >= 1
