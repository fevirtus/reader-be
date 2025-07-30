# SQL Scripts

Thư mục chứa các file SQL cho database setup.

## Files

- `setup_supabase.sql` - Script setup database schema cho Supabase
- `fix_rls_policies.sql` - Script fix RLS policies cho việc đăng ký user

## Sử dụng

### Setup Supabase Database

1. Truy cập Supabase Dashboard
2. Vào **SQL Editor**
3. Copy và paste nội dung file `setup_supabase.sql`
4. Chạy script để tạo:
   - Tables: novels, chapters, user_profiles, reading_progress, bookshelf, user_sessions
   - Indexes: Performance optimization
   - Functions: increment_views, update_reading_progress, cleanup_expired_sessions
   - Triggers: Auto-update updated_at
   - RLS Policies: Row Level Security

### Fix RLS Policies (Nếu gặp lỗi đăng ký)

Nếu gặp lỗi RLS khi đăng ký user, chạy thêm:

1. Copy và paste nội dung file `fix_rls_policies.sql`
2. Chạy script để fix RLS policies

## Schema Overview

### Tables
- **novels**: Lưu thông tin truyện
- **chapters**: Lưu thông tin chương
- **user_profiles**: Profile của user (link với Supabase Auth)
- **reading_progress**: Tiến độ đọc của user
- **bookshelf**: Tủ sách cá nhân của user
- **user_sessions**: Session management

### Functions
- `increment_novel_views(novel_id)`: Tăng lượt xem novel
- `increment_chapter_views(chapter_id)`: Tăng lượt xem chapter
- `update_reading_progress(user_id, novel_id, chapter_id, chapter_number)`: Cập nhật tiến độ đọc
- `cleanup_expired_sessions()`: Xóa session hết hạn

### RLS Policies
- Public read access cho novels và chapters
- Authenticated write access cho novels và chapters
- User-specific access cho reading_progress, bookshelf, user_sessions
- **Special policies** cho việc đăng ký user (bypass RLS)

## Troubleshooting

### Lỗi RLS khi đăng ký
```
Registration failed: {'message': 'new row violates row-level security policy for table "user_profiles"', 'code': '42501'}
```

**Giải pháp:**
1. Chạy `fix_rls_policies.sql` trong Supabase SQL Editor
2. Hoặc disable RLS tạm thời cho development:
   ```sql
   ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;
   ```

### Lỗi function không tồn tại
```
function "update_reading_progress" does not exist
```

**Giải pháp:**
1. Đảm bảo đã chạy `setup_supabase.sql` trước
2. Kiểm tra function trong Supabase Dashboard > Database > Functions 