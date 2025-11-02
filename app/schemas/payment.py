from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


# -----------------------------------------------------------
# PAYMENT MODELS
# -----------------------------------------------------------
class PaymentCreate(BaseModel):
    """Create a new student payment"""
    student_name: str = Field(..., min_length=1, max_length=100)
    student_email: Optional[str] = None
    amount: float = Field(..., gt=0)
    payment_date: datetime
    lesson_id: Optional[str] = None  # Link to lesson if applicable
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response"""
    id: str
    student_name: str
    student_email: Optional[str] = None
    amount: float
    payment_date: datetime
    lesson_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class MonthlyPaymentsResponse(BaseModel):
    """Monthly payment statistics"""
    month: int
    year: int
    total_payments: int
    total_amount: float
    payments: list[PaymentResponse]

