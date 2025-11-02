from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# -----------------------------------------------------------
# ENUMS
# -----------------------------------------------------------
class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# -----------------------------------------------------------
# AUTH / LOGIN MODELS
# -----------------------------------------------------------
class LoginRequest(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class Token(BaseModel):
    """Access token returned to client"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """JWT payload data"""
    sub: str              # user id
    username: str
    role: UserRole
    exp: Optional[int] = None  # expiration timestamp


class UserSummary(BaseModel):
    """Minimal user info returned after login"""
    id: str
    username: str
    role: UserRole
    status: UserStatus
    last_login: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Token + user info returned after successful login"""
    access_token: str
    token_type: str = "bearer"
    user: UserSummary


class LogoutResponse(BaseModel):
    """Response when user logs out"""
    message: str = "Successfully logged out"


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)


class ProfileUpdate(BaseModel):
    """User updates their own profile"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


# -----------------------------------------------------------
# USER CREATION / UPDATE MODELS
# -----------------------------------------------------------
class UserCreate(BaseModel):
    """Admin creates a teacher or another admin"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: UserRole
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birthdate: Optional[datetime] = None


class UserUpdate(BaseModel):
    """Admin updates user information"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[UserStatus] = None
    role: Optional[UserRole] = None


class TeacherSignup(BaseModel):
    """Teacher self-signup"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone: Optional[str] = None
    birthdate: Optional[datetime] = None  # Format: YYYY-MM-DD


# -----------------------------------------------------------
# RESPONSE MODELS
# -----------------------------------------------------------
class UserResponse(BaseModel):
    """Full user information response"""
    id: str
    username: str
    role: UserRole
    status: UserStatus
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    birthdate: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
