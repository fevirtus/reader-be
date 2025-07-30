from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .auth import UserProfileResponse


class OAuthURLResponse(BaseModel):
    auth_url: str
    provider: str = "google"


class OAuthCallbackResponse(BaseModel):
    session_token: str
    expires_at: datetime
    user: UserProfileResponse
    is_new_user: bool
    provider: str = "google"


class OAuthTokenResponse(BaseModel):
    token: str
    provider: str = "google"


class OAuthVerifyResponse(BaseModel):
    valid: bool
    user_info: Optional[dict] = None
    error: Optional[str] = None 