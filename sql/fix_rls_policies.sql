-- Fix RLS policies cho việc đăng ký user
-- Chạy file này trong Supabase SQL Editor sau khi đã chạy setup_supabase.sql

-- Xóa policy cũ cho user_profiles
DROP POLICY IF EXISTS "Users can insert their own profile" ON user_profiles;
DROP POLICY IF EXISTS "Allow registration insert" ON user_profiles;

-- Tạo policy mới cho phép insert user profile khi đăng ký
CREATE POLICY "Allow registration insert" ON user_profiles
    FOR INSERT WITH CHECK (true);

-- Tạo policy cho phép user xem và update profile của mình
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

-- Fix policy cho user_sessions
DROP POLICY IF EXISTS "Users can create their own sessions" ON user_sessions;

CREATE POLICY "Allow session creation" ON user_sessions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own sessions" ON user_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- Fix policy cho reading_progress
DROP POLICY IF EXISTS "Users can insert their own reading progress" ON reading_progress;

CREATE POLICY "Allow reading progress insert" ON reading_progress
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own reading progress" ON reading_progress
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own reading progress" ON reading_progress
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own reading progress" ON reading_progress
    FOR DELETE USING (auth.uid() = user_id);

-- Fix policy cho bookshelf
DROP POLICY IF EXISTS "Users can add to their own bookshelf" ON bookshelf;

CREATE POLICY "Allow bookshelf insert" ON bookshelf
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can view their own bookshelf" ON bookshelf
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can remove from their own bookshelf" ON bookshelf
    FOR DELETE USING (auth.uid() = user_id); 