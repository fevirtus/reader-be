import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path
from supabase import create_client
from app.core.config import settings


class SyncService:
    def __init__(self):
        self.supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
        self.storage_path = Path("storage/novels")
    
    def scan_novels_directory(self) -> List[Dict]:
        """Quét thư mục storage/novels/ để tìm các novel"""
        novels = []
        
        if not self.storage_path.exists():
            print(f"❌ Storage path not found: {self.storage_path}")
            return novels
        
        for novel_dir in self.storage_path.iterdir():
            if novel_dir.is_dir():
                book_info_path = novel_dir / "book_info.json"
                
                if book_info_path.exists():
                    try:
                        with open(book_info_path, 'r', encoding='utf-8') as f:
                            book_info = json.load(f)
                            book_info['_storage_path'] = str(novel_dir)
                            novels.append(book_info)
                            print(f"✅ Found novel: {book_info.get('title', 'Unknown')}")
                    except Exception as e:
                        print(f"❌ Error reading {book_info_path}: {e}")
                else:
                    print(f"⚠️ No book_info.json found in {novel_dir}")
        
        return novels
    
    def novel_exists(self, title: str) -> Optional[Dict]:
        """Kiểm tra xem novel có tồn tại không"""
        try:
            existing_novel = self.supabase_admin.table('novels').select('*').eq('title', title).execute()
            return existing_novel.data[0] if existing_novel.data else None
        except Exception as e:
            print(f"❌ Error checking novel existence: {e}")
            return None
    
    def update_novel_chapter_count(self, novel_id: str) -> None:
        """Cập nhật total_chapters count cho novel"""
        try:
            # Đếm số chapters của novel
            chapters_response = self.supabase_admin.table('chapters').select('id', count='exact').eq('novel_id', novel_id).execute()
            total_chapters = chapters_response.count if chapters_response.count is not None else 0
            
            # Cập nhật novel
            self.supabase_admin.table('novels').update({
                'total_chapters': total_chapters,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', novel_id).execute()
            
            print(f"📊 Updated novel {novel_id} total_chapters: {total_chapters}")
        except Exception as e:
            print(f"❌ Error updating novel chapter count: {e}")
    
    def sync_novel_to_db(self, book_info: Dict) -> bool:
        """Sync một novel vào database"""
        try:
            title = book_info.get('title', '')
            author = book_info.get('author', '')
            description = book_info.get('description', '')
            cover_image = book_info.get('cover_url', '')  # Map cover_url to cover_image
            status = book_info.get('status', 'ongoing')
            chapters = book_info.get('chapters', [])
            
            print(f"🔄 Syncing novel: {title}")
            
            # Kiểm tra novel đã tồn tại chưa
            existing_novel = self.novel_exists(title)
            
            if existing_novel:
                # Novel đã tồn tại, chỉ sync chapters
                novel_id = existing_novel['id']
                print(f"📚 Novel already exists: {title} (ID: {novel_id})")
                print(f"🔄 Skipping novel update, only syncing chapters...")
                
            else:
                # Tạo novel mới
                print(f"🆕 Creating new novel: {title}")
                
                novel_data = {
                    'title': title,
                    'author': author,
                    'description': description,
                    'cover_image': cover_image,
                    'status': status,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                
                novel_response = self.supabase_admin.table('novels').insert(novel_data).execute()
                novel_id = novel_response.data[0]['id']
            
            # Sync chapters
            self.sync_chapters(novel_id, chapters)
            
            # Cập nhật total_chapters count
            self.update_novel_chapter_count(novel_id)
            
            print(f"✅ Successfully synced novel: {title}")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing novel {book_info.get('title', 'Unknown')}: {e}")
            return False
    
    def sync_chapters(self, novel_id: str, chapters: List[Dict]) -> None:
        """Sync chapters cho một novel"""
        try:
            print(f"📚 Syncing {len(chapters)} chapters for novel {novel_id}")
            
            for chapter_info in chapters:
                chapter_title = chapter_info.get('title', '')
                chapter_number = chapter_info.get('number', 0)
                chapter_filename = chapter_info.get('filename', '')
                chapter_word_count = chapter_info.get('word_count', 0)
                
                # Kiểm tra chapter đã tồn tại chưa
                existing_chapter = self.supabase_admin.table('chapters').select('*').eq('novel_id', novel_id).eq('title', chapter_title).execute()
                
                if existing_chapter.data:
                    # Chapter đã tồn tại, kiểm tra xem có cần update không
                    existing_chapter_data = existing_chapter.data[0]
                    chapter_id = existing_chapter_data['id']
                    
                    # Chỉ update nếu có thay đổi
                    needs_update = (
                        existing_chapter_data['title'] != chapter_title or
                        existing_chapter_data['chapter_number'] != chapter_number or
                        existing_chapter_data['content_file'] != chapter_filename or
                        existing_chapter_data['word_count'] != chapter_word_count
                    )
                    
                    if needs_update:
                        print(f"📝 Updating chapter: {chapter_title}")
                        update_data = {
                            'title': chapter_title,
                            'chapter_number': chapter_number,
                            'content_file': chapter_filename,  # Map filename to content_file
                            'word_count': chapter_word_count,
                            'updated_at': datetime.now(timezone.utc).isoformat()
                        }
                        self.supabase_admin.table('chapters').update(update_data).eq('id', chapter_id).execute()
                    else:
                        print(f"✅ Chapter already up-to-date: {chapter_title}")
                    
                else:
                    # Tạo chapter mới
                    print(f"🆕 Creating chapter: {chapter_title}")
                    
                    chapter_data = {
                        'novel_id': novel_id,
                        'title': chapter_title,
                        'chapter_number': chapter_number,
                        'content_file': chapter_filename,  # Map filename to content_file
                        'word_count': chapter_word_count,
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    }
                    
                    self.supabase_admin.table('chapters').insert(chapter_data).execute()
            
            print(f"✅ Successfully synced {len(chapters)} chapters")
            
        except Exception as e:
            print(f"❌ Error syncing chapters for novel {novel_id}: {e}")
    
    def sync_all_novels(self) -> Dict:
        """Sync tất cả novels từ storage vào database"""
        print("🚀 Starting novel sync job...")
        
        start_time = datetime.now()
        novels = self.scan_novels_directory()
        
        if not novels:
            print("❌ No novels found in storage")
            return {
                'success': False,
                'message': 'No novels found in storage',
                'novels_processed': 0,
                'duration': 0
            }
        
        print(f"📚 Found {len(novels)} novels to sync")
        
        success_count = 0
        error_count = 0
        
        for book_info in novels:
            if self.sync_novel_to_db(book_info):
                success_count += 1
            else:
                error_count += 1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            'success': error_count == 0,
            'novels_processed': len(novels),
            'novels_success': success_count,
            'novels_error': error_count,
            'duration': duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
        
        print(f"✅ Sync job completed:")
        print(f"   📚 Novels processed: {len(novels)}")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   ⏱️ Duration: {duration:.2f}s")
        
        return result
    
    def sync_chapters_only(self, novel_title: str, chapters: List[Dict]) -> bool:
        """Sync chỉ chapters cho novel đã tồn tại"""
        try:
            print(f"🔄 Syncing chapters only for novel: {novel_title}")
            
            # Kiểm tra novel có tồn tại không
            existing_novel = self.novel_exists(novel_title)
            if not existing_novel:
                print(f"❌ Novel not found: {novel_title}")
                return False
            
            novel_id = existing_novel['id']
            print(f"📚 Found existing novel: {novel_title} (ID: {novel_id})")
            
            # Sync chapters
            self.sync_chapters(novel_id, chapters)
            
            # Cập nhật total_chapters count
            self.update_novel_chapter_count(novel_id)
            
            print(f"✅ Successfully synced chapters for novel: {novel_title}")
            return True
            
        except Exception as e:
            print(f"❌ Error syncing chapters for novel {novel_title}: {e}")
            return False


# Global sync service instance
sync_service = SyncService() 