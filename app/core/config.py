from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # App
    DEBUG: bool = False
    PROJECT_NAME: str = "HireAI"
    VERSION: str = "1.0.0"

    GROQ_API_KEY: str
    
    class Config:
        env_file = Path(ROOT_DIR, ".env")


try:
    settings = Settings()
    print(f"✅ Environment loaded successfully")
    print(f"📁 Looking for .env file at: {Path(ROOT_DIR, ".env")}")
    print(f"🔗 Database URL: {settings.DATABASE_URL}")
except Exception as e:
    print(f"❌ Error loading environment: {e}")
    settings = Settings()