from fastapi import HTTPException, Depends, Header
from typing import Optional
from app.services.auth_service import AuthService


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Middleware để lấy current user từ Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Session token required"
        )
    
    # Xử lý Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    session_token = authorization.replace("Bearer ", "")
    
    auth_service = AuthService()
    user_data = auth_service.validate_session(session_token)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token"
        )
    
    return user_data['user']


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Middleware để lấy current user (optional)"""
    if not authorization:
        return None
    
    # Xử lý Bearer token
    if not authorization.startswith("Bearer "):
        return None
    
    session_token = authorization.replace("Bearer ", "")
    
    auth_service = AuthService()
    user_data = auth_service.validate_session(session_token)
    
    return user_data['user'] if user_data else None 