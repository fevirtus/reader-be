from typing import List, Optional
from app.schemas.chapter import ChapterCreate, ChapterUpdate
from app.services.markdown_service import MarkdownService
from app.services.supabase_service import SupabaseService


class ChapterService:
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.markdown_service = MarkdownService()
    
    def create_chapter(self, chapter_data: ChapterCreate) -> Optional[dict]:
        """Tạo chapter mới"""
        data = chapter_data.dict()
        
        # Đếm số từ từ file markdown
        content = self.markdown_service.read_markdown_file(chapter_data.content_file)
        if content:
            data['word_count'] = self.markdown_service.get_word_count(content)
        
        return self.supabase_service.create_chapter(data)
    
    def get_chapter(self, chapter_id: int) -> Optional[dict]:
        """Lấy chapter theo ID"""
        return self.supabase_service.get_chapter(chapter_id)
    
    def get_chapters_by_novel(self, novel_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Lấy danh sách chapters của một novel"""
        return self.supabase_service.get_chapters_by_novel(novel_id, skip, limit)
    
    def get_chapter_by_number(self, novel_id: int, chapter_number: float) -> Optional[dict]:
        """Lấy chapter theo số chương"""
        return self.supabase_service.get_chapter_by_number(novel_id, chapter_number)
    
    def update_chapter(self, chapter_id: int, chapter_data: ChapterUpdate) -> Optional[dict]:
        """Cập nhật chapter"""
        update_data = chapter_data.dict(exclude_unset=True)
        
        # Cập nhật word count nếu content thay đổi
        if 'content_file' in update_data:
            content = self.markdown_service.read_markdown_file(update_data['content_file'])
            if content:
                update_data['word_count'] = self.markdown_service.get_word_count(content)
        
        return self.supabase_service.update_chapter(chapter_id, update_data)
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """Xóa chapter"""
        # Xóa file markdown
        chapter = self.get_chapter(chapter_id)
        if chapter and chapter.get('content_file'):
            self.markdown_service.delete_markdown_file(chapter['content_file'])
        
        return self.supabase_service.delete_chapter(chapter_id)
    
    def increment_views(self, chapter_id: int) -> bool:
        """Tăng số lượt xem chapter"""
        return self.supabase_service.increment_chapter_views(chapter_id)
    
    def get_chapter_content(self, chapter_id: int, format: str = "markdown") -> Optional[str]:
        """Lấy nội dung chapter"""
        chapter = self.get_chapter(chapter_id)
        if not chapter or not chapter.get('content_file'):
            return None
        
        content = self.markdown_service.read_markdown_file(chapter['content_file'])
        if not content:
            return None
        
        if format == "html":
            return self.markdown_service.convert_to_html(content)
        return content
    
    def get_next_chapter(self, novel_id: int, current_chapter_number: float) -> Optional[dict]:
        """Lấy chapter tiếp theo"""
        chapters = self.get_chapters_by_novel(novel_id)
        for chapter in chapters:
            if chapter['chapter_number'] > current_chapter_number:
                return chapter
        return None
    
    def get_previous_chapter(self, novel_id: int, current_chapter_number: float) -> Optional[dict]:
        """Lấy chapter trước đó"""
        chapters = self.get_chapters_by_novel(novel_id)
        for chapter in reversed(chapters):
            if chapter['chapter_number'] < current_chapter_number:
                return chapter
        return None
    
    def get_chapter_navigation(self, novel_id: int, chapter_number: float) -> dict:
        """Lấy thông tin navigation cho chapter"""
        return self.supabase_service.get_chapter_navigation(novel_id, chapter_number) 