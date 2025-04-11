from pydantic_settings import BaseSettings
from typing import List
import secrets

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "客服派单平台"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # 数据库配置

    DATABASE_URL: str = "sqlite://./data/db.sqlite3"

    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 