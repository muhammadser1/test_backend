"""
Subject pricing configuration for teacher payments.
NOW USES DATABASE INSTEAD OF HARDCODED VALUES!

Admins manage pricing through API endpoints.
This module provides helper functions to fetch pricing from database.
"""

from typing import Optional
from app.db import mongo_db
from app.models.pricing import Pricing


# Default prices (fallback if subject not found in database)
DEFAULT_INDIVIDUAL_PRICE = 45.0
DEFAULT_GROUP_PRICE = 28.0


def get_subject_price(subject: str, education_level: str, lesson_type: str = "individual") -> float:
    """
    Get the price per hour for a specific subject, education level, and lesson type from DATABASE.
    
    Args:
        subject: Subject name (e.g., "Math", "Arabic")
        education_level: Education level ("elementary", "middle", "secondary")
        lesson_type: "individual" or "group"
    
    Returns:
        Price per hour for the subject, education level, and lesson type
    """
    # Fetch from database
    pricing = Pricing.find_by_subject_and_level(subject, education_level, mongo_db.pricing_collection)
    
    if pricing:
        return pricing.get_price(lesson_type)
    
    # Fallback to defaults if not found
    return DEFAULT_INDIVIDUAL_PRICE if lesson_type.lower() == "individual" else DEFAULT_GROUP_PRICE


def calculate_subject_earnings(hours: float, subject: str, education_level: str, lesson_type: str = "individual") -> float:
    """
    Calculate earnings for a specific subject, education level, and lesson type.
    
    Args:
        hours: Total hours taught
        subject: Subject name
        education_level: Education level ("elementary", "middle", "secondary")
        lesson_type: "individual" or "group"
    
    Returns:
        Total earnings for this subject
    """
    price_per_hour = get_subject_price(subject, education_level, lesson_type)
    return round(hours * price_per_hour, 2)


def get_all_subject_prices() -> dict:
    """
    Get all subject prices from DATABASE for admin reference.
    
    Returns:
        Dictionary of all subject prices (with education level, individual and group rates)
    """
    pricing_list = Pricing.get_all(mongo_db.pricing_collection)
    
    result = {}
    for pricing in pricing_list:
        # Create key with subject + education level
        key = f"{pricing.subject.lower()}_{pricing.education_level.value if hasattr(pricing.education_level, 'value') else pricing.education_level}"
        result[key] = {
            "subject": pricing.subject,
            "education_level": pricing.education_level.value if hasattr(pricing.education_level, 'value') else pricing.education_level,
            "individual": pricing.individual_price,
            "group": pricing.group_price
        }
    
    return result

