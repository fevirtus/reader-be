from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from typing import List
from app.schemas.novel import NovelResponse, NovelCreate, NovelUpdate
from app.services.novel_service import NovelService
from app.services.chapter_service import ChapterService
from app.services.epub_service import EpubService
from app.services.user_service import UserService
from app.core.auth import get_current_user
import tempfile
import os

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


@router.post("/upload-epub")
async def upload_epub_and_create_novel(
    epub_file: UploadFile = File(..., description="EPUB file để upload"),
    novel_title: str = Query(None, description="Tên novel (nếu không có sẽ lấy từ EPUB)"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload EPUB file và tạo novel mới từ EPUB (chỉ admin)
    
    - **epub_file**: EPUB file để upload
    - **novel_title**: Tên novel (tùy chọn, nếu không có sẽ lấy từ EPUB)
    """
    # Kiểm tra quyền admin
    user_service = UserService()
    if not user_service.is_admin(current_user['id']):
        raise HTTPException(status_code=403, detail="Chỉ admin mới có quyền upload EPUB")
    
    # Kiểm tra file type
    if not epub_file.filename.lower().endswith('.epub'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file EPUB")
    
    # Kiểm tra kích thước file (giới hạn 100MB)
    if epub_file.size and epub_file.size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File quá lớn (tối đa 100MB)")
    
    try:
        # Lưu file tạm thời
        with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as temp_file:
            content = await epub_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Xử lý EPUB file
        epub_service = EpubService()
        
        # Kiểm tra tính hợp lệ của EPUB
        if not epub_service.validate_epub_file(temp_file_path):
            os.unlink(temp_file_path)
            raise HTTPException(status_code=400, detail="EPUB file không hợp lệ")
        
        # Xử lý EPUB và trích xuất thông tin
        epub_data = epub_service.process_epub_upload(temp_file_path, novel_title)
        
        if not epub_data:
            os.unlink(temp_file_path)
            raise HTTPException(status_code=400, detail="Không thể xử lý EPUB file")
        
        # Tạo novel trong database
        novel_service = NovelService()
        chapter_service = ChapterService()
        
        # Tạo novel
        novel_data = NovelCreate(
            title=epub_data['title'],
            description=f"Truyện được tạo từ EPUB: {epub_data['title']}",
            author=epub_data['creator'],
            status="ongoing",
            total_chapters=epub_data['total_chapters'],
            language=epub_data['language']
        )
        
        novel = novel_service.create_novel(novel_data.dict())
        
        if not novel:
            os.unlink(temp_file_path)
            raise HTTPException(status_code=400, detail="Không thể tạo novel trong database")
        
        # Tạo chapters
        created_chapters = []
        for chapter_info in epub_data['chapters']:
            chapter_data = {
                'novel_id': novel['id'],
                'chapter_number': chapter_info['number'],
                'title': chapter_info['title'],
                'content_file': chapter_info['filename'],
                'word_count': chapter_info['word_count']
            }
            
            chapter = chapter_service.create_chapter(chapter_data)
            if chapter:
                created_chapters.append(chapter)
        
        # Xóa file tạm
        os.unlink(temp_file_path)
        
        return {
            "message": "Upload EPUB thành công",
            "novel": novel,
            "total_chapters_created": len(created_chapters),
            "epub_info": {
                "title": epub_data['title'],
                "creator": epub_data['creator'],
                "language": epub_data['language'],
                "total_chapters": epub_data['total_chapters']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Đảm bảo xóa file tạm nếu có lỗi
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý EPUB: {str(e)}") 