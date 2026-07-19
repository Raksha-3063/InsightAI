import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "insightai"
    JWT_SECRET: str = "supersecretjwtkeyinsightai2026!!!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    UPLOAD_DIR: str = "backend/app/uploads"
    
    # Celery & Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_ENABLED: bool = False  # Set to True in environment/docker to enable background worker

    # AI Copilot Settings
    GEMINI_API_KEY: str = "mock_key"
    AI_PROVIDER: str = "mock"  # Set to "gemini" in .env to use Google Generative AI
    AI_MODEL: str = "gemini-2.5-flash"
    AI_TEMPERATURE: float = 0.2
    AI_MAX_TOKENS: int = 2048
    AI_RATE_LIMIT_PER_MINUTE: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
