#!/usr/bin/env python3
"""
Test script cho Supabase integration
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time

load_dotenv()

def test_supabase_connection():
    """Test kết nối Supabase"""
    print("🔍 Testing Supabase connection...")
    
    # Kiểm tra environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables are set")
    
    try:
        # Import SupabaseService từ app
        from app.services.supabase_service import SupabaseService
        
        # Tạo instance của SupabaseService
        supabase_service = SupabaseService()
        
        # Test kết nối bằng cách đếm số novels
        novels = supabase_service.get_novels(limit=1)
        
        if novels is not None:
            print("✅ Supabase connection successful")
            print(f"   Found {len(novels)} novels in database")
            return True
        else:
            print("❌ Supabase connection failed: No data returned")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            print("❌ Database schema not set up")
            print("   Please run sql/setup_supabase.sql in your Supabase SQL Editor")
            return False
        else:
            print(f"❌ Supabase connection failed: {e}")
            return False

def test_database_schema():
    """Test database schema"""
    print("\n🗄️ Testing database schema...")
    
    try:
        from app.services.supabase_service import SupabaseService
        
        supabase_service = SupabaseService()
        
        # Test novels table
        novels = supabase_service.get_novels(limit=1)
        if novels is not None:
            print("✅ Novels table accessible")
        else:
            print("❌ Novels table not accessible")
            return False
        
        # Test chapters table
        chapters = supabase_service.get_chapters_by_novel(1, limit=1)
        if chapters is not None:
            print("✅ Chapters table accessible")
        else:
            print("❌ Chapters table not accessible")
            return False
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "relation" in error_msg and "does not exist" in error_msg:
            print("❌ Database schema not set up")
            print("   Please run sql/setup_supabase.sql in your Supabase SQL Editor")
            return False
        else:
            print(f"❌ Database schema test failed: {e}")
            return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API endpoints...")
    
    # Đợi server khởi động
    print("   Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test novels endpoint
        response = requests.get("http://localhost:8000/api/v1/novels", timeout=10)
        if response.status_code == 200:
            print("✅ Novels endpoint working")
            return True
        else:
            print(f"❌ Novels endpoint failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first:")
        print("   uv run uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 === SUPABASE INTEGRATION TEST ===")
    print()
    
    # Test 1: Supabase connection
    if not test_supabase_connection():
        print("\n❌ Supabase connection test failed")
        print("Please check your .env file and Supabase configuration")
        print("\n📋 Setup instructions:")
        print("1. Create a Supabase project at https://supabase.com")
        print("2. Get your project URL and anon key")
        print("3. Update your .env file with the credentials")
        print("4. Run sql/setup_supabase.sql in Supabase SQL Editor")
        sys.exit(1)
    
    # Test 2: Database schema
    if not test_database_schema():
        print("\n❌ Database schema test failed")
        print("Please run sql/setup_supabase.sql in your Supabase SQL Editor")
        sys.exit(1)
    
    # Test 3: API endpoints
    if not test_api_endpoints():
        print("\n❌ API endpoints test failed")
        sys.exit(1)
    
    print("\n✅ All tests passed!")
    print("🎉 Supabase integration is working correctly!")

if __name__ == "__main__":
    main() 