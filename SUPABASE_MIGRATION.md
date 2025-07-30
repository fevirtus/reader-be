# 🚀 Migration to Supabase

## ✅ Đã hoàn thành migration từ SQLite sang Supabase

### 🔄 Thay đổi chính

#### 1. **Database Layer**
- ❌ **Trước**: SQLAlchemy với SQLite local
- ✅ **Sau**: Supabase PostgreSQL với connection pooling

#### 2. **Service Layer**
- ❌ **Trước**: `NovelService(db: Session)`, `ChapterService(db: Session)`
- ✅ **Sau**: `NovelService()`, `ChapterService()` với Supabase client

#### 3. **API Layer**
- ❌ **Trước**: Cần `Depends(get_db)` cho database session
- ✅ **Sau**: Không cần database session, tự động connection

#### 4. **Configuration**
- ❌ **Trước**: `DATABASE_URL=sqlite:///./reader.db`
- ✅ **Sau**: Supabase environment variables

### 🗄️ Database Schema Changes

#### Supabase Tables
```sql
-- Novels table
CREATE TABLE novels (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    description TEXT,
    cover_image VARCHAR(500),
    status VARCHAR(50) DEFAULT 'ongoing',
    total_chapters INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chapters table
CREATE TABLE chapters (
    id BIGSERIAL PRIMARY KEY,
    novel_id BIGINT REFERENCES novels(id) ON DELETE CASCADE,
    chapter_number DECIMAL(10,2) NOT NULL,
    title VARCHAR(255),
    content_file VARCHAR(500) NOT NULL,
    word_count INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Supabase Functions
```sql
-- Increment novel views
CREATE FUNCTION increment_novel_views(novel_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE novels SET views = views + 1 WHERE id = novel_id;
END;
$$ LANGUAGE plpgsql;

-- Increment chapter views
CREATE FUNCTION increment_chapter_views(chapter_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE chapters SET views = views + 1 WHERE id = chapter_id;
END;
$$ LANGUAGE plpgsql;
```

### 🔧 Code Changes

#### 1. **SupabaseService** (New)
```python
class SupabaseService:
    def __init__(self):
        self.supabase = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
    
    def get_novels(self, skip: int = 0, limit: int = 100, search: Optional[str] = None):
        query = self.supabase.table('novels').select('*')
        if search:
            query = query.or_(f"title.ilike.%{search}%,author.ilike.%{search}%")
        return query.range(skip, skip + limit - 1).execute().data
```

#### 2. **Updated NovelService**
```python
class NovelService:
    def __init__(self):
        self.supabase_service = SupabaseService()
    
    def create_novel(self, novel_data: NovelCreate) -> dict:
        data = novel_data.dict()
        return self.supabase_service.create_novel(data)
```

#### 3. **Updated API Endpoints**
```python
@router.get("/", response_model=List[NovelResponse])
def get_novels(skip: int = Query(0), limit: int = Query(100)):
    service = NovelService()  # No db dependency
    return service.get_novels(skip, limit)
```

### 🐳 Docker Support

#### Dockerfile
```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
version: '3.8'
services:
  reader-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    volumes:
      - ./storage:/app/storage
```

### 🔒 Security Features

#### Row Level Security (RLS)
```sql
-- Enable RLS
ALTER TABLE novels ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;

-- Public read access
CREATE POLICY "Allow public read access to novels" ON novels
    FOR SELECT USING (true);

-- Authenticated write access
CREATE POLICY "Allow authenticated users to create novels" ON novels
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

### 📊 Performance Improvements

#### 1. **Connection Pooling**
- Supabase tự động quản lý connection pooling
- Không cần manual connection management

#### 2. **Indexes**
```sql
CREATE INDEX idx_novels_title ON novels(title);
CREATE INDEX idx_novels_author ON novels(author);
CREATE INDEX idx_chapters_novel_chapter ON chapters(novel_id, chapter_number);
```

#### 3. **Automatic Triggers**
```sql
-- Auto-update updated_at
CREATE TRIGGER update_novels_updated_at 
    BEFORE UPDATE ON novels 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

### 🚀 Deployment Options

#### 1. **Local Development**
```bash
uv run uvicorn main:app --reload
```

#### 2. **Docker Development**
```bash
docker-compose up --build
```

#### 3. **Production with Docker**
```bash
docker-compose up -d
```

#### 4. **Cloud Platforms**
- **Railway**: `railway up`
- **Heroku**: `heroku push heroku main`
- **Vercel**: Deploy with serverless functions

### 🧪 Testing

#### Test Supabase Connection
```bash
uv run python tests/test_supabase.py
```

#### Test API Endpoints
```bash
uv run python tests/test_api.py
```

#### Docker Test
```bash
docker-compose up -d
curl http://localhost:8000/health
```

### 📈 Benefits of Migration

#### 1. **Scalability**
- ✅ PostgreSQL với connection pooling
- ✅ Automatic scaling với Supabase
- ✅ Built-in caching và optimization

#### 2. **Security**
- ✅ Row Level Security (RLS)
- ✅ Built-in authentication
- ✅ Automatic backups

#### 3. **Development Experience**
- ✅ Real-time subscriptions
- ✅ Built-in API documentation
- ✅ Database dashboard

#### 4. **Production Ready**
- ✅ SSL/TLS support
- ✅ CDN integration
- ✅ Monitoring và analytics

### 🔄 Migration Steps

#### 1. **Setup Supabase**
1. Tạo project trên [supabase.com](https://supabase.com)
2. Lấy connection details
3. Chạy `sql/setup_supabase.sql` trong SQL Editor

#### 2. **Update Environment**
```bash
cp env.example .env
# Edit .env với Supabase credentials
```

#### 3. **Test Migration**
```bash
uv sync
uv run python tests/test_supabase.py
```

#### 4. **Deploy**
```bash
# Local
uv run uvicorn main:app --reload

# Docker
docker-compose up --build

# Production
docker-compose up -d
```

### 🎯 Kết quả

✅ **Database**: Migrated từ SQLite sang Supabase PostgreSQL  
✅ **API**: Tất cả endpoints hoạt động với Supabase  
✅ **Docker**: Full containerization support  
✅ **Security**: RLS và authentication ready  
✅ **Performance**: Connection pooling và indexing  
✅ **Scalability**: Cloud-ready architecture  

**Migration completed successfully! 🚀** 