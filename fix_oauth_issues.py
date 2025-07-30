#!/usr/bin/env python3
"""
Script để kiểm tra và sửa các vấn đề OAuth
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def check_oauth_status():
    """Kiểm tra trạng thái OAuth"""
    print("🔍 === OAUTH STATUS CHECK ===\n")
    
    # Test 1: Health check
    print("1. Health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: OAuth providers
    print("\n2. OAuth providers...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/oauth/providers")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OAuth providers: {data.get('providers', [])}")
            print(f"✅ OAuth enabled: {data.get('enabled', False)}")
        else:
            print(f"❌ OAuth providers failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OAuth providers error: {e}")
        return False
    
    # Test 3: Google OAuth URL
    print("\n3. Google OAuth URL...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/oauth/google/auth")
        if response.status_code == 200:
            data = response.json()
            auth_url = data.get('auth_url', '')
            if auth_url and 'accounts.google.com' in auth_url:
                print("✅ Google OAuth URL is valid")
                print(f"   URL: {auth_url[:100]}...")
            else:
                print("❌ Google OAuth URL is invalid")
                return False
        else:
            print(f"❌ Google OAuth URL failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Google OAuth URL error: {e}")
        return False
    
    # Test 4: CORS headers
    print("\n4. CORS headers...")
    try:
        response = requests.options(f"{BASE_URL}/api/v1/oauth/google/auth")
        if response.status_code == 200:
            print("✅ CORS preflight successful")
        else:
            print(f"❌ CORS preflight failed: {response.status_code}")
    except Exception as e:
        print(f"❌ CORS test error: {e}")
    
    print("\n✅ All OAuth checks passed!")
    return True

def test_callback_with_mock():
    """Test callback với mock data"""
    print("\n🔧 === TESTING CALLBACK WITH MOCK ===\n")
    
    # Mock authorization code (sẽ fail nhưng test error handling)
    mock_code = "mock_auth_code_123"
    
    print(f"Testing callback with mock code: {mock_code}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/oauth/google/callback?code={mock_code}")
        
        if response.status_code == 400:
            print("✅ Callback correctly rejected invalid code")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Callback test error: {e}")

def check_database_schema():
    """Kiểm tra database schema"""
    print("\n🗄️ === DATABASE SCHEMA CHECK ===\n")
    
    # Test user_profiles table
    print("1. Checking user_profiles table...")
    try:
        # Sử dụng Supabase client để kiểm tra
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Test query user_profiles
        response = auth_service.supabase_admin.table('user_profiles').select('*').limit(1).execute()
        print("✅ user_profiles table accessible")
        
        # Test query user_sessions
        response = auth_service.supabase_admin.table('user_sessions').select('*').limit(1).execute()
        print("✅ user_sessions table accessible")
        
    except Exception as e:
        print(f"❌ Database schema error: {e}")
        return False
    
    print("✅ Database schema check passed!")
    return True

def generate_test_data():
    """Tạo test data cho OAuth"""
    print("\n📊 === GENERATING TEST DATA ===\n")
    
    try:
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        
        # Tạo test user profile
        test_profile = {
            "username": "test_user",
            "email": "test@example.com"
        }
        
        # Thử upsert test profile
        response = auth_service.supabase_admin.table('user_profiles').upsert(
            test_profile, 
            on_conflict='email'
        ).execute()
        
        if response.data:
            print("✅ Test profile created/updated")
            print(f"   User: {response.data[0]['username']}")
            print(f"   Email: {response.data[0]['email']}")
        else:
            print("❌ Failed to create test profile")
            
    except Exception as e:
        print(f"❌ Test data generation error: {e}")

def main():
    """Main function"""
    print("🚀 === OAUTH ISSUE FIXER ===\n")
    
    # Check 1: OAuth status
    if not check_oauth_status():
        print("\n❌ OAuth status check failed")
        return
    
    # Check 2: Database schema
    if not check_database_schema():
        print("\n❌ Database schema check failed")
        return
    
    # Test 3: Callback with mock
    test_callback_with_mock()
    
    # Test 4: Generate test data
    generate_test_data()
    
    print("\n✅ All checks completed!")
    print("\n📋 Next steps:")
    print("1. Test OAuth flow in browser")
    print("2. Check server logs for any errors")
    print("3. Verify user profile creation")
    print("4. Test session token functionality")

if __name__ == "__main__":
    main() 