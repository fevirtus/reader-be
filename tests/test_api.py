#!/usr/bin/env python3
"""
Test script cho API endpoints
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

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_create_novel():
    """Test create novel"""
    print("\n📚 Testing create novel...")
    
    novel_data = {
        "title": "Test Novel",
        "author": "Test Author",
        "description": "A test novel",
        "status": "ongoing"
    }
    
    try:
        response = requests.post(f"{API_BASE}/novels", json=novel_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Create novel successful")
            print(f"   Novel ID: {data['id']}")
            return data['id']
        else:
            print(f"❌ Create novel failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Create novel error: {e}")
        return None

def test_get_novels():
    """Test get novels"""
    print("\n📚 Testing get novels...")
    
    try:
        response = requests.get(f"{API_BASE}/novels")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get novels successful")
            print(f"   Found {len(data)} novels")
            return True
        else:
            print(f"❌ Get novels failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get novels error: {e}")
        return False

def test_create_chapter(novel_id):
    """Test create chapter"""
    print("\n📖 Testing create chapter...")
    
    # Tạo file markdown test
    test_content = """# Chapter 1

Đây là nội dung chapter 1.

## Tiêu đề phụ

Nội dung tiếp theo...
"""
    
    # Lưu file markdown
    os.makedirs("storage/novels/test_novel", exist_ok=True)
    with open("storage/novels/test_novel/chapter_1.md", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    chapter_data = {
        "novel_id": novel_id,
        "chapter_number": 1.0,
        "title": "Chapter 1",
        "content_file": "storage/novels/test_novel/chapter_1.md"
    }
    
    try:
        response = requests.post(f"{API_BASE}/chapters", json=chapter_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Create chapter successful")
            print(f"   Chapter ID: {data['id']}")
            return data['id']
        else:
            print(f"❌ Create chapter failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Create chapter error: {e}")
        return None

def test_get_chapters(novel_id):
    """Test get chapters"""
    print("\n📖 Testing get chapters...")
    
    try:
        response = requests.get(f"{API_BASE}/chapters?novel_id={novel_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get chapters successful")
            print(f"   Found {len(data)} chapters")
            return True
        else:
            print(f"❌ Get chapters failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get chapters error: {e}")
        return False

def test_get_chapter_content(chapter_id):
    """Test get chapter content"""
    print("\n📖 Testing get chapter content...")
    
    try:
        response = requests.get(f"{API_BASE}/chapters/{chapter_id}/content?format=html")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get chapter content successful")
            print(f"   Content length: {len(data['content'])} characters")
            return True
        else:
            print(f"❌ Get chapter content failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get chapter content error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 === API ENDPOINTS TEST ===")
    print()
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed")
        sys.exit(1)
    
    # Test 2: Create novel
    novel_id = test_create_novel()
    if not novel_id:
        print("\n❌ Create novel failed")
        sys.exit(1)
    
    # Test 3: Get novels
    if not test_get_novels():
        print("\n❌ Get novels failed")
        sys.exit(1)
    
    # Test 4: Create chapter
    chapter_id = test_create_chapter(novel_id)
    if not chapter_id:
        print("\n❌ Create chapter failed")
        sys.exit(1)
    
    # Test 5: Get chapters
    if not test_get_chapters(novel_id):
        print("\n❌ Get chapters failed")
        sys.exit(1)
    
    # Test 6: Get chapter content
    if not test_get_chapter_content(chapter_id):
        print("\n❌ Get chapter content failed")
        sys.exit(1)
    
    print("\n✅ All API tests passed!")
    print("🎉 API endpoints are working correctly!")

if __name__ == "__main__":
    main() 