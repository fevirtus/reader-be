# 🚀 Frontend Redirect Guide

## 📋 Cách sử dụng OAuth redirect cho Frontend

### 1. **Cấu hình Backend**

Backend đã được cấu hình để redirect về `http://localhost:3000/callback`:

```python
# app/core/config.py
frontend_redirect_uri: str = "http://localhost:3000/callback"
```

### 2. **Frontend Integration**

#### A. Lấy cấu hình từ backend
```typescript
// Lấy cấu hình OAuth
const getOAuthConfig = async () => {
  const response = await fetch('http://localhost:8000/api/v1/oauth/frontend-config')
  const config = await response.json()
  
  return {
    frontendRedirectUri: config.frontend_redirect_uri, // http://localhost:3000/callback
    oauthEnabled: config.oauth_enabled,
    providers: config.providers
  }
}
```

#### B. Sử dụng redirect endpoint
```typescript
// Frontend có thể sử dụng redirect endpoint
const handleOAuthRedirect = async (code: string) => {
  // Redirect về backend, backend sẽ redirect về frontend
  window.location.href = `http://localhost:8000/api/v1/oauth/google/callback/redirect?code=${code}`
}
```

### 3. **OAuth Flow hoàn chỉnh**

#### Bước 1: Lấy OAuth URL
```typescript
const loginWithGoogle = async () => {
  const response = await fetch('http://localhost:8000/api/v1/oauth/google/auth')
  const data = await response.json()
  
  if (data.auth_url) {
    // Mở popup hoặc redirect
    window.location.href = data.auth_url
  }
}
```

#### Bước 2: Google redirect về backend
```
Google → http://localhost:8000/api/v1/oauth/google/callback/redirect?code=...
```

#### Bước 3: Backend redirect về frontend
```
Backend → http://localhost:3000/callback?session_token=...&is_new_user=...
```

#### Bước 4: Frontend xử lý callback
```typescript
// Trong trang /callback
const handleCallback = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const sessionToken = urlParams.get('session_token')
  const isNewUser = urlParams.get('is_new_user')
  const error = urlParams.get('error')
  
  if (sessionToken) {
    // Lưu session token
    localStorage.setItem('session_token', sessionToken)
    
    // Redirect về dashboard
    window.location.href = '/dashboard'
  } else if (error) {
    // Xử lý lỗi
    console.error('OAuth error:', error)
  }
}
```

### 4. **Frontend Callback Page**

Tạo trang `/callback` trong frontend:

```vue
<!-- pages/callback.vue -->
<template>
  <div class="callback-container">
    <div class="loading-spinner">
      <div class="spinner"></div>
      <p>Đang xử lý đăng nhập...</p>
    </div>
  </div>
</template>

<script setup>
onMounted(() => {
  handleCallback()
})

const handleCallback = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const sessionToken = urlParams.get('session_token')
  const isNewUser = urlParams.get('is_new_user')
  const error = urlParams.get('error')
  
  if (sessionToken) {
    // Lưu session token
    localStorage.setItem('session_token', sessionToken)
    
    // Hiển thị thông báo cho user mới
    if (isNewUser === 'true') {
      // Có thể hiển thị toast notification
      console.log('Chào mừng bạn đến với Reader!')
    }
    
    // Redirect về dashboard
    window.location.href = '/dashboard'
  } else if (error) {
    // Xử lý lỗi
    console.error('OAuth error:', error)
    // Redirect về login với error
    window.location.href = `/login?error=${encodeURIComponent(error)}`
  }
}
</script>

<style scoped>
.callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
```

### 5. **Backend Endpoints**

#### A. Frontend Config
```
GET /api/v1/oauth/frontend-config
Response: {
  "frontend_redirect_uri": "http://localhost:3000/callback",
  "oauth_enabled": true,
  "providers": ["google"]
}
```

#### B. OAuth Auth URL
```
GET /api/v1/oauth/google/auth?state=...
Response: {
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "provider": "google"
}
```

#### C. OAuth Callback Redirect
```
GET /api/v1/oauth/google/callback/redirect?code=...&redirect_uri=...
Redirect: http://localhost:3000/callback?session_token=...&is_new_user=...
```

### 6. **URL Parameters**

#### Success Response
```
http://localhost:3000/callback?session_token=abc123...&is_new_user=true
```

#### Error Response
```
http://localhost:3000/callback?error=Google%20OAuth%20callback%20failed
```

### 7. **Testing**

#### Test Frontend Config
```bash
curl http://localhost:8000/api/v1/oauth/frontend-config
```

#### Test Redirect (với mock code)
```bash
curl http://localhost:8000/api/v1/oauth/google/callback/redirect?code=mock_code
```

### 8. **Production Setup**

#### A. Cập nhật Google OAuth Console
Thêm redirect URI:
```
http://localhost:8000/api/v1/oauth/google/callback/redirect
```

#### B. Cập nhật Environment Variables
```env
FRONTEND_REDIRECT_URI=https://yourdomain.com/callback
```

### 9. **Security Features**

- ✅ State parameter support
- ✅ Error handling
- ✅ Session token management
- ✅ CORS support
- ✅ Rate limiting awareness

### 10. **Benefits**

- ✅ **Simple Integration**: Frontend chỉ cần redirect về backend
- ✅ **Automatic Handling**: Backend xử lý tất cả OAuth logic
- ✅ **Flexible**: Có thể thay đổi redirect URI qua config
- ✅ **Secure**: Session token được tạo và quản lý bởi backend
- ✅ **Error Handling**: Lỗi được truyền về frontend

## ✅ **Kết luận**

Backend đã được cấu hình để redirect về `http://localhost:3000/callback`. Frontend chỉ cần:

1. Tạo trang `/callback` để xử lý response
2. Sử dụng redirect endpoint của backend
3. Xử lý session token và error

Tất cả OAuth logic được xử lý bởi backend, frontend chỉ cần redirect và nhận kết quả! 