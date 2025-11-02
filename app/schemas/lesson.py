from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# -----------------------------------------------------------
# ENUMS
# -----------------------------------------------------------
class LessonType(str, Enum):
    """Defines whether a lesson is individual or group."""
    INDIVIDUAL = "individual"
    GROUP = "group"


class LessonStatus(str, Enum):
    """Lesson life cycle."""
    PENDING = "pending"      # Waiting for admin approval
    APPROVED = "approved"       # Admin approved the lesson
    REJECTED = "rejected"     # Admin rejected the lesson
    COMPLETED = "completed"   # Lesson finished
    CANCELLED = "cancelled"   # Soft deleted or cancelled


class EducationLevel(str, Enum):
    """Education levels for lessons and pricing"""
    ELEMENTARY = "elementary"  # ابتدائي
    MIDDLE = "middle"  # اعدادي
    SECONDARY = "secondary"  # ثانوي


# -----------------------------------------------------------
# STUDENT INFO
# -----------------------------------------------------------
class StudentInfo(BaseModel):
    """Student information in a lesson."""
    student_name: str = Field(..., min_length=1, max_length=100)
    student_email: Optional[str] = None


# -----------------------------------------------------------
# LESSON MODELS
# -----------------------------------------------------------
class LessonBase(BaseModel):
    """Base lesson information shared by all models."""
    subject: str = Field(..., min_length=1, max_length=100)
    education_level: EducationLevel = Field(..., description="Education level (elementary, middle, secondary)")
    lesson_type: LessonType
    scheduled_date: datetime
    duration_minutes: int = Field(..., gt=0, le=480)  # 1–480 min
    max_students: Optional[int] = Field(None, gt=0)


class LessonCreate(LessonBase):
    """Used to create a new lesson."""
    teacher_id: Optional[str] = None
    students: Optional[List[StudentInfo]] = Field(default_factory=list)


class LessonUpdate(BaseModel):
    """Used to edit lesson info or mark status. Can only update if NOT completed."""
    subject: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    scheduled_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, gt=0, le=480)
    max_students: Optional[int] = Field(None, gt=0)
    students: Optional[List[StudentInfo]] = None
    status: Optional[LessonStatus] = None


class LessonResponse(LessonBase):
    """Returned when fetching a lesson."""
    id: str
    teacher_id: str
    teacher_name: str
    status: LessonStatus
    students: List[StudentInfo] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LessonsStatsResponse(BaseModel):
    """Statistics for lessons with filters applied."""
    total_lessons: int
    total_hours: float
    lessons: List[LessonResponse]
