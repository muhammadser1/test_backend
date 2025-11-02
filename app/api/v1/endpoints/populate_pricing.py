"""
Pricing Population Endpoints
Populate database with default subject pricing
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.api.deps import get_current_admin
from app.schemas.user import UserResponse
from app.models.pricing import Pricing, EducationLevel
from app.db import mongo_db

router = APIRouter()


# Default subjects with pricing
DEFAULT_SUBJECTS = [
    {
        "subject": "Mathematics",
        "individual_price": 50.0,
        "group_price": 30.0
    },
    {
        "subject": "Physics",
        "individual_price": 55.0,
        "group_price": 35.0
    },
    {
        "subject": "Chemistry",
        "individual_price": 55.0,
        "group_price": 35.0
    },
    {
        "subject": "Biology",
        "individual_price": 50.0,
        "group_price": 30.0
    },
    {
        "subject": "English",
        "individual_price": 45.0,
        "group_price": 25.0
    },
    {
        "subject": "History",
        "individual_price": 40.0,
        "group_price": 25.0
    },
    {
        "subject": "Geography",
        "individual_price": 40.0,
        "group_price": 25.0
    },
    {
        "subject": "Computer Science",
        "individual_price": 60.0,
        "group_price": 40.0
    },
    {
        "subject": "Programming",
        "individual_price": 65.0,
        "group_price": 45.0
    },
    {
        "subject": "Arabic",
        "individual_price": 45.0,
        "group_price": 25.0
    },
    {
        "subject": "French",
        "individual_price": 50.0,
        "group_price": 30.0
    },
    {
        "subject": "Spanish",
        "individual_price": 50.0,
        "group_price": 30.0
    },
    {
        "subject": "Music",
        "individual_price": 55.0,
        "group_price": 35.0
    },
    {
        "subject": "Art",
        "individual_price": 50.0,
        "group_price": 30.0
    },
    {
        "subject": "Physical Education",
        "individual_price": 40.0,
        "group_price": 20.0
    }
]


@router.post("/populate-defaults")
def populate_default_pricing(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Populate database with default subject pricing for all education levels
    - Creates pricing for elementary, middle, and secondary levels
    - Only adds subject+level combinations that don't already exist
    - Admin only
    """
    created_count = 0
    skipped_count = 0
    errors = []
    
    # Price multipliers for each education level
    level_multipliers = {
        EducationLevel.ELEMENTARY: 0.85,  # 15% less than base
        EducationLevel.MIDDLE: 1.0,       # base price
        EducationLevel.SECONDARY: 1.20,   # 20% more than base
    }
    
    for subject_data in DEFAULT_SUBJECTS:
        subject_name = subject_data["subject"]
        
        # Create pricing for each education level
        for level, multiplier in level_multipliers.items():
            # Check if subject + level combination already exists
            if Pricing.subject_and_level_exists(subject_name, level.value, mongo_db.pricing_collection):
                skipped_count += 1
                continue
            
            try:
                # Create new pricing with adjusted prices based on education level
                new_pricing = Pricing(
                    subject=subject_data["subject"],
                    education_level=level,
                    individual_price=round(subject_data["individual_price"] * multiplier, 2),
                    group_price=round(subject_data["group_price"] * multiplier, 2)
                )
                
                new_pricing.save(mongo_db.pricing_collection)
                created_count += 1
                
            except Exception as e:
                errors.append({
                    "subject": f"{subject_name} ({level.value})",
                    "error": str(e)
                })
    
    return {
        "success": True,
        "message": f"Pricing population completed for all education levels",
        "created": created_count,
        "skipped": skipped_count,
        "total_combinations": len(DEFAULT_SUBJECTS) * 3,  # 3 levels per subject
        "errors": errors if errors else None,
        "triggered_by": current_admin.get("email", "unknown")
    }


@router.post("/populate-custom")
def populate_custom_pricing(
    subjects: List[dict],
    current_admin: dict = Depends(get_current_admin)
):
    """
    Populate database with custom subject pricing
    - Only adds subject+level combinations that don't already exist
    - Admin only
    
    Expected format:
    [
        {
            "subject": "Subject Name",
            "education_level": "elementary" | "middle" | "secondary",
            "individual_price": 50.0,
            "group_price": 30.0
        },
        ...
    ]
    """
    created_count = 0
    skipped_count = 0
    errors = []
    
    for subject_data in subjects:
        # Validate required fields
        if not all(key in subject_data for key in ["subject", "education_level", "individual_price", "group_price"]):
            errors.append({
                "subject": subject_data.get("subject", "Unknown"),
                "error": "Missing required fields: subject, education_level, individual_price, group_price"
            })
            continue
        
        subject_name = subject_data["subject"]
        education_level = subject_data["education_level"]
        
        # Validate education level
        try:
            level_enum = EducationLevel(education_level)
        except ValueError:
            errors.append({
                "subject": f"{subject_name} ({education_level})",
                "error": f"Invalid education_level. Must be: elementary, middle, or secondary"
            })
            continue
        
        # Check if subject + level combination already exists
        if Pricing.subject_and_level_exists(subject_name, education_level, mongo_db.pricing_collection):
            skipped_count += 1
            continue
        
        try:
            # Create new pricing
            new_pricing = Pricing(
                subject=subject_data["subject"],
                education_level=level_enum,
                individual_price=subject_data["individual_price"],
                group_price=subject_data["group_price"]
            )
            
            new_pricing.save(mongo_db.pricing_collection)
            created_count += 1
            
        except Exception as e:
            errors.append({
                "subject": f"{subject_name} ({education_level})",
                "error": str(e)
            })
    
    return {
        "success": True,
        "message": f"Custom pricing population completed",
        "created": created_count,
        "skipped": skipped_count,
        "total_entries": len(subjects),
        "errors": errors if errors else None,
        "triggered_by": current_admin.get("email", "unknown")
    }


@router.get("/default-subjects")
def get_default_subjects():
    """
    Get list of default subjects with pricing
    Public endpoint - no auth required
    """
    return {
        "subjects": DEFAULT_SUBJECTS,
        "total": len(DEFAULT_SUBJECTS),
        "note": "These are the default subjects that can be populated using /populate-defaults endpoint"
    }

