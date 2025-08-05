from typing import List, Optional, Dict, Any
from app.services.markdown_service import MarkdownService
from app.services.supabase_service import SupabaseService
from app.services.cache_service import cache_service


class ChapterService:
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.markdown_service = MarkdownService()
    
    def get_chapter(self, chapter_id: int) -> Optional[dict]:
        """Lấy chapter theo ID với cache"""
        # Kiểm tra cache trước
        cache_key = f"chapter:{chapter_id}"
        cached_chapter = cache_service.get(cache_key)
        
        if cached_chapter:
            return cached_chapter
        
        # Nếu không có trong cache, lấy từ database
        chapter = self.supabase_service.get_chapter(chapter_id)
        
        if chapter:
            # Cache trong 1 giờ
            cache_service.set(cache_key, chapter, ttl=3600)
        
        return chapter
    
    def get_chapters_by_novel(self, novel_id: int, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Lấy danh sách chapters của một novel với pagination"""
        # Tạo cache key
        cache_key = f"chapters:novel:{novel_id}:page:{page}:limit:{limit}"
        cached_result = cache_service.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Nếu không có trong cache, lấy từ database
        result = self.supabase_service.get_chapters_by_novel_with_pagination(novel_id, page, limit)
        
        # Cache trong 30 phút
        cache_service.set(cache_key, result, ttl=1800)
        
        return result
    
    def increment_views(self, chapter_id: int) -> bool:
        """Tăng số lượt xem chapter"""
        return self.supabase_service.increment_chapter_views(chapter_id)
    
    def get_chapter_content(self, chapter_id: int, format: str = "markdown") -> Optional[str]:
        """Lấy nội dung chapter với cache"""
        # Tạo cache key cho content
        cache_key = f"chapter_content:{chapter_id}:{format}"
        cached_content = cache_service.get(cache_key)
        
        if cached_content:
            return cached_content
        
        # Nếu không có trong cache, lấy từ file
        chapter = self.get_chapter(chapter_id)
        if not chapter or not chapter.get('content_file'):
            return None
        
        # Lấy novel title để tìm đúng directory
        novel = self.supabase_service.get_novel(chapter['novel_id'])
        novel_title = novel.get('title') if novel else None
        
        content = self.markdown_service.read_markdown_file(chapter['content_file'], novel_title)
        if not content:
            return None
        
        if format == "html":
            content = self.markdown_service.convert_to_html(content)
        
        # Cache content trong 2 giờ
        cache_service.set(cache_key, content, ttl=7200)
        
        return content
    
    def create_chapter(self, chapter_data: dict) -> Optional[dict]:
        """Tạo chapter mới (admin only)"""
        try:
            response = self.supabase_service.supabase_admin.table('chapters').insert(chapter_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating chapter: {e}")
            return None
    
    def update_chapter(self, chapter_id: int, chapter_data: dict) -> Optional[dict]:
        """Cập nhật chapter (admin only)"""
        try:
            response = self.supabase_service.supabase_admin.table('chapters').update(chapter_data).eq('id', chapter_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating chapter: {e}")
            return None
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """Xóa chapter (admin only)"""
        try:
            response = self.supabase_service.supabase_admin.table('chapters').delete().eq('id', chapter_id).execute()
            success = len(response.data) > 0
            
            if success:
                # Invalidate cache
                self._invalidate_chapter_cache(chapter_id)
            
            return success
        except Exception as e:
            print(f"Error deleting chapter: {e}")
            return False
    
    def _invalidate_chapter_cache(self, chapter_id: int) -> None:
        """Invalidate cache cho chapter"""
        # Xóa cache của chapter cụ thể
        cache_service.delete(f"chapter:{chapter_id}")
        
        # Xóa cache content
        cache_service.delete(f"chapter_content:{chapter_id}:markdown")
        cache_service.delete(f"chapter_content:{chapter_id}:html")
        
        # Xóa cache chapters list (vì có thể thay đổi)
        self._clear_chapters_list_cache()
    
    def _clear_chapters_list_cache(self) -> None:
        """Xóa tất cả cache của chapters list"""
        keys_to_delete = []
        for key in cache_service.cache.keys():
            if key.startswith("chapters:"):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            cache_service.delete(key) 