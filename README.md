# 📚 Reader Backend API

Backend API cho webapp đọc truyện với Supabase, hỗ trợ authentication, reading progress và bookshelf.

## 🚀 Features

- **📖 Novel Management**: CRUD operations cho novels và chapters
- **👤 Authentication**: Đăng ký, đăng nhập với session 7 ngày
- **📊 Reading Progress**: Theo dõi tiến độ đọc cho từng user
- **📚 Bookshelf**: Tủ sách cá nhân cho user
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

### Authentication API

- `POST /api/v1/auth/register` - Đăng ký user
- `POST /api/v1/auth/login` - Đăng nhập
- `POST /api/v1/auth/logout` - Đăng xuất
- `GET /api/v1/auth/me` - Lấy profile hiện tại
- `PUT /api/v1/auth/me` - Cập nhật profile

### Novels API

- `GET /api/v1/novels` - Lấy danh sách novels
- `POST /api/v1/novels` - Tạo novel mới
- `GET /api/v1/novels/{novel_id}` - Lấy thông tin novel
- `PUT /api/v1/novels/{novel_id}` - Cập nhật novel
- `DELETE /api/v1/novels/{novel_id}` - Xóa novel

### Chapters API

- `GET /api/v1/chapters` - Lấy danh sách chapters
- `POST /api/v1/chapters` - Tạo chapter mới
- `GET /api/v1/chapters/{chapter_id}` - Lấy thông tin chapter
- `GET /api/v1/chapters/{chapter_id}/content` - Lấy nội dung chapter
- `PUT /api/v1/chapters/{chapter_id}` - Cập nhật chapter
- `DELETE /api/v1/chapters/{chapter_id}` - Xóa chapter

### Reading Progress API

- `POST /api/v1/reading/progress` - Cập nhật tiến độ đọc
- `GET /api/v1/reading/progress` - Lấy tiến độ đọc
- `GET /api/v1/reading/progress/with-novels` - Lấy tiến độ với thông tin novel
- `GET /api/v1/reading/stats` - Lấy thống kê đọc

### Bookshelf API

- `POST /api/v1/reading/bookshelf` - Thêm novel vào tủ sách
- `GET /api/v1/reading/bookshelf` - Lấy tủ sách
- `DELETE /api/v1/reading/bookshelf/{novel_id}` - Xóa novel khỏi tủ sách
- `GET /api/v1/reading/bookshelf/{novel_id}/check` - Kiểm tra novel có trong tủ sách

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

## 🔒 Security

- **Row Level Security (RLS)**: User chỉ có thể truy cập data của mình
- **Session Management**: Token-based sessions với 7 ngày expiration
- **Input Validation**: Pydantic schemas cho tất cả API endpoints
- **CORS**: Configured cho cross-origin requests

## 🧪 Testing

```bash
# Test tất cả
uv run python tests/test_supabase.py
uv run python tests/test_auth_simple.py
uv run python tests/test_api.py
uv run python tests/demo.py
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

### Lỗi Email Confirmation
```
Email confirmation required. Please check your email and confirm your account.
```
**Giải pháp**: Disable email confirmation trong Supabase Auth settings

### Lỗi RLS
```
Registration failed: {'message': 'new row violates row-level security policy for table "user_profiles"', 'code': '42501'}
```
**Giải pháp**: Chạy `sql/fix_rls_policies.sql`

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