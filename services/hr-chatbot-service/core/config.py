"""
Configuration Management
Loads and validates environment variables
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
from typing import Optional, Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # LLM Provider Configuration
    llm_provider: Literal["openai", "azure", "anthropic", "google", "ollama"] = Field(
        default="openai", env="LLM_PROVIDER"
    )

    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(
        default=None, env="OPENAI_BASE_URL"
    )
    openai_organization: Optional[str] = Field(
        default=None, env="OPENAI_ORGANIZATION"
    )

    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = Field(
        default=None, env="AZURE_OPENAI_API_KEY"
    )
    azure_openai_endpoint: Optional[str] = Field(
        default=None, env="AZURE_OPENAI_ENDPOINT"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview", env="AZURE_OPENAI_API_VERSION"
    )
    azure_openai_deployment_name: Optional[str] = Field(
        default=None, env="AZURE_OPENAI_DEPLOYMENT_NAME"
    )
    azure_openai_embedding_deployment_name: Optional[str] = Field(
        default=None, env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    )

    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(
        default=None, env="ANTHROPIC_API_KEY"
    )
    anthropic_base_url: Optional[str] = Field(
        default=None, env="ANTHROPIC_BASE_URL"
    )

    # Google Configuration
    google_api_key: Optional[str] = Field(
        default=None, env="GOOGLE_API_KEY"
    )
    google_project_id: Optional[str] = Field(
        default=None, env="GOOGLE_PROJECT_ID"
    )
    google_location: str = Field(
        default="us-central1", env="GOOGLE_LOCATION"
    )

    # Ollama Configuration
    ollama_base_url: str = Field(
        default="http://localhost:11434", env="OLLAMA_BASE_URL"
    )

    # Embedding Configuration
    embedding_provider: Literal["openai", "azure", "anthropic", "google", "ollama"] = Field(
        default="openai", env="EMBEDDING_PROVIDER"
    )

    embedding_model: str = Field(
        default="text-embedding-3-small", env="EMBEDDING_MODEL"
    )
    embedding_dimensions: Optional[int] = Field(
        default=1536, env="EMBEDDING_DIMENSIONS"
    )
    
    # LLM Model Configuration
    llm_model: str = Field(default="gpt-4o-mini", env="LLM_MODEL")

    llm_temperature: float = Field(
        default=0.0, ge=0.0, le=2.0, env="LLM_TEMPERATURE"
    )

    # Milvus Configuration
    milvus_uri: str = Field(default="http://localhost:19530", env="MILVUS_URI")
    milvus_collection_name: str = Field(default="hr_policies", env="MILVUS_COLLECTION_NAME")
    milvus_token: Optional[str] = Field(default=None, env="MILVUS_TOKEN")

    # HRMS API Configuration
    hrms_api_url: str = Field(
        default="http://localhost:8001", env="HRMS_API_URL"
    )
    hrms_api_timeout: int = Field(default=30, ge=1, le=300, env="HRMS_API_TIMEOUT")

    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: Literal["HS256", "HS384", "HS512", "RS256"] = Field(
        default="HS256", env="JWT_ALGORITHM"
    )
    access_token_expire_minutes: int = Field(
        default=1440, ge=1, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/chatbot.db", env="DATABASE_URL")

    # Application Configuration
    app_name: str = Field(default="HR Chatbot Service", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info", env="LOG_LEVEL"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, ge=1, le=65535, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    

    @field_validator("milvus_uri", "hrms_api_url", "database_url")
    @classmethod
    def validate_urls(cls, v: str) -> str:
        """Validate that URLs are properly formatted"""
        if not v:
            raise ValueError("URL cannot be empty")
        return v
    
    @model_validator(mode="after")
    def validate_provider_config(self):
        """Validate provider-specific configuration and models"""

        # Validate LLM provider API keys and required fields
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when llm_provider is 'openai'"
            )
        elif self.llm_provider == "azure":
            if not self.azure_openai_api_key:
                raise ValueError(
                    "AZURE_OPENAI_API_KEY is required when llm_provider is 'azure'"
                )
            if not self.azure_openai_endpoint:
                raise ValueError(
                    "AZURE_OPENAI_ENDPOINT is required when llm_provider is 'azure'"
                )
            if not self.azure_openai_deployment_name:
                raise ValueError(
                    "AZURE_OPENAI_DEPLOYMENT_NAME is required when "
                    "llm_provider is 'azure'"
                )
        elif self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when llm_provider is 'anthropic'"
            )
        elif self.llm_provider == "google" and not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required when llm_provider is 'google'"
            )
        elif self.llm_provider == "ollama":
            # Ollama does not require an API key
            pass

        # Validate embedding provider API keys
        if self.embedding_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when embedding_provider is 'openai'"
            )
        elif self.embedding_provider == "azure":
            if not self.azure_openai_api_key:
                raise ValueError(
                    "AZURE_OPENAI_API_KEY is required when "
                    "embedding_provider is 'azure'"
                )
            if not self.azure_openai_endpoint:
                raise ValueError(
                    "AZURE_OPENAI_ENDPOINT is required when "
                    "embedding_provider is 'azure'"
                )
            if not self.azure_openai_embedding_deployment_name:
                raise ValueError(
                    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME is required when "
                    "embedding_provider is 'azure'"
                )
        elif self.embedding_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required when "
                "embedding_provider is 'anthropic'"
            )
        elif self.embedding_provider == "google" and not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY is required when embedding_provider is 'google'"
            )
        elif self.embedding_provider == "ollama":
            # Ollama does not require an API key
            pass

        # Validate models based on provider
        self._validate_llm_model()
        self._validate_embedding_model()

        return self
    
    def _validate_llm_model(self):
        """Validate LLM model based on provider"""
        openai_models = {
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4",
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4-0125-preview",
            "gpt-4-1106-preview", "gpt-4-turbo-preview"
        }
        anthropic_models = {
            "claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229", "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307", "claude-2.1", "claude-2.0",
            "claude-instant-1.2"
        }
        google_models = {
            "gemini-pro", "gemini-pro-vision", "gemini-1.5-pro",
            "gemini-1.5-flash", "gemini-1.0-pro", "gemini-2.5-flash"
        }

        if self.llm_provider == "openai":
            if self.llm_model not in openai_models:
                raise ValueError(
                    f"Invalid OpenAI model '{self.llm_model}'. "
                    f"Allowed: {', '.join(sorted(openai_models))}"
                )
        elif self.llm_provider == "anthropic":
            if self.llm_model not in anthropic_models:
                raise ValueError(
                    f"Invalid Anthropic model '{self.llm_model}'. "
                    f"Allowed: {', '.join(sorted(anthropic_models))}"
                )
        elif self.llm_provider == "google":
            if self.llm_model not in google_models:
                raise ValueError(
                    f"Invalid Google model '{self.llm_model}'. "
                    f"Allowed: {', '.join(sorted(google_models))}"
                )
        # Azure and Ollama use deployment/custom names, skip validation
    
    def _validate_embedding_model(self):
        """Validate embedding model based on provider"""
        openai_embedding_models = {
            "text-embedding-3-small", "text-embedding-3-large",
            "text-embedding-ada-002"
        }
        anthropic_embedding_models = {
            "voyage-2", "voyage-lite-02-instruct"
        }
        google_embedding_models = {
            "embedding-001", "text-embedding-004", "embedding-gecko-001"
        }
        ollama_embedding_models = {
            "nomic-embed-text", "mxbai-embed-large", "all-minilm"
        }

        if self.embedding_provider == "openai":
            if self.embedding_model not in openai_embedding_models:
                raise ValueError(
                    f"Invalid OpenAI embedding model '{self.embedding_model}'. "
                    f"Allowed: {', '.join(sorted(openai_embedding_models))}"
                )
        elif self.embedding_provider == "anthropic":
            # Anthropic uses Voyage AI for embeddings via langchain-anthropic
            if self.embedding_model not in anthropic_embedding_models:
                raise ValueError(
                    f"Invalid Anthropic/Voyage embedding model "
                    f"'{self.embedding_model}'. "
                    f"Allowed: {', '.join(sorted(anthropic_embedding_models))}"
                )
        elif self.embedding_provider == "google":
            if self.embedding_model not in google_embedding_models:
                raise ValueError(
                    f"Invalid Google embedding model '{self.embedding_model}'. "
                    f"Allowed: {', '.join(sorted(google_embedding_models))}"
                )
        elif self.embedding_provider == "ollama":
            # Ollama models are flexible, just check if it's a common one
            # or allow any string for custom models
            if (self.embedding_model not in ollama_embedding_models and
                not self.embedding_model):
                raise ValueError(
                    f"Embedding model must be specified for Ollama. "
                    f"Common models: {', '.join(sorted(ollama_embedding_models))}"
                )
        # Azure uses deployment names, skip validation

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
