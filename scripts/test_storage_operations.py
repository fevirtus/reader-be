#!/usr/bin/env python3
"""
Script để test storage operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.novel_service import NovelService
from app.services.chapter_service import ChapterService

def test_storage_operations():
    """Test các operations với storage"""
    try:
        novel_service = NovelService()
        chapter_service = ChapterService()
        
        print("🔍 Testing storage operations...")
        
        # Test 1: Tạo novel và thư mục storage
        print("\n1. Testing create novel with storage...")
        novel_data = {
            'title': 'Test Novel Storage',
            'author': 'Test Author',
            'description': 'Test novel for storage operations',
            'status': 'ongoing'
        }
        
        novel = novel_service.create_novel(novel_data)
        if novel:
            print(f"✅ Created novel: {novel['title']} (ID: {novel['id']})")
            novel_id = novel['id']
            novel_title = novel['title']
        else:
            print("❌ Failed to create novel")
            return
        
        # Test 2: Tạo chapter với file content
        print("\n2. Testing create chapter with file...")
        chapter_data = {
            'novel_id': novel_id,
            'chapter_number': 1,
            'title': 'Test Chapter 1',
            'content_file': '1.html',
            'word_count': 1500
        }
        
        # Tạo file content
        content = """
        <h1>Test Chapter 1</h1>
        <p>Đây là nội dung test cho chapter 1.</p>
        <p>Nội dung này sẽ được lưu trong file storage.</p>
        """
        
        # Tạo file content
        chapter_service._create_chapter_file(novel_title, '1.html', content)
        
        chapter = chapter_service.create_chapter(chapter_data)
        if chapter:
            print(f"✅ Created chapter: {chapter['title']} (ID: {chapter['id']})")
            chapter_id = chapter['id']
        else:
            print("❌ Failed to create chapter")
            return
        
        # Test 3: Update novel title (đổi tên thư mục)
        print("\n3. Testing update novel title (rename directory)...")
        update_data = {
            'title': 'Test Novel Storage Updated',
            'description': 'Updated description'
        }
        
        updated_novel = novel_service.update_novel(novel_id, update_data)
        if updated_novel:
            print(f"✅ Updated novel title: {updated_novel['title']}")
            novel_title = updated_novel['title']
        else:
            print("❌ Failed to update novel")
            return
        
        # Test 4: Update chapter content file (đổi tên file)
        print("\n4. Testing update chapter content file...")
        update_chapter_data = {
            'content_file': '1_updated.html',
            'title': 'Test Chapter 1 Updated'
        }
        
        updated_chapter = chapter_service.update_chapter(chapter_id, update_chapter_data)
        if updated_chapter:
            print(f"✅ Updated chapter: {updated_chapter['title']}")
        else:
            print("❌ Failed to update chapter")
            return
        
        # Test 5: Delete chapter (xóa file)
        print("\n5. Testing delete chapter (delete file)...")
        success = chapter_service.delete_chapter(chapter_id)
        if success:
            print("✅ Deleted chapter and file")
        else:
            print("❌ Failed to delete chapter")
            return
        
        # Test 6: Delete novel (xóa thư mục)
        print("\n6. Testing delete novel (delete directory)...")
        success = novel_service.delete_novel(novel_id)
        if success:
            print("✅ Deleted novel and directory")
        else:
            print("❌ Failed to delete novel")
            return
        
        print("\n🎉 All storage operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_storage_operations() 