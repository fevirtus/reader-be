import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from supabase import create_client, Client
from app.core.config import settings
from app.schemas.auth import UserRegister, UserLogin, UserProfile


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
    
    def register_user(self, user_data: UserRegister) -> Dict:
        """Đăng ký user mới"""
        try:
            # Kiểm tra user đã tồn tại chưa
            if self.check_user_exists(user_data.email):
                raise Exception("User with this email already exists")
            
            # Tạo user trong Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "username": user_data.username
                    }
                }
            })
            
            if auth_response.user:
                # Tạo user profile sử dụng service role key để bypass RLS
                profile_data = {
                    "id": auth_response.user.id,
                    "username": user_data.username,
                    "email": user_data.email
                }
                
                profile_response = self.supabase_admin.table('user_profiles').insert(profile_data).execute()
                
                # Tạo session token giống như login
                session_token = self._create_session_token()
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                
                # Lưu session vào database sử dụng service role key
                session_data = {
                    "user_id": auth_response.user.id,
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat()
                }
                
                self.supabase_admin.table('user_sessions').insert(session_data).execute()
                
                return {
                    "session_token": session_token,
                    "expires_at": expires_at,
                    "user": profile_response.data[0]
                }
            else:
                raise Exception("Failed to create user")
                
        except Exception as e:
            error_msg = str(e)
            if "duplicate key value violates unique constraint" in error_msg:
                raise Exception("User with this email already exists")
            elif "Email address" in error_msg and "is invalid" in error_msg:
                raise Exception("Email confirmation required. Please check your email and confirm your account.")
            elif "already registered" in error_msg.lower():
                raise Exception("User with this email already exists.")
            else:
                raise Exception(f"Registration failed: {error_msg}")
    
    def login_user(self, user_data: UserLogin) -> Dict:
        """Đăng nhập user"""
        try:
            # Đăng nhập với Supabase Auth
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if auth_response.user:
                # Lấy user profile
                profile_response = self.supabase.table('user_profiles').select('*').eq('id', auth_response.user.id).execute()
                
                if profile_response.data:
                    profile = profile_response.data[0]
                    
                    # Tạo session token
                    session_token = self._create_session_token()
                    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                    
                    # Lưu session vào database sử dụng service role key
                    session_data = {
                        "user_id": auth_response.user.id,
                        "session_token": session_token,
                        "expires_at": expires_at.isoformat()
                    }
                    
                    self.supabase_admin.table('user_sessions').insert(session_data).execute()
                    
                    return {
                        "session_token": session_token,
                        "expires_at": expires_at,
                        "user": profile
                    }
                else:
                    raise Exception("User profile not found")
            else:
                raise Exception("Invalid credentials")
                
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate session token"""
        try:
            # Tìm session trong database
            session_response = self.supabase.table('user_sessions').select('*').eq('session_token', session_token).execute()
            
            if session_response.data:
                session = session_response.data[0]
                expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
                
                # Kiểm tra session có hết hạn chưa
                if expires_at > datetime.now(timezone.utc).replace(tzinfo=expires_at.tzinfo):
                    # Lấy user profile
                    profile_response = self.supabase.table('user_profiles').select('*').eq('id', session['user_id']).execute()
                    
                    if profile_response.data:
                        return {
                            "user": profile_response.data[0],
                            "session": session
                        }
            
            return None
            
        except Exception as e:
            print(f"Session validation error: {e}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Đăng xuất user"""
        try:
            # Xóa session khỏi database
            self.supabase_admin.table('user_sessions').delete().eq('session_token', session_token).execute()
            return True
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
            update_response = self.supabase.table('user_profiles').update(profile_data).eq('id', user_id).execute()
            return update_response.data[0] if update_response.data else None
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
    
    def _hash_password(self, password: str) -> str:
        """Hash password (không cần thiết vì Supabase tự xử lý)"""
        return hashlib.sha256(password.encode()).hexdigest() 