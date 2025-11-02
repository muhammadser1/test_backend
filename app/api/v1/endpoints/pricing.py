"""
Admin Pricing Management Endpoints

Admins can create, read, update, and delete subject pricing.
Teachers and public can query pricing.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Dict, Optional
from app.schemas.pricing import (
    PricingCreate,
    PricingUpdate,
    PricingResponse,
    PricingListResponse,
    PricingLookupResponse
)
from app.models.pricing import Pricing
from app.api.deps import get_current_admin, get_current_user, get_optional_user
from app.db import mongo_db

router = APIRouter()


# ===== Admin Endpoints (CRUD) =====

@router.post("/", response_model=PricingResponse, status_code=status.HTTP_201_CREATED)
def create_pricing(
    pricing_data: PricingCreate,
    current_user: Dict = Depends(get_current_admin)
):
    """
    Admin creates new subject pricing
    - Subject + Education Level combination must be unique
    - Both individual and group prices required
    """
    # Check if subject + education_level combination already exists
    if Pricing.subject_and_level_exists(
        pricing_data.subject, 
        pricing_data.education_level.value, 
        mongo_db.pricing_collection
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pricing for subject '{pricing_data.subject}' at '{pricing_data.education_level.value}' level already exists"
        )
    
    # Create pricing
    new_pricing = Pricing(
        subject=pricing_data.subject,
        education_level=pricing_data.education_level,
        individual_price=pricing_data.individual_price,
        group_price=pricing_data.group_price
    )
    
    new_pricing.save(mongo_db.pricing_collection)
    
    return PricingResponse(
        id=new_pricing._id,
        subject=new_pricing.subject,
        education_level=new_pricing.education_level,
        individual_price=new_pricing.individual_price,
        group_price=new_pricing.group_price
    )


@router.get("/", response_model=PricingListResponse)
def get_all_pricing(
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Get all pricing (public endpoint)
    Available to everyone - no authentication required
    """
    # Get all pricing
    pricing_list = Pricing.get_all(mongo_db.pricing_collection)
    
    pricing_responses = [
        PricingResponse(
            id=p._id,
            subject=p.subject,
            education_level=p.education_level,
            individual_price=p.individual_price,
            group_price=p.group_price
        )
        for p in pricing_list
    ]
    
    return PricingListResponse(
        total=len(pricing_responses),
        pricing=pricing_responses
    )


@router.get("/{pricing_id}", response_model=PricingResponse)
def get_pricing_by_id(
    pricing_id: str,
    current_user: Dict = Depends(get_current_admin)
):
    """
    Admin gets pricing by ID
    """
    pricing = Pricing.find_by_id(pricing_id, mongo_db.pricing_collection)
    
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing not found"
        )
    
    return PricingResponse(
        id=pricing._id,
        subject=pricing.subject,
        education_level=pricing.education_level,
        individual_price=pricing.individual_price,
        group_price=pricing.group_price
    )


@router.put("/{pricing_id}", response_model=PricingResponse)
def update_pricing(
    pricing_id: str,
    pricing_update: PricingUpdate,
    current_user: Dict = Depends(get_current_admin)
):
    """
    Admin updates pricing
    - Can update prices or education level
    - Cannot change to existing subject + education_level combination
    """
    pricing = Pricing.find_by_id(pricing_id, mongo_db.pricing_collection)
    
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing not found"
        )
    
    # Check if trying to change to existing subject + education_level combination
    new_subject = pricing_update.subject if pricing_update.subject else pricing.subject
    new_level = pricing_update.education_level.value if pricing_update.education_level else pricing.education_level.value
    
    # Only check if subject or education_level is being changed
    if (pricing_update.subject and pricing_update.subject != pricing.subject) or \
       (pricing_update.education_level and pricing_update.education_level != pricing.education_level):
        if Pricing.subject_and_level_exists(new_subject, new_level, mongo_db.pricing_collection, exclude_id=pricing_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pricing for subject '{new_subject}' at '{new_level}' level already exists"
            )
    
    # Update fields
    update_data = pricing_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(pricing, field):
            setattr(pricing, field, value)
    
    pricing.update_in_db(mongo_db.pricing_collection)
    
    return PricingResponse(
        id=pricing._id,
        subject=pricing.subject,
        education_level=pricing.education_level,
        individual_price=pricing.individual_price,
        group_price=pricing.group_price
    )


@router.delete("/{pricing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pricing(
    pricing_id: str,
    current_user: Dict = Depends(get_current_admin)
):
    """
    Admin deletes pricing
    """
    pricing = Pricing.find_by_id(pricing_id, mongo_db.pricing_collection)
    
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing not found"
        )
    
    Pricing.delete(pricing_id, mongo_db.pricing_collection)
    return None


# ===== Public/Teacher Endpoints (Query) =====

@router.get("/lookup/{subject}/{education_level}", response_model=PricingLookupResponse)
def lookup_price(
    subject: str,
    education_level: str,
    lesson_type: str = "individual",
    current_user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Lookup price for a specific subject, education level, and lesson type
    Available to all users (authenticated or not)
    """
    pricing = Pricing.find_by_subject_and_level(subject, education_level, mongo_db.pricing_collection)
    
    if not pricing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pricing not found for subject '{subject}' at '{education_level}' level"
        )
    
    price_per_hour = pricing.get_price(lesson_type)
    
    return PricingLookupResponse(
        subject=pricing.subject,
        education_level=pricing.education_level.value if hasattr(pricing.education_level, 'value') else pricing.education_level,
        lesson_type=lesson_type,
        price_per_hour=price_per_hour,
        found=True
    )


@router.get("/public/all", response_model=List[PricingResponse])
def get_public_pricing():
    """
    Get all pricing (public endpoint, no auth required)
    Useful for displaying pricing on public pages
    """
    pricing_list = Pricing.get_all(mongo_db.pricing_collection)
    
    return [
        PricingResponse(
            id=p._id,
            subject=p.subject,
            education_level=p.education_level,
            individual_price=p.individual_price,
            group_price=p.group_price
        )
        for p in pricing_list
    ]


# @router.get("/subject-prices", response_model=AllSubjectPricesResponse)
# def get_subject_prices(
#     current_admin: Dict = Depends(get_current_admin)
# ):
#     """
#     Admin gets all subject prices for reference.
#     Useful to know the pricing structure.
#     """
#     from app.schemas.earnings import AllSubjectPricesResponse, SubjectPriceResponse
#     from app.core.pricing import get_all_subject_prices, DEFAULT_INDIVIDUAL_PRICE, DEFAULT_GROUP_PRICE
    
#     all_prices = get_all_subject_prices()
    
#     price_list = [
#         SubjectPriceResponse(
#             subject=subject,
#             individual_price=prices["individual"],
#             group_price=prices["group"]
#         )
#         for subject, prices in sorted(all_prices.items())
#     ]
    
#     return AllSubjectPricesResponse(
#         prices=price_list,
#         default_individual_price=DEFAULT_INDIVIDUAL_PRICE,
#         default_group_price=DEFAULT_GROUP_PRICE
#     )