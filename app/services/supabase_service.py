from supabase import create_client, Client
from typing import Dict, List, Optional, Any
from app.core.config import settings


class SupabaseService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
    
    def get_novels(self, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Dict]:
        """Lấy danh sách novels từ Supabase"""
        query = self.supabase.table('novels').select('*')
        
        if search:
            query = query.or_(f"title.ilike.%{search}%,author.ilike.%{search}%")
        
        query = query.range(skip, skip + limit - 1).order('created_at', desc=True)
        response = query.execute()
        
        return response.data
    
    def get_novel(self, novel_id: int) -> Optional[Dict]:
        """Lấy novel theo ID"""
        response = self.supabase.table('novels').select('*').eq('id', novel_id).execute()
        return response.data[0] if response.data else None
    
    def create_novel(self, novel_data: Dict) -> Dict:
        """Tạo novel mới"""
        response = self.supabase.table('novels').insert(novel_data).execute()
        return response.data[0]
    
    def update_novel(self, novel_id: int, novel_data: Dict) -> Optional[Dict]:
        """Cập nhật novel"""
        response = self.supabase.table('novels').update(novel_data).eq('id', novel_id).execute()
        return response.data[0] if response.data else None
    
    def delete_novel(self, novel_id: int) -> bool:
        """Xóa novel"""
        response = self.supabase.table('novels').delete().eq('id', novel_id).execute()
        return len(response.data) > 0
    
    def increment_novel_views(self, novel_id: int) -> bool:
        """Tăng lượt xem novel"""
        response = self.supabase.rpc('increment_novel_views', {'novel_id': novel_id}).execute()
        return True
    
    def get_chapters_by_novel(self, novel_id: int, skip: int = 0, limit: int = 100) -> List[Dict]:
        """Lấy danh sách chapters của novel"""
        response = self.supabase.table('chapters').select('*').eq('novel_id', novel_id).range(skip, skip + limit - 1).order('chapter_number').execute()
        return response.data
    
    def get_chapter(self, chapter_id: int) -> Optional[Dict]:
        """Lấy chapter theo ID"""
        response = self.supabase.table('chapters').select('*').eq('id', chapter_id).execute()
        return response.data[0] if response.data else None
    
    def get_chapter_by_number(self, novel_id: int, chapter_number: float) -> Optional[Dict]:
        """Lấy chapter theo số chương"""
        response = self.supabase.table('chapters').select('*').eq('novel_id', novel_id).eq('chapter_number', chapter_number).execute()
        return response.data[0] if response.data else None
    
    def create_chapter(self, chapter_data: Dict) -> Dict:
        """Tạo chapter mới"""
        response = self.supabase.table('chapters').insert(chapter_data).execute()
        return response.data[0]
    
    def update_chapter(self, chapter_id: int, chapter_data: Dict) -> Optional[Dict]:
        """Cập nhật chapter"""
        response = self.supabase.table('chapters').update(chapter_data).eq('id', chapter_id).execute()
        return response.data[0] if response.data else None
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """Xóa chapter"""
        response = self.supabase.table('chapters').delete().eq('id', chapter_id).execute()
        return len(response.data) > 0
    
    def increment_chapter_views(self, chapter_id: int) -> bool:
        """Tăng lượt xem chapter"""
        response = self.supabase.rpc('increment_chapter_views', {'chapter_id': chapter_id}).execute()
        return True
    
    def get_chapter_navigation(self, novel_id: int, chapter_number: float) -> Dict:
        """Lấy thông tin navigation cho chapter"""
        # Lấy chapter hiện tại
        current = self.get_chapter_by_number(novel_id, chapter_number)
        if not current:
            return {}
        
        # Lấy chapter trước
        prev_response = self.supabase.table('chapters').select('id,chapter_number,title').eq('novel_id', novel_id).lt('chapter_number', chapter_number).order('chapter_number', desc=True).limit(1).execute()
        previous = prev_response.data[0] if prev_response.data else None
        
        # Lấy chapter sau
        next_response = self.supabase.table('chapters').select('id,chapter_number,title').eq('novel_id', novel_id).gt('chapter_number', chapter_number).order('chapter_number').limit(1).execute()
        next_chapter = next_response.data[0] if next_response.data else None
        
        return {
            "current": {
                "id": current['id'],
                "chapter_number": current['chapter_number'],
                "title": current['title']
            },
            "previous": previous,
            "next": next_chapter
        } 