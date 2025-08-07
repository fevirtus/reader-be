from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Supabase Configuration
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./reader.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = True
    allowed_hosts: List[str] = ["*"]
    
    # File Storage
    storage_path: str = "./storage"
    
    # Google OAuth Configuration
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/oauth/google/callback"
    frontend_redirect_uri: str = "http://localhost:3000/callback"
    
    # OAuth Settings
    oauth_enabled: bool = True
    oauth_providers: List[str] = ["google"]

    class Config:
        env_file = ".env"


settings = Settings() 