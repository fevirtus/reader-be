-- Setup database schema cho Reader Backend trên Supabase

-- Tạo bảng user_profiles (sử dụng Supabase Auth)
-- Users sẽ được tạo tự động bởi Supabase Auth
-- Chúng ta chỉ cần tạo profile table để lưu thông tin bổ sung
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    avatar_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tạo bảng novels
CREATE TABLE IF NOT EXISTS novels (
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

-- Tạo bảng chapters
CREATE TABLE IF NOT EXISTS chapters (
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

-- Tạo bảng reading progress (tiến độ đọc)
CREATE TABLE IF NOT EXISTS reading_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    novel_id BIGINT REFERENCES novels(id) ON DELETE CASCADE,
    chapter_id BIGINT REFERENCES chapters(id) ON DELETE CASCADE,
    chapter_number DECIMAL(10,2) NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, novel_id)
);

-- Tạo bảng bookshelf (tủ sách)
CREATE TABLE IF NOT EXISTS bookshelf (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    novel_id BIGINT REFERENCES novels(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, novel_id)
);

-- Tạo bảng user sessions (để quản lý session 7 ngày)
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tạo indexes cho performance
CREATE INDEX IF NOT EXISTS idx_novels_title ON novels(title);
CREATE INDEX IF NOT EXISTS idx_novels_author ON novels(author);
CREATE INDEX IF NOT EXISTS idx_novels_status ON novels(status);
CREATE INDEX IF NOT EXISTS idx_novels_created_at ON novels(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chapters_novel_id ON chapters(novel_id);
CREATE INDEX IF NOT EXISTS idx_chapters_chapter_number ON chapters(chapter_number);
CREATE INDEX IF NOT EXISTS idx_chapters_novel_chapter ON chapters(novel_id, chapter_number);

CREATE INDEX IF NOT EXISTS idx_reading_progress_user_id ON reading_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_reading_progress_novel_id ON reading_progress(novel_id);
CREATE INDEX IF NOT EXISTS idx_reading_progress_user_novel ON reading_progress(user_id, novel_id);

CREATE INDEX IF NOT EXISTS idx_bookshelf_user_id ON bookshelf(user_id);
CREATE INDEX IF NOT EXISTS idx_bookshelf_novel_id ON bookshelf(novel_id);
CREATE INDEX IF NOT EXISTS idx_bookshelf_user_novel ON bookshelf(user_id, novel_id);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

-- Tạo function để tăng lượt xem novel
CREATE OR REPLACE FUNCTION increment_novel_views(novel_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE novels SET views = views + 1 WHERE id = novel_id;
END;
$$ LANGUAGE plpgsql;

-- Tạo function để tăng lượt xem chapter
CREATE OR REPLACE FUNCTION increment_chapter_views(chapter_id BIGINT)
RETURNS VOID AS $$
BEGIN
    UPDATE chapters SET views = views + 1 WHERE id = chapter_id;
END;
$$ LANGUAGE plpgsql;

-- Tạo function để cập nhật reading progress
CREATE OR REPLACE FUNCTION update_reading_progress(
    p_user_id UUID,
    p_novel_id BIGINT,
    p_chapter_id BIGINT,
    p_chapter_number DECIMAL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO reading_progress (user_id, novel_id, chapter_id, chapter_number)
    VALUES (p_user_id, p_novel_id, p_chapter_id, p_chapter_number)
    ON CONFLICT (user_id, novel_id)
    DO UPDATE SET
        chapter_id = EXCLUDED.chapter_id,
        chapter_number = EXCLUDED.chapter_number,
        read_at = NOW(),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Tạo function để cleanup expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS VOID AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Tạo function để auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tạo triggers cho tất cả tables
CREATE TRIGGER update_novels_updated_at 
    BEFORE UPDATE ON novels 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chapters_updated_at 
    BEFORE UPDATE ON chapters 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reading_progress_updated_at 
    BEFORE UPDATE ON reading_progress 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_sessions_updated_at 
    BEFORE UPDATE ON user_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Tạo RLS (Row Level Security) policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE novels ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE reading_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookshelf ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Policy cho user_profiles - cho phép insert khi đăng ký
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Policy đặc biệt cho việc đăng ký - cho phép insert profile cho user mới
CREATE POLICY "Allow registration insert" ON user_profiles
    FOR INSERT WITH CHECK (true);

-- Policy cho novels - public read, authenticated write
CREATE POLICY "Allow public read access to novels" ON novels
    FOR SELECT USING (true);

CREATE POLICY "Allow authenticated users to create novels" ON novels
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update novels" ON novels
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to delete novels" ON novels
    FOR DELETE USING (auth.role() = 'authenticated');

-- Policy cho chapters - public read, authenticated write
CREATE POLICY "Allow public read access to chapters" ON chapters
    FOR SELECT USING (true);

CREATE POLICY "Allow authenticated users to create chapters" ON chapters
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to update chapters" ON chapters
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Allow authenticated users to delete chapters" ON chapters
    FOR DELETE USING (auth.role() = 'authenticated');

-- Policy cho reading_progress - users can only access their own
CREATE POLICY "Users can view their own reading progress" ON reading_progress
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own reading progress" ON reading_progress
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own reading progress" ON reading_progress
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own reading progress" ON reading_progress
    FOR DELETE USING (auth.uid() = user_id);

-- Policy cho bookshelf - users can only access their own
CREATE POLICY "Users can view their own bookshelf" ON bookshelf
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can add to their own bookshelf" ON bookshelf
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can remove from their own bookshelf" ON bookshelf
    FOR DELETE USING (auth.uid() = user_id);

-- Policy cho user_sessions - users can only access their own
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own sessions" ON user_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own sessions" ON user_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Insert sample data (optional)
INSERT INTO novels (title, author, description, status) VALUES
('Tu Tiên Giới', 'Tác giả A', 'Truyện tu tiên đỉnh cao', 'ongoing'),
('Võ Đế Trọng Sinh', 'Tác giả B', 'Truyện võ hiệp trọng sinh', 'completed'),
('Thành Thần Chi Lộ', 'Tác giả C', 'Truyện thành thần', 'ongoing')
ON CONFLICT DO NOTHING; 