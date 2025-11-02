from pydantic import BaseModel
from typing import List, Optional


class SubjectEarnings(BaseModel):
    """Earnings breakdown for a specific subject, education level, and lesson type."""
    subject: str
    education_level: str  # "elementary", "middle", or "secondary"
    lesson_type: str  # "individual" or "group"
    total_hours: float
    price_per_hour: float
    total_earnings: float
    lesson_count: int


class TeacherEarningsReport(BaseModel):
    """Complete earnings report for a teacher."""
    teacher_id: str
    teacher_name: str
    month: Optional[int] = None
    year: Optional[int] = None
    total_hours: float
    total_earnings: float
    by_subject: List[SubjectEarnings]
    total_lessons: int


class SubjectPriceResponse(BaseModel):
    """Subject pricing information."""
    subject: str
    individual_price: float
    group_price: float


class AllSubjectPricesResponse(BaseModel):
    """All subject prices."""
    prices: List[SubjectPriceResponse]
    default_individual_price: float
    default_group_price: float


class EducationLevelHours(BaseModel):
    """Hours breakdown by education level."""
    elementary: float = 0.0  # ابتدائي
    middle: float = 0.0      # إعدادي
    secondary: float = 0.0   # ثانوي


class TeacherDetailedStats(BaseModel):
    """Detailed teacher statistics with education level breakdowns."""
    teacher_id: str
    teacher_name: str
    total_individual_hours: float
    total_group_hours: float
    individual_hours_by_level: EducationLevelHours
    group_hours_by_level: EducationLevelHours


class TeachersDetailedStatsResponse(BaseModel):
    """Response for detailed teachers statistics."""
    total_teachers: int
    teachers: List[TeacherDetailedStats]


class StudentDetailedStats(BaseModel):
    """Detailed student statistics with education level breakdowns."""
    student_id: str
    student_name: str
    individual_hours: float
    group_hours: float
    total_hours: float
    education_level: str  # "elementary", "middle", or "secondary"


class StudentsDetailedStatsResponse(BaseModel):
    """Response for detailed students statistics."""
    total_students: int
    students: List[StudentDetailedStats]