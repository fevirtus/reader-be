from typing import List, Optional, Dict, Any
from app.services.supabase_service import SupabaseService
from app.services.cache_service import cache_service


class NovelService:
    def __init__(self):
        self.supabase_service = SupabaseService()
    
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
            response = self.supabase_service.supabase_admin.table('novels').insert(novel_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating novel: {e}")
            return None
    
    def update_novel(self, novel_id: int, novel_data: dict) -> Optional[dict]:
        """Cập nhật novel (admin only)"""
        try:
            response = self.supabase_service.supabase_admin.table('novels').update(novel_data).eq('id', novel_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating novel: {e}")
            return None
    
    def delete_novel(self, novel_id: int) -> bool:
        """Xóa novel (admin only)"""
        try:
            response = self.supabase_service.supabase_admin.table('novels').delete().eq('id', novel_id).execute()
            success = len(response.data) > 0
            
            if success:
                # Invalidate cache
                self._invalidate_novel_cache(novel_id)
            
            return success
        except Exception as e:
            print(f"Error deleting novel: {e}")
            return False
    
    def _invalidate_novel_cache(self, novel_id: int) -> None:
        """Invalidate cache cho novel"""
        # Xóa cache của novel cụ thể
        cache_service.delete(f"novel:{novel_id}")
        
        # Xóa tất cả cache novels list (vì có thể thay đổi)
        self._clear_novels_list_cache()
    
    def _clear_novels_list_cache(self) -> None:
        """Xóa tất cả cache của novels list"""
        keys_to_delete = []
        for key in cache_service.cache.keys():
            if key.startswith("novels:"):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            cache_service.delete(key) 