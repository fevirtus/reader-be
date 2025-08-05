-- Script để thêm column role vào user_profiles
-- Chạy script này nếu column role chưa tồn tại

-- Thêm column role nếu chưa tồn tại
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

-- Cập nhật tất cả users hiện tại thành role 'user' nếu chưa có role
UPDATE user_profiles 
SET role = 'user' 
WHERE role IS NULL;

-- Tạo admin user đầu tiên (thay đổi user_id theo nhu cầu)
-- UPDATE user_profiles SET role = 'admin' WHERE id = 'your-user-id-here'; 