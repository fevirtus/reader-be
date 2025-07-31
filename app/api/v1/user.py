from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from app.schemas.auth import UserProfileUpdate, UserProfileResponse, SessionResponse
from app.services.auth_service import AuthService
from app.core.auth import get_current_user

class ValidateSessionRequest(BaseModel):
    session_token: str

router = APIRouter()

@router.get("/profile", response_model=UserProfileResponse)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Lấy thông tin user hiện tại"""
    return UserProfileResponse(**current_user)

@router.put("/profile", response_model=UserProfileResponse)
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

@router.post("/logout")
def logout_user(current_user: dict = Depends(get_current_user), authorization: str = Header(None)):
    """Đăng xuất user"""
    auth_service = AuthService()
    try:
        # Extract session token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        session_token = authorization.replace("Bearer ", "")
        success = auth_service.logout_user(session_token)
        
        if success:
            return {"message": "Logged out successfully"}
        else:
            raise HTTPException(status_code=400, detail="Logout failed")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/validate-session")
def validate_session(request: ValidateSessionRequest):
    """Validate session token"""
    auth_service = AuthService()
    try:
        result = auth_service.validate_session(request.session_token)
        if result:
            return {"valid": True, "user": result["user"]}
        else:
            return {"valid": False}
    except Exception as e:
        return {"valid": False, "error": str(e)}

@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Alias cho /profile - để tương thích với frontend cũ"""
    return UserProfileResponse(**current_user)

@router.put("/me", response_model=UserProfileResponse)
def update_me(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Alias cho /profile - để tương thích với frontend cũ"""
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