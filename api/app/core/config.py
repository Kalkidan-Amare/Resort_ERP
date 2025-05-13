import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Kuriftu Hotel Booking System"
    PROJECT_VERSION: str = "1.0.0"
    
    # Configuration for application
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database configuration - direct URL for Supabase
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    TOKEN: str = os.getenv("TOKEN", "")
    ENDPOINT: str = os.getenv("ENDPOINT", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "")
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    
settings = Settings()
