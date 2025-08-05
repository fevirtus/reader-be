from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.services.cache_service import cache_service
from app.services.user_service import UserService
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_cache_stats(current_user: dict = Depends(get_current_user)):
    """Lấy thống kê cache (admin only)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xem cache stats")
    
    stats = cache_service.get_stats()
    return {
        "success": True,
        "data": stats
    }


@router.post("/clear")
async def clear_cache(current_user: dict = Depends(get_current_user)):
    """Xóa tất cả cache (admin only)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa cache")
    
    cache_service.clear()
    return {
        "success": True,
        "message": "Đã xóa tất cả cache"
    }


@router.post("/cleanup")
async def cleanup_expired_cache(current_user: dict = Depends(get_current_user)):
    """Dọn dẹp cache hết hạn (admin only)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền dọn dẹp cache")
    
    cleaned_count = cache_service.cleanup_expired()
    return {
        "success": True,
        "message": f"Đã dọn dẹp {cleaned_count} cache entries hết hạn",
        "cleaned_count": cleaned_count
    }


@router.delete("/novels/{novel_id}")
async def clear_novel_cache(novel_id: int, current_user: dict = Depends(get_current_user)):
    """Xóa cache của novel cụ thể (admin only)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa cache")
    
    # Xóa cache novel
    cache_service.delete(f"novel:{novel_id}")
    
    # Xóa cache novels list
    keys_to_delete = []
    for key in cache_service.cache.keys():
        if key.startswith("novels:"):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache_service.delete(key)
    
    return {
        "success": True,
        "message": f"Đã xóa cache cho novel {novel_id}"
    }


@router.delete("/chapters/{chapter_id}")
async def clear_chapter_cache(chapter_id: int, current_user: dict = Depends(get_current_user)):
    """Xóa cache của chapter cụ thể (admin only)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa cache")
    
    # Xóa cache chapter
    cache_service.delete(f"chapter:{chapter_id}")
    cache_service.delete(f"chapter_content:{chapter_id}:markdown")
    cache_service.delete(f"chapter_content:{chapter_id}:html")
    
    # Xóa cache chapters list
    keys_to_delete = []
    for key in cache_service.cache.keys():
        if key.startswith("chapters:"):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache_service.delete(key)
    
    return {
        "success": True,
        "message": f"Đã xóa cache cho chapter {chapter_id}"
    }


@router.get("/keys")
async def list_cache_keys(current_user: dict = Depends(get_current_user)):
    """Liệt kê tất cả cache keys (admin only)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xem cache keys")
    
    keys = list(cache_service.cache.keys())
    return {
        "success": True,
        "data": {
            "total_keys": len(keys),
            "keys": keys[:100]  # Giới hạn 100 keys để tránh response quá lớn
        }
    } 