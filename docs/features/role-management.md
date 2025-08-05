# Role Management System

## Tổng quan

Hệ thống phân quyền với 2 role chính:
- **User**: Người dùng thường, chỉ có thể đọc content
- **Admin**: Quản trị viên, có quyền CRUD novels và chapters

## Database Schema

### User Profiles
```sql
CREATE TABLE user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    avatar_url VARCHAR(500),
    bio TEXT,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Admin Management

#### 1. Kiểm tra admin status
```http
GET /api/v1/admin/check-admin
Authorization: Bearer <token>
```

Response:
```json
{
    "user_id": "uuid",
    "is_admin": true,
    "role": "admin"
}
```

#### 2. Lấy danh sách users (admin only)
```http
GET /api/v1/admin/users
Authorization: Bearer <admin_token>
```

#### 3. Lấy users theo role
```http
GET /api/v1/admin/users/{role}
Authorization: Bearer <admin_token>
```

#### 4. Thay đổi role của user
```http
POST /api/v1/admin/users/role
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "user_id": "uuid",
    "role": "admin"
}
```

### Novel Management (Admin Only)

#### 1. Tạo novel
```http
POST /api/v1/novels
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "title": "Tên truyện",
    "author": "Tác giả",
    "description": "Mô tả",
    "cover_image": "url",
    "status": "ongoing"
}
```

#### 2. Cập nhật novel
```http
PUT /api/v1/novels/{novel_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "title": "Tên mới",
    "author": "Tác giả mới"
}
```

#### 3. Xóa novel
```http
DELETE /api/v1/novels/{novel_id}
Authorization: Bearer <admin_token>
```

### Chapter Management (Admin Only)

#### 1. Tạo chapter
```http
POST /api/v1/chapters
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "novel_id": 1,
    "chapter_number": 1.0,
    "title": "Chương 1",
    "content_file": "1.md"
}
```

#### 2. Cập nhật chapter
```http
PUT /api/v1/chapters/{chapter_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
    "title": "Tên chapter mới",
    "content_file": "new_file.md"
}
```

#### 3. Xóa chapter
```http
DELETE /api/v1/chapters/{chapter_id}
Authorization: Bearer <admin_token>
```

## Database Policies

### Novels
- **SELECT**: Public (tất cả users)
- **INSERT/UPDATE/DELETE**: Chỉ admin

### Chapters
- **SELECT**: Public (tất cả users)
- **INSERT/UPDATE/DELETE**: Chỉ admin

### User Profiles
- **SELECT**: User có thể xem profile của chính mình, admin có thể xem tất cả
- **UPDATE**: User có thể update profile của chính mình, admin có thể update tất cả

## Functions

### is_admin(user_id)
Kiểm tra user có role admin không

### change_user_role(target_user_id, new_role)
Thay đổi role của user (chỉ admin mới có quyền)

## Setup

### 1. Chạy SQL setup
```bash
# Chạy file setup_supabase.sql trên Supabase
```

### 2. Tạo admin đầu tiên
```bash
# Sau khi user đăng ký, lấy user_id và chạy:
python scripts/create_admin.py <user_id>
```

## Security

- Tất cả admin endpoints yêu cầu authentication
- Role được kiểm tra ở cả API level và database level
- Admin có thể thay đổi role của user khác
- User thường chỉ có thể đọc content

## Error Handling

- **403 Forbidden**: Không có quyền truy cập
- **404 Not Found**: Resource không tồn tại
- **400 Bad Request**: Dữ liệu không hợp lệ 