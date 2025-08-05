from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from app.schemas.novel import NovelResponse, NovelCreate, NovelUpdate
from app.services.novel_service import NovelService
from app.services.user_service import UserService
from app.core.auth import get_current_user

router = APIRouter()


@router.get("")
@router.get("/")
def get_novels(
    page: int = Query(1, ge=1, description="Trang hiện tại (bắt đầu từ 1)"),
    limit: int = Query(20, ge=1, le=100, description="Số bản ghi trả về"),
    search: str = Query(None, description="Từ khóa tìm kiếm"),
    status: str = Query(None, description="Trạng thái novel (ongoing, completed)"),
    author: str = Query(None, description="Tác giả"),
):
    """
    Lấy danh sách novels với pagination
    
    - **page**: Trang hiện tại (bắt đầu từ 1)
    - **limit**: Số bản ghi trả về (tối đa 100)
    - **search**: Từ khóa tìm kiếm trong title và description
    - **status**: Lọc theo trạng thái (ongoing, completed)
    - **author**: Lọc theo tác giả
    """
    service = NovelService()
    
    if search:
        result = service.search_novels(search, page, limit)
    else:
        result = service.get_novels(page, limit, status, author)
    
    return result


@router.get("/{novel_id}", response_model=NovelResponse)
def get_novel(novel_id: int):
    """
    Lấy thông tin novel theo ID
    
    - **novel_id**: ID của novel
    - Tự động tăng số lượt xem khi truy cập
    """
    service = NovelService()
    novel = service.get_novel(novel_id)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel không tồn tại")
    
    # Tăng số lượt xem
    service.increment_views(novel_id)
    
    return novel


# Admin endpoints
@router.post("", response_model=NovelResponse)
def create_novel(
    novel_data: NovelCreate,
    current_user: dict = Depends(get_current_user)
):
    """Tạo novel mới (chỉ admin)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền tạo novel")
    
    service = NovelService()
    novel = service.create_novel(novel_data)
    
    if not novel:
        raise HTTPException(status_code=400, detail="Không thể tạo novel")
    
    return novel


@router.put("/{novel_id}", response_model=NovelResponse)
def update_novel(
    novel_id: int,
    novel_data: NovelUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Cập nhật novel (chỉ admin)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền cập nhật novel")
    
    service = NovelService()
    novel = service.update_novel(novel_id, novel_data)
    
    if not novel:
        raise HTTPException(status_code=404, detail="Novel không tồn tại")
    
    return novel


@router.delete("/{novel_id}")
def delete_novel(
    novel_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Xóa novel (chỉ admin)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa novel")
    
    service = NovelService()
    success = service.delete_novel(novel_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Novel không tồn tại")
    
    return {"message": "Novel đã được xóa thành công"} 