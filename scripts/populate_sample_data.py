"""
Script to populate real database with sample teacher and lessons
Then query with filters and print summary

Run with: python scripts/populate_sample_data.py
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.mongodb import mongo_db
from app.models.user import User, UserRole, UserStatus
from app.models.lesson import Lesson, LessonType, LessonStatus
from app.core.security import get_password_hash


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_section(text):
    """Print a formatted section"""
    print(f"\n{'-'*60}")
    print(f"  {text}")
    print(f"{'-'*60}")


def create_teacher():
    """Create a sample teacher in the database"""
    print_section("Step 1: Creating Teacher")
    
    # Check if teacher already exists
    existing = mongo_db.users_collection.find_one({"username": "john_doe_teacher"})
    if existing:
        print("[WARNING] Teacher 'john_doe_teacher' already exists. Deleting old data...")
        mongo_db.users_collection.delete_one({"username": "john_doe_teacher"})
        # Also delete their lessons
        mongo_db.lessons_collection.delete_many({"teacher_id": existing["_id"]})
    
    # Create new teacher
    teacher = User(
        username="john_doe_teacher",
        email="john.doe@example.com",
        hashed_password=get_password_hash("password123"),
        first_name="John",
        last_name="Doe",
        role=UserRole.TEACHER,
        status=UserStatus.ACTIVE,
        phone="+1234567890"
    )
    
    teacher.save(mongo_db.users_collection)
    
    print(f"[SUCCESS] Created Teacher:")
    print(f"   ID: {teacher._id}")
    print(f"   Username: {teacher.username}")
    print(f"   Email: {teacher.email}")
    print(f"   Name: {teacher.get_full_name()}")
    print(f"   Password: password123")
    
    return teacher


def create_lessons(teacher):
    """Create sample lessons for the teacher"""
    print_section("Step 2: Creating Lessons")
    
    # Lesson data: (title, subject, type, duration, num_students, date_offset)
    lessons_data = [
        # Mathematics lessons (5 total: 3 individual, 2 group)
        ("Algebra Basics", "Mathematics", LessonType.INDIVIDUAL, 60, 1, 0),
        ("Calculus Introduction", "Mathematics", LessonType.INDIVIDUAL, 90, 1, 1),
        ("Geometry Fundamentals", "Mathematics", LessonType.INDIVIDUAL, 60, 1, 2),
        ("Math Problem Solving", "Mathematics", LessonType.GROUP, 120, 5, 3),
        ("Advanced Mathematics", "Mathematics", LessonType.GROUP, 90, 3, 4),
        
        # Physics lessons (4 total: 2 individual, 2 group)
        ("Mechanics Basics", "Physics", LessonType.INDIVIDUAL, 120, 1, 5),
        ("Electromagnetism", "Physics", LessonType.INDIVIDUAL, 90, 1, 6),
        ("Thermodynamics Group", "Physics", LessonType.GROUP, 120, 4, 7),
        ("Quantum Physics Intro", "Physics", LessonType.GROUP, 90, 3, 8),
        
        # Chemistry lessons (3 total: 1 individual, 2 group)
        ("Organic Chemistry", "Chemistry", LessonType.INDIVIDUAL, 60, 1, 9),
        ("Chemical Reactions Lab", "Chemistry", LessonType.GROUP, 120, 6, 10),
        ("Molecular Structure", "Chemistry", LessonType.GROUP, 90, 4, 11),
        
        # Biology lessons (3 total: 2 individual, 1 group)
        ("Cell Biology", "Biology", LessonType.INDIVIDUAL, 90, 1, 12),
        ("Human Anatomy", "Biology", LessonType.INDIVIDUAL, 60, 1, 13),
        ("Ecology and Environment", "Biology", LessonType.GROUP, 120, 5, 14),
        
        # English lessons (2 total: 1 individual, 1 group)
        ("Grammar Fundamentals", "English", LessonType.INDIVIDUAL, 60, 1, 15),
        ("Creative Writing Workshop", "English", LessonType.GROUP, 90, 8, 16),
    ]
    
    created_lessons = []
    
    for title, subject, lesson_type, duration, num_students, days_ahead in lessons_data:
        # Create lesson
        scheduled_date = datetime.now() + timedelta(days=days_ahead)
        
        # Create student list
        students = []
        if lesson_type == LessonType.INDIVIDUAL:
            students = [{"student_name": "Individual Student", "student_email": "student@example.com"}]
        else:
            students = [
                {"student_name": f"Student {i+1}", "student_email": f"student{i+1}@example.com"}
                for i in range(num_students)
            ]
        
        lesson = Lesson(
            teacher_id=teacher._id,
            teacher_name=teacher.get_full_name(),
            title=title,
            subject=subject,
            description=f"{subject} lesson on {title}",
            lesson_type=lesson_type,
            scheduled_date=scheduled_date,
            duration_minutes=duration,
            max_students=num_students,
            students=students,
            status=LessonStatus.PENDING,
            notes=f"Sample lesson for {subject}"
        )
        
        lesson.save(mongo_db.lessons_collection)
        created_lessons.append(lesson)
        
        type_icon = "[IND]" if lesson_type == LessonType.INDIVIDUAL else "[GRP]"
        print(f"  {type_icon} {title} ({subject}) - {duration} min - {len(students)} student(s)")
    
    print(f"\n[SUCCESS] Created {len(created_lessons)} lessons")
    return created_lessons


def query_and_print_summary(teacher):
    """Query lessons with different filters and print summary"""
    print_section("Step 3: Querying Lessons with Filters")
    
    # Get all lessons for this teacher
    all_lessons = list(mongo_db.lessons_collection.find({"teacher_id": teacher._id}))
    
    print(f"\nOVERALL SUMMARY:")
    print(f"   Total Lessons: {len(all_lessons)}")
    
    # Calculate total hours
    total_hours = sum(lesson["duration_minutes"] for lesson in all_lessons) / 60.0
    print(f"   Total Hours: {total_hours:.1f} hours")
    
    # Filter by lesson type
    print(f"\nBY LESSON TYPE:")
    individual_lessons = [l for l in all_lessons if l["lesson_type"] == LessonType.INDIVIDUAL]
    group_lessons = [l for l in all_lessons if l["lesson_type"] == LessonType.GROUP]
    
    individual_hours = sum(l["duration_minutes"] for l in individual_lessons) / 60.0
    group_hours = sum(l["duration_minutes"] for l in group_lessons) / 60.0
    
    print(f"   [IND] Individual: {len(individual_lessons)} lessons ({individual_hours:.1f} hours)")
    print(f"   [GRP] Group: {len(group_lessons)} lessons ({group_hours:.1f} hours)")
    
    # Filter by subject
    print(f"\nBY SUBJECT:")
    subjects = {}
    for lesson in all_lessons:
        subject = lesson["subject"]
        if subject not in subjects:
            subjects[subject] = {
                "total": 0,
                "individual": 0,
                "group": 0,
                "hours": 0.0,
                "students": 0
            }
        
        subjects[subject]["total"] += 1
        subjects[subject]["hours"] += lesson["duration_minutes"] / 60.0
        subjects[subject]["students"] += len(lesson["students"])
        
        if lesson["lesson_type"] == LessonType.INDIVIDUAL:
            subjects[subject]["individual"] += 1
        else:
            subjects[subject]["group"] += 1
    
    for subject, data in sorted(subjects.items()):
        print(f"\n   {subject}:")
        print(f"      Total Lessons: {data['total']}")
        print(f"      Individual: {data['individual']}, Group: {data['group']}")
        print(f"      Total Hours: {data['hours']:.1f}")
        print(f"      Total Students: {data['students']}")
    
    # Filter by date range (next 7 days)
    print(f"\nUPCOMING (Next 7 Days):")
    now = datetime.now()
    next_week = now + timedelta(days=7)
    
    upcoming_lessons = [
        l for l in all_lessons 
        if now <= l["scheduled_date"] <= next_week
    ]
    
    for lesson in sorted(upcoming_lessons, key=lambda x: x["scheduled_date"]):
        date_str = lesson["scheduled_date"].strftime("%Y-%m-%d")
        type_icon = "[IND]" if lesson["lesson_type"] == LessonType.INDIVIDUAL else "[GRP]"
        print(f"   {type_icon} {date_str} - {lesson['title']} ({lesson['subject']}) - {lesson['duration_minutes']} min")
    
    print(f"\n   Total upcoming: {len(upcoming_lessons)} lessons")
    
    # Student count summary
    print(f"\nSTUDENT SUMMARY:")
    total_students = sum(len(l["students"]) for l in all_lessons)
    avg_students = total_students / len(all_lessons) if all_lessons else 0
    
    print(f"   Total Student Enrollments: {total_students}")
    print(f"   Average Students per Lesson: {avg_students:.1f}")
    
    # Lessons by status
    print(f"\nBY STATUS:")
    status_counts = {}
    for lesson in all_lessons:
        status = lesson["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   {status}: {count} lessons")


def demonstrate_specific_queries(teacher):
    """Demonstrate specific MongoDB queries"""
    print_section("Step 4: Demonstrating Specific Queries")
    
    # Query 1: Find all Mathematics individual lessons
    print("\n[QUERY 1] Individual Mathematics lessons")
    math_individual = list(mongo_db.lessons_collection.find({
        "teacher_id": teacher._id,
        "subject": "Mathematics",
        "lesson_type": LessonType.INDIVIDUAL
    }))
    print(f"   Found {len(math_individual)} lessons:")
    for lesson in math_individual:
        print(f"   - {lesson['title']} ({lesson['duration_minutes']} min)")
    
    # Query 2: Find all group lessons with 5+ students
    print("\n[QUERY 2] Group lessons with 5+ students")
    large_groups = list(mongo_db.lessons_collection.find({
        "teacher_id": teacher._id,
        "lesson_type": LessonType.GROUP
    }))
    large_groups = [l for l in large_groups if len(l["students"]) >= 5]
    print(f"   Found {len(large_groups)} lessons:")
    for lesson in large_groups:
        print(f"   - {lesson['title']} ({lesson['subject']}) - {len(lesson['students'])} students")
    
    # Query 3: Find lessons longer than 90 minutes
    print("\n[QUERY 3] Lessons longer than 90 minutes")
    long_lessons = list(mongo_db.lessons_collection.find({
        "teacher_id": teacher._id,
        "duration_minutes": {"$gt": 90}
    }))
    print(f"   Found {len(long_lessons)} lessons:")
    for lesson in long_lessons:
        print(f"   - {lesson['title']} ({lesson['subject']}) - {lesson['duration_minutes']} min")
    
    # Query 4: Count lessons by subject using aggregation
    print("\n[QUERY 4] Lesson count by subject (using aggregation)")
    pipeline = [
        {"$match": {"teacher_id": teacher._id}},
        {"$group": {
            "_id": "$subject",
            "count": {"$sum": 1},
            "total_hours": {"$sum": {"$divide": ["$duration_minutes", 60]}}
        }},
        {"$sort": {"count": -1}}
    ]
    
    results = list(mongo_db.lessons_collection.aggregate(pipeline))
    print(f"   Results:")
    for result in results:
        print(f"   - {result['_id']}: {result['count']} lessons, {result['total_hours']:.1f} hours")


def main():
    """Main execution function"""
    print_header("Sample Data Population Script")
    
    print("Connecting to MongoDB...")
    
    # Initialize MongoDB connection
    try:
        mongo_db.connect()
        print(f"   [SUCCESS] Connected to MongoDB")
        print(f"   Database: {mongo_db.db.name}")
        print(f"   Collections: users, lessons")
    except Exception as e:
        print(f"\n[ERROR] MongoDB connection failed: {e}")
        print("\nPlease check:")
        print("  1. Do you have a .env file in the project root?")
        print("  2. Does .env have MONGO_CLUSTER_URL set?")
        print("  3. Is your MongoDB server running?")
        print("\nExample .env:")
        print("  MONGO_CLUSTER_URL=mongodb://localhost:27017")
        print("  MONGO_DATABASE=institute_db")
        sys.exit(1)
    
    try:
        # Step 1: Create teacher
        teacher = create_teacher()
        
        # Step 2: Create lessons
        lessons = create_lessons(teacher)
        
        # Step 3: Query and print summary
        query_and_print_summary(teacher)
        
        # Step 4: Demonstrate specific queries
        demonstrate_specific_queries(teacher)
        
        print_header("[SUCCESS] Script Completed Successfully!")
        
        print("\nYou can now:")
        print(f"   1. Login with username: 'john_doe_teacher', password: 'password123'")
        print(f"   2. View lessons in the API: GET /api/v1/lessons/my-lessons")
        print(f"   3. Filter by type: ?lesson_type=individual or ?lesson_type=group")
        print(f"   4. Query the database directly using MongoDB Compass")
        print(f"   5. Run this script again to regenerate fresh data")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Close MongoDB connection
        if mongo_db.client:
            mongo_db.close()
            print("\n[INFO] MongoDB connection closed")


if __name__ == "__main__":
    main()

