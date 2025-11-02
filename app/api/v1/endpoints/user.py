from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
import logging
from app.schemas.user import (
    LoginRequest, 
    LoginResponse, 
    UserSummary,
    LogoutResponse, 
    TeacherSignup, 
    UserResponse,
    UserRole,
    UserStatus,
    ProfileUpdate,
    ChangePasswordRequest
)
from app.models.user import User
from app.db import mongo_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    """
    User login - returns access token and user info
    """
    # Find user by username using model method
    user = User.find_by_username(credentials.username, mongo_db.users_collection)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Check if user is active using model method
    if not user.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status.value}",
        )
    
    # Update last login using model method
    user.update_last_login()
    user.update_in_db(mongo_db.users_collection, {"last_login": user.last_login})
    
    # Create access token
    token_data = {
        "sub": str(user._id),
        "username": user.username,
        "role": user.role.value,
    }
    access_token = create_access_token(token_data)
    
    # Return login response with token and user info
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserSummary(
            id=str(user._id),
            username=user.username,
            role=user.role,
            status=user.status,
            last_login=user.last_login
        )
    )


@router.post("/logout", response_model=LogoutResponse)
def logout(current_user: dict = Depends(get_current_user)):
    """
    User logout (client should delete token)
    """
    return LogoutResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's full profile
    """
    return UserResponse(
        id=str(current_user["_id"]),
        username=current_user["username"],
        role=current_user["role"],
        status=current_user.get("status", "active"),
        email=current_user.get("email"),
        first_name=current_user.get("first_name"),
        last_name=current_user.get("last_name"),
        phone=current_user.get("phone"),
        birthdate=current_user.get("birthdate"),
        last_login=current_user.get("last_login"),
        created_at=current_user.get("created_at", datetime.utcnow()),
        updated_at=current_user.get("updated_at"),
    )


@router.put("/me", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's profile (name, phone, email)
    """
    user_id = str(current_user["_id"])
    username = current_user.get("username")
    
    logger.info(f"Profile update requested by user {username} (ID: {user_id})")
    
    # Get user from database
    user = User.find_by_id(user_id, mongo_db.users_collection)
    
    if not user:
        logger.warning(f"User not found for profile update: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Log current values
    old_values = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone
    }
    logger.debug(f"Current profile values for {username}: {old_values}")
    
    # Check email uniqueness if updating email
    if profile_data.email and profile_data.email != user.email:
        logger.info(f"User {username} attempting to change email from {user.email} to {profile_data.email}")
        if User.email_exists(profile_data.email, mongo_db.users_collection):
            logger.warning(f"Email already exists: {profile_data.email} for user {username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )
    
    # Prepare update data
    update_data = profile_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Log changes
    changes = {}
    for key, new_value in update_data.items():
        if key in old_values and old_values[key] != new_value:
            changes[key] = {"old": old_values[key], "new": new_value}
    
    if changes:
        logger.info(f"Profile update changes for {username}: {changes}")
    else:
        logger.info(f"No actual changes detected for {username}")
    
    # Update user
    try:
        user.update_in_db(mongo_db.users_collection, update_data)
        logger.info(f"Profile updated successfully for user {username} (ID: {user_id})")
    except Exception as e:
        logger.error(f"Error updating profile for user {username} (ID: {user_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Get updated user
    updated_user = User.find_by_id(user_id, mongo_db.users_collection)
    
    return UserResponse(
        id=updated_user._id,
        username=updated_user.username,
        role=updated_user.role,
        status=updated_user.status,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        phone=updated_user.phone,
        birthdate=updated_user.birthdate,
        last_login=updated_user.last_login,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
    )


@router.put("/me/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Change current user's password
    """
    # Get user from database
    user = User.find_by_id(str(current_user["_id"]), mongo_db.users_collection)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    
    # Update password
    new_hashed_password = get_password_hash(password_data.new_password)
    user.update_in_db(mongo_db.users_collection, {
        "hashed_password": new_hashed_password,
        "updated_at": datetime.utcnow()
    })
    
    return {"message": "Password updated successfully"}


