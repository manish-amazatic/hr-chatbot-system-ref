"""
Configuration Management
Loads and validates environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    llm_model: str = Field(default="gpt-4o-mini", env="LLM_MODEL")
    openai_temperature: float = Field(default=0.0, env="OPENAI_TEMPERATURE")

    # Milvus Configuration
    milvus_uri: str = Field(default="http://localhost:19530", env="MILVUS_URI")
    milvus_collection_name: str = Field(default="hr_policies", env="MILVUS_COLLECTION_NAME")
    milvus_token: Optional[str] = Field(default=None, env="MILVUS_TOKEN")

    # HRMS API Configuration
    hrms_api_url: str = Field(default="http://localhost:8001", env="HRMS_API_URL")
    hrms_api_timeout: int = Field(default=30, env="HRMS_API_TIMEOUT")

    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/chatbot.db", env="DATABASE_URL")

    # Application Configuration
    app_name: str = Field(default="HR Chatbot Service", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="info", env="LOG_LEVEL")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Convenience accessor
settings = get_settings()
