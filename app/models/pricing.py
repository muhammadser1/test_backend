"""
Pricing Model for MongoDB

Represents subject pricing in the database.
Admins can manage pricing through API endpoints.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class EducationLevel(str, Enum):
    """Education levels for pricing"""
    ELEMENTARY = "elementary"  # ابتدائي
    MIDDLE = "middle"  # اعدادي
    SECONDARY = "secondary"  # ثانوي


class Pricing:
    """
    Pricing Model - Represents the 'pricing' collection in MongoDB
    Stores pricing per subject and education level for individual and group lessons
    """
    
    def __init__(
        self,
        subject: str,
        education_level: EducationLevel,
        individual_price: float,
        group_price: float,
        _id: Optional[str] = None
    ):
        self._id = _id or str(uuid.uuid4())
        self.subject = subject.strip()  # e.g., "Mathematics", "Physics", "Arabic"
        self.education_level = education_level  # elementary, middle, secondary
        self.individual_price = individual_price
        self.group_price = group_price
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Pricing object to dictionary for MongoDB insertion"""
        return {
            "_id": self._id,
            "subject": self.subject,
            "education_level": self.education_level.value if isinstance(self.education_level, EducationLevel) else self.education_level,
            "individual_price": self.individual_price,
            "group_price": self.group_price
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Pricing":
        """Create Pricing object from MongoDB document"""
        return Pricing(
            _id=data.get("_id"),
            subject=data.get("subject"),
            education_level=EducationLevel(data.get("education_level", "elementary")),
            individual_price=data.get("individual_price"),
            group_price=data.get("group_price")
        )
    
    # ===== Database Methods =====
    
    @staticmethod
    def find_by_subject_and_level(subject: str, education_level: str, db_collection) -> Optional["Pricing"]:
        """Find pricing by subject name and education level (case-insensitive)
        
        First tries exact match, then tries to find any pricing for the subject
        (handles cases where education_level is None or doesn't match)
        """
        # First, try exact match
        pricing_doc = db_collection.find_one({
            "subject": {"$regex": f"^{subject}$", "$options": "i"},
            "education_level": education_level
        })
        
        if pricing_doc:
            return Pricing.from_dict(pricing_doc)
        
        # If not found, try to find any pricing for this subject (handle None education_level)
        pricing_doc = db_collection.find_one({
            "subject": {"$regex": f"^{subject}$", "$options": "i"}
        })
        
        if pricing_doc:
            return Pricing.from_dict(pricing_doc)
        
        return None
    
    @staticmethod
    def find_by_subject(subject: str, db_collection) -> list["Pricing"]:
        """Find all pricing for a subject (all education levels)"""
        pricing_docs = db_collection.find({
            "subject": {"$regex": f"^{subject}$", "$options": "i"}
        }).sort("education_level", 1)
        return [Pricing.from_dict(doc) for doc in pricing_docs]
    
    @staticmethod
    def find_by_id(pricing_id: str, db_collection) -> Optional["Pricing"]:
        """Find pricing by ID"""
        pricing_doc = db_collection.find_one({"_id": pricing_id})
        if pricing_doc:
            return Pricing.from_dict(pricing_doc)
        return None
    
    @staticmethod
    def get_all(db_collection) -> list["Pricing"]:
        """Get all pricing"""
        pricing_docs = db_collection.find({}).sort("subject", 1)
        return [Pricing.from_dict(doc) for doc in pricing_docs]
    
    @staticmethod
    def subject_and_level_exists(subject: str, education_level: str, db_collection, exclude_id: Optional[str] = None) -> bool:
        """Check if subject + education level combination already exists (case-insensitive)"""
        query = {
            "subject": {"$regex": f"^{subject}$", "$options": "i"},
            "education_level": education_level
        }
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        return db_collection.count_documents(query) > 0
    
    def save(self, db_collection):
        """Insert pricing into database"""
        db_collection.insert_one(self.to_dict())
    
    def update_in_db(self, db_collection):
        """Update pricing in database"""
        db_collection.update_one(
            {"_id": self._id},
            {"$set": self.to_dict()}
        )
    
    @staticmethod
    def delete(pricing_id: str, db_collection) -> bool:
        """Delete pricing from database"""
        result = db_collection.delete_one({"_id": pricing_id})
        return result.deleted_count > 0
    
    # ===== Business Logic Methods =====
    
    def get_price(self, lesson_type: str) -> float:
        """Get price for specific lesson type"""
        if lesson_type.lower() == "group":
            return self.group_price
        return self.individual_price
    
    def calculate_earnings(self, hours: float, lesson_type: str) -> float:
        """Calculate earnings for given hours and lesson type"""
        price_per_hour = self.get_price(lesson_type)
        return round(hours * price_per_hour, 2)

