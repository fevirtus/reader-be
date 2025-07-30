# 🔐 Google OAuth Frontend Setup Guide

## 📋 Cập nhật Google OAuth Console cho Frontend

### 1. **Cập nhật Authorized Redirect URIs**

Đăng nhập vào [Google Cloud Console](https://console.cloud.google.com/) và cập nhật OAuth 2.0 credentials:

#### Bước 1: Vào OAuth Credentials
1. Truy cập **APIs & Services** > **Credentials**
2. Click vào OAuth 2.0 Client ID hiện có
3. Click **Edit**

#### Bước 2: Cập nhật Redirect URIs
Thêm các redirect URI sau vào **Authorized redirect URIs**:

```
http://localhost:8000/api/v1/oauth/google/callback
http://localhost:3000/auth/callback
https://yourdomain.com/api/v1/oauth/google/callback
https://yourdomain.com/auth/callback
```

#### Bước 3: Cập nhật Authorized JavaScript origins
Thêm các origins sau vào **Authorized JavaScript origins**:

```
http://localhost:3000
http://localhost:8000
https://yourdomain.com
```

### 2. **Cập nhật Environment Variables**

Cập nhật file `.env`:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/google/callback

# OAuth Settings
OAUTH_ENABLED=True
OAUTH_PROVIDERS=["google"]
```

### 3. **Frontend Integration**

Frontend code hiện tại đã tương thích với backend:

```typescript
// Đăng nhập với Google
const loginWithGoogle = async () => {
  const response = await fetch('http://localhost:8000/api/v1/oauth/google/auth')
  const data = await response.json()
  
  if (data.auth_url) {
    // Mở popup window
    const popup = window.open(data.auth_url, 'google-login', 'width=500,height=600')
  }
}

// Xử lý callback
const handleCallback = async (code: string) => {
  const response = await fetch(`http://localhost:8000/api/v1/oauth/google/callback?code=${code}`)
  const data = await response.json()
  
  if (data.session_token) {
    localStorage.setItem('session_token', data.session_token)
    // Redirect hoặc update UI
  }
}
```

### 4. **Backend Endpoints**

Backend đã được cập nhật để hỗ trợ:

#### OAuth Endpoints
- `GET /api/v1/oauth/google/auth?state=...` - Tạo OAuth URL
- `GET /api/v1/oauth/google/callback?code=...&state=...` - Xử lý callback
- `OPTIONS /api/v1/oauth/google/auth` - CORS preflight
- `OPTIONS /api/v1/oauth/google/callback` - CORS preflight

#### Response Format
```json
{
  "session_token": "abc123...",
  "expires_at": "2024-01-01T12:00:00Z",
  "user": {
    "id": "user-id",
    "username": "John Doe",
    "email": "john@example.com",
    "avatar_url": "https://...",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  },
  "is_new_user": true,
  "provider": "google"
}
```

### 5. **Testing**

#### Test Backend
```bash
# Test OAuth functionality
uv run python tests/test_oauth.py

# Test frontend compatibility
uv run python tests/test_oauth_frontend.py
```

#### Test Frontend Integration
1. Chạy backend: `uv run python main.py`
2. Chạy frontend: `npm run dev`
3. Test OAuth flow trong browser

### 6. **Production Setup**

#### Cập nhật Google Console cho Production
1. Thêm production domain vào **Authorized JavaScript origins**
2. Thêm production callback URLs vào **Authorized redirect URIs**
3. Cập nhật environment variables

#### Environment Variables cho Production
```env
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/google/callback
```

### 7. **Security Features**

#### ✅ Đã implement:
- State parameter để chống CSRF
- CORS headers cho popup windows
- Session token management
- Error handling
- User profile creation/update

#### 🔒 Security Best Practices:
- Sử dụng HTTPS trong production
- Validate state parameter
- Secure session token storage
- Rate limiting (có thể thêm sau)

### 8. **Troubleshooting**

#### Lỗi "Invalid redirect URI"
- Kiểm tra redirect URI trong Google Console
- Đảm bảo URI khớp với `GOOGLE_REDIRECT_URI`

#### Lỗi CORS
- Kiểm tra CORS headers
- Đảm bảo frontend domain được allow

#### Lỗi "User not allowed"
- Đã được fix trong backend
- Kiểm tra RLS policies trong Supabase

### 9. **Migration Checklist**

- [ ] Cập nhật Google OAuth Console
- [ ] Cập nhật environment variables
- [ ] Test backend endpoints
- [ ] Test frontend integration
- [ ] Test production setup
- [ ] Monitor OAuth success rates

## ✅ Kết quả

Backend đã được cập nhật để tương thích hoàn toàn với frontend hiện tại mà không cần thay đổi code frontend!

### 🎯 **Các thay đổi chính:**
1. ✅ Cập nhật redirect URI
2. ✅ Hỗ trợ state parameter
3. ✅ Thêm CORS OPTIONS endpoints
4. ✅ Cải thiện error handling
5. ✅ Fix user profile creation issues 