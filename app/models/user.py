from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# MongoDB Model (works with PyMongo)
class User:
    """
    User Model - Represents the 'users' collection in MongoDB
    This works with PyMongo (not an ORM, just helper methods)
    """
    
    def __init__(
        self,
        username: str,
        hashed_password: str,
        role: UserRole = UserRole.TEACHER,
        status: UserStatus = UserStatus.ACTIVE,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        birthdate: Optional[datetime] = None,
        _id: Optional[str] = None,
        last_login: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or str(uuid.uuid4())
        self.username = username
        self.hashed_password = hashed_password
        self.role = role
        self.status = status
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.birthdate = birthdate
        self.last_login = last_login
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User object to dictionary for MongoDB insertion"""
        return {
            "_id": self._id,
            "username": self.username,
            "hashed_password": self.hashed_password,
            "role": self.role.value if isinstance(self.role, UserRole) else self.role,
            "status": self.status.value if isinstance(self.status, UserStatus) else self.status,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "birthdate": self.birthdate,
            "last_login": self.last_login,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create User object from MongoDB document"""
        return cls(
            _id=data.get("_id"),
            username=data.get("username"),
            hashed_password=data.get("hashed_password"),
            role=UserRole(data.get("role", "teacher")),
            status=UserStatus(data.get("status", "active")),
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone=data.get("phone"),
            birthdate=data.get("birthdate"),
            last_login=data.get("last_login"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    # Business logic methods
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE
    
    def is_admin(self) -> bool:
        """Check if user is an admin"""
        return self.role == UserRole.ADMIN
    
    def is_teacher(self) -> bool:
        """Check if user is a teacher"""
        return self.role == UserRole.TEACHER
    
    def get_full_name(self) -> str:
        """Get user's full name or username as fallback"""
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full_name if full_name else self.username
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
    
    # Static database methods
    @staticmethod
    def find_by_username(username: str, db_collection) -> Optional["User"]:
        """Find user by username from database"""
        user_doc = db_collection.find_one({"username": username})
        if user_doc:
            return User.from_dict(user_doc)
        return None
    
    @staticmethod
    def find_by_email(email: str, db_collection) -> Optional["User"]:
        """Find user by email from database"""
        user_doc = db_collection.find_one({"email": email})
        if user_doc:
            return User.from_dict(user_doc)
        return None
    
    @staticmethod
    def find_by_id(user_id: str, db_collection) -> Optional["User"]:
        """Find user by ID from database"""
        user_doc = db_collection.find_one({"_id": user_id})
        if user_doc:
            return User.from_dict(user_doc)
        return None
    
    @staticmethod
    def username_exists(username: str, db_collection) -> bool:
        """Check if username already exists"""
        return db_collection.find_one({"username": username}) is not None
    
    @staticmethod
    def email_exists(email: str, db_collection) -> bool:
        """Check if email already exists"""
        return db_collection.find_one({"email": email}) is not None
    
    def save(self, db_collection):
        """Insert user into database"""
        db_collection.insert_one(self.to_dict())
    
    def update_in_db(self, db_collection, update_data: Dict[str, Any]):
        """Update user in database"""
        update_data["updated_at"] = datetime.utcnow()
        db_collection.update_one(
            {"_id": self._id},
            {"$set": update_data}
        )
    
    def __repr__(self):
        return f"<User(id={self._id}, username={self.username}, role={self.role})>"

