#!/usr/bin/env python3

from app.services.auth_service import AuthService
from app.services.oauth_service import OAuthService

def debug_user():
    """Debug user trong database"""
    try:
        print("🔍 Debugging user in database...")
        
        auth_service = AuthService()
        oauth_service = OAuthService()
        
        email = "fevirtus@gmail.com"
        
        # Kiểm tra user exists
        print(f"🔍 Checking if user exists: {email}")
        exists = auth_service.check_user_exists(email)
        print(f"User exists: {exists}")
        
        # Kiểm tra user profile
        print(f"🔍 Checking user profile for: {email}")
        try:
            profile_response = auth_service.supabase_admin.table('user_profiles').select('*').eq('email', email).execute()
            print(f"Profile response: {profile_response.data}")
            
            if profile_response.data:
                profile = profile_response.data[0]
                print(f"✅ Found profile: {profile}")
                
                # Test session token
                session_token = auth_service._create_session_token()
                print(f"🔑 Created session token: {session_token}")
                
                # Lưu session
                session_data = {
                    "user_id": profile['id'],
                    "session_token": session_token,
                    "expires_at": "2025-12-31T23:59:59+00:00"
                }
                
                session_response = auth_service.supabase_admin.table('user_sessions').insert(session_data).execute()
                print(f"Session saved: {session_response.data}")
                
                # Test validate session
                validation = auth_service.validate_session(session_token)
                print(f"Session validation: {validation}")
                
            else:
                print("❌ No profile found")
                
        except Exception as e:
            print(f"❌ Error checking profile: {e}")
        
        print("✅ Debug completed")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    debug_user() 