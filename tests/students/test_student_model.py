"""
Tests for Student Model
"""
import pytest
from datetime import datetime
from app.models.student import Student


def test_student_creation():
    """Test creating a student"""
    student = Student(
        full_name="محمد أحمد علي",
        email="mohammed@example.com",
        phone="+1234567890",
        birthdate=datetime(2010, 5, 15)
    )
    
    assert student.full_name == "محمد أحمد علي"
    assert student.email == "mohammed@example.com"
    assert student.phone == "+1234567890"
    assert student.is_active is True


def test_student_to_dict():
    """Test converting student to dictionary"""
    student = Student(
        full_name="محمد أحمد علي",
        email="mohammed@example.com"
    )
    
    student_dict = student.to_dict()
    
    assert student_dict["full_name"] == "محمد أحمد علي"
    assert student_dict["email"] == "mohammed@example.com"
    assert student_dict["is_active"] is True
    assert "_id" in student_dict


def test_student_from_dict():
    """Test creating student from dictionary"""
    data = {
        "_id": "test-id-123",
        "full_name": "محمد أحمد علي",
        "email": "mohammed@example.com",
        "phone": "+1234567890",
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    student = Student.from_dict(data)
    
    assert student._id == "test-id-123"
    assert student.full_name == "محمد أحمد علي"
    assert student.email == "mohammed@example.com"


def test_student_default_active():
    """Test that student is active by default"""
    student = Student(full_name="Test Student")
    assert student.is_active is True


def test_student_repr():
    """Test student string representation"""
    student = Student(
        _id="test-id",
        full_name="Test Student",
        is_active=True
    )
    
    repr_str = repr(student)
    assert "test-id" in repr_str
    assert "Test Student" in repr_str
    assert "active=True" in repr_str

