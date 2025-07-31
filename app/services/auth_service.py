import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from supabase import create_client, Client
from app.core.config import settings


class AuthService:
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
    
    def check_user_exists(self, email: str) -> bool:
        """Kiểm tra user đã tồn tại chưa"""
        try:
            print(f"🔍 Checking if user exists: {email}")
            # Kiểm tra trong user_profiles trước
            response = self.supabase_admin.table('user_profiles').select('id').eq('email', email).execute()
            if len(response.data) > 0:
                print(f"User exists in profiles: {len(response.data)}")
                return True
            
            # Nếu không có trong profiles, kiểm tra trong auth.users
            auth_response = self.supabase_admin.auth.admin.list_users()
            for user in auth_response.users:
                if user.email == email:
                    print(f"User exists in auth.users: {user.id}")
                    return True
            
            print(f"User does not exist")
            return False
        except Exception as e:
            print(f"Check user exists error: {e}")
            return False
    

    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token"""
        try:
            print(f"🔍 Validating session token: {session_token[:10]}...")
            
            # Tìm session trong database sử dụng service role key
            session_response = self.supabase_admin.table('user_sessions').select('*').eq('session_token', session_token).execute()
            
            if session_response.data:
                session = session_response.data[0]
                print(f"✅ Found session for user: {session['user_id']}")
                
                expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
                
                # Kiểm tra session có hết hạn chưa
                if expires_at > datetime.now(timezone.utc).replace(tzinfo=expires_at.tzinfo):
                    # Lấy user profile sử dụng service role key
                    profile_response = self.supabase_admin.table('user_profiles').select('*').eq('id', session['user_id']).execute()
                    
                    if profile_response.data:
                        print(f"✅ Found user profile: {profile_response.data[0]['username']}")
                        return {
                            "user": profile_response.data[0],
                            "session": session
                        }
                    else:
                        print(f"❌ No user profile found for user_id: {session['user_id']}")
                else:
                    print(f"❌ Session expired at: {expires_at}")
            else:
                print(f"❌ No session found for token: {session_token[:10]}...")
            
            return None
            
        except Exception as e:
            print(f"Session validation error: {e}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Đăng xuất user"""
        try:
            print(f"🔧 Logging out user with session: {session_token[:10]}...")
            
            # Xóa session khỏi database sử dụng service role key
            delete_response = self.supabase_admin.table('user_sessions').delete().eq('session_token', session_token).execute()
            
            if delete_response.data:
                print(f"✅ Session deleted successfully")
                return True
            else:
                print(f"❌ No session found to delete")
                return False
        except Exception as e:
            print(f"Logout error: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Lấy user profile"""
        try:
            profile_response = self.supabase.table('user_profiles').select('*').eq('id', user_id).execute()
            return profile_response.data[0] if profile_response.data else None
        except Exception as e:
            print(f"Get profile error: {e}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> Optional[Dict]:
        """Cập nhật user profile"""
        try:
            print(f"🔧 Updating profile for user: {user_id}")
            print(f"📝 Update data: {profile_data}")
            
            # Sử dụng service role key để bypass RLS
            update_response = self.supabase_admin.table('user_profiles').update(profile_data).eq('id', user_id).execute()
            
            if update_response.data:
                print(f"✅ Profile updated successfully")
                return update_response.data[0]
            else:
                print(f"❌ No profile found to update")
                return None
        except Exception as e:
            print(f"Update profile error: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> bool:
        """Xóa các session đã hết hạn"""
        try:
            # Gọi function cleanup trong database
            self.supabase_admin.rpc('cleanup_expired_sessions').execute()
            return True
        except Exception as e:
            print(f"Cleanup sessions error: {e}")
            return False
    
    def _create_session_token(self) -> str:
        """Tạo session token ngẫu nhiên"""
        return secrets.token_urlsafe(32) 