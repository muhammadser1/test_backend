"""
Student Model - Represents students in the system
"""
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from app.models.lesson import EducationLevel


class Student:
    """
    Student Model - Represents the 'students' collection in MongoDB
    """
    
    def __init__(
        self,
        full_name: str,
        phone: Optional[str] = None,
        education_level: Optional[EducationLevel] = None,
        notes: Optional[str] = None,
        is_active: bool = True,
        _id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = _id or str(uuid.uuid4())
        self.full_name = full_name
        self.phone = phone
        self.education_level = education_level
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Student object to dictionary for MongoDB insertion"""
        education_level_value = self.education_level.value if isinstance(self.education_level, EducationLevel) else self.education_level
        return {
            "_id": self._id,
            "full_name": self.full_name,
            "phone": self.phone,
            "education_level": education_level_value,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Student":
        """Create Student object from MongoDB document"""
        education_level = data.get("education_level")
        if education_level:
            try:
                education_level = EducationLevel(education_level)
            except ValueError:
                education_level = None
        
        return cls(
            _id=data.get("_id"),
            full_name=data.get("full_name"),
            phone=data.get("phone"),
            education_level=education_level,
            notes=data.get("notes"),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    # Static database methods
    @staticmethod
    def find_by_id(student_id: str, db_collection) -> Optional["Student"]:
        """Find student by ID from database"""
        student_doc = db_collection.find_one({"_id": student_id})
        if student_doc:
            return Student.from_dict(student_doc)
        return None
    
    @staticmethod
    def find_by_name(name: str, db_collection) -> list["Student"]:
        """Find students by name (case-insensitive, partial match)"""
        student_docs = db_collection.find({
            "full_name": {"$regex": name, "$options": "i"}
        })
        return [Student.from_dict(doc) for doc in student_docs]
    
    @staticmethod
    def name_exists(name: str, db_collection, exclude_id: Optional[str] = None) -> bool:
        """Check if student name already exists (case-insensitive exact match)"""
        query = {
            "full_name": {"$regex": f"^{name}$", "$options": "i"}
        }
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        return db_collection.find_one(query) is not None
    
    @staticmethod
    def find_by_email(email: str, db_collection) -> Optional["Student"]:
        """Find student by email"""
        student_doc = db_collection.find_one({"email": email})
        if student_doc:
            return Student.from_dict(student_doc)
        return None
    
    @staticmethod
    def get_all_active(db_collection) -> list["Student"]:
        """Get all active students"""
        student_docs = db_collection.find({"is_active": True}).sort("full_name", 1)
        return [Student.from_dict(doc) for doc in student_docs]
    
    @staticmethod
    def get_all(db_collection) -> list["Student"]:
        """Get all students (active and inactive)"""
        student_docs = db_collection.find().sort("full_name", 1)
        return [Student.from_dict(doc) for doc in student_docs]
    
    def save(self, db_collection):
        """Insert student into database"""
        db_collection.insert_one(self.to_dict())
    
    def update_in_db(self, db_collection, update_data: Dict[str, Any]):
        """Update student in database"""
        update_data["updated_at"] = datetime.utcnow()
        db_collection.update_one(
            {"_id": self._id},
            {"$set": update_data}
        )
    
    def delete(self, db_collection):
        """Soft delete: Mark student as inactive"""
        self.is_active = False
        self.update_in_db(db_collection, {"is_active": False})
    
    def __repr__(self):
        return f"<Student(id={self._id}, name={self.full_name}, active={self.is_active})>"

