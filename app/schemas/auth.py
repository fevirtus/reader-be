from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    username: str
    email: EmailStr
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileResponse


class SessionResponse(BaseModel):
    session_token: str
    expires_at: datetime
    user: UserProfileResponse 