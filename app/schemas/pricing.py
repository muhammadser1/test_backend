"""
Pricing Schemas for API request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class EducationLevel(str, Enum):
    """Education levels for pricing"""
    ELEMENTARY = "elementary"  # ابتدائي
    MIDDLE = "middle"  # اعدادي
    SECONDARY = "secondary"  # ثانوي


class PricingBase(BaseModel):
    """Base pricing information"""
    subject: str = Field(..., min_length=1, max_length=100, description="Subject name (e.g., Mathematics, Physics, Arabic)")
    education_level: EducationLevel = Field(..., description="Education level (elementary, middle, secondary)")
    individual_price: float = Field(..., gt=0, description="Price per hour for individual lessons")
    group_price: float = Field(..., gt=0, description="Price per hour for group lessons")
    
    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v):
        """Ensure subject is properly formatted"""
        return v.strip().title()  # "mathematics" -> "Mathematics"


class PricingCreate(PricingBase):
    """Schema for creating new pricing"""
    pass


class PricingUpdate(BaseModel):
    """Schema for updating pricing (all fields optional)"""
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    education_level: Optional[EducationLevel] = None
    individual_price: Optional[float] = Field(None, gt=0)
    group_price: Optional[float] = Field(None, gt=0)
    
    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v):
        if v:
            return v.strip().title()
        return v


class PricingResponse(PricingBase):
    """Schema for pricing response"""
    id: str = Field(..., description="Pricing ID")
    
    class Config:
        from_attributes = True


class PricingListResponse(BaseModel):
    """Schema for list of pricing"""
    total: int
    pricing: list[PricingResponse]


class PricingLookupResponse(BaseModel):
    """Schema for price lookup by subject, education level, and lesson type"""
    subject: str
    education_level: str
    lesson_type: str
    price_per_hour: float
    found: bool = True

