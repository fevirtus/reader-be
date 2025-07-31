from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.auth import SessionResponse
from app.services.auth_service import AuthService
from app.core.auth import get_current_user

router = APIRouter()

# Auth router giờ chỉ chứa các endpoint liên quan đến authentication
# User management đã được chuyển sang user.py 