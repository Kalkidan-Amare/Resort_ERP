import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Kuriftu Hotel Booking System"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database settings
    DB_NAME: str = os.getenv("DB_NAME", "kuriftu_hotel")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "358529")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Construct DATABASE_URL from individual components
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Debug mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
settings = Settings()
