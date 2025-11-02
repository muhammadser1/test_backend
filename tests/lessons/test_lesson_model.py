"""
Comprehensive tests for Lesson model
Tests: Business logic, data conversion, database operations
"""
import pytest
from datetime import datetime
from app.models.lesson import Lesson, LessonType, LessonStatus


class TestLessonModelCreation:
    """Test Lesson model instantiation"""
    
    def test_create_lesson_with_required_fields(self):
        """Test creating lesson with only required fields"""
        lesson = Lesson(
            teacher_id="teacher-123",
            teacher_name="John Teacher",
            title="Math Lesson",
            subject="Mathematics",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 15, 10, 0),
            duration_minutes=60
        )
        
        assert lesson.teacher_id == "teacher-123"
        assert lesson.teacher_name == "John Teacher"
        assert lesson.title == "Math Lesson"
        assert lesson.subject == "Mathematics"
        assert lesson.lesson_type == LessonType.INDIVIDUAL
        assert lesson.duration_minutes == 60
        assert lesson.status == LessonStatus.PENDING  # Default
        assert lesson._id is not None  # Auto-generated
        assert lesson.created_at is not None
        assert lesson.students == []
    
    def test_create_lesson_with_all_fields(self):
        """Test creating lesson with all fields"""
        students = [
            {"student_name": "Student 1", "student_email": "s1@example.com"},
            {"student_name": "Student 2", "student_email": "s2@example.com"}
        ]
        
        lesson = Lesson(
            teacher_id="teacher-456",
            teacher_name="Jane Teacher",
            title="Physics Group Lesson",
            description="Introduction to Physics",
            subject="Physics",
            lesson_type=LessonType.GROUP,
            scheduled_date=datetime(2024, 2, 20, 14, 0),
            duration_minutes=90,
            max_students=10,
            status=LessonStatus.COMPLETED,
            students=students,
            notes="Great session",
            homework="Chapter 5 exercises",
            _id="custom-lesson-id",
            completed_at=datetime(2024, 2, 20, 15, 30)
        )
        
        assert lesson._id == "custom-lesson-id"
        assert lesson.max_students == 10
        assert lesson.status == LessonStatus.COMPLETED
        assert len(lesson.students) == 2
        assert lesson.notes == "Great session"
        assert lesson.homework == "Chapter 5 exercises"
    
    def test_lesson_id_auto_generation(self):
        """Test that lesson ID is auto-generated if not provided"""
        lesson1 = Lesson(
            teacher_id="t1",
            teacher_name="Teacher 1",
            title="Lesson 1",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        lesson2 = Lesson(
            teacher_id="t2",
            teacher_name="Teacher 2",
            title="Lesson 2",
            subject="Physics",
            lesson_type=LessonType.GROUP,
            scheduled_date=datetime(2024, 1, 2),
            duration_minutes=60
        )
        
        assert lesson1._id is not None
        assert lesson2._id is not None
        assert lesson1._id != lesson2._id


class TestLessonBusinessLogic:
    """Test Lesson model business logic methods"""
    
    def test_is_pending_returns_true_for_pending_lesson(self):
        """Test is_pending() for pending lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.PENDING
        )
        assert lesson.is_pending() is True
    
    def test_is_pending_returns_false_for_completed_lesson(self):
        """Test is_pending() for completed lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.COMPLETED
        )
        assert lesson.is_pending() is False
    
    def test_is_completed_returns_true_for_completed_lesson(self):
        """Test is_completed() for completed lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.COMPLETED
        )
        assert lesson.is_completed() is True
    
    def test_is_cancelled_returns_true_for_cancelled_lesson(self):
        """Test is_cancelled() for cancelled lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.CANCELLED
        )
        assert lesson.is_cancelled() is True
    
    def test_is_individual_returns_true_for_individual_lesson(self):
        """Test is_individual() for individual lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        assert lesson.is_individual() is True
    
    def test_is_group_returns_true_for_group_lesson(self):
        """Test is_group() for group lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.GROUP,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        assert lesson.is_group() is True
    
    def test_can_be_updated_returns_true_for_pending(self):
        """Test can_be_updated() returns True for pending lessons"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.PENDING
        )
        assert lesson.can_be_updated() is True
    
    def test_can_be_updated_returns_false_for_completed(self):
        """Test can_be_updated() returns False for completed lessons"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.COMPLETED
        )
        assert lesson.can_be_updated() is False
    
    def test_get_duration_hours_converts_correctly(self):
        """Test get_duration_hours() converts minutes to hours"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=90  # 1.5 hours
        )
        assert lesson.get_duration_hours() == 1.5
    
    def test_get_student_count_returns_correct_count(self):
        """Test get_student_count() returns number of students"""
        students = [
            {"student_name": "S1"},
            {"student_name": "S2"},
            {"student_name": "S3"}
        ]
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.GROUP,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            students=students
        )
        assert lesson.get_student_count() == 3
    
    def test_mark_completed_sets_status_and_timestamps(self):
        """Test mark_completed() updates status and sets completed_at"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.PENDING
        )
        
        assert lesson.completed_at is None
        
        lesson.mark_completed()
        
        assert lesson.status == LessonStatus.COMPLETED
        assert lesson.completed_at is not None
        assert lesson.updated_at is not None
    
    def test_cancel_sets_status_and_updated_at(self):
        """Test cancel() updates status and sets updated_at"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.PENDING
        )
        
        lesson.cancel()
        
        assert lesson.status == LessonStatus.CANCELLED
        assert lesson.updated_at is not None


class TestLessonDataConversion:
    """Test Lesson model data conversion methods"""
    
    def test_to_dict_converts_all_fields(self):
        """Test to_dict() includes all lesson fields"""
        students = [{"student_name": "Student 1"}]
        lesson = Lesson(
            teacher_id="teacher-123",
            teacher_name="John Teacher",
            title="Math Lesson",
            description="Algebra basics",
            subject="Mathematics",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 15),
            duration_minutes=60,
            max_students=5,
            students=students,
            notes="Test notes",
            homework="Page 10-15"
        )
        
        data = lesson.to_dict()
        
        assert data["_id"] == lesson._id
        assert data["teacher_id"] == "teacher-123"
        assert data["teacher_name"] == "John Teacher"
        assert data["title"] == "Math Lesson"
        assert data["lesson_type"] == "individual"  # Enum to value
        assert data["status"] == "pending"  # Enum to value
        assert data["students"] == students
    
    def test_to_dict_handles_enum_conversion(self):
        """Test to_dict() properly converts enums to strings"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Test",
            subject="Math",
            lesson_type=LessonType.GROUP,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.COMPLETED
        )
        
        data = lesson.to_dict()
        
        assert data["lesson_type"] == "group"
        assert data["status"] == "completed"
        assert isinstance(data["lesson_type"], str)
        assert isinstance(data["status"], str)
    
    def test_from_dict_creates_lesson_from_database_doc(self):
        """Test from_dict() recreates Lesson from database document"""
        doc = {
            "_id": "lesson-123",
            "teacher_id": "teacher-456",
            "teacher_name": "Test Teacher",
            "title": "Chemistry Lesson",
            "description": "Chemical reactions",
            "subject": "Chemistry",
            "lesson_type": "group",
            "scheduled_date": datetime(2024, 1, 20),
            "duration_minutes": 90,
            "max_students": 8,
            "status": "pending",
            "students": [{"student_name": "S1"}],
            "notes": "Good session",
            "homework": "Lab report",
            "created_at": datetime(2024, 1, 10),
            "updated_at": None,
            "completed_at": None
        }
        
        lesson = Lesson.from_dict(doc)
        
        assert lesson._id == "lesson-123"
        assert lesson.teacher_id == "teacher-456"
        assert lesson.title == "Chemistry Lesson"
        assert lesson.lesson_type == LessonType.GROUP
        assert lesson.status == LessonStatus.PENDING
    
    def test_roundtrip_conversion(self):
        """Test Lesson -> dict -> Lesson maintains data"""
        original = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Roundtrip",
            subject="Physics",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 3, 1),
            duration_minutes=60,
            students=[{"student_name": "Student 1"}]
        )
        
        data = original.to_dict()
        recreated = Lesson.from_dict(data)
        
        assert recreated.teacher_id == original.teacher_id
        assert recreated.title == original.title
        assert recreated.lesson_type == original.lesson_type
        assert recreated.duration_minutes == original.duration_minutes


class TestLessonDatabaseMethods:
    """Test Lesson model database interaction methods"""
    
    def test_find_by_id_returns_lesson_when_exists(self, mock_db):
        """Test find_by_id() finds existing lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Find Me",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        mock_db["lessons"].insert_one(lesson.to_dict())
        
        found = Lesson.find_by_id(lesson._id, mock_db["lessons"])
        
        assert found is not None
        assert found._id == lesson._id
        assert found.title == "Find Me"
    
    def test_find_by_id_returns_none_when_not_exists(self, mock_db):
        """Test find_by_id() returns None for non-existent lesson"""
        found = Lesson.find_by_id("nonexistent-id", mock_db["lessons"])
        assert found is None
    
    def test_find_by_teacher_id_returns_all_teacher_lessons(self, mock_db):
        """Test find_by_teacher_id() finds all lessons by teacher"""
        teacher_id = "teacher-123"
        
        lesson1 = Lesson(
            teacher_id=teacher_id,
            teacher_name="Teacher",
            title="Lesson 1",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        lesson2 = Lesson(
            teacher_id=teacher_id,
            teacher_name="Teacher",
            title="Lesson 2",
            subject="Physics",
            lesson_type=LessonType.GROUP,
            scheduled_date=datetime(2024, 1, 2),
            duration_minutes=90
        )
        lesson3 = Lesson(
            teacher_id="other-teacher",
            teacher_name="Other",
            title="Lesson 3",
            subject="Chemistry",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 3),
            duration_minutes=60
        )
        
        mock_db["lessons"].insert_one(lesson1.to_dict())
        mock_db["lessons"].insert_one(lesson2.to_dict())
        mock_db["lessons"].insert_one(lesson3.to_dict())
        
        found = Lesson.find_by_teacher_id(teacher_id, mock_db["lessons"])
        
        assert len(found) == 2
        assert all(l.teacher_id == teacher_id for l in found)
    
    def test_find_by_status_returns_matching_lessons(self, mock_db):
        """Test find_by_status() finds lessons by status"""
        lesson1 = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Pending 1",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.PENDING
        )
        lesson2 = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Completed",
            subject="Physics",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 2),
            duration_minutes=60,
            status=LessonStatus.COMPLETED
        )
        lesson3 = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Pending 2",
            subject="Chemistry",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 3),
            duration_minutes=60,
            status=LessonStatus.PENDING
        )
        
        mock_db["lessons"].insert_one(lesson1.to_dict())
        mock_db["lessons"].insert_one(lesson2.to_dict())
        mock_db["lessons"].insert_one(lesson3.to_dict())
        
        pending = Lesson.find_by_status(LessonStatus.PENDING, mock_db["lessons"])
        
        assert len(pending) == 2
        assert all(l.is_pending() for l in pending)
    
    def test_calculate_total_hours_sums_lesson_durations(self):
        """Test calculate_total_hours() sums durations and converts to hours"""
        lesson1 = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="L1",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        lesson2 = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="L2",
            subject="Physics",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 2),
            duration_minutes=90
        )
        lesson3 = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="L3",
            subject="Chemistry",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 3),
            duration_minutes=120
        )
        
        lessons = [lesson1, lesson2, lesson3]
        total_hours = Lesson.calculate_total_hours(lessons)
        
        assert total_hours == 4.5  # (60 + 90 + 120) / 60 = 4.5
    
    def test_calculate_total_hours_returns_zero_for_empty_list(self):
        """Test calculate_total_hours() returns 0 for empty list"""
        total = Lesson.calculate_total_hours([])
        assert total == 0.0
    
    def test_save_inserts_lesson_into_database(self, mock_db):
        """Test save() inserts lesson document into database"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Save Test",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        
        # Database should be empty
        assert mock_db["lessons"].count_documents({}) == 0
        
        # Save lesson
        lesson.save(mock_db["lessons"])
        
        # Lesson should be in database
        assert mock_db["lessons"].count_documents({}) == 1
        found = mock_db["lessons"].find_one({"title": "Save Test"})
        assert found is not None
    
    def test_update_in_db_updates_lesson_fields(self, mock_db):
        """Test update_in_db() updates lesson in database"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="Old Title",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60
        )
        mock_db["lessons"].insert_one(lesson.to_dict())
        
        # Update lesson
        update_data = {"title": "New Title", "notes": "Updated notes"}
        lesson.update_in_db(mock_db["lessons"], update_data)
        
        # Check database
        found = mock_db["lessons"].find_one({"_id": lesson._id})
        assert found["title"] == "New Title"
        assert found["notes"] == "Updated notes"
        assert found["updated_at"] is not None
    
    def test_delete_cancels_lesson(self, mock_db):
        """Test delete() soft deletes by cancelling lesson"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="Teacher",
            title="To Delete",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.PENDING
        )
        mock_db["lessons"].insert_one(lesson.to_dict())
        
        # Delete lesson (soft delete)
        lesson.delete(mock_db["lessons"])
        
        # Lesson still exists but is cancelled
        found = mock_db["lessons"].find_one({"_id": lesson._id})
        assert found is not None
        assert found["status"] == "cancelled"


class TestLessonRepr:
    """Test Lesson model string representation"""
    
    def test_repr_shows_lesson_info(self):
        """Test __repr__() shows lesson ID, title, teacher, and status"""
        lesson = Lesson(
            teacher_id="t1",
            teacher_name="John Teacher",
            title="Math Lesson",
            subject="Math",
            lesson_type=LessonType.INDIVIDUAL,
            scheduled_date=datetime(2024, 1, 1),
            duration_minutes=60,
            status=LessonStatus.PENDING,
            _id="lesson-456"
        )
        
        repr_str = repr(lesson)
        
        assert "lesson-456" in repr_str
        assert "Math Lesson" in repr_str
        assert "John Teacher" in repr_str
        assert "pending" in repr_str.lower() or "PENDING" in repr_str

