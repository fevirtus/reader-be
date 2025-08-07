from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from app.schemas.user import RoleUpdateRequest, RoleUpdateResponse, UserProfileResponse
from app.services.user_service import UserService
from app.services.novel_service import NovelService
from app.services.chapter_service import ChapterService
from app.core.auth import get_current_user

router = APIRouter()
user_service = UserService()
novel_service = NovelService()
chapter_service = ChapterService()


@router.get("/users", response_model=List[UserProfileResponse])
async def get_all_users(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Trang hiện tại"),
    limit: int = Query(20, ge=1, le=100, description="Số bản ghi trả về"),
    search: str = Query(None, description="Từ khóa tìm kiếm"),
    role: str = Query(None, description="Lọc theo vai trò")
):
    """Lấy danh sách tất cả users với pagination (chỉ admin)"""
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập")
    
    users = user_service.get_all_users_paginated(current_user['id'], page, limit, search, role)
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


@router.get("/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """Lấy thống kê tổng quan cho admin dashboard"""
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập")
    
    try:
        # Lấy thống kê novels
        novels_stats = novel_service.get_stats()
        
        # Lấy thống kê chapters
        chapters_stats = chapter_service.get_stats()
        
        # Lấy thống kê users
        users_stats = user_service.get_stats()
        
        return {
            "totalNovels": novels_stats.get("total", 0),
            "totalChapters": chapters_stats.get("total", 0),
            "totalUsers": users_stats.get("total", 0),
            "totalViews": novels_stats.get("total_views", 0) + chapters_stats.get("total_views", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thống kê: {str(e)}")


@router.get("/activities")
async def get_recent_activities(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50, description="Số hoạt động trả về")
):
    """Lấy danh sách hoạt động gần đây cho admin dashboard"""
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền truy cập")
    
    try:
        # Lấy hoạt động từ novels
        novel_activities = novel_service.get_recent_activities(limit // 2)
        
        # Lấy hoạt động từ users
        user_activities = user_service.get_recent_activities(limit // 2)
        
        # Kết hợp và sắp xếp theo thời gian
        all_activities = novel_activities + user_activities
        all_activities.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "activities": all_activities[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy hoạt động: {str(e)}") 