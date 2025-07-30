# Tests

Thư mục chứa các file test cho Reader Backend API.

## Files

- `test_api.py` - Test các API endpoints cơ bản
- `test_auth.py` - Test authentication và reading features
- `test_supabase.py` - Test kết nối Supabase
- `demo.py` - Demo các tính năng của API

## Chạy tests

```bash
# Test API cơ bản
uv run python tests/test_api.py

# Test authentication
uv run python tests/test_auth.py

# Test Supabase connection
uv run python tests/test_supabase.py

# Demo features
uv run python tests/demo.py
```

## Lưu ý

- Đảm bảo server đang chạy trước khi test
- Cần cấu hình Supabase trước khi chạy test_auth.py
- Các test sẽ tạo dữ liệu mẫu trong database 