#!/usr/bin/env python3
"""
Script để test cache system
"""

import sys
import time
from pathlib import Path

# Thêm thư mục gốc vào Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.cache_service import cache_service
from app.services.novel_service import NovelService
from app.services.chapter_service import ChapterService


def test_cache_basic():
    """Test cache cơ bản"""
    print("🧪 Testing basic cache functionality...")
    
    # Test set/get
    cache_service.set("test:key", "test_value", ttl=10)
    result = cache_service.get("test:key")
    
    if result == "test_value":
        print("✅ Basic set/get works")
    else:
        print("❌ Basic set/get failed")
        return False
    
    # Test expiration
    cache_service.set("test:expire", "expire_value", ttl=1)
    time.sleep(2)
    result = cache_service.get("test:expire")
    
    if result is None:
        print("✅ Cache expiration works")
    else:
        print("❌ Cache expiration failed")
        return False
    
    # Test delete
    cache_service.set("test:delete", "delete_value")
    cache_service.delete("test:delete")
    result = cache_service.get("test:delete")
    
    if result is None:
        print("✅ Cache delete works")
    else:
        print("❌ Cache delete failed")
        return False
    
    return True


def test_novel_cache():
    """Test novel cache"""
    print("\n📚 Testing novel cache...")
    
    novel_service = NovelService()
    
    # Test get novel (should cache)
    start_time = time.time()
    novel1 = novel_service.get_novel(4)
    first_request_time = time.time() - start_time
    
    # Test get novel again (should use cache)
    start_time = time.time()
    novel2 = novel_service.get_novel(4)
    second_request_time = time.time() - start_time
    
    if novel1 and novel2 and novel1 == novel2:
        print(f"✅ Novel cache works (First: {first_request_time:.3f}s, Second: {second_request_time:.3f}s)")
        
        if second_request_time < first_request_time:
            print("✅ Cache is faster than database")
        else:
            print("⚠️ Cache might not be working as expected")
    else:
        print("❌ Novel cache failed")
        return False
    
    return True


def test_chapter_cache():
    """Test chapter cache"""
    print("\n📖 Testing chapter cache...")
    
    chapter_service = ChapterService()
    
    # Test get chapter (should cache)
    start_time = time.time()
    chapter1 = chapter_service.get_chapter(1)
    first_request_time = time.time() - start_time
    
    # Test get chapter again (should use cache)
    start_time = time.time()
    chapter2 = chapter_service.get_chapter(1)
    second_request_time = time.time() - start_time
    
    if chapter1 and chapter2 and chapter1 == chapter2:
        print(f"✅ Chapter cache works (First: {first_request_time:.3f}s, Second: {second_request_time:.3f}s)")
        
        if second_request_time < first_request_time:
            print("✅ Cache is faster than database")
        else:
            print("⚠️ Cache might not be working as expected")
    else:
        print("❌ Chapter cache failed")
        return False
    
    return True


def test_chapter_content_cache():
    """Test chapter content cache"""
    print("\n📄 Testing chapter content cache...")
    
    chapter_service = ChapterService()
    
    # Test get content (should cache)
    start_time = time.time()
    content1 = chapter_service.get_chapter_content(1, "markdown")
    first_request_time = time.time() - start_time
    
    # Test get content again (should use cache)
    start_time = time.time()
    content2 = chapter_service.get_chapter_content(1, "markdown")
    second_request_time = time.time() - start_time
    
    if content1 and content2 and content1 == content2:
        print(f"✅ Content cache works (First: {first_request_time:.3f}s, Second: {second_request_time:.3f}s)")
        
        if second_request_time < first_request_time:
            print("✅ Cache is faster than file system")
        else:
            print("⚠️ Cache might not be working as expected")
    else:
        print("❌ Content cache failed")
        return False
    
    return True


def test_cache_stats():
    """Test cache statistics"""
    print("\n📊 Testing cache statistics...")
    
    # Clear cache first
    cache_service.clear()
    
    # Add some test data
    cache_service.set("test:1", "value1", ttl=60)
    cache_service.set("test:2", "value2", ttl=60)
    cache_service.set("test:3", "value3", ttl=1)  # Will expire
    
    # Wait for expiration
    time.sleep(2)
    
    # Get stats
    stats = cache_service.get_stats()
    
    print(f"📈 Cache stats: {stats}")
    
    if stats['total_entries'] >= 2 and stats['valid_entries'] >= 2:
        print("✅ Cache statistics work")
        return True
    else:
        print("❌ Cache statistics failed")
        return False


def test_cache_cleanup():
    """Test cache cleanup"""
    print("\n🧹 Testing cache cleanup...")
    
    # Clear cache first
    cache_service.clear()
    
    # Add some test data
    cache_service.set("cleanup:1", "value1", ttl=1)
    cache_service.set("cleanup:2", "value2", ttl=1)
    cache_service.set("cleanup:3", "value3", ttl=60)
    
    # Wait for expiration
    time.sleep(2)
    
    # Cleanup expired entries
    cleaned_count = cache_service.cleanup_expired()
    
    stats = cache_service.get_stats()
    
    print(f"🧹 Cleaned {cleaned_count} expired entries")
    print(f"📊 Remaining entries: {stats['valid_entries']}")
    
    if cleaned_count >= 2 and stats['expired_entries'] == 0:
        print("✅ Cache cleanup works")
        return True
    else:
        print("❌ Cache cleanup failed")
        return False


def main():
    print("🚀 Cache System Test")
    print("=" * 50)
    
    tests = [
        test_cache_basic,
        test_novel_cache,
        test_chapter_cache,
        test_chapter_content_cache,
        test_cache_stats,
        test_cache_cleanup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Cache system is working correctly.")
    else:
        print("💥 Some tests failed. Please check the cache implementation.")
    
    # Final cleanup
    cache_service.clear()
    print("🧹 Cache cleared")


if __name__ == "__main__":
    main() 