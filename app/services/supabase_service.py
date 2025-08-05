from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from app.core.config import settings


class SupabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
    
    def get_novels(self, skip: int = 0, limit: int = 100, search: Optional[str] = None, status: Optional[str] = None, author: Optional[str] = None) -> List[Dict]:
        """
        Lấy danh sách novels từ Supabase với filtering (legacy method)
        
        Args:
            skip: Số bản ghi bỏ qua
            limit: Số bản ghi trả về
            search: Từ khóa tìm kiếm trong title và author
            status: Lọc theo trạng thái (ongoing, completed)
            author: Lọc theo tác giả
        """
        query = self.supabase.table('novels').select('*')
        
        # Apply filters
        if search:
            query = query.or_(f"title.ilike.%{search}%,author.ilike.%{search}%")
        
        if status:
            query = query.eq('status', status)
        
        if author:
            query = query.eq('author', author)
        
        query = query.range(skip, skip + limit - 1).order('created_at', desc=True)
        response = query.execute()
        
        return response.data
    
    def get_novels_with_pagination(self, page: int = 1, limit: int = 20, search: Optional[str] = None, status: Optional[str] = None, author: Optional[str] = None) -> Dict[str, Any]:
        """
        Lấy danh sách novels với pagination metadata
        
        Args:
            page: Trang hiện tại (bắt đầu từ 1)
            limit: Số bản ghi trả về
            search: Từ khóa tìm kiếm trong title và author
            status: Lọc theo trạng thái (ongoing, completed)
            author: Lọc theo tác giả
        """
        # Tính toán skip
        skip = (page - 1) * limit
        
        # Query để lấy tổng số bản ghi
        count_query = self.supabase.table('novels').select('id', count='exact')
        
        # Apply filters cho count query
        if search:
            count_query = count_query.or_(f"title.ilike.%{search}%,author.ilike.%{search}%")
        if status:
            count_query = count_query.eq('status', status)
        if author:
            count_query = count_query.eq('author', author)
        
        count_response = count_query.execute()
        total = count_response.count if count_response.count is not None else 0
        
        # Query để lấy data
        data_query = self.supabase.table('novels').select('*')
        
        # Apply filters cho data query
        if search:
            data_query = data_query.or_(f"title.ilike.%{search}%,author.ilike.%{search}%")
        if status:
            data_query = data_query.eq('status', status)
        if author:
            data_query = data_query.eq('author', author)
        
        data_query = data_query.range(skip, skip + limit - 1).order('created_at', desc=True)
        data_response = data_query.execute()
        
        # Tính toán pagination metadata
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        next_page = page + 1 if has_next else None
        prev_page = page - 1 if has_prev else None
        
        return {
            "items": data_response.data,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": next_page,
            "prev_page": prev_page
        }
    
    def get_novel(self, novel_id: int) -> Optional[Dict]:
        """Lấy novel theo ID"""
        response = self.supabase.table('novels').select('*').eq('id', novel_id).execute()
        return response.data[0] if response.data else None
    

    
    def increment_novel_views(self, novel_id: int) -> bool:
        """Tăng lượt xem novel"""
        response = self.supabase.rpc('increment_novel_views', {'novel_id': novel_id}).execute()
        return True
    
    def get_chapters_by_novel(self, novel_id: int, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lấy danh sách chapters của novel (legacy method)"""
        response = self.supabase.table('chapters').select('*').eq('novel_id', novel_id).range(skip, skip + limit - 1).order('chapter_number').execute()
        return response.data
    
    def get_chapters_by_novel_with_pagination(self, novel_id: int, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """
        Lấy danh sách chapters của novel với pagination metadata
        
        Args:
            novel_id: ID của novel
            page: Trang hiện tại (bắt đầu từ 1)
            limit: Số bản ghi trả về
        """
        # Tính toán skip
        skip = (page - 1) * limit
        
        # Query để lấy tổng số chapters
        count_response = self.supabase.table('chapters').select('id', count='exact').eq('novel_id', novel_id).execute()
        total = count_response.count if count_response.count is not None else 0
        
        # Query để lấy data
        data_response = self.supabase.table('chapters').select('*').eq('novel_id', novel_id).range(skip, skip + limit - 1).order('chapter_number').execute()
        
        # Tính toán pagination metadata
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        next_page = page + 1 if has_next else None
        prev_page = page - 1 if has_prev else None
        
        return {
            "items": data_response.data,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev,
            "next_page": next_page,
            "prev_page": prev_page
        }
    
    def get_chapter(self, chapter_id: int) -> Optional[Dict]:
        """Lấy chapter theo ID"""
        response = self.supabase.table('chapters').select('*').eq('id', chapter_id).execute()
        return response.data[0] if response.data else None
    
    def increment_chapter_views(self, chapter_id: int) -> bool:
        """Tăng lượt xem chapter"""
        response = self.supabase.rpc('increment_chapter_views', {'chapter_id': chapter_id}).execute()
        return True