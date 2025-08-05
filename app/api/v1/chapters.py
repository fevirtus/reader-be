from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.schemas.chapter import ChapterResponse, ChapterCreate, ChapterUpdate
from app.schemas.reading import ReadingProgressCreate
from app.services.chapter_service import ChapterService
from app.services.reading_service import ReadingService
from app.services.user_service import UserService
from app.core.auth import get_optional_user, get_current_user

router = APIRouter()


@router.get("")
@router.get("/")
def get_chapters(
    novel_id: int = Query(..., description="ID của novel"),
    page: Optional[int] = Query(None, ge=1, description="Trang hiện tại (bắt đầu từ 1)"),
    skip: Optional[int] = Query(None, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(50, ge=1, le=200, description="Số bản ghi trả về"),
):
    """
    Lấy danh sách chapters của một novel với pagination
    
    - **novel_id**: ID của novel
    - **page**: Trang hiện tại (bắt đầu từ 1) - ưu tiên hơn skip
    - **skip**: Số bản ghi bỏ qua (chỉ dùng khi không có page)
    - **limit**: Số bản ghi trả về (tối đa 200)
    """
    service = ChapterService()
    
    # Nếu có page thì sử dụng page, ngược lại tính page từ skip
    if page is not None:
        result = service.get_chapters_by_novel(novel_id, page, limit)
    elif skip is not None:
        # Tính page từ skip
        calculated_page = (skip // limit) + 1
        result = service.get_chapters_by_novel(novel_id, calculated_page, limit)
    else:
        # Mặc định page = 1
        result = service.get_chapters_by_novel(novel_id, 1, limit)
    
    return result


@router.get("/{chapter_id}")
def get_chapter_content(
    chapter_id: int,
    format: str = Query("markdown", regex="^(markdown|html)$", description="Định dạng nội dung"),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Lấy nội dung chapter để hiển thị
    
    - **chapter_id**: ID của chapter
    - **format**: Định dạng nội dung (markdown/html)
    - Tự động cập nhật reading progress nếu user đã đăng nhập
    """
    service = ChapterService()
    chapter = service.get_chapter(chapter_id)
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    content = service.get_chapter_content(chapter_id, format)
    
    if not content:
        raise HTTPException(status_code=404, detail="Nội dung chapter không tồn tại")
    
    # Tăng số lượt xem
    service.increment_views(chapter_id)
    
    # Tự động cập nhật reading progress nếu user đã đăng nhập
    if current_user:
        reading_service = ReadingService()
        progress_data = ReadingProgressCreate(
            novel_id=chapter['novel_id'],
            chapter_id=chapter_id,
            chapter_number=chapter['chapter_number']
        )
        reading_service.update_reading_progress(current_user['id'], progress_data)
    
    return {
        "content": content, 
        "format": format,
        "chapter_info": {
            "id": chapter['id'],
            "title": chapter['title'],
            "chapter_number": chapter['chapter_number'],
            "novel_id": chapter['novel_id']
        }
    }


# Admin endpoints
@router.post("", response_model=ChapterResponse)
def create_chapter(
    chapter_data: ChapterCreate,
    current_user: dict = Depends(get_current_user)
):
    """Tạo chapter mới (chỉ admin)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền tạo chapter")
    
    service = ChapterService()
    chapter = service.create_chapter(chapter_data)
    
    if not chapter:
        raise HTTPException(status_code=400, detail="Không thể tạo chapter")
    
    return chapter


@router.put("/{chapter_id}", response_model=ChapterResponse)
def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Cập nhật chapter (chỉ admin)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền cập nhật chapter")
    
    service = ChapterService()
    chapter = service.update_chapter(chapter_id, chapter_data)
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    return chapter


@router.delete("/{chapter_id}")
def delete_chapter(
    chapter_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Xóa chapter (chỉ admin)"""
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền xóa chapter")
    
    service = ChapterService()
    success = service.delete_chapter(chapter_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    return {"message": "Chapter đã được xóa thành công"} 