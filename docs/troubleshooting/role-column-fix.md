# Sửa lỗi Column Role

## Vấn đề
```
ERROR: 42703: column "role" does not exist
```

## Nguyên nhân
Column `role` chưa được tạo trong bảng `user_profiles` vì:
1. Database được tạo trước khi thêm role system
2. Script setup chưa được chạy hoàn toàn

## Giải pháp

### Bước 1: Chạy SQL trên Supabase Dashboard

1. Đăng nhập vào [Supabase Dashboard](https://supabase.com/dashboard)
2. Chọn project của bạn
3. Vào **SQL Editor**
4. Chạy script sau:

```sql
-- Thêm column role vào user_profiles
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'user_profiles' 
        AND column_name = 'role'
    ) THEN
        ALTER TABLE user_profiles ADD COLUMN role VARCHAR(20) DEFAULT 'user';
        
        -- Thêm constraint
        ALTER TABLE user_profiles ADD CONSTRAINT check_role CHECK (role IN ('user', 'admin'));
        
        RAISE NOTICE 'Added role column to user_profiles table';
    ELSE
        RAISE NOTICE 'Role column already exists in user_profiles table';
    END IF;
END $$;

-- Cập nhật tất cả users hiện tại thành role 'user'
UPDATE user_profiles 
SET role = 'user' 
WHERE role IS NULL;
```

### Bước 2: Tạo Admin User

Sau khi thêm column role, tạo admin user đầu tiên:

```sql
-- Thay thế 'your-user-id-here' bằng user_id thực tế
UPDATE user_profiles 
SET role = 'admin' 
WHERE id = 'your-user-id-here';
```

### Bước 3: Kiểm tra

Chạy script kiểm tra:

```bash
uv run python scripts/fix_database.py
```

## Kiểm tra thủ công

### 1. Kiểm tra column role
```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'user_profiles' 
AND column_name = 'role';
```

### 2. Kiểm tra users và roles
```sql
SELECT id, username, email, role 
FROM user_profiles 
LIMIT 10;
```

### 3. Kiểm tra functions
```sql
SELECT routine_name, routine_type
FROM information_schema.routines 
WHERE routine_name IN ('is_admin', 'change_user_role');
```

## Troubleshooting

### Lỗi: "column does not exist"
- Đảm bảo đã chạy script thêm column
- Kiểm tra tên bảng và column chính xác

### Lỗi: "function does not exist"
- Chạy lại file `setup_supabase.sql` hoàn chỉnh
- Kiểm tra các functions đã được tạo

### Lỗi: "permission denied"
- Đảm bảo sử dụng service role key
- Kiểm tra RLS policies

## API Test

Sau khi sửa lỗi, test API:

```bash
# Kiểm tra admin status
curl -X GET "http://localhost:8000/api/v1/admin/check-admin" \
  -H "Authorization: Bearer <token>"

# Tạo novel (admin only)
curl -X POST "http://localhost:8000/api/v1/novels" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Novel","author":"Test Author"}'
```

## Kết quả mong đợi

Sau khi sửa lỗi:
- ✅ Column `role` tồn tại trong `user_profiles`
- ✅ Tất cả users có role mặc định là 'user'
- ✅ Có ít nhất 1 admin user
- ✅ Functions `is_admin()` và `change_user_role()` hoạt động
- ✅ API admin endpoints hoạt động 