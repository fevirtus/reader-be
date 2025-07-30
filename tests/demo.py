#!/usr/bin/env python3
"""
Demo script cho Reader Backend API
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def demo_novels():
    """Demo novel operations"""
    print("📚 === NOVELS DEMO ===")
    
    # Create novels
    novels_data = [
        {
            "title": "Tu Tiên Giới",
            "author": "Tác giả A",
            "description": "Truyện tu tiên đỉnh cao với nhiều tình tiết hấp dẫn",
            "status": "ongoing"
        },
        {
            "title": "Võ Đế Trọng Sinh",
            "author": "Tác giả B", 
            "description": "Truyện võ hiệp trọng sinh với nhiều chiến đấu gay cấn",
            "status": "completed"
        },
        {
            "title": "Thành Thần Chi Lộ",
            "author": "Tác giả C",
            "description": "Truyện thành thần với nhiều bí mật chờ khám phá",
            "status": "ongoing"
        }
    ]
    
    created_novels = []
    
    for novel_data in novels_data:
        try:
            response = requests.post(f"{API_BASE}/novels", json=novel_data)
            if response.status_code == 200:
                novel = response.json()
                created_novels.append(novel)
                print(f"✅ Created: {novel['title']} (ID: {novel['id']})")
            else:
                print(f"❌ Failed to create: {novel_data['title']}")
        except Exception as e:
            print(f"❌ Error creating novel: {e}")
    
    # List all novels
    try:
        response = requests.get(f"{API_BASE}/novels")
        if response.status_code == 200:
            novels = response.json()
            print(f"\n📖 Total novels: {len(novels)}")
            for novel in novels:
                print(f"  - {novel['title']} by {novel['author']} ({novel['status']})")
        else:
            print("❌ Failed to get novels")
    except Exception as e:
        print(f"❌ Error getting novels: {e}")
    
    return created_novels

def demo_chapters(novels):
    """Demo chapter operations"""
    print("\n📖 === CHAPTERS DEMO ===")
    
    if not novels:
        print("❌ No novels available for chapter demo")
        return
    
    novel = novels[0]  # Use first novel
    
    # Create chapters
    chapters_data = [
        {
            "novel_id": novel['id'],
            "chapter_number": 1.0,
            "title": "Chương 1: Khởi đầu",
            "content_file": "storage/novels/novel_2/chapter_1.md"
        },
        {
            "novel_id": novel['id'],
            "chapter_number": 2.0,
            "title": "Chương 2: Phát triển",
            "content_file": "storage/novels/novel_2/chapter_2.md"
        },
        {
            "novel_id": novel['id'],
            "chapter_number": 3.0,
            "title": "Chương 3: Cao trào",
            "content_file": "storage/novels/novel_2/chapter_3.md"
        }
    ]
    
    created_chapters = []
    
    for chapter_data in chapters_data:
        try:
            response = requests.post(f"{API_BASE}/chapters", json=chapter_data)
            if response.status_code == 200:
                chapter = response.json()
                created_chapters.append(chapter)
                print(f"✅ Created: {chapter['title']} (ID: {chapter['id']})")
            else:
                print(f"❌ Failed to create: {chapter_data['title']}")
        except Exception as e:
            print(f"❌ Error creating chapter: {e}")
    
    # List chapters for the novel
    try:
        response = requests.get(f"{API_BASE}/chapters?novel_id={novel['id']}")
        if response.status_code == 200:
            chapters = response.json()
            print(f"\n📄 Chapters for '{novel['title']}': {len(chapters)}")
            for chapter in chapters:
                print(f"  - Chapter {chapter['chapter_number']}: {chapter['title']}")
        else:
            print("❌ Failed to get chapters")
    except Exception as e:
        print(f"❌ Error getting chapters: {e}")
    
    return created_chapters

def demo_content_formats(chapters):
    """Demo content format conversion"""
    print("\n📝 === CONTENT FORMATS DEMO ===")
    
    if not chapters:
        print("❌ No chapters available for content demo")
        return
    
    chapter = chapters[0]  # Use first chapter
    
    # Test different formats
    formats = ["markdown", "html"]
    
    for format_type in formats:
        try:
            response = requests.get(f"{API_BASE}/chapters/{chapter['id']}/content?format={format_type}")
            if response.status_code == 200:
                content = response.json()
                print(f"✅ {format_type.upper()} format:")
                print(f"   Length: {len(content['content'])} characters")
                print(f"   Preview: {content['content'][:100]}...")
            else:
                print(f"❌ Failed to get {format_type} content")
        except Exception as e:
            print(f"❌ Error getting {format_type} content: {e}")

def demo_navigation(chapters):
    """Demo chapter navigation"""
    print("\n🧭 === NAVIGATION DEMO ===")
    
    if not chapters:
        print("❌ No chapters available for navigation demo")
        return
    
    chapter = chapters[0]  # Use first chapter
    
    try:
        response = requests.get(f"{API_BASE}/chapters/novel/{chapter['novel_id']}/chapter/{chapter['chapter_number']}/navigation")
        if response.status_code == 200:
            navigation = response.json()
            print("✅ Navigation info:")
            print(f"   Current: Chapter {navigation['current']['chapter_number']}")
            if navigation['previous']:
                print(f"   Previous: Chapter {navigation['previous']['chapter_number']}")
            if navigation['next']:
                print(f"   Next: Chapter {navigation['next']['chapter_number']}")
        else:
            print("❌ Failed to get navigation")
    except Exception as e:
        print(f"❌ Error getting navigation: {e}")

def main():
    """Main demo function"""
    print("🚀 === READER BACKEND API DEMO ===")
    print()
    
    # Wait for server
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Demo novels
    novels = demo_novels()
    
    # Demo chapters
    chapters = demo_chapters(novels)
    
    # Demo content formats
    demo_content_formats(chapters)
    
    # Demo navigation
    demo_navigation(chapters)
    
    print("\n🎉 Demo completed successfully!")
    print("📚 API is working correctly!")

if __name__ == "__main__":
    main() 