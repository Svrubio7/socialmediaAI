"""
Application configuration using Pydantic Settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,https://social-media-ai-frontend.onrender.com"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=[str(BASE_DIR / ".env"), ".env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "Social Media AI SaaS"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"  # Must be 32 bytes for AES-256

    # CORS: comma-separated env (e.g. CORS_ORIGINS=https://app.example.com,...) or default list
    CORS_ORIGINS: str = DEFAULT_CORS_ORIGINS
    CORS_ORIGIN_REGEX: str = r"^https://.*\.vercel\.app$"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into list (stripped, non-empty)."""
        origins = [o.strip() for o in (self.CORS_ORIGINS or "").split(",") if o.strip()]
        if origins:
            return origins
        return [o.strip() for o in DEFAULT_CORS_ORIGINS.split(",") if o.strip()]

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/socialmediaai"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # File storage: "local" or "supabase"
    # With supabase, one bucket holds videos/, thumbnails/, editor/outputs/, branding/
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "temp/storage"
    STORAGE_PUBLIC_BASE_URL: str = ""
    SUPABASE_STORAGE_BUCKET: str = "videos"
    SUPABASE_STORAGE_PRIVATE: bool = True
    SUPABASE_STORAGE_SIGNED_URL_TTL: int = 3600

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Editor integration
    EDITOR_ENGINE_DEFAULT: str = "legacy"
    EDITOR_ELEVO_ENABLED: bool = True
    EDITOR_API_DIAGNOSTICS: bool = False
    EDITOR_SIGNED_UPLOAD_RATE_LIMIT: int = 30
    EDITOR_SIGNED_UPLOAD_RATE_WINDOW_SEC: int = 60

    # AI APIs
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Gemini Model Configuration
    GEMINI_MODEL: str = "gemini-2.0-flash"  # Upgraded from gemini-1.5-pro
    GEMINI_VISION_MODEL: str = "gemini-2.0-flash"  # For video/image analysis
    
    # Video Analysis Settings
    FRAME_EXTRACTION_FPS: float = 5.0  # 5 fps = 0.2s intervals
    FRAME_EXTRACTION_INTERVAL_MS: int = 200  # 200ms between frames
    AUDIO_SAMPLE_RATE: int = 16000  # 16kHz for audio analysis
    MAX_VIDEO_DURATION_SECONDS: int = 300  # 5 minutes max for analysis
    MAX_FRAMES_PER_ANALYSIS: int = 1500  # 5 minutes * 5fps = 1500 frames
    TEMP_PROCESSING_DIR: str = "temp/processing"

    # OAuth - Instagram
    INSTAGRAM_CLIENT_ID: str = ""
    INSTAGRAM_CLIENT_SECRET: str = ""

    # OAuth - TikTok
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""

    # OAuth - YouTube
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""

    # OAuth - Facebook
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""

    # Server
    PORT: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
