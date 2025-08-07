import httpx
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
from google.auth.transport.requests import Request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from app.core.config import settings
from app.services.auth_service import AuthService


class OAuthService:
    def __init__(self):
        self.auth_service = AuthService()
        self.google_client_id = settings.google_client_id
        self.google_client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri

    def get_google_auth_url(self, state: str = None) -> str:
        """Tạo Google OAuth URL"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.google_client_id,
                        "client_secret": self.google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                    }
                },
                scopes=[
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "openid"
                ]
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Tạo authorization URL với state parameter
            auth_params = {
                'access_type': 'offline',
                'include_granted_scopes': 'true'
            }
            
            if state:
                auth_params['state'] = state
            
            auth_url, _ = flow.authorization_url(**auth_params)
            
            return auth_url
        except Exception as e:
            raise Exception(f"Failed to create Google auth URL: {str(e)}")

    async def handle_google_callback(self, code: str) -> Dict:
        """Xử lý Google OAuth callback"""
        try:
            print(f"🔄 Processing Google OAuth callback with code: {code[:20]}...")
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.google_client_id,
                        "client_secret": self.google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri],
                    }
                },
                scopes=[
                    "https://www.googleapis.com/auth/userinfo.profile",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "openid"
                ]
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for tokens
            print("🔄 Exchanging code for tokens...")
            flow.fetch_token(code=code)
            print("✅ Token exchange successful")
            
            # Get user info from Google API
            print("🔄 Getting user info from Google API...")
            user_info = await self._get_google_user_info(flow.credentials.token)
            print(f"✅ Got user info: {user_info.get('email', 'N/A')}")
            
            # Extract user information
            google_user_id = user_info['id']
            email = user_info['email']
            name = user_info.get('name', email.split('@')[0])
            picture = user_info.get('picture')
            
            print(f"📧 User email: {email}")
            print(f"👤 User name: {name}")
            print(f"🆔 Google user ID: {google_user_id}")
            
            # Check if user exists
            print("🔄 Checking if user exists...")
            existing_user = self.auth_service.check_user_exists(email)
            print(f"User exists: {existing_user}")
            
            if existing_user:
                # User exists, login
                print("🔄 Logging in existing user...")
                return await self._login_existing_user(email)
            else:
                # User doesn't exist, create new user
                print("🔄 Creating new user...")
                return await self._create_new_user_from_google(
                    google_user_id, email, name, picture
                )
                
        except Exception as e:
            print(f"❌ Google OAuth callback error: {e}")
            raise Exception(f"Google OAuth callback failed: {str(e)}")

    async def _get_google_user_info(self, access_token: str) -> Dict:
        """Lấy user info từ Google API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"Failed to get Google user info: {str(e)}")

    async def _login_existing_user(self, email: str) -> Dict:
        """Login user đã tồn tại"""
        try:
            print(f"🔍 Looking for existing user with email: {email}")
            
            # Lấy user profile
            profile_response = self.auth_service.supabase_admin.table('user_profiles').select('*').eq('email', email).execute()
            print(f"Profile response: {profile_response.data}")
            
            if profile_response.data:
                profile = profile_response.data[0]
                print(f"✅ Found existing user profile: {profile['username']}")
                
                # Tạo session token
                session_token = self.auth_service._create_session_token()
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                
                # Lưu session vào database
                session_data = {
                    "user_id": profile['id'],
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat()
                }
                
                self.auth_service.supabase_admin.table('user_sessions').insert(session_data).execute()
                
                return {
                    "session_token": session_token,
                    "expires_at": expires_at,
                    "user": profile,
                    "is_new_user": False
                }
            else:
                print(f"❌ User profile not found for email: {email}")
                # Thử tạo profile cho user đã tồn tại trong auth.users
                return await self._create_profile_for_existing_user(email)
                
        except Exception as e:
            print(f"❌ Login existing user error: {e}")
            raise Exception(f"Login existing user failed: {str(e)}")

    async def _create_profile_for_existing_user(self, email: str) -> Dict:
        """Tạo profile cho user đã tồn tại trong auth.users"""
        try:
            print(f"🔧 Creating profile for existing user: {email}")
            
            # Thử tìm user profile hiện có trước
            try:
                existing_profile = self.auth_service.supabase_admin.table('user_profiles').select('*').eq('email', email).execute()
                
                if existing_profile.data:
                    profile = existing_profile.data[0]
                    print(f"✅ Found existing profile: {profile['username']}")
                    
                    # Tạo session token
                    session_token = self.auth_service._create_session_token()
                    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                    
                    # Lưu session vào database
                    session_data = {
                        "user_id": profile['id'],
                        "session_token": session_token,
                        "expires_at": expires_at.isoformat()
                    }
                    
                    self.auth_service.supabase_admin.table('user_sessions').insert(session_data).execute()
                    
                    return {
                        "session_token": session_token,
                        "expires_at": expires_at,
                        "user": profile,
                        "is_new_user": False
                    }
                    
            except Exception as find_error:
                print(f"❌ Error finding existing profile: {find_error}")
            
            # Nếu không tìm thấy profile, thử tạo mới với username unique
            try:
                import uuid
                import time
                
                # Tạo username unique bằng cách thêm timestamp
                base_username = email.split('@')[0]
                unique_username = f"{base_username}_{int(time.time())}"
                
                user_id = str(uuid.uuid4())
                print(f"🔄 Creating profile with unique username: {unique_username}")
                
                profile_data = {
                    "id": user_id,
                    "username": unique_username,
                    "email": email
                }
                
                profile_response = self.auth_service.supabase_admin.table('user_profiles').insert(profile_data).execute()
                profile = profile_response.data[0]
                print(f"✅ Created profile with unique username: {profile}")
                
                # Tạo session token
                session_token = self.auth_service._create_session_token()
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                
                # Lưu session vào database
                session_data = {
                    "user_id": user_id,
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat()
                }
                
                self.auth_service.supabase_admin.table('user_sessions').insert(session_data).execute()
                
                return {
                    "session_token": session_token,
                    "expires_at": expires_at,
                    "user": profile,
                    "is_new_user": False
                }
                
            except Exception as create_error:
                print(f"❌ Profile creation failed: {create_error}")
                
                # Fallback: thử tạo với UUID cho username
                try:
                    user_id = str(uuid.uuid4())
                    username_uuid = str(uuid.uuid4())[:8]  # Lấy 8 ký tự đầu
                    
                    profile_data = {
                        "id": user_id,
                        "username": username_uuid,
                        "email": email
                    }
                    
                    profile_response = self.auth_service.supabase_admin.table('user_profiles').insert(profile_data).execute()
                    profile = profile_response.data[0]
                    print(f"✅ Created profile with UUID username: {profile}")
                    
                    # Tạo session token
                    session_token = self.auth_service._create_session_token()
                    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                    
                    # Lưu session vào database
                    session_data = {
                        "user_id": user_id,
                        "session_token": session_token,
                        "expires_at": expires_at.isoformat()
                    }
                    
                    self.auth_service.supabase_admin.table('user_sessions').insert(session_data).execute()
                    
                    return {
                        "session_token": session_token,
                        "expires_at": expires_at,
                        "user": profile,
                        "is_new_user": False
                    }
                    
                except Exception as final_error:
                    print(f"❌ Final fallback failed: {final_error}")
                    raise Exception(f"All profile creation methods failed: {str(final_error)}")
                
        except Exception as e:
            print(f"❌ Create profile for existing user error: {e}")
            raise Exception(f"Create profile for existing user failed: {str(e)}")

    async def _create_new_user_from_google(
        self, google_user_id: str, email: str, name: str, picture: Optional[str]
    ) -> Dict:
        """Tạo user mới từ Google OAuth"""
        try:
            # Tạo user trong Supabase Auth (không cần password)
            auth_response = self.auth_service.supabase.auth.sign_up({
                "email": email,
                "password": f"google_{google_user_id}",  # Temporary password
                "options": {
                    "data": {
                        "username": name,
                        "provider": "google",
                        "google_user_id": google_user_id
                    }
                }
            })
            
            if auth_response.user:
                # Tạo user profile
                profile_data = {
                    "id": auth_response.user.id,
                    "username": name,
                    "email": email,
                    "avatar_url": picture
                }
                
                try:
                    profile_response = self.auth_service.supabase_admin.table('user_profiles').insert(profile_data).execute()
                    profile = profile_response.data[0]
                    print(f"✅ Created new user profile: {profile}")
                except Exception as insert_error:
                    print(f"❌ Failed to insert profile: {insert_error}")
                    # Thử tạo profile với upsert
                    profile_response = self.auth_service.supabase_admin.table('user_profiles').upsert(profile_data, on_conflict='id').execute()
                    profile = profile_response.data[0]
                    print(f"✅ Created profile with upsert: {profile}")
                
                # Tạo session token
                session_token = self.auth_service._create_session_token()
                expires_at = datetime.now(timezone.utc) + timedelta(days=7)
                
                # Lưu session vào database
                session_data = {
                    "user_id": auth_response.user.id,
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat()
                }
                
                self.auth_service.supabase_admin.table('user_sessions').insert(session_data).execute()
                
                return {
                    "session_token": session_token,
                    "expires_at": expires_at,
                    "user": profile,
                    "is_new_user": True
                }
            else:
                raise Exception("Failed to create user from Google OAuth")
                
        except Exception as e:
            raise Exception(f"Create new user from Google failed: {str(e)}")

    def verify_google_token(self, token: str) -> Optional[Dict]:
        """Verify Google ID token"""
        try:
            id_info = id_token.verify_oauth2_token(
                token,
                Request(),
                self.google_client_id
            )
            return id_info
        except Exception as e:
            print(f"Google token verification failed: {e}")
            return None 