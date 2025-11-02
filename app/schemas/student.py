"""
Student Schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.lesson import EducationLevel


class StudentCreate(BaseModel):
    """Create a new student"""
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = None
    education_level: Optional[EducationLevel] = Field(None, description="Education level (elementary, middle, secondary)")
    notes: Optional[str] = None


class StudentUpdate(BaseModel):
    """Update student information"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = None
    education_level: Optional[EducationLevel] = Field(None, description="Education level (elementary, middle, secondary)")
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class StudentResponse(BaseModel):
    """Student response"""
    id: str
    full_name: str
    phone: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    """List of students"""
    total: int
    students: list[StudentResponse]

