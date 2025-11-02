"""
Complete End-to-End Integration Tests

This module contains comprehensive workflow tests that simulate real user scenarios:
- User authentication and password management  
- Creating and managing lessons (individual and group)
- Filtering and aggregating data by various criteria
- Testing the complete flow from login to data analysis
"""

import pytest
from unittest.mock import patch
from app.schemas.user import UserRole, UserStatus
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def setup_test_users(mock_db):
    """Setup admin and teacher users in the database."""
    # Create admin user
    admin = User(
        username="admin_user",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        first_name="Admin",
        last_name="Test",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE
    )
    mock_db["users"].insert_one(admin.to_dict())
    
    # Create teacher user
    teacher = User(
        username="teacher_user",
        email="teacher@test.com",
        hashed_password=get_password_hash("teacher123"),
        first_name="Teacher",
        last_name="Test",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        phone="1234567890"
    )
    mock_db["users"].insert_one(teacher.to_dict())
    
    return {"admin": admin, "teacher": teacher}


class TestCompleteAuthFlow:
    """Test complete authentication and password management workflow."""
    
    def test_login_admin_reset_password_relogin(self, client, mock_db, setup_test_users):
        """
        Complete workflow:
        1. Teacher logs in successfully
        2. Admin logs in and resets teacher's password
        3. Teacher tries old password (should fail)
        4. Teacher logs in with new password (should succeed)
        """
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_user_mongo, \
             patch('app.api.v1.endpoints.admin.mongo_db') as mock_admin_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            
            mock_user_mongo.users_collection = mock_db["users"]
            mock_admin_mongo.users_collection = mock_db["users"]
            mock_deps.users_collection = mock_db["users"]
            
            # Step 1: Teacher logs in
            login = client.post(
                "/api/v1/user/login",
                json={"username": "teacher_user", "password": "teacher123"}
            )
            assert login.status_code == 200
            teacher_token = login.json()["access_token"]
            print("\n[PASS] Step 1: Teacher logged in successfully")
            
            # Step 2: Admin logs in and resets password
            admin_login = client.post(
                "/api/v1/user/login",
                json={"username": "admin_user", "password": "admin123"}
            )
            assert admin_login.status_code == 200
            admin_token = admin_login.json()["access_token"]
            
            teacher_id = setup_test_users["teacher"]._id
            reset = client.post(
                f"/api/v1/admin/users/{teacher_id}/reset-password",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"new_password": "newpass456"}
            )
            assert reset.status_code == 200
            print("[PASS] Step 2: Admin reset teacher's password")
            
            # Step 3: Old password should fail
            old_login = client.post(
                "/api/v1/user/login",
                json={"username": "teacher_user", "password": "teacher123"}
            )
            assert old_login.status_code == 401
            print("[PASS] Step 3: Old password rejected")
            
            # Step 4: New password should work
            new_login = client.post(
                "/api/v1/user/login",
                json={"username": "teacher_user", "password": "newpass456"}
            )
            assert new_login.status_code == 200
            new_token = new_login.json()["access_token"]
            assert new_token != teacher_token
            print("[PASS] Step 4: New password works!\n")


class TestCompleteLessonFlow:
    """Test complete lesson creation and filtering workflow."""
    
    def test_create_lessons_and_filter_by_type_and_subject(self, client, mock_db, setup_test_users):
        """
        Complete workflow:
        1. Login as teacher
        2. Create 10+ individual lessons with different subjects (some repeated)
        3. Create group lessons
        4. Filter by type (individual vs group)
        5. Filter by subject and verify totals
        6. Calculate hours by category
        """
        with patch('app.api.v1.endpoints.user.mongo_db') as mock_user_mongo, \
             patch('app.api.v1.endpoints.lessons.mongo_db') as mock_lesson_mongo, \
             patch('app.api.deps.mongo_db') as mock_deps:
            
            mock_user_mongo.users_collection = mock_db["users"]
            mock_lesson_mongo.users_collection = mock_db["users"]
            mock_lesson_mongo.lessons_collection = mock_db["lessons"]
            mock_deps.users_collection = mock_db["users"]
            
            # Step 1: Login
            login = client.post(
                "/api/v1/user/login",
                json={"username": "teacher_user", "password": "teacher123"}
            )
            token = login.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("\n[PASS] Step 1: Teacher logged in")
            
            # Step 2: Create individual lessons (12 total)
            individual_data = [
                # Mathematics (3 lessons)
                ("Mathematics", 60), ("Mathematics", 90), ("Mathematics", 60),
                # Physics (3 lessons)
                ("Physics", 120), ("Physics", 60), ("Physics", 90),
                # Chemistry (2 lessons)
                ("Chemistry", 60), ("Chemistry", 120),
                # Biology (2 lessons)  
                ("Biology", 90), ("Biology", 60),
                # English (2 lessons)
                ("English", 60), ("English", 90),
            ]
            
            for idx, (subject, duration) in enumerate(individual_data):
                resp = client.post(
                    "/api/v1/lessons/submit",
                    headers=headers,
                    json={
                        "title": f"{subject} Lesson {idx+1}",
                        "lesson_type": "individual",
                        "subject": subject,
                        "scheduled_date": f"2024-01-{10+idx:02d}T10:00:00",
                        "duration_minutes": duration,
                        "students": [{"student_name": f"Student {idx+1}"}],
                        "max_students": 1
                    }
                )
                assert resp.status_code == 201
            
            print("[PASS] Step 2: Created 12 individual lessons")
            
            # Step 3: Create group lessons (5 total)
            group_data = [
                ("Mathematics", 120, ["S1", "S2", "S3"]),
                ("Physics", 90, ["S4", "S5"]),
                ("Chemistry", 120, ["S6", "S7", "S8"]),
                ("Biology", 60, ["S9", "S10"]),
                ("English", 90, ["S11", "S12"]),
            ]
            
            for idx, (subject, duration, students) in enumerate(group_data):
                resp = client.post(
                    "/api/v1/lessons/submit",
                    headers=headers,
                    json={
                        "title": f"{subject} Group Lesson {idx+1}",
                        "lesson_type": "group",
                        "subject": subject,
                        "scheduled_date": f"2024-02-{10+idx:02d}T14:00:00",
                        "duration_minutes": duration,
                        "students": [{"student_name": name} for name in students],
                        "max_students": len(students)
                    }
                )
                assert resp.status_code == 201
            
            print("[PASS] Step 3: Created 5 group lessons")
            
            # Step 4: Get all lessons
            all_lessons_resp = client.get("/api/v1/lessons/my-lessons", headers=headers)
            assert all_lessons_resp.status_code == 200
            lessons_data = all_lessons_resp.json()
            all_lessons = lessons_data["lessons"]
            assert len(all_lessons) == 17  # 12 individual + 5 group
            assert lessons_data["total_lessons"] == 17
            assert lessons_data["total_hours"] == 24.0
            print("[PASS] Step 4: Retrieved all 17 lessons (24.0 total hours)")
            
            # Step 5: Filter by type
            individual_count = sum(1 for l in all_lessons if l["lesson_type"] == "individual")
            group_count = sum(1 for l in all_lessons if l["lesson_type"] == "group")
            assert individual_count == 12
            assert group_count == 5
            print(f"[PASS] Step 5: Filtered by type - Individual: {individual_count}, Group: {group_count}")
            
            # Step 6: Analyze by subject
            subjects = {}
            for lesson in all_lessons:
                subj = lesson["subject"]
                if subj not in subjects:
                    subjects[subj] = {"total": 0, "individual": 0, "group": 0, "hours": 0.0}
                
                subjects[subj]["total"] += 1
                hours = lesson["duration_minutes"] / 60.0
                subjects[subj]["hours"] += hours
                
                if lesson["lesson_type"] == "individual":
                    subjects[subj]["individual"] += 1
                else:
                    subjects[subj]["group"] += 1
            
            # Verify Mathematics: 3 individual + 1 group = 4 total
            assert subjects["Mathematics"]["total"] == 4
            assert subjects["Mathematics"]["individual"] == 3
            assert subjects["Mathematics"]["group"] == 1
            assert subjects["Mathematics"]["hours"] == 5.5  # (60+90+60)/60 + 120/60 = 3.5 + 2.0
            
            # Verify Physics: 3 individual + 1 group = 4 total
            assert subjects["Physics"]["total"] == 4
            assert subjects["Physics"]["individual"] == 3
            assert subjects["Physics"]["group"] == 1
            assert subjects["Physics"]["hours"] == 6.0  # (120+60+90)/60 + 90/60 = 4.5 + 1.5
            
            print("\n[PASS] Step 6: Subject Analysis:")
            for subj, data in subjects.items():
                print(f"  {subj}: {data['total']} lessons ({data['individual']} individual, "
                      f"{data['group']} group) = {data['hours']} hours")
            
            # Step 7: Calculate overall totals
            total_individual_hours = sum(
                l["duration_minutes"] / 60.0 
                for l in all_lessons if l["lesson_type"] == "individual"
            )
            total_group_hours = sum(
                l["duration_minutes"] / 60.0 
                for l in all_lessons if l["lesson_type"] == "group"
            )
            
            # Individual: 60+90+60+120+60+90+60+120+90+60+60+90 = 960 min = 16 hours
            assert total_individual_hours == 16.0
            # Group: 120+90+120+60+90 = 480 min = 8 hours
            assert total_group_hours == 8.0
            # Total: 24 hours
            assert total_individual_hours + total_group_hours == 24.0
            
            print("\n[PASS] Step 7: Overall Totals:")
            print(f"  Individual hours: {total_individual_hours}")
            print(f"  Group hours: {total_group_hours}")
            print(f"  Total hours: {total_individual_hours + total_group_hours}\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
