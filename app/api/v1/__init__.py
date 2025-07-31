from fastapi import APIRouter
from .novels import router as novels_router
from .chapters import router as chapters_router
from .auth import router as auth_router
from .user import router as user_router
from .reading import router as reading_router
from .oauth import router as oauth_router

api_router = APIRouter()

api_router.include_router(novels_router, prefix="/novels", tags=["novels"])
api_router.include_router(chapters_router, prefix="/chapters", tags=["chapters"])
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(reading_router, prefix="/reading", tags=["reading"])
api_router.include_router(oauth_router, prefix="/oauth", tags=["oauth"]) 