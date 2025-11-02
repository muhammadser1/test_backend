from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from app.core.security import verify_token
from app.db import mongo_db

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    Get current authenticated user from token
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Find user by string ID (UUID)
    user = mongo_db.users_collection.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.get("status") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.get('status')}",
        )
    
    return user


def get_current_admin(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Verify that current user is an admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_current_teacher(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Verify that current user is a teacher
    """
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required",
        )
    return current_user


def get_current_admin_or_teacher(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    Verify that current user is either an admin or a teacher
    """
    role = current_user.get("role")
    if role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or teacher access required",
        )
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
) -> Optional[Dict]:
    """
    Get current user if authenticated, otherwise return None.
    Used for endpoints that are public but may have different behavior for authenticated users.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        return None
    
    user_id: str = payload.get("sub")
    if not user_id:
        return None
    
    user = mongo_db.users_collection.find_one({"_id": user_id})
    
    if not user or user.get("status") != "active":
        return None
    
    return user

