from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional, Dict
from datetime import datetime
from app.schemas.lesson import (
    LessonCreate,
    LessonResponse,
    LessonUpdate,
    LessonsStatsResponse,
    StudentInfo,
    LessonType,
    LessonStatus,
)
from app.models.lesson import Lesson
from app.models.user import User
from app.api.deps import get_current_user, get_current_admin, get_current_teacher
from app.db import mongo_db

router = APIRouter()


# ==================== TEACHER ENDPOINTS ====================

@router.post("/submit", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def submit_lesson(
    lesson_data: LessonCreate,
    current_user: Dict = Depends(get_current_teacher)
):
    """
    Teacher creates a new lesson (individual or group) - starts as pending
    """
    # Get teacher info using User model
    teacher = User.from_dict(current_user)
    teacher_name = teacher.get_full_name()
    
    # Create lesson using Lesson model
    new_lesson = Lesson(
        teacher_id=str(current_user["_id"]),
        teacher_name=teacher_name,
        lesson_type=lesson_data.lesson_type,
        subject=lesson_data.subject,
        education_level=lesson_data.education_level,
        scheduled_date=lesson_data.scheduled_date,
        duration_minutes=lesson_data.duration_minutes,
        max_students=lesson_data.max_students,
        status=LessonStatus.PENDING,
        students=[student.model_dump() for student in (lesson_data.students or [])],
    )
    
    # Save to database using model method
    new_lesson.save(mongo_db.lessons_collection)
    
    return LessonResponse(
        id=new_lesson._id,
        teacher_id=new_lesson.teacher_id,
        teacher_name=new_lesson.teacher_name,
        lesson_type=new_lesson.lesson_type,
        subject=new_lesson.subject,
        education_level=new_lesson.education_level,
        scheduled_date=new_lesson.scheduled_date,
        duration_minutes=new_lesson.duration_minutes,
        max_students=new_lesson.max_students,
        status=new_lesson.status,
        students=[StudentInfo(**s) for s in new_lesson.students],
        created_at=new_lesson.created_at,
        updated_at=new_lesson.updated_at,
        completed_at=new_lesson.completed_at,
    )


@router.get("/my-lessons", response_model=Dict)
def get_my_lessons(
    current_user: Dict = Depends(get_current_teacher),
    lesson_type: Optional[str] = Query(None, description="Filter by: individual or group"),
    lesson_status: Optional[str] = Query(None, description="Filter by: pending, completed, cancelled"),
    student_name: Optional[str] = Query(None, description="Filter by student name"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Teacher gets their own lessons with filters and statistics
    - Filter by: type (individual/group), status, student name, month, year
    - Returns: lessons + total_lessons + total_hours + individual/group breakdown
    """
    query = {"teacher_id": str(current_user["_id"])}
    
    # Type filter
    if lesson_type:
        query["lesson_type"] = lesson_type
    
    # Status filter
    if lesson_status:
        query["status"] = lesson_status
    
    # Student name filter
    if student_name:
        query["students.student_name"] = {"$regex": student_name, "$options": "i"}
    
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
    
    # Get lessons
    lessons_docs = list(mongo_db.lessons_collection.find(query).skip(skip).limit(limit).sort("scheduled_date", -1))
    lessons = [Lesson.from_dict(doc) for doc in lessons_docs]
    
    # Calculate total hours using model method
    total_hours = Lesson.calculate_total_hours(lessons)
    
    # Calculate individual vs group statistics
    individual_hours = 0.0
    group_hours = 0.0
    individual_count = 0
    group_count = 0
    
    for lesson in lessons:
        hours = lesson.get_duration_hours()
        if lesson.lesson_type.value == "individual":
            individual_hours += hours
            individual_count += 1
        else:
            group_hours += hours
            group_count += 1
    
    # Convert to response
    lesson_responses = [
        LessonResponse(
            id=lesson._id,
            teacher_id=lesson.teacher_id,
            teacher_name=lesson.teacher_name,
            lesson_type=lesson.lesson_type,
            subject=lesson.subject,
            education_level=lesson.education_level,
            scheduled_date=lesson.scheduled_date,
            duration_minutes=lesson.duration_minutes,
            max_students=lesson.max_students,
            status=lesson.status,
            students=[StudentInfo(**s) for s in lesson.students],
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
            completed_at=lesson.completed_at,
        )
        for lesson in lessons
    ]
    
    # Build extended response with breakdown
    response = {
        "total_lessons": len(lessons),
        "total_hours": round(total_hours, 2),
        "individual": {
            "lessons": individual_count,
            "hours": round(individual_hours, 2)
        },
        "group": {
            "lessons": group_count,
            "hours": round(group_hours, 2)
        },
        "lessons": lesson_responses
    }
    
    return response


@router.get("/summary", response_model=Dict)
def get_lessons_summary(
    current_user: Dict = Depends(get_current_teacher)
):
    """
    Get detailed summary of lessons grouped by subject and type
    Returns breakdown like:
    - Mathematics individual: X lessons, Y hours
    - Mathematics group: X lessons, Y hours
    - Physics individual: X lessons, Y hours
    - etc.
    """
    teacher_id = str(current_user["_id"])
    
    # MongoDB aggregation pipeline
    pipeline = [
        # Match teacher's lessons
        {"$match": {"teacher_id": teacher_id}},
        
        # Group by subject and type
        {"$group": {
            "_id": {
                "subject": "$subject",
                "lesson_type": "$lesson_type"
            },
            "total_lessons": {"$sum": 1},
            "total_minutes": {"$sum": "$duration_minutes"},
            "total_students": {"$sum": {"$size": "$students"}},
            "pending_count": {
                "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
            },
            "completed_count": {
                "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
            },
            "cancelled_count": {
                "$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}
            }
        }},
        
        # Sort by subject and type
        {"$sort": {"_id.subject": 1, "_id.lesson_type": 1}}
    ]
    
    results = list(mongo_db.lessons_collection.aggregate(pipeline))
    
    # Format results
    summary_by_subject = {}
    overall_stats = {
        "total_lessons": 0,
        "total_hours": 0.0,
        "individual_lessons": 0,
        "individual_hours": 0.0,
        "group_lessons": 0,
        "group_hours": 0.0
    }
    
    for result in results:
        subject = result["_id"]["subject"]
        lesson_type = result["_id"]["lesson_type"]
        total_lessons = result["total_lessons"]
        total_hours = result["total_minutes"] / 60.0
        
        # Initialize subject if not exists
        if subject not in summary_by_subject:
            summary_by_subject[subject] = {
                "total_lessons": 0,
                "total_hours": 0.0,
                "individual": {
                    "lessons": 0,
                    "hours": 0.0,
                    "students": 0,
                    "pending": 0,
                    "completed": 0,
                    "cancelled": 0
                },
                "group": {
                    "lessons": 0,
                    "hours": 0.0,
                    "students": 0,
                    "pending": 0,
                    "completed": 0,
                    "cancelled": 0
                }
            }
        
        # Update subject totals
        summary_by_subject[subject]["total_lessons"] += total_lessons
        summary_by_subject[subject]["total_hours"] += total_hours
        
        # Update type-specific stats
        type_key = "individual" if lesson_type == "individual" else "group"
        summary_by_subject[subject][type_key]["lessons"] = total_lessons
        summary_by_subject[subject][type_key]["hours"] = total_hours
        summary_by_subject[subject][type_key]["students"] = result["total_students"]
        summary_by_subject[subject][type_key]["pending"] = result["pending_count"]
        summary_by_subject[subject][type_key]["completed"] = result["completed_count"]
        summary_by_subject[subject][type_key]["cancelled"] = result["cancelled_count"]
        
        # Update overall stats
        overall_stats["total_lessons"] += total_lessons
        overall_stats["total_hours"] += total_hours
        
        if lesson_type == "individual":
            overall_stats["individual_lessons"] += total_lessons
            overall_stats["individual_hours"] += total_hours
        else:
            overall_stats["group_lessons"] += total_lessons
            overall_stats["group_hours"] += total_hours
    
    return {
        "overall": overall_stats,
        "by_subject": summary_by_subject
    }


@router.put("/update-lesson/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: str,
    lesson_update: LessonUpdate,
    current_user: Dict = Depends(get_current_teacher)
):
    """
    Teacher updates their own lesson
    - Can only update if status is pending (NOT completed or cancelled)
    """
    # Find lesson using model method
    lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Check ownership
    if lesson.teacher_id != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lesson",
        )
    
    # Check if can be updated using model method
    if not lesson.can_be_updated():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update {lesson.status.value} lesson. Only pending lessons can be updated.",
        )
    
    # Prepare update
    update_data = lesson_update.model_dump(exclude_unset=True)
    
    if "students" in update_data and update_data["students"]:
        update_data["students"] = [s.model_dump() if hasattr(s, 'model_dump') else s for s in update_data["students"]]
    
    if "lesson_type" in update_data:
        update_data["lesson_type"] = update_data["lesson_type"].value
    
    if "status" in update_data:
        # If marking as completed, set completed_at
        if update_data["status"] == LessonStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        update_data["status"] = update_data["status"].value
    
    # Update using model method
    lesson.update_in_db(mongo_db.lessons_collection, update_data)
    
    # Get updated lesson
    updated_lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    return LessonResponse(
        id=updated_lesson._id,
        teacher_id=updated_lesson.teacher_id,
        teacher_name=updated_lesson.teacher_name,
        lesson_type=updated_lesson.lesson_type,
        subject=updated_lesson.subject,
        education_level=updated_lesson.education_level,
        scheduled_date=updated_lesson.scheduled_date,
        duration_minutes=updated_lesson.duration_minutes,
        max_students=updated_lesson.max_students,
        status=updated_lesson.status,
        students=[StudentInfo(**s) for s in updated_lesson.students],
        created_at=updated_lesson.created_at,
        updated_at=updated_lesson.updated_at,
        completed_at=updated_lesson.completed_at,
    )


@router.delete("/delete-lesson/{lesson_id}")
def delete_lesson(
    lesson_id: str,
    current_user: Dict = Depends(get_current_teacher)
):
    """
    Teacher 'deletes' their own lesson (soft delete - changes status to cancelled)
    - Can only delete pending lessons
    """
    # Find lesson using model method
    lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Check ownership
    if lesson.teacher_id != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this lesson",
        )
    
    # Can only delete pending lessons
    if not lesson.is_pending():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete {lesson.status.value} lesson. Only pending lessons can be deleted.",
        )
    
    # Soft delete using model method
    lesson.delete(mongo_db.lessons_collection)
    
    return {"message": "Lesson cancelled successfully"}


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson_by_id(
    lesson_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get a specific lesson by ID
    - Teachers can only see their own
    - Admins can see any
    """
    # Find lesson using model method
    lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    # Check permission
    if current_user["role"] == "teacher" and lesson.teacher_id != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this lesson",
        )
    
    return LessonResponse(
        id=lesson._id,
        teacher_id=lesson.teacher_id,
        teacher_name=lesson.teacher_name,
        lesson_type=lesson.lesson_type,
        subject=lesson.subject,
        education_level=lesson.education_level,
        scheduled_date=lesson.scheduled_date,
        duration_minutes=lesson.duration_minutes,
        max_students=lesson.max_students,
        status=lesson.status,
        students=[StudentInfo(**s) for s in lesson.students],
        created_at=lesson.created_at,
        updated_at=lesson.updated_at,
        completed_at=lesson.completed_at,
    )


# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/all", response_model=LessonsStatsResponse)
def get_all_lessons_admin(
    current_admin: Dict = Depends(get_current_admin),
    teacher_id: Optional[str] = Query(None, description="Filter by teacher ID"),
    student_name: Optional[str] = Query(None, description="Filter by student name"),
    status: Optional[str] = Query(None, description="Filter by status (pending, approved, rejected, completed, cancelled)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month (1-12)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filter by year"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """
    Admin views all lessons with filters
    - Filter by teacher, student name, status, month, year
    - Returns all lessons with total count and hours
    """
    query = {}
    
    # Teacher filter
    if teacher_id:
        query["teacher_id"] = teacher_id
    
    # Status filter
    if status:
        query["status"] = status
    
    # Student name filter
    if student_name:
        query["students.student_name"] = {"$regex": student_name, "$options": "i"}
    
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
    
    # Get lessons
    lessons_docs = list(mongo_db.lessons_collection.find(query).skip(skip).limit(limit).sort("scheduled_date", -1))
    lessons = [Lesson.from_dict(doc) for doc in lessons_docs]
    
    # Calculate total hours
    total_hours = Lesson.calculate_total_hours(lessons)
    
    # Convert to response
    lesson_responses = [
        LessonResponse(
            id=lesson._id,
            teacher_id=lesson.teacher_id,
            teacher_name=lesson.teacher_name,
            lesson_type=lesson.lesson_type,
            subject=lesson.subject,
            education_level=lesson.education_level,
            scheduled_date=lesson.scheduled_date,
            duration_minutes=lesson.duration_minutes,
            max_students=lesson.max_students,
            status=lesson.status,
            students=[StudentInfo(**s) for s in lesson.students],
            created_at=lesson.created_at,
            updated_at=lesson.updated_at,
            completed_at=lesson.completed_at,
        )
        for lesson in lessons
    ]
    
    return LessonsStatsResponse(
        total_lessons=len(lessons),
        total_hours=total_hours,
        lessons=lesson_responses
    )


@router.put("/admin/approve/{lesson_id}", response_model=LessonResponse)
def approve_lesson(
    lesson_id: str,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin approves a pending lesson
    """
    lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    if not lesson.is_pending():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve {lesson.status.value} lesson. Only pending lessons can be approved.",
        )
    
    # Approve lesson
    lesson.approve()
    lesson.update_in_db(mongo_db.lessons_collection, {
        "status": lesson.status.value,
        "updated_at": lesson.updated_at
    })
    
    # Get updated lesson
    updated_lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    return LessonResponse(
        id=updated_lesson._id,
        teacher_id=updated_lesson.teacher_id,
        teacher_name=updated_lesson.teacher_name,
        lesson_type=updated_lesson.lesson_type,
        subject=updated_lesson.subject,
        education_level=updated_lesson.education_level,
        scheduled_date=updated_lesson.scheduled_date,
        duration_minutes=updated_lesson.duration_minutes,
        max_students=updated_lesson.max_students,
        status=updated_lesson.status,
        students=[StudentInfo(**s) for s in updated_lesson.students],
        created_at=updated_lesson.created_at,
        updated_at=updated_lesson.updated_at,
        completed_at=updated_lesson.completed_at,
    )


@router.put("/admin/reject/{lesson_id}", response_model=LessonResponse)
def reject_lesson(
    lesson_id: str,
    current_admin: Dict = Depends(get_current_admin)
):
    """
    Admin rejects a pending lesson
    """
    lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    
    if not lesson.is_pending():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject {lesson.status.value} lesson. Only pending lessons can be rejected.",
        )
    
    # Reject lesson
    lesson.reject()
    lesson.update_in_db(mongo_db.lessons_collection, {
        "status": lesson.status.value,
        "updated_at": lesson.updated_at
    })
    
    # Get updated lesson
    updated_lesson = Lesson.find_by_id(lesson_id, mongo_db.lessons_collection)
    
    return LessonResponse(
        id=updated_lesson._id,
        teacher_id=updated_lesson.teacher_id,
        teacher_name=updated_lesson.teacher_name,
        lesson_type=updated_lesson.lesson_type,
        subject=updated_lesson.subject,
        education_level=updated_lesson.education_level,
        scheduled_date=updated_lesson.scheduled_date,
        duration_minutes=updated_lesson.duration_minutes,
        max_students=updated_lesson.max_students,
        status=updated_lesson.status,
        students=[StudentInfo(**s) for s in updated_lesson.students],
        created_at=updated_lesson.created_at,
        updated_at=updated_lesson.updated_at,
        completed_at=updated_lesson.completed_at,
    )
