from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse
from app.schemas.reading import ReadingProgressCreate
from app.services.chapter_service import ChapterService
from app.services.reading_service import ReadingService
from app.core.auth import get_optional_user

router = APIRouter()


@router.post("/", response_model=ChapterResponse)
def create_chapter(chapter_data: ChapterCreate):
    """Tạo chapter mới"""
    service = ChapterService()
    chapter = service.create_chapter(chapter_data)
    
    if not chapter:
        raise HTTPException(status_code=400, detail="Không thể tạo chapter")
    
    return chapter


@router.get("/", response_model=List[ChapterResponse])
def get_chapters(
    novel_id: int = Query(..., description="ID của novel"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Lấy danh sách chapters của một novel"""
    service = ChapterService()
    chapters = service.get_chapters_by_novel(novel_id, skip, limit)
    return chapters


@router.get("/{chapter_id}", response_model=ChapterResponse)
def get_chapter(chapter_id: int, current_user: Optional[dict] = Depends(get_optional_user)):
    """Lấy thông tin chapter theo ID"""
    service = ChapterService()
    chapter = service.get_chapter(chapter_id)
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
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
    
    return chapter


@router.get("/{chapter_id}/content")
def get_chapter_content(
    chapter_id: int,
    format: str = Query("markdown", regex="^(markdown|html)$"),
):
    """Lấy nội dung chapter"""
    service = ChapterService()
    content = service.get_chapter_content(chapter_id, format)
    
    if not content:
        raise HTTPException(status_code=404, detail="Nội dung chapter không tồn tại")
    
    return {"content": content, "format": format}


@router.get("/novel/{novel_id}/chapter/{chapter_number}")
def get_chapter_by_number(
    novel_id: int,
    chapter_number: float,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Lấy chapter theo số chương"""
    service = ChapterService()
    chapter = service.get_chapter_by_number(novel_id, chapter_number)
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    # Tăng số lượt xem
    service.increment_views(chapter['id'])
    
    # Tự động cập nhật reading progress nếu user đã đăng nhập
    if current_user:
        reading_service = ReadingService()
        progress_data = ReadingProgressCreate(
            novel_id=novel_id,
            chapter_id=chapter['id'],
            chapter_number=chapter_number
        )
        reading_service.update_reading_progress(current_user['id'], progress_data)
    
    return chapter


@router.get("/novel/{novel_id}/chapter/{chapter_number}/content")
def get_chapter_content_by_number(
    novel_id: int,
    chapter_number: float,
    format: str = Query("markdown", regex="^(markdown|html)$"),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Lấy nội dung chapter theo số chương"""
    service = ChapterService()
    chapter = service.get_chapter_by_number(novel_id, chapter_number)
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    content = service.get_chapter_content(chapter['id'], format)
    
    if not content:
        raise HTTPException(status_code=404, detail="Nội dung chapter không tồn tại")
    
    # Tăng số lượt xem
    service.increment_views(chapter['id'])
    
    # Tự động cập nhật reading progress nếu user đã đăng nhập
    if current_user:
        reading_service = ReadingService()
        progress_data = ReadingProgressCreate(
            novel_id=novel_id,
            chapter_id=chapter['id'],
            chapter_number=chapter_number
        )
        reading_service.update_reading_progress(current_user['id'], progress_data)
    
    return {"content": content, "format": format}


@router.get("/novel/{novel_id}/chapter/{chapter_number}/navigation")
def get_chapter_navigation(
    novel_id: int,
    chapter_number: float,
):
    """Lấy thông tin navigation (chapter trước/sau)"""
    service = ChapterService()
    navigation = service.get_chapter_navigation(novel_id, chapter_number)
    
    if not navigation:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    return navigation


@router.put("/{chapter_id}", response_model=ChapterResponse)
def update_chapter(chapter_id: int, chapter_data: ChapterUpdate):
    """Cập nhật chapter"""
    service = ChapterService()
    chapter = service.update_chapter(chapter_id, chapter_data)
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    return chapter


@router.delete("/{chapter_id}")
def delete_chapter(chapter_id: int):
    """Xóa chapter"""
    service = ChapterService()
    success = service.delete_chapter(chapter_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Chapter không tồn tại")
    
    return {"message": "Chapter đã được xóa thành công"} 