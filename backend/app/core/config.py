from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/email.db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Default Email Server Settings (one.com)
    DEFAULT_IMAP_HOST: str = "imap.one.com"
    DEFAULT_IMAP_PORT: int = 993
    DEFAULT_IMAP_SSL: bool = True
    
    DEFAULT_POP3_HOST: str = "pop.one.com"
    DEFAULT_POP3_PORT: int = 995
    DEFAULT_POP3_SSL: bool = True
    
    DEFAULT_SMTP_HOST: str = "send.one.com"
    DEFAULT_SMTP_PORT: int = 465
    DEFAULT_SMTP_SSL: bool = True
    
    # File Upload
    MAX_FILE_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    
    # Email Configuration
    MAX_EMAILS_PER_FETCH: int = 50
    EMAIL_CACHE_TIMEOUT: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
