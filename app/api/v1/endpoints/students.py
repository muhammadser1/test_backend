"""
Student Management Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Optional
from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse
)
from app.models.student import Student
from app.api.deps import get_current_admin, get_current_user, get_current_admin_or_teacher
from app.db import mongo_db

router = APIRouter()


# ===== Admin Endpoints (CRUD) =====

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    current_user: Dict = Depends(get_current_admin_or_teacher)
):
    """
    Admin or Teacher creates a new student
    """
    # Check if student name already exists
    if Student.name_exists(student_data.full_name, mongo_db.students_collection):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with name '{student_data.full_name}' already exists"
        )
    
    # Create student
    new_student = Student(
        full_name=student_data.full_name,
        phone=student_data.phone,
        education_level=student_data.education_level,
        notes=student_data.notes
    )
    
    new_student.save(mongo_db.students_collection)
    
    return StudentResponse(
        id=new_student._id,
        full_name=new_student.full_name,
        phone=new_student.phone,
        education_level=new_student.education_level,
        notes=new_student.notes,
        is_active=new_student.is_active,
        created_at=new_student.created_at,
        updated_at=new_student.updated_at
    )


@router.get("/", response_model=StudentListResponse)
def get_all_students(
    include_inactive: bool = False,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all students
    - Teachers and admins can view
    - Optional: include inactive students
    """
    if include_inactive:
        students = Student.get_all(mongo_db.students_collection)
    else:
        students = Student.get_all_active(mongo_db.students_collection)
    
    student_responses = [
        StudentResponse(
            id=s._id,
            full_name=s.full_name,
            phone=s.phone,
            education_level=s.education_level,
            notes=s.notes,
            is_active=s.is_active,
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in students
    ]
    
    return StudentListResponse(
        total=len(student_responses),
        students=student_responses
    )


@router.get("/search", response_model=StudentListResponse)
def search_students(
    name: str = Query(..., min_length=1, description="Search by student name"),
    current_user: Dict = Depends(get_current_user)
):
    """
    Search students by name
    - Teachers and admins can search
    - Case-insensitive, partial match
    """
    students = Student.find_by_name(name, mongo_db.students_collection)
    
    student_responses = [
        StudentResponse(
            id=s._id,
            full_name=s.full_name,
            phone=s.phone,
            education_level=s.education_level,
            notes=s.notes,
            is_active=s.is_active,
            created_at=s.created_at,
            updated_at=s.updated_at
        )
        for s in students
    ]
    
    return StudentListResponse(
        total=len(student_responses),
        students=student_responses
    )


@router.get("/{student_id}", response_model=StudentResponse)
def get_student_by_id(
    student_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get student by ID
    - Teachers and admins can view
    """
    student = Student.find_by_id(student_id, mongo_db.students_collection)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return StudentResponse(
        id=student._id,
        full_name=student.full_name,
        phone=student.phone,
        education_level=student.education_level,
        notes=student.notes,
        is_active=student.is_active,
        created_at=student.created_at,
        updated_at=student.updated_at
    )


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin updates student information
    """
    student = Student.find_by_id(student_id, mongo_db.students_collection)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update fields
    update_data = student_update.model_dump(exclude_unset=True)
    
    # Check if name is being updated and if it already exists
    if "full_name" in update_data and update_data["full_name"] != student.full_name:
        if Student.name_exists(update_data["full_name"], mongo_db.students_collection, exclude_id=student_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with name '{update_data['full_name']}' already exists"
            )
    
    for field, value in update_data.items():
        if hasattr(student, field):
            setattr(student, field, value)
    
    student.update_in_db(mongo_db.students_collection, update_data)
    
    return StudentResponse(
        id=student._id,
        full_name=student.full_name,
        phone=student.phone,
        education_level=student.education_level,
        notes=student.notes,
        is_active=student.is_active,
        created_at=student.created_at,
        updated_at=student.updated_at
    )


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: str,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin deletes student (soft delete - marks as inactive)
    """
    student = Student.find_by_id(student_id, mongo_db.students_collection)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student.delete(mongo_db.students_collection)
    return None

