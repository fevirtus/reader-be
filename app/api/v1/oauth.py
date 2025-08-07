from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from app.schemas.oauth import (
    OAuthURLResponse, OAuthCallbackResponse, OAuthVerifyResponse
)
from app.services.oauth_service import OAuthService

router = APIRouter()

@router.get("/google/auth", response_model=OAuthURLResponse)
async def google_auth(state: str = Query(None, description="State parameter for security")):
    """Tạo Google OAuth URL"""
    try:
        oauth_service = OAuthService()
        auth_url = oauth_service.get_google_auth_url(state)
        return OAuthURLResponse(auth_url=auth_url, provider="google")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.options("/google/auth")
async def google_auth_options():
    """Handle CORS preflight for Google OAuth"""
    return {}

@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(None, description="State parameter for security")
):
    """Xử lý Google OAuth callback - redirect về frontend"""
    try:
        from app.core.config import settings
        
        oauth_service = OAuthService()
        result = await oauth_service.handle_google_callback(code)
        
        # Redirect về frontend với session token
        print(f"🔗 Redirecting to frontend with session token: {result['session_token']}")
        frontend_url = f"{settings.frontend_redirect_uri}?session_token={result['session_token']}&is_new_user={result['is_new_user']}"
        print(f"🔗 Frontend URL: {frontend_url}")
        
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        # Redirect về frontend với error
        error_url = f"{settings.frontend_redirect_uri}?error={str(e)}"
        return RedirectResponse(url=error_url)

@router.options("/google/callback")
async def google_callback_options():
    """Handle CORS preflight for Google OAuth callback"""
    return {}

@router.get("/google/callback/redirect")
async def google_callback_redirect(
    code: str = Query(..., description="Authorization code from Google"),
    redirect_uri: str = Query(None, description="Frontend redirect URI")
):
    """Xử lý Google OAuth callback với redirect về frontend"""
    try:
        from app.core.config import settings
        
        # Sử dụng config hoặc parameter
        frontend_uri = redirect_uri or settings.frontend_redirect_uri
        
        oauth_service = OAuthService()
        result = await oauth_service.handle_google_callback(code)
        
        # Tạo URL với session token để redirect về frontend
        frontend_url = f"{frontend_uri}?session_token={result['session_token']}&is_new_user={result['is_new_user']}"
        
        return RedirectResponse(url=frontend_url)
    except Exception as e:
        # Redirect về frontend với error
        frontend_uri = redirect_uri or settings.frontend_redirect_uri
        error_url = f"{frontend_uri}?error={str(e)}"
        return RedirectResponse(url=error_url)

@router.post("/google/verify", response_model=OAuthVerifyResponse)
async def verify_google_token(token: str = Query(..., description="Google ID token")):
    """Verify Google ID token"""
    try:
        oauth_service = OAuthService()
        user_info = oauth_service.verify_google_token(token)
        
        if user_info:
            return OAuthVerifyResponse(valid=True, user_info=user_info)
        else:
            return OAuthVerifyResponse(valid=False, error="Invalid token")
    except Exception as e:
        return OAuthVerifyResponse(valid=False, error=str(e))

@router.get("/providers")
async def get_oauth_providers():
    """Lấy danh sách OAuth providers được hỗ trợ"""
    from app.core.config import settings
    
    return {
        "providers": settings.oauth_providers,
        "enabled": settings.oauth_enabled
    }

@router.get("/frontend-config")
async def get_frontend_config():
    """Lấy cấu hình cho frontend"""
    from app.core.config import settings
    
    return {
        "frontend_redirect_uri": settings.frontend_redirect_uri,
        "oauth_enabled": settings.oauth_enabled,
        "providers": settings.oauth_providers
    } 