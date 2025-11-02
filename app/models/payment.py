from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid


# MongoDB Model (works with PyMongo)
class Payment:
    """
    Payment Model - Represents the 'payments' collection in MongoDB
    This works with PyMongo (not an ORM, just helper methods)
    """
    
    def __init__(
        self,
        student_name: str,
        amount: float,
        payment_date: datetime,
        created_by: str,  # Admin ID who created the payment
        student_email: Optional[str] = None,
        lesson_id: Optional[str] = None,
        notes: Optional[str] = None,
        _id: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self._id = _id or str(uuid.uuid4())
        self.student_name = student_name
        self.student_email = student_email
        self.amount = amount
        self.payment_date = payment_date
        self.lesson_id = lesson_id
        self.notes = notes
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Payment object to dictionary for MongoDB insertion"""
        return {
            "_id": self._id,
            "student_name": self.student_name,
            "student_email": self.student_email,
            "amount": self.amount,
            "payment_date": self.payment_date,
            "lesson_id": self.lesson_id,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payment":
        """Create Payment object from MongoDB document"""
        return cls(
            _id=data.get("_id"),
            student_name=data.get("student_name"),
            student_email=data.get("student_email"),
            amount=data.get("amount"),
            payment_date=data.get("payment_date"),
            lesson_id=data.get("lesson_id"),
            notes=data.get("notes"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
        )
    
    # Business logic methods
    def is_recent(self, days: int = 30) -> bool:
        """Check if payment was made within the last N days"""
        days_ago = datetime.utcnow() - timedelta(days=days)
        return self.payment_date >= days_ago
    
    def get_month(self) -> int:
        """Get the month of payment"""
        return self.payment_date.month
    
    def get_year(self) -> int:
        """Get the year of payment"""
        return self.payment_date.year
    
    # Static database methods
    @staticmethod
    def find_by_id(payment_id: str, db_collection) -> Optional["Payment"]:
        """Find payment by ID from database"""
        payment_doc = db_collection.find_one({"_id": payment_id})
        if payment_doc:
            return Payment.from_dict(payment_doc)
        return None
    
    @staticmethod
    def find_by_student_name(student_name: str, db_collection) -> list["Payment"]:
        """Find all payments by student name (case-insensitive)"""
        payment_docs = db_collection.find({
            "student_name": {"$regex": student_name, "$options": "i"}
        })
        return [Payment.from_dict(doc) for doc in payment_docs]
    
    @staticmethod
    def find_by_month(month: int, year: int, db_collection) -> list["Payment"]:
        """Find all payments in a specific month"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        payment_docs = db_collection.find({
            "payment_date": {
                "$gte": start_date,
                "$lt": end_date
            }
        }).sort("payment_date", -1)
        
        return [Payment.from_dict(doc) for doc in payment_docs]
    
    @staticmethod
    def find_by_lesson_id(lesson_id: str, db_collection) -> list["Payment"]:
        """Find all payments for a specific lesson"""
        payment_docs = db_collection.find({"lesson_id": lesson_id})
        return [Payment.from_dict(doc) for doc in payment_docs]
    
    @staticmethod
    def calculate_total(payments: list["Payment"]) -> float:
        """Calculate total amount from list of payments"""
        return round(sum(p.amount for p in payments), 2)
    
    def save(self, db_collection):
        """Insert payment into database"""
        db_collection.insert_one(self.to_dict())
    
    def delete(self, db_collection):
        """Delete payment from database"""
        db_collection.delete_one({"_id": self._id})
    
    def __repr__(self):
        return f"<Payment(id={self._id}, student={self.student_name}, amount={self.amount})>"

