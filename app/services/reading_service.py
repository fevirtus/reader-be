from typing import List, Optional, Dict
from supabase import create_client, Client
from app.core.config import settings
from app.schemas.reading import ReadingProgressCreate, ReadingProgressUpdate


class ReadingService:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        # Tạo client với service role key cho admin operations
        self.supabase_admin: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )

    def update_reading_progress(self, user_id: str, progress_data: ReadingProgressCreate) -> Dict:
        """Cập nhật tiến độ đọc"""
        try:
            # Sử dụng RPC function để update reading progress
            result = self.supabase_admin.rpc('update_reading_progress', {
                'p_user_id': user_id,
                'p_novel_id': progress_data.novel_id,
                'p_chapter_id': progress_data.chapter_id,
                'p_chapter_number': progress_data.chapter_number
            }).execute()
            
            # Lấy reading progress đã cập nhật
            progress_response = self.supabase.table('reading_progress').select('*').eq('user_id', user_id).eq('novel_id', progress_data.novel_id).execute()
            
            if progress_response.data:
                return progress_response.data[0]
            else:
                raise Exception("Failed to update reading progress")
                
        except Exception as e:
            raise Exception(f"Update reading progress failed: {str(e)}")

    def get_reading_progress(self, user_id: str, novel_id: Optional[int] = None) -> List[Dict]:
        """Lấy tiến độ đọc của user"""
        try:
            query = self.supabase.table('reading_progress').select('*').eq('user_id', user_id)
            
            if novel_id:
                query = query.eq('novel_id', novel_id)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            print(f"Get reading progress error: {e}")
            return []

    def get_reading_progress_with_novels(self, user_id: str) -> List[Dict]:
        """Lấy tiến độ đọc với thông tin novel"""
        try:
            response = self.supabase.table('reading_progress').select(
                '*, novels(title, author, cover_image)'
            ).eq('user_id', user_id).execute()
            
            return response.data
            
        except Exception as e:
            print(f"Get reading progress with novels error: {e}")
            return []

    def add_to_bookshelf(self, user_id: str, novel_id: int) -> bool:
        """Thêm novel vào tủ sách"""
        try:
            bookshelf_data = {
                "user_id": user_id,
                "novel_id": novel_id
            }
            
            self.supabase_admin.table('bookshelf').insert(bookshelf_data).execute()
            return True
            
        except Exception as e:
            print(f"Add to bookshelf error: {e}")
            return False

    def remove_from_bookshelf(self, user_id: str, novel_id: int) -> bool:
        """Xóa novel khỏi tủ sách"""
        try:
            self.supabase_admin.table('bookshelf').delete().eq('user_id', user_id).eq('novel_id', novel_id).execute()
            return True
            
        except Exception as e:
            print(f"Remove from bookshelf error: {e}")
            return False

    def get_bookshelf(self, user_id: str) -> List[Dict]:
        """Lấy tủ sách của user"""
        try:
            response = self.supabase.table('bookshelf').select(
                '*, novels(title, author, description, cover_image, status, total_chapters, views, rating)'
            ).eq('user_id', user_id).execute()
            
            return response.data
            
        except Exception as e:
            print(f"Get bookshelf error: {e}")
            return []

    def is_in_bookshelf(self, user_id: str, novel_id: int) -> bool:
        """Kiểm tra novel có trong tủ sách không"""
        try:
            response = self.supabase.table('bookshelf').select('id').eq('user_id', user_id).eq('novel_id', novel_id).execute()
            return len(response.data) > 0
            
        except Exception as e:
            print(f"Check bookshelf error: {e}")
            return False

    def get_reading_stats(self, user_id: str) -> Dict:
        """Lấy thống kê đọc của user"""
        try:
            # Đếm số novels đã đọc
            novels_read_response = self.supabase.table('reading_progress').select('novel_id').eq('user_id', user_id).execute()
            novels_read = len(set(item['novel_id'] for item in novels_read_response.data))
            
            # Đếm tổng số chapters đã đọc
            chapters_read_response = self.supabase.table('reading_progress').select('id').eq('user_id', user_id).execute()
            chapters_read = len(chapters_read_response.data)
            
            # Đếm số novels trong bookshelf
            bookshelf_response = self.supabase.table('bookshelf').select('id').eq('user_id', user_id).execute()
            bookshelf_count = len(bookshelf_response.data)
            
            return {
                "novels_read": novels_read,
                "chapters_read": chapters_read,
                "bookshelf_count": bookshelf_count
            }
            
        except Exception as e:
            print(f"Get reading stats error: {e}")
            return {
                "novels_read": 0,
                "chapters_read": 0,
                "bookshelf_count": 0
            } 