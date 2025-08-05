from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.user import RoleUpdateRequest, RoleUpdateResponse, UserProfileResponse
from app.services.user_service import UserService
from app.core.auth import get_current_user

router = APIRouter()
user_service = UserService()


@router.get("/users", response_model=List[UserProfileResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Lấy danh sách tất cả users (chỉ admin)"""
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập")
    
    users = user_service.get_all_users(current_user['id'])
    return users


@router.get("/users/{role}", response_model=List[UserProfileResponse])
async def get_users_by_role(role: str, current_user: dict = Depends(get_current_user)):
    """Lấy danh sách users theo role (chỉ admin)"""
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập")
    
    if role not in ['user', 'admin']:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")
    
    users = user_service.get_users_by_role(current_user['id'], role)
    return users


@router.post("/users/role", response_model=RoleUpdateResponse)
async def change_user_role(
    request: RoleUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Thay đổi role của user (chỉ admin)"""
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền thay đổi role")
    
    if request.role not in ['user', 'admin']:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")
    
    success = user_service.change_user_role(current_user['id'], request.user_id, request.role)
    
    if success:
        return RoleUpdateResponse(
            success=True,
            message=f"Đã thay đổi role của user {request.user_id} thành {request.role}",
            user_id=request.user_id,
            new_role=request.role
        )
    else:
        raise HTTPException(status_code=400, detail="Không thể thay đổi role")


@router.get("/users/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(user_id: str, current_user: dict = Depends(get_current_user)):
    """Lấy thông tin profile của user (chỉ admin hoặc chính user đó)"""
    # Admin có thể xem profile của bất kỳ user nào
    # User thường chỉ có thể xem profile của chính mình
    if not user_service.is_admin(current_user['id']) and current_user['id'] != user_id:
        raise HTTPException(status_code=403, detail="Không có quyền truy cập")
    
    profile = user_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    
    return profile


@router.get("/check-admin")
async def check_admin_status(current_user: dict = Depends(get_current_user)):
    """Kiểm tra user có phải admin không"""
    is_admin = user_service.is_admin(current_user['id'])
    return {
        "user_id": current_user['id'],
        "is_admin": is_admin,
        "role": "admin" if is_admin else "user"
    } 