# 🔐 Google OAuth Setup Guide

## 📋 Cấu hình Google OAuth cho Reader Backend

### 1. **Tạo Google OAuth Credentials**

#### Bước 1: Tạo Google Cloud Project
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project có sẵn
3. Enable Google+ API và Google OAuth2 API

#### Bước 2: Tạo OAuth 2.0 Credentials
1. Vào **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Chọn **Web application**
4. Điền thông tin:
   - **Name**: Reader Backend OAuth
   - **Authorized JavaScript origins**: `http://localhost:3000`
   - **Authorized redirect URIs**: 
     - `http://localhost:8000/api/v1/oauth/google/callback`
     - `http://localhost:3000/auth/callback`

#### Bước 3: Lấy Credentials
- **Client ID**: Copy từ Google Console
- **Client Secret**: Copy từ Google Console

### 2. **Cấu hình Environment Variables**

Thêm vào file `.env`:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/google/callback

# OAuth Settings
OAUTH_ENABLED=True
OAUTH_PROVIDERS=["google"]
```

### 3. **Install Dependencies**

```bash
# Install Google OAuth dependencies
uv sync
```

### 4. **Test OAuth Setup**

```bash
# Test OAuth functionality
uv run python tests/test_oauth.py
```

## 🔄 OAuth Flow

### 1. **Frontend Integration**

#### Bước 1: Lấy OAuth URL
```javascript
// Lấy Google OAuth URL
const getGoogleAuthUrl = async () => {
  const response = await fetch('/api/v1/oauth/google/auth');
  const data = await response.json();
  return data.auth_url;
};

// Redirect user đến Google
const loginWithGoogle = async () => {
  const authUrl = await getGoogleAuthUrl();
  window.location.href = authUrl;
};
```

#### Bước 2: Handle Callback
```javascript
// Trong callback page
const handleCallback = async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  
  if (code) {
    const response = await fetch(`/api/v1/oauth/google/callback?code=${code}`);
    const data = await response.json();
    
    // Lưu session token
    localStorage.setItem('session_token', data.session_token);
    
    // Redirect về dashboard
    window.location.href = '/dashboard';
  }
};
```

### 2. **Backend Flow**

1. **User clicks "Login with Google"**
2. **Frontend calls** `GET /api/v1/oauth/google/auth`
3. **Backend returns** Google OAuth URL
4. **User redirected to Google** for authentication
5. **Google redirects back** with authorization code
6. **Backend processes code** and creates/updates user
7. **Backend returns** session token
8. **Frontend stores** session token for future requests

## 📚 API Endpoints

### OAuth Endpoints

- `GET /api/v1/oauth/providers` - Lấy danh sách OAuth providers
- `GET /api/v1/oauth/google/auth` - Tạo Google OAuth URL
- `GET /api/v1/oauth/google/callback` - Xử lý Google OAuth callback
- `GET /api/v1/oauth/google/callback/redirect` - Callback với redirect về frontend
- `POST /api/v1/oauth/google/verify` - Verify Google ID token

### Response Examples

#### Google OAuth URL
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "provider": "google"
}
```

#### OAuth Callback
```json
{
  "session_token": "abc123...",
  "expires_at": "2024-01-01T12:00:00Z",
  "user": {
    "id": "user-id",
    "username": "John Doe",
    "email": "john@example.com",
    "avatar_url": "https://...",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "is_new_user": true,
  "provider": "google"
}
```

## 🔒 Security Features

### 1. **Token Verification**
- Verify Google ID tokens
- Validate token expiration
- Check token audience

### 2. **User Management**
- Auto-create users from Google profile
- Link existing users by email
- Handle duplicate accounts

### 3. **Session Management**
- Create secure session tokens
- 7-day session expiration
- Automatic session cleanup

## 🚨 Troubleshooting

### Lỗi "Invalid redirect URI"
**Giải pháp:**
1. Kiểm tra redirect URI trong Google Console
2. Đảm bảo URI khớp với `GOOGLE_REDIRECT_URI`
3. Thêm domain vào authorized origins

### Lỗi "Client ID not found"
**Giải pháp:**
1. Kiểm tra `GOOGLE_CLIENT_ID` trong `.env`
2. Đảm bảo OAuth credentials đã được tạo
3. Enable Google+ API trong Google Console

### Lỗi "Invalid authorization code"
**Giải pháp:**
1. Kiểm tra code không bị sử dụng 2 lần
2. Đảm bảo code chưa hết hạn
3. Verify redirect URI khớp với authorization request

## 🎯 Benefits

### 1. **User Experience**
- ✅ Không cần nhớ password
- ✅ One-click login
- ✅ Auto-fill profile information
- ✅ Secure authentication

### 2. **Security**
- ✅ No password storage
- ✅ Google's security standards
- ✅ Token-based authentication
- ✅ Automatic session management

### 3. **Development**
- ✅ Reduced registration friction
- ✅ Higher conversion rates
- ✅ Better user retention
- ✅ Simplified user management

## 📊 Production Considerations

### 1. **Domain Configuration**
- Update redirect URIs for production domain
- Configure authorized origins
- Set up SSL certificates

### 2. **Environment Variables**
```env
# Production
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/v1/oauth/google/callback
OAUTH_ENABLED=True
```

### 3. **Monitoring**
- Monitor OAuth success rates
- Track user registration sources
- Log authentication events

## ✅ Checklist

- [ ] Google Cloud Project created
- [ ] OAuth 2.0 credentials configured
- [ ] Redirect URIs added
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] OAuth endpoints tested
- [ ] Frontend integration completed
- [ ] Production domain configured 