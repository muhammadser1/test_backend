from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


# Enums
class LessonType(str, Enum):
    INDIVIDUAL = "individual"
    GROUP = "group"


class LessonStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EducationLevel(str, Enum):
    """Education levels for lessons and pricing"""
    ELEMENTARY = "elementary"  # ابتدائي
    MIDDLE = "middle"  # اعدادي
    SECONDARY = "secondary"  # ثانوي


# MongoDB Model (works with PyMongo)
class Lesson:
    """
    Lesson Model - Represents the 'lessons' collection in MongoDB
    This works with PyMongo (not an ORM, just helper methods)
    """
    
    def __init__(
        self,
        teacher_id: str,
        teacher_name: str,
        subject: str,
        education_level: EducationLevel,
        lesson_type: LessonType,
        scheduled_date: datetime,
        duration_minutes: int,
        status: LessonStatus = LessonStatus.PENDING,
        max_students: Optional[int] = None,
        students: Optional[List[Dict[str, Any]]] = None,
        _id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        self._id = _id or str(uuid.uuid4())
        self.teacher_id = teacher_id
        self.teacher_name = teacher_name
        self.lesson_type = lesson_type
        self.subject = subject
        self.education_level = education_level
        self.scheduled_date = scheduled_date
        self.duration_minutes = duration_minutes
        self.max_students = max_students
        self.status = status
        self.students = students or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
        self.completed_at = completed_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Lesson object to dictionary for MongoDB insertion"""
        return {
            "_id": self._id,
            "teacher_id": self.teacher_id,
            "teacher_name": self.teacher_name,
            "lesson_type": self.lesson_type.value if isinstance(self.lesson_type, LessonType) else self.lesson_type,
            "subject": self.subject,
            "education_level": self.education_level.value if isinstance(self.education_level, EducationLevel) else self.education_level,
            "scheduled_date": self.scheduled_date,
            "duration_minutes": self.duration_minutes,
            "max_students": self.max_students,
            "status": self.status.value if isinstance(self.status, LessonStatus) else self.status,
            "students": self.students,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lesson":
        """Create Lesson object from MongoDB document"""
        return cls(
            _id=data.get("_id"),
            teacher_id=data.get("teacher_id"),
            teacher_name=data.get("teacher_name"),
            lesson_type=LessonType(data.get("lesson_type", "individual")),
            subject=data.get("subject"),
            education_level=EducationLevel(data.get("education_level", "elementary")),
            scheduled_date=data.get("scheduled_date"),
            duration_minutes=data.get("duration_minutes"),
            max_students=data.get("max_students"),
            status=LessonStatus(data.get("status", "pending")),
            students=data.get("students", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            completed_at=data.get("completed_at")
        )
    
    # Business logic methods
    def is_pending(self) -> bool:
        """Check if lesson is pending"""
        return self.status == LessonStatus.PENDING
    
    def is_completed(self) -> bool:
        """Check if lesson is completed"""
        return self.status == LessonStatus.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if lesson is cancelled"""
        return self.status == LessonStatus.CANCELLED
    
    def is_individual(self) -> bool:
        """Check if lesson is individual"""
        return self.lesson_type == LessonType.INDIVIDUAL
    
    def is_group(self) -> bool:
        """Check if lesson is group"""
        return self.lesson_type == LessonType.GROUP
    
    def can_be_updated(self) -> bool:
        """Check if lesson can be updated (only pending lessons)"""
        return self.status == LessonStatus.PENDING
    
    def get_duration_hours(self) -> float:
        """Get lesson duration in hours"""
        return round(self.duration_minutes / 60, 2)
    
    def get_student_count(self) -> int:
        """Get number of students in this lesson"""
        return len(self.students)
    
    def mark_completed(self):
        """Mark lesson as completed"""
        self.status = LessonStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def cancel(self):
        """Cancel lesson"""
        self.status = LessonStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def approve(self):
        """Approve lesson (admin action)"""
        self.status = LessonStatus.APPROVED
        self.updated_at = datetime.utcnow()
    
    def reject(self):
        """Reject lesson (admin action)"""
        self.status = LessonStatus.REJECTED
        self.updated_at = datetime.utcnow()
    
    def is_approved(self) -> bool:
        """Check if lesson is approved"""
        return self.status == LessonStatus.APPROVED
    
    def is_rejected(self) -> bool:
        """Check if lesson is rejected"""
        return self.status == LessonStatus.REJECTED
    
    # Static database methods
    @staticmethod
    def find_by_id(lesson_id: str, db_collection) -> Optional["Lesson"]:
        """Find lesson by ID from database"""
        lesson_doc = db_collection.find_one({"_id": lesson_id})
        if lesson_doc:
            return Lesson.from_dict(lesson_doc)
        return None
    
    @staticmethod
    def find_by_teacher_id(teacher_id: str, db_collection) -> List["Lesson"]:
        """Find all lessons by teacher ID"""
        lesson_docs = db_collection.find({"teacher_id": teacher_id})
        return [Lesson.from_dict(doc) for doc in lesson_docs]
    
    @staticmethod
    def find_by_status(status: LessonStatus, db_collection) -> List["Lesson"]:
        """Find all lessons by status"""
        lesson_docs = db_collection.find({"status": status.value})
        return [Lesson.from_dict(doc) for doc in lesson_docs]
    
    @staticmethod
    def calculate_total_hours(lessons: List["Lesson"]) -> float:
        """Calculate total hours from list of lessons"""
        total_minutes = sum(lesson.duration_minutes for lesson in lessons)
        return round(total_minutes / 60, 2)
    
    def save(self, db_collection):
        """Insert lesson into database"""
        db_collection.insert_one(self.to_dict())
    
    def update_in_db(self, db_collection, update_data: Dict[str, Any]):
        """Update lesson in database"""
        update_data["updated_at"] = datetime.utcnow()
        db_collection.update_one(
            {"_id": self._id},
            {"$set": update_data}
        )
    
    def delete(self, db_collection):
        """Soft delete: Cancel lesson"""
        self.cancel()
        self.update_in_db(db_collection, {
            "status": self.status.value,
            "updated_at": self.updated_at
        })
    
    def __repr__(self):
        return f"<Lesson(id={self._id}, subject={self.subject}, teacher={self.teacher_name}, status={self.status})>"

