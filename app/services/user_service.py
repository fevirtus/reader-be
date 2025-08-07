from typing import List, Optional, Dict, Any
from app.services.supabase_service import SupabaseService
from supabase import create_client
from app.core.config import settings


class UserService:
    def __init__(self):
        self.supabase_service = SupabaseService()
        # Tạo client với service key để bypass RLS khi cần
        self.supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Lấy thông tin profile của user"""
        try:
            # Thử với anon key trước
            response = self.supabase_service.supabase.table('user_profiles').select('*').eq('id', user_id).execute()
            if response.data:
                return response.data[0]
            else:
                # Nếu không tìm thấy với anon key, thử với service key
                response = self.supabase_admin.table('user_profiles').select('*').eq('id', user_id).execute()
                if response.data:
                    return response.data[0]
                else:
                    return None
        except Exception as e:
            print(f"Error getting user profile: {e}")
            return None
    
    def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Cập nhật thông tin profile của user"""
        try:
            self.supabase_service.supabase.table('user_profiles').update(profile_data).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error updating user profile: {e}")
            return False
    
    def is_admin(self, user_id: str) -> bool:
        """Kiểm tra user có role admin không"""
        try:
            profile = self.get_user_profile(user_id)
            if profile:
                role = profile.get('role')
                return role == 'admin'
            else:
                return False
        except Exception as e:
            print(f"Error checking admin role: {e}")
            return False
    
    def change_user_role(self, admin_user_id: str, target_user_id: str, new_role: str) -> bool:
        """Thay đổi role của user (chỉ admin mới có quyền)"""
        try:
            # Kiểm tra admin có quyền không
            if not self.is_admin(admin_user_id):
                print(f"User {admin_user_id} is not admin")
                return False
            
            # Kiểm tra role hợp lệ
            if new_role not in ['user', 'admin']:
                print(f"Invalid role: {new_role}")
                return False
            
            # Thay đổi role
            self.supabase_service.supabase.table('user_profiles').update({
                'role': new_role
            }).eq('id', target_user_id).execute()
            
            print(f"Changed user {target_user_id} role to {new_role}")
            return True
        except Exception as e:
            print(f"Error changing user role: {e}")
            return False
    
    def get_all_users(self, admin_user_id: str) -> List[Dict]:
        """Lấy danh sách tất cả users (chỉ admin)"""
        try:
            if not self.is_admin(admin_user_id):
                return []
            
            # Sử dụng service key để bypass RLS
            response = self.supabase_admin.table('user_profiles').select('*').execute()
            return response.data
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def get_all_users_paginated(self, admin_user_id: str, page: int = 1, limit: int = 20, search: str = None, role: str = None) -> Dict:
        """Lấy danh sách users với pagination và filter"""
        try:
            if not self.is_admin(admin_user_id):
                return {"items": [], "total": 0, "page": page, "limit": limit}
            
            query = self.supabase_admin.table('user_profiles').select('*')
            
            # Apply filters
            if search:
                query = query.or_(f"email.ilike.%{search}%,name.ilike.%{search}%")
            
            if role:
                query = query.eq('role', role)
            
            # Get total count
            count_query = query
            count_response = count_query.execute()
            total = len(count_response.data)
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            
            return {
                "items": response.data,
                "total": total,
                "page": page,
                "limit": limit,
                "total_pages": (total + limit - 1) // limit,
                "has_next": page * limit < total,
                "has_prev": page > 1,
                "next_page": page + 1 if page * limit < total else None,
                "prev_page": page - 1 if page > 1 else None
            }
        except Exception as e:
            print(f"Error getting paginated users: {e}")
            return {"items": [], "total": 0, "page": page, "limit": limit}
    
    def get_users_by_role(self, admin_user_id: str, role: str) -> List[Dict]:
        """Lấy danh sách users theo role (chỉ admin)"""
        try:
            if not self.is_admin(admin_user_id):
                return []
            
            response = self.supabase_admin.table('user_profiles').select('*').eq('role', role).execute()
            return response.data
        except Exception as e:
            print(f"Error getting users by role: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê users"""
        try:
            # Tổng số users
            total_response = self.supabase_admin.table('user_profiles').select('id').execute()
            total = len(total_response.data)
            
            # Số admin
            admin_response = self.supabase_admin.table('user_profiles').select('id').eq('role', 'admin').execute()
            admin_count = len(admin_response.data)
            
            # Số user thường
            user_count = total - admin_count
            
            return {
                "total": total,
                "admin_count": admin_count,
                "user_count": user_count
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {"total": 0, "admin_count": 0, "user_count": 0}
    
    def get_recent_activities(self, limit: int = 5) -> List[Dict]:
        """Lấy hoạt động gần đây của users"""
        try:
            # Lấy users mới đăng ký gần đây
            response = self.supabase_admin.table('user_profiles').select('*').order('created_at', desc=True).limit(limit).execute()
            
            activities = []
            for user in response.data:
                activities.append({
                    "id": f"user_{user['id']}",
                    "type": "user_registration",
                    "description": f"User {user.get('name', user.get('email', 'Unknown'))} đã đăng ký",
                    "created_at": user.get('created_at'),
                    "user_id": user['id']
                })
            
            return activities
        except Exception as e:
            print(f"Error getting user activities: {e}")
            return [] 