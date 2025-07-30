# 🚀 Supabase Setup Guide

## 📋 Cấu hình Supabase cho Reader Backend

### 1. **Tạo Supabase Project**

1. Truy cập [supabase.com](https://supabase.com)
2. Tạo project mới
3. Lấy thông tin connection:
   - **Project URL**: `https://your-project-ref.supabase.co`
   - **Anon Key**: `your-anon-key`
   - **Service Role Key**: `your-service-role-key`

### 2. **Setup Database Schema**

1. Vào **SQL Editor** trong Supabase Dashboard
2. Copy và paste nội dung file `sql/setup_supabase.sql`
3. Chạy script để tạo tables và functions

### 3. **Cấu hình Authentication (Quan trọng!)**

#### Disable Email Confirmation (Development)

1. Vào **Authentication** > **Settings**
2. Tìm **Email Auth** section
3. **Disable** "Enable email confirmations"
4. Hoặc set **Confirm email** thành `false`

#### Cấu hình khác (Optional)

1. **Site URL**: Set thành `http://localhost:3000` (frontend URL)
2. **Redirect URLs**: Thêm `http://localhost:3000/auth/callback`
3. **JWT Expiry**: Set thành `604800` (7 days)

### 4. **Cấu hình Environment Variables**

Cập nhật file `.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database Configuration (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
ALLOWED_HOSTS=["*"]

# File Storage (Local for markdown files)
STORAGE_PATH=./storage/novels
```

### 5. **Fix RLS Policies (Nếu cần)**

Nếu gặp lỗi RLS khi đăng ký:

1. Copy và paste nội dung file `sql/fix_rls_policies.sql`
2. Chạy script để fix RLS policies

### 6. **Test Setup**

```bash
# Test Supabase connection
uv run python tests/test_supabase.py

# Test Authentication (sau khi disable email confirmation)
uv run python tests/test_auth_simple.py

# Test API
uv run python tests/test_api.py
```

## 🔧 Troubleshooting

### Lỗi Email Confirmation

```
Email confirmation required. Please check your email and confirm your account.
```

**Giải pháp:**
1. Disable email confirmation trong Supabase Auth settings
2. Hoặc sử dụng email thật và confirm

### Lỗi RLS

```
Registration failed: {'message': 'new row violates row-level security policy for table "user_profiles"', 'code': '42501'}
```

**Giải pháp:**
1. Chạy `sql/fix_rls_policies.sql`
2. Hoặc disable RLS tạm thời:
   ```sql
   ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
   ```

### Lỗi Function không tồn tại

```
function "update_reading_progress" does not exist
```

**Giải pháp:**
1. Đảm bảo đã chạy `sql/setup_supabase.sql`
2. Kiểm tra function trong Supabase Dashboard > Database > Functions

### Lỗi Connection

```
Supabase connection failed
```

**Giải pháp:**
1. Kiểm tra environment variables
2. Kiểm tra network connection
3. Kiểm tra Supabase project status

## 📊 Production Setup

### 1. **Enable Email Confirmation**
- Bật lại email confirmation trong production
- Cấu hình email provider (SendGrid, etc.)

### 2. **Enable RLS**
- Đảm bảo RLS được enable cho tất cả tables
- Test security policies

### 3. **Cấu hình SSL**
- Set up custom domain
- Configure SSL certificates

### 4. **Monitoring**
- Set up Supabase monitoring
- Configure alerts

## 🎯 Quick Start

1. **Tạo Supabase project**
2. **Disable email confirmation**
3. **Chạy `sql/setup_supabase.sql`**
4. **Cập nhật `.env`**
5. **Test với `tests/test_auth_simple.py`**

## ✅ Checklist

- [ ] Supabase project created
- [ ] Database schema setup
- [ ] Email confirmation disabled
- [ ] Environment variables configured
- [ ] RLS policies fixed (if needed)
- [ ] Authentication test passed
- [ ] API test passed 