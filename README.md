# 📚 Reader Backend API

Backend API cho webapp đọc truyện với Supabase, hỗ trợ OAuth authentication, automatic content sync và reading progress.

## 🚀 Features

- **🔐 OAuth Authentication**: Google OAuth 2.0 với session management
- **📖 Novel Management**: Read-only APIs với automatic sync từ storage
- **📊 Reading Progress**: Theo dõi tiến độ đọc cho từng user
- **📚 Bookshelf**: Tủ sách cá nhân cho user
- **🔄 Auto Sync**: Tự động sync novels từ storage/novels/ mỗi giờ
- **📝 Markdown Support**: Lưu trữ nội dung chapter dưới dạng markdown
- **🔒 Security**: Row Level Security (RLS) với Supabase
- **🐳 Docker Support**: Containerized với Docker và Docker Compose

## 🛠️ Tech Stack

- **FastAPI**: Python web framework
- **Supabase**: Backend-as-a-Service (PostgreSQL, Auth, Storage)
- **Pydantic**: Data validation và serialization
- **Docker**: Containerization
- **Markdown**: Content storage format

## 📋 Prerequisites

- Python 3.8+
- uv (Python package manager)
- Docker (optional)
- Supabase account

## ⚡ Quick Start

### 1. **Setup Supabase (Quan trọng!)**

Trước khi chạy app, bạn cần setup Supabase:

1. **Tạo Supabase project** tại [supabase.com](https://supabase.com)
2. **Disable email confirmation** trong Auth settings
3. **Chạy database schema** từ `sql/setup_supabase.sql`
4. **Cập nhật `.env`** với Supabase credentials

Xem chi tiết: [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)

### 2. **Install Dependencies**

```bash
# Install uv if not installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### 3. **Configure Environment**

Copy `.env.example` to `.env` và cập nhật:

```env
# Supabase Configuration
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Database Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
ALLOWED_HOSTS=["*"]
STORAGE_PATH=./storage/novels
```

### 4. **Run Development Server**

```bash
# Start server
uv run uvicorn main:app --reload

# Server sẽ chạy tại http://localhost:8000
# API docs: http://localhost:8000/docs
```

### 5. **Test Setup**

```bash
# Test Supabase connection
uv run python tests/test_supabase.py

# Test Authentication (sau khi disable email confirmation)
uv run python tests/test_auth_simple.py

# Test API endpoints
uv run python tests/test_api.py

# Demo features
uv run python tests/demo.py
```

## 🐳 Docker Setup

### Development

```bash
# Build và run với Docker Compose
docker-compose up --build

# Hoặc chỉ backend
docker-compose up reader-backend
```

### Production

```bash
# Build production image
docker build -t reader-backend .

# Run container
docker run -p 8000:8000 --env-file .env reader-backend
```

## 📚 API Documentation

### 🔐 Authentication & User Management
- `GET /api/v1/user/profile` - Lấy profile hiện tại
- `PUT /api/v1/user/profile` - Cập nhật profile
- `POST /api/v1/user/logout` - Đăng xuất
- `POST /api/v1/user/validate-session` - Validate session token
- `GET /api/v1/user/me` - Alias cho profile (backward compatibility)
- `PUT /api/v1/user/me` - Alias cho profile (backward compatibility)

### 🔑 OAuth Authentication
- `GET /api/v1/oauth/google/auth` - Lấy Google OAuth URL
- `GET /api/v1/oauth/google/callback` - Handle OAuth callback (redirects to frontend)
- `GET /api/v1/oauth/google/callback/redirect` - Alternative callback với custom redirect
- `POST /api/v1/oauth/google/verify` - Verify Google ID token
- `GET /api/v1/oauth/providers` - Lấy danh sách OAuth providers
- `GET /api/v1/oauth/frontend-config` - Lấy cấu hình cho frontend

### 📚 Novels (Read-Only)
- `GET /api/v1/novels` - Lấy danh sách novels với filtering và pagination
- `GET /api/v1/novels/{novel_id}` - Lấy thông tin novel

**Note**: Novels được quản lý tự động qua sync service. Không có API tạo/sửa/xóa.

### 📖 Chapters (Read-Only)
- `GET /api/v1/chapters` - Lấy chapters theo novel ID với phân trang
- `GET /api/v1/chapters/{chapter_id}` - Lấy nội dung chapter (markdown/html)

**Note**: Chapters được quản lý tự động qua sync service. Không có API tạo/sửa/xóa.

### 📊 Reading Progress
- `POST /api/v1/reading/progress` - Cập nhật tiến độ đọc
- `GET /api/v1/reading/progress` - Lấy tiến độ đọc
- `GET /api/v1/reading/progress/with-novels` - Lấy tiến độ với thông tin novel
- `POST /api/v1/reading/bookshelf` - Thêm novel vào tủ sách
- `DELETE /api/v1/reading/bookshelf/{novel_id}` - Xóa novel khỏi tủ sách
- `GET /api/v1/reading/bookshelf` - Lấy tủ sách
- `GET /api/v1/reading/bookshelf/{novel_id}/check` - Kiểm tra novel có trong tủ sách
- `GET /api/v1/reading/stats` - Lấy thống kê đọc
- `GET /api/v1/reading/novels/{novel_id}/progress` - Lấy tiến độ novel (guest users)
- `GET /api/v1/reading/novels/{novel_id}/bookshelf-check` - Kiểm tra bookshelf (guest users)

### 🔄 Sync Service
- `POST /api/v1/sync/novels` - Manual sync novels từ storage
- `POST /api/v1/sync/novels/background` - Background sync novels
- `GET /api/v1/sync/novels/status` - Lấy trạng thái sync
- `POST /api/v1/sync/scheduler/start` - Start hourly sync scheduler
- `POST /api/v1/sync/scheduler/stop` - Stop sync scheduler
- `GET /api/v1/sync/scheduler/status` - Lấy trạng thái scheduler

## 🗄️ Database Schema

### Tables

- **novels**: Thông tin truyện (title, author, description, status, etc.)
- **chapters**: Thông tin chương (novel_id, chapter_number, title, content_file, etc.)
- **user_profiles**: Profile user (username, email, avatar, bio)
- **reading_progress**: Tiến độ đọc (user_id, novel_id, chapter_id, chapter_number)
- **bookshelf**: Tủ sách cá nhân (user_id, novel_id)
- **user_sessions**: Session management (user_id, session_token, expires_at)

### Functions

- `increment_novel_views(novel_id)` - Tăng lượt xem novel
- `increment_chapter_views(chapter_id)` - Tăng lượt xem chapter
- `update_reading_progress(user_id, novel_id, chapter_id, chapter_number)` - Cập nhật tiến độ đọc
- `cleanup_expired_sessions()` - Xóa session hết hạn

## 📁 Storage Structure

### Novel Storage
```
storage/
└── novels/
    ├── novel_1/
    │   └── book_info.json
    ├── novel_2/
    │   └── book_info.json
    └── novel_3/
        └── book_info.json
```

### Book Info JSON Format
```json
{
  "title": "Novel Title",
  "author": "Author Name", 
  "description": "Novel description",
  "cover_url": "https://example.com/cover.jpg",
  "status": "ongoing",
  "chapters": [
    {
      "title": "Chapter Title",
      "number": 1,
      "content": "Chapter content...",
      "url": "https://example.com/chapter1"
    }
  ]
}
```

## 🔄 Sync Service

### Automatic Sync
- **Hourly Sync**: Tự động sync novels từ storage mỗi giờ
- **Manual Sync**: API để trigger sync thủ công
- **Background Sync**: Sync trong background không block API
- **Status Monitoring**: API để check trạng thái sync

### Sync Features
- ✅ **Auto Create**: Tạo novels mới từ storage folders
- ✅ **Auto Update**: Cập nhật novels khi book_info.json thay đổi
- ✅ **Auto Delete**: Xóa novels khi folder bị xóa
- ✅ **Chapter Sync**: Sync tất cả chapters của novel
- ✅ **Error Handling**: Log errors và continue sync

## 🔒 Security

- **Row Level Security (RLS)**: User chỉ có thể truy cập data của mình
- **Session Management**: Token-based sessions với 7 ngày expiration
- **Input Validation**: Pydantic schemas cho tất cả API endpoints
- **CORS**: Configured cho cross-origin requests

## 🎯 Key Features

### ✅ OAuth-Only Authentication
- **Google OAuth 2.0**: Single sign-on với Google
- **Session Management**: 7-day session tokens
- **No Traditional Login**: Email/password authentication removed
- **Frontend Integration**: Seamless redirect flow

### ✅ Automatic Content Management
- **Storage Sync**: Automatically sync novels từ `storage/novels/` folders
- **Hourly Updates**: Scheduled sync job runs every hour
- **No Manual Management**: Novels được tạo/update/delete dựa trên storage folders
- **Read-Only APIs**: Novel APIs là read-only cho security

### ✅ Advanced Filtering
- **Search**: Search novels by title và author
- **Status Filter**: Filter by ongoing/completed status
- **Author Filter**: Filter by specific author
- **Pagination**: Efficient pagination với skip/limit

## 🧪 Testing

```bash
# Test tất cả
uv run python tests/test_supabase.py
uv run python tests/test_auth_simple.py
uv run python tests/test_api.py
uv run python tests/demo.py

# Test sync service
uv run python test_sync.py
```

## 📁 Project Structure

```
reader-be/
├── app/
│   ├── api/v1/          # API routes
│   ├── core/            # Config, auth, database
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── sql/                 # Database scripts
├── tests/               # Test files
├── storage/             # Markdown files
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose
└── main.py             # FastAPI app entry point
```

## 🚨 Troubleshooting

### Lỗi OAuth Configuration
```
Google OAuth callback failed
```
**Giải pháp**: 
1. Kiểm tra Google OAuth credentials trong `.env`
2. Verify redirect URI trong Google Console
3. Xem [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md)

### Lỗi Session Token
```
Invalid or expired session token
```
**Giải pháp**: 
1. Kiểm tra Authorization header format: `Bearer <token>`
2. Verify session token không expired
3. Re-authenticate nếu cần

### Lỗi RLS
```
User not allowed
```
**Giải pháp**: Chạy `sql/fix_rls_policies.sql` và restart server

### Lỗi Sync Service
```
Sync job failed
```
**Giải pháp**: 
1. Kiểm tra storage/novels/ folder structure
2. Verify book_info.json format
3. Check sync service logs

### Lỗi Connection
```
Supabase connection failed
```
**Giải pháp**: Kiểm tra environment variables và network connection

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

Nếu gặp vấn đề, hãy:
1. Kiểm tra [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)
2. Chạy tests để debug
3. Tạo issue với thông tin chi tiết