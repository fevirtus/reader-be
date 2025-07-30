from typing import List, Optional
from app.schemas.novel import NovelCreate, NovelUpdate
from app.services.supabase_service import SupabaseService


class NovelService:
    def __init__(self):
        self.supabase_service = SupabaseService()
    
    def create_novel(self, novel_data: NovelCreate) -> dict:
        """Tạo novel mới"""
        data = novel_data.dict()
        return self.supabase_service.create_novel(data)
    
    def get_novel(self, novel_id: int) -> Optional[dict]:
        """Lấy novel theo ID"""
        return self.supabase_service.get_novel(novel_id)
    
    def get_novels(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Lấy danh sách novels với pagination"""
        return self.supabase_service.get_novels(skip, limit)
    
    def search_novels(self, query: str, skip: int = 0, limit: int = 100) -> List[dict]:
        """Tìm kiếm novels theo title hoặc author"""
        return self.supabase_service.get_novels(skip, limit, query)
    
    def update_novel(self, novel_id: int, novel_data: NovelUpdate) -> Optional[dict]:
        """Cập nhật novel"""
        update_data = novel_data.dict(exclude_unset=True)
        return self.supabase_service.update_novel(novel_id, update_data)
    
    def delete_novel(self, novel_id: int) -> bool:
        """Xóa novel"""
        return self.supabase_service.delete_novel(novel_id)
    
    def increment_views(self, novel_id: int) -> bool:
        """Tăng số lượt xem"""
        return self.supabase_service.increment_novel_views(novel_id)
    
    def update_total_chapters(self, novel_id: int, total: int) -> bool:
        """Cập nhật tổng số chương"""
        return self.supabase_service.update_novel(novel_id, {"total_chapters": total}) is not None 