from fastapi import HTTPException, Depends, Header
from typing import Optional
from app.services.auth_service import AuthService


async def get_current_user(session_token: Optional[str] = Header(None)) -> dict:
    """Middleware để lấy current user từ session token"""
    if not session_token:
        raise HTTPException(
            status_code=401,
            detail="Session token required"
        )
    
    auth_service = AuthService()
    user_data = auth_service.validate_session(session_token)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token"
        )
    
    return user_data['user']


async def get_optional_user(session_token: Optional[str] = Header(None)) -> Optional[dict]:
    """Middleware để lấy current user (optional)"""
    if not session_token:
        return None
    
    auth_service = AuthService()
    user_data = auth_service.validate_session(session_token)
    
    return user_data['user'] if user_data else None 