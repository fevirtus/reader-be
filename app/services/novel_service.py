from typing import List, Optional, Dict, Any
from app.services.supabase_service import SupabaseService
from app.services.cache_service import cache_service
from supabase import create_client
from app.core.config import settings
import os
import shutil


class NovelService:
    def __init__(self):
        self.supabase_service = SupabaseService()
        # Tạo client với service key để bypass RLS khi cần
        self.supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    
    def get_novel(self, novel_id: int) -> Optional[dict]:
        """Lấy novel theo ID với cache"""
        # Kiểm tra cache trước
        cache_key = f"novel:{novel_id}"
        cached_novel = cache_service.get(cache_key)
        
        if cached_novel:
            return cached_novel
        
        # Nếu không có trong cache, lấy từ database
        novel = self.supabase_service.get_novel(novel_id)
        
        if novel:
            # Cache trong 30 phút
            cache_service.set(cache_key, novel, ttl=1800)
        
        return novel
    
    def get_novels(self, page: int = 1, limit: int = 20, status: str = None, author: str = None) -> Dict[str, Any]:
        """
        Lấy danh sách novels với pagination và filtering
        
        Args:
            page: Trang hiện tại (bắt đầu từ 1)
            limit: Số bản ghi trả về
            status: Lọc theo trạng thái (ongoing, completed)
            author: Lọc theo tác giả
        """
        # Tạo cache key dựa trên parameters
        cache_key = f"novels:page:{page}:limit:{limit}:status:{status}:author:{author}"
        cached_result = cache_service.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Nếu không có trong cache, lấy từ database
        result = self.supabase_service.get_novels_with_pagination(page, limit, status=status, author=author)
        
        # Cache trong 15 phút cho danh sách
        cache_service.set(cache_key, result, ttl=900)
        
        return result
    
    def search_novels(self, query: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Tìm kiếm novels theo title hoặc author với pagination"""
        # Tạo cache key cho search
        cache_key = f"novels:search:{query}:page:{page}:limit:{limit}"
        cached_result = cache_service.get(cache_key)
        
        if cached_result:
            return cached_result
        
        # Nếu không có trong cache, lấy từ database
        result = self.supabase_service.get_novels_with_pagination(page, limit, search=query)
        
        # Cache trong 10 phút cho search results
        cache_service.set(cache_key, result, ttl=600)
        
        return result
    
    def increment_views(self, novel_id: int) -> bool:
        """Tăng số lượt xem"""
        return self.supabase_service.increment_novel_views(novel_id)
    
    def update_total_chapters(self, novel_id: int, total: int) -> bool:
        """Cập nhật tổng số chương"""
        return self.supabase_service.update_novel(novel_id, {"total_chapters": total}) is not None
    
    def create_novel(self, novel_data: dict) -> Optional[dict]:
        """Tạo novel mới (admin only)"""
        try:
            # Sử dụng service key để bypass RLS cho admin operations
            response = self.supabase_admin.table('novels').insert(novel_data).execute()
            novel = response.data[0] if response.data else None
            
            if novel:
                # Clear cache khi tạo novel mới
                self._clear_novels_list_cache()
                print("✅ Cleared novels cache after creating novel")
            
            return novel
        except Exception as e:
            print(f"Error creating novel: {e}")
            return None
    
    def update_novel(self, novel_id: int, novel_data: dict) -> Optional[dict]:
        """Cập nhật novel (admin only)"""
        try:
            # Lấy thông tin novel hiện tại
            current_novel = self.get_novel(novel_id)
            if not current_novel:
                print(f"Novel {novel_id} không tồn tại")
                return None
            
            # Kiểm tra xem có đổi tên không
            old_title = current_novel.get('title')
            new_title = novel_data.get('title')
            
            # Cập nhật novel trong database
            response = self.supabase_admin.table('novels').update(novel_data).eq('id', novel_id).execute()
            updated_novel = response.data[0] if response.data else None
            
            if updated_novel and old_title and new_title and old_title != new_title:
                # Đổi tên thư mục storage nếu title thay đổi
                self._rename_novel_storage(old_title, new_title)
            
            if updated_novel:
                # Clear cache khi update novel
                self._clear_novels_list_cache()
                print("✅ Cleared novels cache after updating novel")
            
            return updated_novel
        except Exception as e:
            print(f"Error updating novel: {e}")
            return None
    
    def delete_novel(self, novel_id: int) -> bool:
        """Xóa novel (admin only)"""
        try:
            # Lấy thông tin novel trước khi xóa
            novel = self.get_novel(novel_id)
            if not novel:
                print(f"Novel {novel_id} không tồn tại")
                return False
            
            # Xóa novel từ database
            response = self.supabase_admin.table('novels').delete().eq('id', novel_id).execute()
            success = len(response.data) > 0
            
            if success:
                # Xóa thư mục storage của novel
                self._delete_novel_storage(novel['title'])
                
                # Xóa cache
                self._invalidate_novel_cache(novel_id)
                self._clear_novels_list_cache()
            
            return success
        except Exception as e:
            print(f"Error deleting novel: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê novels"""
        try:
            # Tổng số novels
            total_response = self.supabase_service.supabase.table('novels').select('id').execute()
            total = len(total_response.data)
            
            # Tổng lượt xem
            views_response = self.supabase_service.supabase.table('novels').select('views').execute()
            total_views = sum(novel.get('views', 0) for novel in views_response.data)
            
            # Số novels theo trạng thái
            ongoing_response = self.supabase_service.supabase.table('novels').select('id').eq('status', 'ongoing').execute()
            ongoing_count = len(ongoing_response.data)
            
            completed_response = self.supabase_service.supabase.table('novels').select('id').eq('status', 'completed').execute()
            completed_count = len(completed_response.data)
            
            return {
                "total": total,
                "total_views": total_views,
                "ongoing_count": ongoing_count,
                "completed_count": completed_count
            }
        except Exception as e:
            print(f"Error getting novel stats: {e}")
            return {"total": 0, "total_views": 0, "ongoing_count": 0, "completed_count": 0}
    
    def get_recent_activities(self, limit: int = 5) -> List[Dict]:
        """Lấy hoạt động gần đây của novels"""
        try:
            # Lấy novels mới tạo gần đây
            response = self.supabase_service.supabase.table('novels').select('*').order('created_at', desc=True).limit(limit).execute()
            
            activities = []
            for novel in response.data:
                activities.append({
                    "id": f"novel_{novel['id']}",
                    "type": "novel_created",
                    "description": f"Truyện '{novel.get('title', 'Unknown')}' đã được tạo",
                    "created_at": novel.get('created_at'),
                    "novel_id": novel['id']
                })
            
            return activities
        except Exception as e:
            print(f"Error getting novel activities: {e}")
            return []
    
    def _invalidate_novel_cache(self, novel_id: int) -> None:
        """Xóa cache của novel"""
        cache_key = f"novel:{novel_id}"
        cache_service.delete(cache_key)
    
    def _clear_novels_list_cache(self) -> None:
        """Xóa cache của danh sách novels"""
        try:
            # Xóa tất cả cache keys bắt đầu với "novels:"
            # Đây là danh sách các pattern cache cần xóa
            cache_patterns = [
                "novels:page:",
                "novels:search:",
                "novels:limit:",
                "novels:status:",
                "novels:author:"
            ]
            
            # Xóa cache cho các pattern này
            for pattern in cache_patterns:
                # Lấy tất cả keys bắt đầu với pattern
                keys_to_delete = []
                
                # Thử xóa một số key phổ biến
                for page in range(1, 11):  # Xóa cache cho 10 trang đầu
                    for limit in [10, 20, 50, 100]:
                        for status in [None, 'ongoing', 'completed']:
                            for author in [None, '']:
                                cache_key = f"novels:page:{page}:limit:{limit}:status:{status}:author:{author}"
                                if cache_service.get(cache_key):
                                    cache_service.delete(cache_key)
                                    print(f"Cleared cache: {cache_key}")
                
                # Xóa search cache
                for page in range(1, 6):
                    for limit in [10, 20, 50]:
                        cache_key = f"novels:search:*:page:{page}:limit:{limit}"
                        if cache_service.get(cache_key):
                            cache_service.delete(cache_key)
                            print(f"Cleared search cache: {cache_key}")
            
            print("✅ Cleared all novels list cache")
        except Exception as e:
            print(f"Error clearing novels cache: {e}")
    
    def _delete_novel_storage(self, novel_title: str) -> None:
        """Xóa thư mục storage của novel"""
        try:
            # Tạo đường dẫn đến thư mục novel
            novel_dir = os.path.join(settings.storage_path, novel_title)
            
            if os.path.exists(novel_dir):
                # Xóa toàn bộ thư mục và nội dung
                shutil.rmtree(novel_dir)
                print(f"Đã xóa thư mục storage: {novel_dir}")
            else:
                print(f"Thư mục storage không tồn tại: {novel_dir}")
        except Exception as e:
            print(f"Error deleting novel storage: {e}")
    
    def _rename_novel_storage(self, old_title: str, new_title: str) -> None:
        """Đổi tên thư mục storage của novel"""
        try:
            old_dir = os.path.join(settings.storage_path, old_title)
            new_dir = os.path.join(settings.storage_path, new_title)
            
            if os.path.exists(old_dir):
                # Đổi tên thư mục
                os.rename(old_dir, new_dir)
                print(f"Đã đổi tên thư mục storage: {old_dir} -> {new_dir}")
            else:
                print(f"Thư mục storage không tồn tại: {old_dir}")
        except Exception as e:
            print(f"Error renaming novel storage: {e}")
    
    def _create_novel_storage(self, novel_title: str) -> None:
        """Tạo thư mục storage cho novel"""
        try:
            novel_dir = os.path.join(settings.storage_path, novel_title)
            
            if not os.path.exists(novel_dir):
                os.makedirs(novel_dir)
                print(f"Đã tạo thư mục storage: {novel_dir}")
            else:
                print(f"Thư mục storage đã tồn tại: {novel_dir}")
        except Exception as e:
            print(f"Error creating novel storage: {e}") 