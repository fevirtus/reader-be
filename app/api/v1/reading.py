from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.schemas.reading import (
    ReadingProgressCreate, ReadingProgressUpdate, ReadingProgressResponse,
    ReadingProgressWithNovel, BookshelfAdd, BookshelfResponse
)
from app.services.reading_service import ReadingService
from app.core.auth import get_current_user, get_optional_user

router = APIRouter()


@router.post("/progress", response_model=ReadingProgressResponse)
def update_reading_progress(
    progress_data: ReadingProgressCreate,
    current_user: dict = Depends(get_current_user)
):
    """Cập nhật tiến độ đọc"""
    reading_service = ReadingService()
    
    result = reading_service.update_reading_progress(current_user['id'], progress_data)
    
    if result:
        return ReadingProgressResponse(**result)
    else:
        raise HTTPException(status_code=400, detail="Failed to update reading progress")


@router.get("/progress", response_model=List[ReadingProgressResponse])
def get_reading_progress(
    novel_id: Optional[int] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Lấy tiến độ đọc của user"""
    reading_service = ReadingService()
    
    progress_list = reading_service.get_reading_progress(current_user['id'], novel_id)
    return [ReadingProgressResponse(**progress) for progress in progress_list]


@router.get("/progress/with-novels", response_model=List[ReadingProgressWithNovel])
def get_reading_progress_with_novels(current_user: dict = Depends(get_current_user)):
    """Lấy tiến độ đọc với thông tin novel"""
    reading_service = ReadingService()
    
    progress_list = reading_service.get_reading_progress_with_novels(current_user['id'])
    return [ReadingProgressWithNovel(**progress) for progress in progress_list]


@router.post("/bookshelf", response_model=BookshelfResponse)
def add_to_bookshelf(
    bookshelf_data: BookshelfAdd,
    current_user: dict = Depends(get_current_user)
):
    """Thêm novel vào tủ sách"""
    reading_service = ReadingService()
    
    success = reading_service.add_to_bookshelf(current_user['id'], bookshelf_data.novel_id)
    
    if success:
        # Lấy thông tin bookshelf đã thêm
        bookshelf_list = reading_service.get_bookshelf(current_user['id'])
        for item in bookshelf_list:
            if item['novel_id'] == bookshelf_data.novel_id:
                return BookshelfResponse(**item)
        
        raise HTTPException(status_code=400, detail="Failed to get bookshelf info")
    else:
        raise HTTPException(status_code=400, detail="Failed to add to bookshelf")


@router.delete("/bookshelf/{novel_id}")
def remove_from_bookshelf(
    novel_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Xóa novel khỏi tủ sách"""
    reading_service = ReadingService()
    
    success = reading_service.remove_from_bookshelf(current_user['id'], novel_id)
    
    if success:
        return {"message": "Removed from bookshelf successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to remove from bookshelf")


@router.get("/bookshelf", response_model=List[BookshelfResponse])
def get_bookshelf(current_user: dict = Depends(get_current_user)):
    """Lấy tủ sách của user"""
    reading_service = ReadingService()
    
    bookshelf_list = reading_service.get_bookshelf(current_user['id'])
    return [BookshelfResponse(**item) for item in bookshelf_list]


@router.get("/bookshelf/{novel_id}/check")
def check_bookshelf(
    novel_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Kiểm tra novel có trong tủ sách không"""
    reading_service = ReadingService()
    
    is_in_bookshelf = reading_service.is_in_bookshelf(current_user['id'], novel_id)
    return {"in_bookshelf": is_in_bookshelf}


@router.get("/stats")
def get_reading_stats(current_user: dict = Depends(get_current_user)):
    """Lấy thống kê đọc của user"""
    reading_service = ReadingService()
    
    stats = reading_service.get_reading_stats(current_user['id'])
    return stats


# Endpoints cho guest users (không cần đăng nhập)
@router.get("/novels/{novel_id}/progress")
def get_novel_progress_for_guest(
    novel_id: int,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Lấy tiến độ đọc của novel (cho guest users)"""
    if not current_user:
        return {"chapter_number": 0, "has_progress": False}
    
    reading_service = ReadingService()
    progress_list = reading_service.get_reading_progress(current_user['id'], novel_id)
    
    if progress_list:
        latest_progress = progress_list[0]  # Lấy progress mới nhất
        return {
            "chapter_number": latest_progress['chapter_number'],
            "chapter_id": latest_progress['chapter_id'],
            "has_progress": True
        }
    else:
        return {"chapter_number": 0, "has_progress": False}


@router.get("/novels/{novel_id}/bookshelf-check")
def check_bookshelf_for_guest(
    novel_id: int,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """Kiểm tra novel có trong tủ sách không (cho guest users)"""
    if not current_user:
        return {"in_bookshelf": False}
    
    reading_service = ReadingService()
    is_in_bookshelf = reading_service.is_in_bookshelf(current_user['id'], novel_id)
    return {"in_bookshelf": is_in_bookshelf} 