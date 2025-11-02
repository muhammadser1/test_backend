"""
Dashboard/Statistics Endpoints
Provides overview statistics for admins
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Dict, Optional
from app.api.deps import get_current_admin
from app.db import mongo_db
from app.schemas.earnings import TeacherEarningsReport, SubjectEarnings, TeachersDetailedStatsResponse, TeacherDetailedStats, EducationLevelHours, StudentsDetailedStatsResponse, StudentDetailedStats
from app.models.user import User
from app.core.pricing import get_subject_price, calculate_subject_earnings
from datetime import datetime
from collections import defaultdict

router = APIRouter()


@router.get("/stats")
def get_dashboard_stats(
    current_admin: Dict = Depends(get_current_admin),
    month: Optional[int] = None,
    year: Optional[int] = None
):
    """
    Admin dashboard statistics
    Optional filters: month (1-12) and year (2000-2100)
    
    Returns:
    - Total teachers count
    - Total students count
    - Pending lessons count
    - Completed lessons count
    - Cancelled lessons count
    - Total payments count
    - Total revenue
    """
    from datetime import datetime
    
    # Count teachers (always total, not filtered by month)
    teachers_count = mongo_db.users_collection.count_documents({"role": "teacher", "status": "active"})
    
    # Count admins (always total, not filtered by month)
    admins_count = mongo_db.users_collection.count_documents({"role": "admin", "status": "active"})
    
    # Count students (always total, not filtered by month)
    students_count = mongo_db.students_collection.count_documents({"is_active": True})
    
    # Build lesson query with optional month filter
    lesson_query = {}
    if month and year:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
    
    # Count lessons by status
    pending_query = {**lesson_query, "status": "pending"}
    completed_query = {**lesson_query, "status": "completed"}
    cancelled_query = {**lesson_query, "status": "cancelled"}
    
    pending_lessons_count = mongo_db.lessons_collection.count_documents(pending_query)
    completed_lessons_count = mongo_db.lessons_collection.count_documents(completed_query)
    cancelled_lessons_count = mongo_db.lessons_collection.count_documents(cancelled_query)
    total_lessons_count = mongo_db.lessons_collection.count_documents(lesson_query)
    
    # Build payment query with optional month filter
    payment_query = {}
    if month and year:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        payment_query["payment_date"] = {"$gte": start_date, "$lt": end_date}
    
    # Count payments and calculate total revenue
    payments_count = mongo_db.payments_collection.count_documents(payment_query)
    
    # Calculate total revenue from payments
    pipeline = [{"$match": payment_query}, {"$group": {"_id": None, "total": {"$sum": "$amount"}}}]
    result = list(mongo_db.payments_collection.aggregate(pipeline))
    total_revenue = result[0]["total"] if result else 0
    
    # Count pricing subjects (always total, not filtered by month)
    pricing_count = mongo_db.pricing_collection.count_documents({"is_active": True})
    
    response = {
        "users": {
            "total_teachers": teachers_count,
            "total_admins": admins_count,
            "total_users": teachers_count + admins_count
        },
        "students": {
            "total_students": students_count
        },
        "lessons": {
            "total_lessons": total_lessons_count,
            "pending_lessons": pending_lessons_count,
            "completed_lessons": completed_lessons_count,
            "cancelled_lessons": cancelled_lessons_count
        },
        "payments": {
            "total_payments": payments_count,
            "total_revenue": round(total_revenue, 2)
        },
        "pricing": {
            "active_subjects": pricing_count
        }
    }
    
    # Add filter info if month/year provided
    if month and year:
        response["filter"] = {
            "month": month,
            "year": year,
            "note": "Statistics filtered by month and year"
        }
    
    return response


@router.get("/stats/teachers")
def get_teachers_stats(
    current_admin: Dict = Depends(get_current_admin),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter lessons by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter lessons by year"),
    search: Optional[str] = Query(None, description="Search teachers by name or username"),
    status: Optional[str] = Query("active", description="Filter teachers by status (active, suspended, inactive)")
):
    """
    Get detailed statistics about teachers
    
    Optional filters:
    - month (1-12) and year (2000-2100): Filter lesson statistics by date range
    - search: Search for teachers by name or username
    - status: Filter teachers by status (default: active)
    
    Returns:
    - List of teachers with their lesson statistics
    - Total count of teachers
    """
    from datetime import datetime
    
    # Build teacher query
    teacher_query = {"role": "teacher"}
    
    # Add status filter
    if status:
        teacher_query["status"] = status
    
    # Add search filter
    if search:
        # Search by username, first_name, or last_name
        teacher_query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
        ]
    
    # Get teachers matching the filters
    teachers = list(mongo_db.users_collection.find(teacher_query))
    
    # Build lesson query with optional month/year filter
    lesson_query = {}
    if year:
        if month:
            # Filter by specific month and year
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
        else:
            # Filter by entire year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
    
    teacher_stats = []
    
    for teacher in teachers:
        teacher_id = teacher["_id"]
        teacher_id_str = str(teacher_id)  # Convert ObjectId to string
        teacher_name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip() or teacher["username"]
        
        # Count lessons for this teacher with date filter applied
        teacher_lesson_query = {**lesson_query, "teacher_id": teacher_id_str}
        teacher_lessons = list(mongo_db.lessons_collection.find(teacher_lesson_query))
        
        pending = len([l for l in teacher_lessons if l.get("status") == "pending"])
        completed = len([l for l in teacher_lessons if l.get("status") == "completed"])
        cancelled = len([l for l in teacher_lessons if l.get("status") == "cancelled"])
        
        # Calculate total hours taught
        total_minutes = sum(l.get("duration_minutes", 0) for l in teacher_lessons)
        total_hours = round(total_minutes / 60, 2)
        
        teacher_stats.append({
            "teacher_id": teacher_id_str,
            "teacher_name": teacher_name,
            "username": teacher["username"],
            "email": teacher.get("email"),
            "phone": teacher.get("phone"),
            "status": teacher.get("status"),
            "total_lessons": len(teacher_lessons),
            "pending_lessons": pending,
            "completed_lessons": completed,
            "cancelled_lessons": cancelled,
            "total_hours": total_hours,
            "created_at": teacher.get("created_at"),
            "last_login": teacher.get("last_login")
        })
    
    response = {
        "total_teachers": len(teacher_stats),
        "teachers": teacher_stats
    }
    
    # Add filter info if filters are applied
    filters_applied = {}
    if year:
        if month:
            filters_applied["lesson_date_filter"] = {
                "month": month,
                "year": year,
                "note": "Lesson statistics filtered by month and year"
            }
        else:
            filters_applied["lesson_date_filter"] = {
                "year": year,
                "note": "Lesson statistics filtered by year"
            }
    if search:
        filters_applied["search"] = search
    if status:
        filters_applied["status"] = status
    
    if filters_applied:
        response["filters"] = filters_applied
    
    return response


@router.get("/stats/students")
def get_students_stats(
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Get detailed statistics about students
    """
    # Get all active students
    students = list(mongo_db.students_collection.find({"is_active": True}))
    
    student_stats = []
    
    for student in students:
        student_name = student["full_name"]
        
        # Count payments for this student
        student_payments = list(mongo_db.payments_collection.find({
            "student_name": {"$regex": student_name, "$options": "i"}
        }))
        
        total_paid = sum(p.get("amount", 0) for p in student_payments)
        
        student_stats.append({
            "student_id": student["_id"],
            "student_name": student_name,
            "email": student.get("email"),
            "phone": student.get("phone"),
            "total_payments": len(student_payments),
            "total_paid": round(total_paid, 2)
        })
    
    return {
        "total_students": len(student_stats),
        "students": student_stats
    }


@router.get("/stats/lessons")
def get_lessons_stats(
    current_admin: Dict = Depends(get_current_admin),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year")
):
    """
    Get detailed statistics about lessons
    Optional filters: month (1-12) and year (2000-2100)
    """
    from datetime import datetime
    
    # Build query with optional month filter
    query = {}
    if month and year:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
    
    # Count by type
    individual_query = {**query, "lesson_type": "individual"}
    group_query = {**query, "lesson_type": "group"}
    
    individual_count = mongo_db.lessons_collection.count_documents(individual_query)
    group_count = mongo_db.lessons_collection.count_documents(group_query)
    
    # Count by status
    pending_query = {**query, "status": "pending"}
    approved_query = {**query, "status": "approved"}
    rejected_query = {**query, "status": "rejected"}
    completed_query = {**query, "status": "completed"}
    cancelled_query = {**query, "status": "cancelled"}
    
    pending_count = mongo_db.lessons_collection.count_documents(pending_query)
    approved_count = mongo_db.lessons_collection.count_documents(approved_query)
    rejected_count = mongo_db.lessons_collection.count_documents(rejected_query)
    completed_count = mongo_db.lessons_collection.count_documents(completed_query)
    cancelled_count = mongo_db.lessons_collection.count_documents(cancelled_query)
    
    # Calculate total hours
    pipeline = [{"$match": query}, {"$group": {"_id": None, "total_minutes": {"$sum": "$duration_minutes"}}}]
    result = list(mongo_db.lessons_collection.aggregate(pipeline))
    total_minutes = result[0]["total_minutes"] if result else 0
    total_hours = round(total_minutes / 60, 2)
    
    response = {
        "by_type": {
            "individual_lessons": individual_count,
            "group_lessons": group_count,
            "total_lessons": individual_count + group_count
        },
        "by_status": {
            "pending_lessons": pending_count,
            "approved_lessons": approved_count,
            "rejected_lessons": rejected_count,
            "completed_lessons": completed_count,
            "cancelled_lessons": cancelled_count,
            "total_lessons": pending_count + approved_count + rejected_count + completed_count + cancelled_count
        },
        "total_hours": total_hours
    }
    
    # Add filter info if month/year provided
    if month and year:
        response["filter"] = {
            "month": month,
            "year": year,
            "note": "Statistics filtered by month and year"
        }
    
    return response


@router.get("/students/payment-status")
def get_all_students_payment_status(
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin gets all students with payment status (what they paid vs what they owe)
    Shows debt/outstanding balance for each student
    - Optional month/year filter
    """
    # Get all active students
    students = list(mongo_db.students_collection.find({"is_active": True}))
    
    student_payment_status = []
    
    for student in students:
        student_name = student["full_name"]
        student_id = str(student["_id"])
        
        print(f"\n=== DEBUG STUDENT PAYMENT STATUS ===")
        print(f"Student: {student_name} (ID: {student_id})")
        
        # Build query for lessons (only approved/completed)
        lesson_query = {
            "$or": [
                {"students.student_name": {"$regex": student_name, "$options": "i"}},
                {"students.student_id": student_id}
            ],
            "status": {"$in": ["approved", "completed"]}
        }
        
        # Build payment query
        payment_query = {"student_name": {"$regex": student_name, "$options": "i"}}
        
        # Date filter if provided
        start_date = None
        end_date = None
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
            payment_query["payment_date"] = {"$gte": start_date, "$lt": end_date}
            print(f"Date filter: {start_date} to {end_date}")
        
        print(f"Lesson query: {lesson_query}")
        
        # Get lessons for this student
        lessons = list(mongo_db.lessons_collection.find(lesson_query))
        print(f"Found {len(lessons)} lessons for student {student_name}")
        
        # Debug: Check all approved/completed lessons in the date range
        debug_query = {
            "status": {"$in": ["approved", "completed"]},
            "scheduled_date": {"$gte": start_date, "$lt": end_date}
        }
        all_lessons_in_range = list(mongo_db.lessons_collection.find(debug_query))
        print(f"Total approved/completed lessons in date range: {len(all_lessons_in_range)}")
        for l in all_lessons_in_range:
            print(f"  Lesson ID: {l.get('_id')}, Subject: {l.get('subject')}, Students: {l.get('students', [])}, Date: {l.get('scheduled_date')}")
        
        print(f"=== END DEBUG ===\n")
        
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
        
        # Get payments for this student
        payments = list(mongo_db.payments_collection.find(payment_query))
        total_paid = sum(p.get("amount", 0) for p in payments)
        
        # Calculate outstanding balance
        outstanding_balance = round(total_cost - total_paid, 2)
        
        student_payment_status.append({
            "student_id": str(student["_id"]),
            "student_name": student_name,
            "phone": student.get("phone"),
            "education_level": student.get("education_level"),
            "total_lessons_cost": round(total_cost, 2),
            "total_paid": round(total_paid, 2),
            "outstanding_balance": outstanding_balance,
            "has_debt": outstanding_balance > 0,
            "lessons_count": len(lessons),
            "payments_count": len(payments),
            "currency": "USD"
        })
    
    # Sort by outstanding balance (debt first)
    student_payment_status.sort(key=lambda x: x["outstanding_balance"], reverse=True)
    
    # Calculate totals
    total_students_with_debt = sum(1 for s in student_payment_status if s["has_debt"])
    total_debt = sum(s["outstanding_balance"] for s in student_payment_status if s["has_debt"])
    
    response = {
        "total_students": len(student_payment_status),
        "students_with_debt": total_students_with_debt,
        "total_debt": round(total_debt, 2),
        "students": student_payment_status
    }
    
    # Warn if any subjects were not found in pricing database
    if missing_subjects:
        # Get unique missing subjects
        unique_missing = {}
        for ms in missing_subjects:
            key = f"{ms['subject']}_{ms['education_level']}_{ms['lesson_type']}"
            if key not in unique_missing:
                unique_missing[key] = ms
        
        response["warning"] = {
            "message": "Some subjects not found in pricing database, used default prices",
            "missing_subjects": list(unique_missing.values())
        }
    
    # Add filter info if month/year provided
    if month and year:
        response["filter"] = {
            "month": month,
            "year": year,
            "note": "Statistics filtered by month and year"
        }
    
    return response


@router.get("/teacher-earnings/{teacher_id}", response_model=TeacherEarningsReport)
def get_teacher_earnings(
    teacher_id: str,
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin gets teacher earnings breakdown by subject.
    Shows total hours per subject, price per hour, and total payment.
    Optionally filter by month and/or year.
    """
    # Verify teacher exists using model method
    teacher = User.find_by_id(teacher_id, mongo_db.users_collection)
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )
    
    # Check if user is a teacher using model method
    if not teacher.is_teacher():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a teacher",
        )
    
    # Build query for lessons
    query = {
        "teacher_id": teacher_id,
        "status": {"$in": ["pending", "completed"]}  # Don't count cancelled lessons
    }
    
    # Date filter
    if month or year:
        date_query = {}
        if year:
            date_query["$gte"] = datetime(year, month or 1, 1)
            if month:
                if month == 12:
                    date_query["$lt"] = datetime(year + 1, 1, 1)
                else:
                    date_query["$lt"] = datetime(year, month + 1, 1)
            else:
                date_query["$lt"] = datetime(year + 1, 1, 1)
        query["scheduled_date"] = date_query
    
    # Get all lessons for this teacher
    lessons = list(mongo_db.lessons_collection.find(query))
    
    # Group by subject, education_level, AND lesson_type
    subject_data = defaultdict(lambda: {"hours": 0.0, "count": 0})
    
    for lesson in lessons:
        subject = lesson.get("subject", "other")
        education_level = lesson.get("education_level", "elementary")  # default to elementary
        lesson_type = lesson.get("lesson_type", "individual")
        duration_minutes = lesson.get("duration_minutes", 0)
        hours = duration_minutes / 60
        
        # Create unique key for subject + education_level + lesson_type
        key = (subject, education_level, lesson_type)
        subject_data[key]["hours"] += hours
        subject_data[key]["count"] += 1
    
    # Calculate earnings per subject + education_level + lesson_type
    subject_earnings_list = []
    total_hours = 0.0
    total_earnings = 0.0
    
    for (subject, education_level, lesson_type), data in subject_data.items():
        hours = round(data["hours"], 2)
        price_per_hour = get_subject_price(subject, education_level, lesson_type)
        earnings = calculate_subject_earnings(hours, subject, education_level, lesson_type)
        
        subject_earnings_list.append(
            SubjectEarnings(
                subject=subject,
                education_level=education_level,
                lesson_type=lesson_type,
                total_hours=hours,
                price_per_hour=price_per_hour,
                total_earnings=earnings,
                lesson_count=data["count"]
            )
        )
        
        total_hours += hours
        total_earnings += earnings
    
    # Sort by subject name, education level, then lesson_type
    subject_earnings_list.sort(key=lambda x: (x.subject, x.education_level, x.lesson_type))
    
    # Get teacher name using model method
    teacher_name = teacher.get_full_name()
    
    return TeacherEarningsReport(
        teacher_id=teacher_id,
        teacher_name=teacher_name,
        month=month,
        year=year,
        total_hours=round(total_hours, 2),
        total_earnings=round(total_earnings, 2),
        by_subject=subject_earnings_list,
        total_lessons=len(lessons)
    )


@router.get("/student-hours/{student_name}")
def get_student_hours_summary(
    student_name: str,
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin gets student hours summary (individual vs group) with optional month/year filter
    Returns total individual hours, total group hours, and lesson count
    """
    # Build query for lessons
    query = {
        "students.student_name": {"$regex": student_name, "$options": "i"},
        "status": {"$in": ["approved", "completed"]}  # Only count approved or completed lessons
    }
    
    # Date filter
    if month or year:
        date_query = {}
        if year:
            date_query["$gte"] = datetime(year, month or 1, 1)
            if month:
                if month == 12:
                    date_query["$lt"] = datetime(year + 1, 1, 1)
                else:
                    date_query["$lt"] = datetime(year, month + 1, 1)
            else:
                date_query["$lt"] = datetime(year + 1, 1, 1)
        query["scheduled_date"] = date_query
    
    # Get all lessons for this student
    lessons = list(mongo_db.lessons_collection.find(query))
    
    # Calculate hours by type
    individual_hours = 0.0
    group_hours = 0.0
    individual_count = 0
    group_count = 0
    
    for lesson in lessons:
        duration_minutes = lesson.get("duration_minutes", 0)
        hours = duration_minutes / 60
        
        if lesson.get("lesson_type") == "individual":
            individual_hours += hours
            individual_count += 1
        else:
            group_hours += hours
            group_count += 1
    
    response = {
        "student_name": student_name,
        "individual_hours": round(individual_hours, 2),
        "group_hours": round(group_hours, 2),
        "total_hours": round(individual_hours + group_hours, 2),
        "individual_lessons": individual_count,
        "group_lessons": group_count,
        "total_lessons": individual_count + group_count
    }
    
    # Add filter info if month/year provided
    if month and year:
        response["filter"] = {
            "month": month,
            "year": year,
            "note": "Statistics filtered by month and year"
        }
    
    return response


@router.get("/stats/teachers-detailed", response_model=TeachersDetailedStatsResponse)
def get_teachers_detailed_stats(
    current_admin: Dict = Depends(get_current_admin),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter lessons by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter lessons by year"),
    search: Optional[str] = Query(None, description="Search teachers by name or username"),
    status: Optional[str] = Query("active", description="Filter teachers by status (active, suspended, inactive)"),
    lesson_status: Optional[str] = Query(
        None,
        description="Filter counted lessons by status (approved, completed, pending, cancelled, rejected). If omitted, defaults to approved lessons only."
    )
):
    """
    Get detailed teacher statistics with education level breakdowns.
    
    Returns comprehensive statistics for each teacher including:
    - Total individual lesson hours
    - Total group lesson hours  
    - Individual hours breakdown by education level (elementary, middle, secondary)
    - Group hours breakdown by education level (elementary, middle, secondary)
    
    By default, only counts approved lessons. Use lesson_status parameter to override.
    
    Optional filters:
    - month (1-12) and year (2000-2100): Filter lesson statistics by date range
    - search: Search for teachers by name or username
    - status: Filter teachers by status (default: active)
    - lesson_status: Filter lessons by status (default: approved)
    """
    from datetime import datetime
    
    # Build teacher query
    teacher_query = {"role": "teacher"}
    
    # Add status filter
    if status:
        teacher_query["status"] = status
    
    # Add search filter
    if search:
        # Search by username, first_name, or last_name
        teacher_query["$or"] = [
            {"username": {"$regex": search, "$options": "i"}},
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
        ]
    
    # Get teachers matching the filters
    teachers = list(mongo_db.users_collection.find(teacher_query))
    
    # Build lesson query with optional month/year/status filter
    lesson_query = {}
    if year:
        if month:
            # Filter by specific month and year
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
        else:
            # Filter by entire year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}

    # Lesson status filter (single value)
    # Default to approved lessons if no status specified
    if lesson_status:
        # Accept only known statuses; ignore invalid input
        allowed_statuses = {"pending", "approved", "rejected", "completed", "cancelled"}
        if lesson_status in allowed_statuses:
            lesson_query["status"] = lesson_status
    else:
        # Default to approved lessons only
        lesson_query["status"] = "approved"
    
    teacher_stats = []
    
    for teacher in teachers:
        teacher_id = teacher["_id"]
        teacher_id_str = str(teacher_id)  # Convert ObjectId to string
        teacher_name = f"{teacher.get('first_name', '')} {teacher.get('last_name', '')}".strip() or teacher["username"]
        
        # Count lessons for this teacher with date/status filters applied
        teacher_lesson_query = {**lesson_query, "teacher_id": teacher_id_str}
        teacher_lessons = list(mongo_db.lessons_collection.find(teacher_lesson_query))
        
        # Initialize counters
        total_individual_hours = 0.0
        total_group_hours = 0.0
        
        individual_hours_by_level = {
            "elementary": 0.0,
            "middle": 0.0,
            "secondary": 0.0
        }
        
        group_hours_by_level = {
            "elementary": 0.0,
            "middle": 0.0,
            "secondary": 0.0
        }
        
        # Process each lesson
        for lesson in teacher_lessons:
            duration_minutes = lesson.get("duration_minutes", 0)
            hours = duration_minutes / 60
            lesson_type = lesson.get("lesson_type", "individual")
            education_level = lesson.get("education_level", "elementary")
            
            # Normalize education level names
            if education_level == "primary":
                education_level = "elementary"
            elif education_level == "preparatory":
                education_level = "middle"
            
            # Ensure education level is valid
            if education_level not in ["elementary", "middle", "secondary"]:
                education_level = "elementary"  # Default fallback
            
            if lesson_type == "individual":
                total_individual_hours += hours
                individual_hours_by_level[education_level] += hours
            else:  # group
                total_group_hours += hours
                group_hours_by_level[education_level] += hours
        
        # Round hours to 2 decimal places
        total_individual_hours = round(total_individual_hours, 2)
        total_group_hours = round(total_group_hours, 2)
        
        for level in individual_hours_by_level:
            individual_hours_by_level[level] = round(individual_hours_by_level[level], 2)
            group_hours_by_level[level] = round(group_hours_by_level[level], 2)
        
        teacher_stats.append(TeacherDetailedStats(
            teacher_id=teacher_id_str,
            teacher_name=teacher_name,
            total_individual_hours=total_individual_hours,
            total_group_hours=total_group_hours,
            individual_hours_by_level=EducationLevelHours(**individual_hours_by_level),
            group_hours_by_level=EducationLevelHours(**group_hours_by_level)
        ))
    
    # Sort teachers by total hours (individual + group)
    teacher_stats.sort(key=lambda x: x.total_individual_hours + x.total_group_hours, reverse=True)
    
    response = TeachersDetailedStatsResponse(
        total_teachers=len(teacher_stats),
        teachers=teacher_stats
    )
    
    return response


@router.get("/stats/students-detailed", response_model=StudentsDetailedStatsResponse)
def get_students_detailed_stats(
    current_admin: Dict = Depends(get_current_admin),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter lessons by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter lessons by year"),
    search: Optional[str] = Query(None, description="Search students by name"),
    education_level: Optional[str] = Query(None, description="Filter students by education level (elementary, middle, secondary)"),
    is_active: Optional[bool] = Query(True, description="Filter students by active status")
):
    """
    Get detailed student statistics with lesson hours breakdown.
    
    Returns comprehensive statistics for each student including:
    - Individual lesson hours
    - Group lesson hours  
    - Total hours
    - Education level
    
    Optional filters:
    - month (1-12) and year (2000-2100): Filter lesson statistics by date range
    - search: Search for students by name
    - education_level: Filter students by education level (elementary, middle, secondary)
    - is_active: Filter students by active status (default: true)
    """
    from datetime import datetime
    
    # Build student query
    student_query = {}
    
    # Add active status filter
    if is_active is not None:
        student_query["is_active"] = is_active
    
    # Add education level filter
    if education_level:
        # Normalize education level names
        if education_level == "primary":
            education_level = "elementary"
        elif education_level == "preparatory":
            education_level = "middle"
        
        # Ensure education level is valid
        if education_level in ["elementary", "middle", "secondary"]:
            student_query["education_level"] = education_level
    
    # Add search filter
    if search:
        # Search by full_name
        student_query["full_name"] = {"$regex": search, "$options": "i"}
    
    # Get students matching the filters
    students = list(mongo_db.students_collection.find(student_query))
    
    # Build lesson query with optional month/year filter
    lesson_query = {}
    if year:
        if month:
            # Filter by specific month and year
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
        else:
            # Filter by entire year
            start_date = datetime(year, 1, 1)
            end_date = datetime(year + 1, 1, 1)
            lesson_query["scheduled_date"] = {"$gte": start_date, "$lt": end_date}
    
    student_stats = []
    
    for student in students:
        student_id = str(student["_id"])
        student_name = student["full_name"]
        student_education_level = student.get("education_level", "elementary")
        
        # Normalize education level names
        if student_education_level == "primary":
            student_education_level = "elementary"
        elif student_education_level == "preparatory":
            student_education_level = "middle"
        
        # Ensure education level is valid
        if student_education_level not in ["elementary", "middle", "secondary"]:
            student_education_level = "elementary"  # Default fallback
        
        # Find lessons for this student
        student_lesson_query = {
            **lesson_query,
            "$or": [
                {"students.student_name": {"$regex": student_name, "$options": "i"}},
                {"students.student_id": student_id}
            ],
            "status": {"$in": ["approved", "completed"]}  # Only count approved or completed lessons
        }
        
        student_lessons = list(mongo_db.lessons_collection.find(student_lesson_query))
        
        # Initialize counters
        individual_hours = 0.0
        group_hours = 0.0
        
        # Process each lesson
        for lesson in student_lessons:
            duration_minutes = lesson.get("duration_minutes", 0)
            hours = duration_minutes / 60
            lesson_type = lesson.get("lesson_type", "individual")
            
            if lesson_type == "individual":
                individual_hours += hours
            else:  # group
                group_hours += hours
        
        # Round hours to 2 decimal places
        individual_hours = round(individual_hours, 2)
        group_hours = round(group_hours, 2)
        total_hours = round(individual_hours + group_hours, 2)
        
        student_stats.append(StudentDetailedStats(
            student_id=student_id,
            student_name=student_name,
            individual_hours=individual_hours,
            group_hours=group_hours,
            total_hours=total_hours,
            education_level=student_education_level
        ))
    
    # Sort students by total hours in descending order
    student_stats.sort(key=lambda x: x.total_hours, reverse=True)
    
    response = StudentsDetailedStatsResponse(
        total_students=len(student_stats),
        students=student_stats
    )
    
    return response