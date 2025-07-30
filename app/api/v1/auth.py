from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.auth import (
    UserRegister, UserLogin, UserProfileUpdate,
    UserProfileResponse, TokenResponse, SessionResponse
)
from app.services.auth_service import AuthService
from app.core.auth import get_current_user

router = APIRouter()

@router.post("/register", response_model=SessionResponse)
def register_user(user_data: UserRegister):
    """Đăng ký user mới"""
    auth_service = AuthService()
    try:
        result = auth_service.register_user(user_data)
        return SessionResponse(
            session_token=result["session_token"],
            expires_at=result["expires_at"],
            user=UserProfileResponse(**result["user"])
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=SessionResponse)
def login_user(user_data: UserLogin):
    """Đăng nhập user"""
    auth_service = AuthService()
    try:
        result = auth_service.login_user(user_data)
        return SessionResponse(
            session_token=result["session_token"],
            expires_at=result["expires_at"],
            user=UserProfileResponse(**result["user"])
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
def logout_user(current_user: dict = Depends(get_current_user), session_token: str = None):
    """Đăng xuất user"""
    auth_service = AuthService()
    try:
        success = auth_service.logout_user(session_token)
        if success:
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(status_code=400, detail="Logout failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Lấy thông tin user hiện tại"""
    return UserProfileResponse(**current_user)

@router.put("/me", response_model=UserProfileResponse)
def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Cập nhật profile của user"""
    auth_service = AuthService()
    try:
        # Convert Pydantic model to dict, excluding None values
        update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        result = auth_service.update_user_profile(current_user["id"], update_data)
        if result:
            return UserProfileResponse(**result)
        else:
            raise HTTPException(status_code=400, detail="Failed to update profile")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate-session")
def validate_session(session_token: str):
    """Validate session token"""
    auth_service = AuthService()
    try:
        result = auth_service.validate_session(session_token)
        if result:
            return {"valid": True, "user": result["user"]}
        else:
            return {"valid": False}
    except Exception as e:
        return {"valid": False, "error": str(e)}

@router.get("/check-email")
def check_email_exists(email: str = Query(..., description="Email to check")):
    """Kiểm tra email đã tồn tại chưa"""
    auth_service = AuthService()
    try:
        exists = auth_service.check_user_exists(email)
        return {"exists": exists, "email": email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 