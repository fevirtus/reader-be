# 🔐 OAuth API Endpoints

## 📋 **Overview**

**Base URL:** `http://localhost:8000/api/v1/oauth`

## 🔧 **Endpoints**

### **1. Get OAuth URL**

```http
GET /google/auth
```

**Description:** Lấy Google OAuth URL để redirect user

**Response (200):**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "provider": "google"
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/oauth/google/auth
```

---

### **2. OAuth Callback**

```http
GET /google/callback
```

**Description:** Xử lý Google OAuth callback và redirect về frontend

**Query Parameters:**
- `code` (required): Authorization code từ Google
- `state` (optional): State parameter cho security

**Response:** Redirect to frontend with session token

**Example:**
```bash
# Google sẽ redirect đến endpoint này
http://localhost:8000/api/v1/oauth/google/callback?code=4/0AVMBsJgOSM0qa1PG-KI1_xg3hvlkKgB-HUnrNn1ivv9G8sdZsM-l-E7hGaHIB3tbhEY4Qw&state=g0RahLW4tbQT3nzdQQ193zwGxUAmLc
```

---

### **3. Frontend Configuration**

```http
GET /frontend-config
```

**Description:** Lấy cấu hình cho frontend

**Response (200):**
```json
{
  "frontend_redirect_uri": "http://localhost:3000/callback",
  "oauth_enabled": true,
  "providers": ["google"]
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/oauth/frontend-config
```

---

### **4. Available Providers**

```http
GET /providers
```

**Description:** Lấy danh sách OAuth providers có sẵn

**Response (200):**
```json
{
  "providers": ["google"]
}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/oauth/providers
```

## 🚀 **Frontend Integration**

### **1. OAuth Login Flow**

```typescript
const loginWithGoogle = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/oauth/google/auth')
    const data = await response.json()
    
    if (data.auth_url) {
      window.location.href = data.auth_url
    }
  } catch (error) {
    console.error('OAuth login error:', error)
  }
}
```

### **2. Handle Callback**

```typescript
const handleCallback = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const sessionToken = urlParams.get('session_token')
  const isNewUser = urlParams.get('is_new_user')
  const error = urlParams.get('error')
  
  if (error) {
    console.error('OAuth error:', error)
    return
  }
  
  if (sessionToken) {
    localStorage.setItem('session_token', sessionToken)
    localStorage.setItem('is_new_user', isNewUser || 'false')
    window.location.href = '/dashboard'
  }
}
```

### **3. Get Frontend Config**

```typescript
const getOAuthConfig = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/oauth/frontend-config')
    const config = await response.json()
    return config
  } catch (error) {
    console.error('Error getting OAuth config:', error)
  }
}
```

## 📊 **Error Codes**

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request (Invalid parameters) |
| 401 | Unauthorized (OAuth error) |
| 500 | Internal Server Error |

## 🔧 **Configuration**

### **Environment Variables**
```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/oauth/google/callback
FRONTEND_REDIRECT_URI=http://localhost:3000/callback
OAUTH_ENABLED=True
OAUTH_PROVIDERS=["google"]
```

### **Google Console Setup**
1. Create Google Cloud Project
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs:
   - `http://localhost:8000/api/v1/oauth/google/callback`
   - `http://localhost:3000/callback`

## 🎯 **Features**

### ✅ **Security**
- State parameter for CSRF protection
- Secure session token generation
- Proper error handling

### ✅ **User Experience**
- One-click Google login
- Automatic profile creation
- Seamless redirect flow

### ✅ **Development**
- RESTful API design
- Clear error messages
- Frontend integration ready 