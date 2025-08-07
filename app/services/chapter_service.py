from typing import List, Optional, Dict, Any
from app.services.markdown_service import ContentService
from app.services.supabase_service import SupabaseService
from app.services.cache_service import cache_service
from supabase import create_client
from app.core.config import settings
import os


class ChapterService:
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.content_service = ContentService()
        # Tạo client với service key để bypass RLS khi cần
        self.supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    
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
        
        content = self.content_service.read_content_file(chapter['content_file'], novel_title)
        if not content:
            return None
        
        # Nếu format là markdown và content là HTML, chuyển đổi
        if format == "markdown" and content.startswith('<'):
            # Content là HTML, giữ nguyên cho markdown format
            pass
        elif format == "html" and not content.startswith('<'):
            # Content là markdown, chuyển đổi thành HTML
            content = self.content_service.convert_to_html(content)
        
        # Cache content trong 2 giờ
        cache_service.set(cache_key, content, ttl=7200)
        
        return content
    
    def create_chapter(self, chapter_data: dict) -> Optional[dict]:
        """Tạo chapter mới (admin only)"""
        try:
            # Sử dụng service key để bypass RLS cho admin operations
            response = self.supabase_admin.table('chapters').insert(chapter_data).execute()
            chapter = response.data[0] if response.data else None
            
            if chapter:
                # Clear cache khi tạo chapter mới
                self._clear_chapters_list_cache()
                print("✅ Cleared chapters cache after creating chapter")
            
            return chapter
        except Exception as e:
            print(f"Error creating chapter: {e}")
            return None
    
    def update_chapter(self, chapter_id: int, chapter_data: dict) -> Optional[dict]:
        """Cập nhật chapter (admin only)"""
        try:
            # Lấy thông tin chapter hiện tại
            current_chapter = self.get_chapter(chapter_id)
            if not current_chapter:
                print(f"Chapter {chapter_id} không tồn tại")
                return None
            
            # Kiểm tra xem có đổi tên file không
            old_content_file = current_chapter.get('content_file')
            new_content_file = chapter_data.get('content_file')
            
            # Cập nhật chapter trong database
            response = self.supabase_admin.table('chapters').update(chapter_data).eq('id', chapter_id).execute()
            updated_chapter = response.data[0] if response.data else None
            
            if updated_chapter and old_content_file and new_content_file and old_content_file != new_content_file:
                # Đổi tên file content nếu content_file thay đổi
                self._update_chapter_file(chapter_id, old_content_file, new_content_file)
            
            if updated_chapter:
                # Clear cache khi update chapter
                self._clear_chapters_list_cache()
                print("✅ Cleared chapters cache after updating chapter")
            
            return updated_chapter
        except Exception as e:
            print(f"Error updating chapter: {e}")
            return None
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """Xóa chapter (admin only)"""
        try:
            # Lấy thông tin chapter trước khi xóa
            chapter = self.get_chapter(chapter_id)
            if not chapter:
                print(f"Chapter {chapter_id} không tồn tại")
                return False
            
            # Xóa chapter từ database
            response = self.supabase_admin.table('chapters').delete().eq('id', chapter_id).execute()
            success = len(response.data) > 0
            
            if success:
                # Xóa file content của chapter
                self._delete_chapter_file(chapter)
                
                # Xóa cache
                self._invalidate_chapter_cache(chapter_id)
                self._clear_chapters_list_cache()
            
            return success
        except Exception as e:
            print(f"Error deleting chapter: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê chapters"""
        try:
            # Tổng số chapters
            total_response = self.supabase_service.supabase.table('chapters').select('id').execute()
            total = len(total_response.data)
            
            # Tổng lượt xem
            views_response = self.supabase_service.supabase.table('chapters').select('views').execute()
            total_views = sum(chapter.get('views', 0) for chapter in views_response.data)
            
            # Tổng số từ
            word_count_response = self.supabase_service.supabase.table('chapters').select('word_count').execute()
            total_words = sum(chapter.get('word_count', 0) for chapter in word_count_response.data)
            
            return {
                "total": total,
                "total_views": total_views,
                "total_words": total_words
            }
        except Exception as e:
            print(f"Error getting chapter stats: {e}")
            return {"total": 0, "total_views": 0, "total_words": 0}
    
    def get_recent_activities(self, limit: int = 5) -> List[Dict]:
        """Lấy hoạt động gần đây của chapters"""
        try:
            # Lấy chapters mới tạo gần đây
            response = self.supabase_service.supabase.table('chapters').select('*').order('created_at', desc=True).limit(limit).execute()
            
            activities = []
            for chapter in response.data:
                # Lấy thông tin novel
                novel = self.supabase_service.get_novel(chapter['novel_id'])
                novel_title = novel.get('title', 'Unknown') if novel else 'Unknown'
                
                activities.append({
                    "id": f"chapter_{chapter['id']}",
                    "type": "chapter_created",
                    "description": f"Chương {chapter.get('chapter_number', 0)} của truyện '{novel_title}' đã được tạo",
                    "created_at": chapter.get('created_at'),
                    "chapter_id": chapter['id'],
                    "novel_id": chapter['novel_id']
                })
            
            return activities
        except Exception as e:
            print(f"Error getting chapter activities: {e}")
            return []
    
    def _invalidate_chapter_cache(self, chapter_id: int) -> None:
        """Xóa cache của chapter"""
        cache_key = f"chapter:{chapter_id}"
        cache_service.delete(cache_key)
        
        # Xóa cache content
        content_cache_key = f"chapter_content:{chapter_id}:markdown"
        cache_service.delete(content_cache_key)
        content_cache_key = f"chapter_content:{chapter_id}:html"
        cache_service.delete(content_cache_key)
    
    def _clear_chapters_list_cache(self) -> None:
        """Xóa cache của danh sách chapters"""
        try:
            # Xóa tất cả cache keys bắt đầu với "chapters:"
            # Thử xóa một số key phổ biến
            for novel_id in range(1, 100):  # Xóa cache cho 100 novels đầu
                for page in range(1, 11):  # Xóa cache cho 10 trang đầu
                    for limit in [10, 20, 50, 100]:
                        cache_key = f"chapters:novel:{novel_id}:page:{page}:limit:{limit}"
                        if cache_service.get(cache_key):
                            cache_service.delete(cache_key)
                            print(f"Cleared chapters cache: {cache_key}")
            
            print("✅ Cleared all chapters list cache")
        except Exception as e:
            print(f"Error clearing chapters cache: {e}")
    
    def _delete_chapter_file(self, chapter: dict) -> None:
        """Xóa file content của chapter"""
        try:
            content_file = chapter.get('content_file')
            if not content_file:
                print("Chapter không có content_file")
                return
            
            # Lấy thông tin novel để tìm đúng thư mục
            novel = self.supabase_service.get_novel(chapter['novel_id'])
            if not novel:
                print(f"Không tìm thấy novel {chapter['novel_id']}")
                return
            
            novel_title = novel.get('title')
            if not novel_title:
                print("Novel không có title")
                return
            
            # Tạo đường dẫn đến file
            file_path = os.path.join(settings.storage_path, novel_title, content_file)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Đã xóa file content: {file_path}")
            else:
                print(f"File content không tồn tại: {file_path}")
        except Exception as e:
            print(f"Error deleting chapter file: {e}")
    
    def _update_chapter_file(self, chapter_id: int, old_content_file: str, new_content_file: str) -> None:
        """Cập nhật tên file content của chapter"""
        try:
            chapter = self.get_chapter(chapter_id)
            if not chapter:
                print(f"Chapter {chapter_id} không tồn tại")
                return
            
            # Lấy thông tin novel
            novel = self.supabase_service.get_novel(chapter['novel_id'])
            if not novel:
                print(f"Không tìm thấy novel {chapter['novel_id']}")
                return
            
            novel_title = novel.get('title')
            if not novel_title:
                print("Novel không có title")
                return
            
            # Tạo đường dẫn đến file cũ và mới
            old_file_path = os.path.join(settings.storage_path, novel_title, old_content_file)
            new_file_path = os.path.join(settings.storage_path, novel_title, new_content_file)
            
            if os.path.exists(old_file_path):
                # Đổi tên file
                os.rename(old_file_path, new_file_path)
                print(f"Đã đổi tên file content: {old_file_path} -> {new_file_path}")
            else:
                print(f"File content cũ không tồn tại: {old_file_path}")
        except Exception as e:
            print(f"Error updating chapter file: {e}")
    
    def _create_chapter_file(self, novel_title: str, content_file: str, content: str) -> None:
        """Tạo file content cho chapter"""
        try:
            # Tạo đường dẫn đến file
            file_path = os.path.join(settings.storage_path, novel_title, content_file)
            
            # Tạo thư mục nếu chưa có
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Ghi nội dung vào file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Đã tạo file content: {file_path}")
        except Exception as e:
            print(f"Error creating chapter file: {e}") 