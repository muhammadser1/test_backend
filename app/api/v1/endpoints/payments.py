from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
from app.schemas.payment import PaymentCreate, PaymentResponse, MonthlyPaymentsResponse
from app.models.payment import Payment
from app.api.deps import get_current_admin
from app.db import mongo_db
from app.core.pricing import get_subject_price

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_data: PaymentCreate,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin adds a new student payment
    """
    # Create payment using Payment model
    new_payment = Payment(
        student_name=payment_data.student_name,
        student_email=payment_data.student_email,
        amount=payment_data.amount,
        payment_date=payment_data.payment_date,
        lesson_id=payment_data.lesson_id,
        notes=payment_data.notes,
        created_by=str(current_admin["_id"])
    )
    
    # Save to database using model method
    new_payment.save(mongo_db.payments_collection)
    
    # Return payment response
    return PaymentResponse(
        id=new_payment._id,
        student_name=new_payment.student_name,
        student_email=new_payment.student_email,
        amount=new_payment.amount,
        payment_date=new_payment.payment_date,
        lesson_id=new_payment.lesson_id,
        notes=new_payment.notes,
        created_at=new_payment.created_at,
    )


@router.get("/")
def get_payments(
    current_admin: Dict = Depends(get_current_admin),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    student_name: Optional[str] = Query(None, description="Filter by student name"),
):
    """
    Admin gets student payments with flexible filtering
    
    Default behavior:
    - No filters: Show all payments
    
    Filter by month:
    - If month provided, year is required: Show only payments from that month
    
    Filter by student name:
    - If student_name provided: Show all payments for that student (all months)
    
    Both filters:
    - If month + year + student_name: Show payments for that student in that month
    """
    # Validate: if month is provided, year must also be provided
    if month is not None and year is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year is required when filtering by month. Please provide both month and year."
        )
    
    # Build query based on filters
    query = {}
    
    # Filter by month and year if provided
    if month and year:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        query["payment_date"] = {"$gte": start_date, "$lt": end_date}
    
    # Filter by student name if provided
    if student_name:
        query["student_name"] = {"$regex": student_name, "$options": "i"}
    
    # Get payments from database
    if query:
        payment_docs = mongo_db.payments_collection.find(query).sort("payment_date", -1)
    else:
        # No filters - get all payments
        payment_docs = mongo_db.payments_collection.find({}).sort("payment_date", -1)
    
    payments = [Payment.from_dict(doc) for doc in payment_docs]
    
    # Calculate total amount
    total_amount = Payment.calculate_total(payments)
    
    # Convert to response
    payment_responses = [
        PaymentResponse(
            id=payment._id,
            student_name=payment.student_name,
            student_email=payment.student_email,
            amount=payment.amount,
            payment_date=payment.payment_date,
            lesson_id=payment.lesson_id,
            notes=payment.notes,
            created_at=payment.created_at,
        )
        for payment in payments
    ]
    
    # Build response
    response = {
        "total_payments": len(payments),
        "total_amount": total_amount,
        "payments": payment_responses
    }
    
    # Add filter info if filters were applied
    if month and year:
        response["filter"] = {
            "month": month,
            "year": year,
            "note": "Filtered by month and year"
        }
    
    if student_name:
        if "filter" not in response:
            response["filter"] = {}
        response["filter"]["student_name"] = student_name
        response["filter"]["note"] = "Filtered by student name" + (" and month" if month and year else "")
    
    return response


@router.get("/student/{student_name}")
def get_student_payments(
    student_name: str,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin gets all payments for a specific student
    - Shows all payments made by the student
    - Shows total amount paid
    """
    # Get all payments for the student
    payments = Payment.find_by_student_name(student_name, mongo_db.payments_collection)
    
    if not payments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No payments found for student '{student_name}'"
        )
    
    # Calculate total amount
    total_amount = Payment.calculate_total(payments)
    
    # Convert to response
    payment_responses = [
        PaymentResponse(
            id=payment._id,
            student_name=payment.student_name,
            student_email=payment.student_email,
            amount=payment.amount,
            payment_date=payment.payment_date,
            lesson_id=payment.lesson_id,
            notes=payment.notes,
            created_at=payment.created_at,
        )
        for payment in payments
    ]
    
    return {
        "student_name": student_name,
        "total_payments": len(payments),
        "total_amount": total_amount,
        "payments": payment_responses
    }


@router.get("/student/{student_name}/total")
def get_student_total(
    student_name: str,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin gets total amount paid by a specific student
    - Quick summary endpoint
    """
    # Get all payments for the student
    payments = Payment.find_by_student_name(student_name, mongo_db.payments_collection)
    
    # Calculate total amount
    total_amount = Payment.calculate_total(payments)
    
    return {
        "student_name": student_name,
        "total_payments": len(payments),
        "total_amount": total_amount,
        "currency": "USD"
    }


@router.get("/student/{student_name}/cost-summary")
def get_student_cost_summary(
    student_name: str,
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin gets student cost summary (lessons cost vs paid amount)
    - Shows total lessons cost for approved/completed lessons
    - Shows total paid amount
    - Shows outstanding balance
    - Optional month/year filter
    """
    # Build query for lessons
    lesson_query = {
        "students.student_name": {"$regex": student_name, "$options": "i"},
        "status": {"$in": ["approved", "completed"]}  # Only count approved or completed lessons
    }
    
    # Date filter
    if month or year:
        if not (month and year):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both month and year are required for filtering"
            )
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
    
    # Get all lessons for this student
    lessons = list(mongo_db.lessons_collection.find(lesson_query))
    
    # Calculate total lesson cost
    total_cost = 0.0
    missing_subjects = []
    for lesson in lessons:
        subject = lesson.get("subject", "")
        education_level = lesson.get("education_level", "elementary")
        lesson_type = lesson.get("lesson_type", "individual")
        duration_minutes = lesson.get("duration_minutes", 0)
        hours = duration_minutes / 60
        
        # Get price per hour from pricing system
        from app.models.pricing import Pricing
        pricing = Pricing.find_by_subject_and_level(subject, education_level, mongo_db.pricing_collection)
        
        if pricing:
            price_per_hour = pricing.get_price(lesson_type)
        else:
            # Subject not found, use default
            from app.core.pricing import DEFAULT_INDIVIDUAL_PRICE, DEFAULT_GROUP_PRICE
            price_per_hour = DEFAULT_INDIVIDUAL_PRICE if lesson_type.lower() == "individual" else DEFAULT_GROUP_PRICE
            missing_subjects.append({
                "subject": subject,
                "education_level": education_level,
                "lesson_type": lesson_type,
                "used_default_price": price_per_hour
            })
        
        lesson_cost = hours * price_per_hour
        total_cost += lesson_cost
    
    # Get total paid
    payment_query = {"student_name": {"$regex": student_name, "$options": "i"}}
    if month and year:
        payment_query["payment_date"] = {"$gte": start_date, "$lt": end_date}
    
    payments = list(mongo_db.payments_collection.find(payment_query))
    total_paid = sum(p.get("amount", 0) for p in payments)
    
    # Calculate outstanding balance
    outstanding_balance = round(total_cost - total_paid, 2)
    
    response = {
        "student_name": student_name,
        "total_lessons_cost": round(total_cost, 2),
        "total_paid": round(total_paid, 2),
        "outstanding_balance": outstanding_balance,
        "lessons_count": len(lessons),
        "payments_count": len(payments),
        "currency": "USD"
    }
    
    # Warn if any subjects were not found in pricing database
    if missing_subjects:
        response["warning"] = {
            "message": "Some subjects not found in pricing database, used default prices",
            "missing_subjects": missing_subjects
        }
    
    # Add filter info if month/year provided
    if month and year:
        response["filter"] = {
            "month": month,
            "year": year,
            "note": "Statistics filtered by month and year"
        }
    
    return response


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(
    payment_id: str,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin deletes a payment record
    """
    payment = Payment.find_by_id(payment_id, mongo_db.payments_collection)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    payment.delete(mongo_db.payments_collection)
    return None
