"""
LLM Processor - Multi-Provider Factory Pattern + Singleton
Dynamically connects to different LLM providers (OpenAI, Azure, Anthropic, Google, Ollama)
"""
import threading
from typing import Optional, Any
import logging

from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from core.config import settings

logger = logging.getLogger(__name__)


class LLMProcessor:
    """
    Multi-Provider LLM Processor using Factory Pattern + Singleton

    Supports:
    - OpenAI (GPT-4, GPT-3.5, etc.)
    - Azure OpenAI
    - Anthropic (Claude 3.5, Claude 3 Opus/Sonnet/Haiku)
    - Google (Gemini Pro, Gemini 1.5)
    - Ollama (Local models: Llama 3, Mistral, etc.)

    This class ensures only one instance exists (Singleton)
    and provides a factory method to create different LLM instances.

    Usage:
        processor = LLMProcessor()
        llm = processor.get_llm()  # Uses settings from config
    """

    _instance: Optional['LLMProcessor'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'LLMProcessor':
        """
        Singleton pattern implementation
        Ensures only one instance of LLMProcessor exists
        """
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    logger.info("Creating new LLMProcessor instance (Singleton)")
                    cls._instance = super(LLMProcessor, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the processor (only once)"""
        if self._initialized:
            return

        self._cache = {}  # Cache for LLM instances
        self._initialized = True
        logger.info(
            f"LLMProcessor initialized with provider: {settings.llm_provider}"
        )

    def get_llm(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any
    ):
        """
        Factory method to get an LLM instance

        Args:
            provider: LLM provider (defaults to settings.llm_provider)
            model: Model name (defaults to settings.llm_model)
            temperature: Temperature parameter (defaults to settings.llm_temperature)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM instance from the specified provider

        Example:
            >>> processor = LLMProcessor()
            >>> llm = processor.get_llm()  # Uses settings
            >>> llm = processor.get_llm(model="gpt-4")  # Override model
            >>> response = llm.invoke("Hello!")
        """
        # Use defaults from settings if not provided
        provider = provider or settings.llm_provider
        model = model or settings.llm_model
        temperature = temperature if temperature is not None else settings.llm_temperature

        # Create cache key
        cache_key = f"{provider}_{model}_{temperature}"

        # Return cached instance if exists
        if cache_key in self._cache:
            logger.debug(f"Returning cached LLM: {cache_key}")
            return self._cache[cache_key]

        # Create new instance based on provider
        logger.info(f"Creating new LLM instance: {provider} - {model}")

        if provider == "openai":
            llm = self._create_openai_llm(model, temperature, **kwargs)
        elif provider == "azure":
            llm = self._create_azure_llm(model, temperature, **kwargs)
        elif provider == "anthropic":
            llm = self._create_anthropic_llm(model, temperature, **kwargs)
        elif provider == "google":
            llm = self._create_google_llm(model, temperature, **kwargs)
        elif provider == "ollama":
            llm = self._create_ollama_llm(model, temperature, **kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        # Cache the instance
        self._cache[cache_key] = llm
        return llm

    def _create_openai_llm(
        self,
        model: str,
        temperature: float,
        **kwargs: Any
    ) -> ChatOpenAI:
        """Create OpenAI LLM instance"""
        params = {
            "model": model,
            "temperature": temperature,
            "openai_api_key": settings.openai_api_key,
        }

        # Add optional parameters
        if settings.openai_base_url:
            params["base_url"] = settings.openai_base_url
        if settings.openai_organization:
            params["openai_organization"] = settings.openai_organization

        params.update(kwargs)
        return ChatOpenAI(**params)

    def _create_azure_llm(
        self,
        model: str,
        temperature: float,
        **kwargs: Any
    ) -> AzureChatOpenAI:
        """Create Azure OpenAI LLM instance"""
        params = {
            "deployment_name": settings.azure_openai_deployment_name or model,
            "temperature": temperature,
            "azure_endpoint": settings.azure_openai_endpoint,
            "api_key": settings.azure_openai_api_key,
            "api_version": settings.azure_openai_api_version,
        }

        params.update(kwargs)
        return AzureChatOpenAI(**params)

    def _create_anthropic_llm(
        self,
        model: str,
        temperature: float,
        **kwargs: Any
    ) -> ChatAnthropic:
        """Create Anthropic Claude LLM instance"""
        params = {
            "model": model,
            "temperature": temperature,
            "anthropic_api_key": settings.anthropic_api_key,
        }

        # Add optional parameters
        if settings.anthropic_base_url:
            params["base_url"] = settings.anthropic_base_url

        params.update(kwargs)
        return ChatAnthropic(**params)

    def _create_google_llm(
        self,
        model: str,
        temperature: float,
        **kwargs: Any
    ) -> ChatGoogleGenerativeAI:
        """Create Google Gemini LLM instance"""
        params = {
            "model": model,
            "temperature": temperature,
            "google_api_key": settings.google_api_key,
        }

        # Add optional parameters
        if settings.google_project_id:
            params["project"] = settings.google_project_id

        params.update(kwargs)
        return ChatGoogleGenerativeAI(**params)

    def _create_ollama_llm(
        self,
        model: str,
        temperature: float,
        **kwargs: Any
    ) -> ChatOllama:
        """Create Ollama (local) LLM instance"""
        params = {
            "model": model,
            "temperature": temperature,
            "base_url": settings.ollama_base_url,
        }

        params.update(kwargs)
        return ChatOllama(**params)

    def clear_cache(self):
        """Clear cached LLM instances"""
        logger.info("Clearing LLM cache")
        self._cache.clear()

    def get_cached_models(self) -> list:
        """Get list of cached model keys"""
        return list(self._cache.keys())

    def get_current_provider(self) -> str:
        """Get the currently configured provider"""
        return settings.llm_provider

    def get_current_model(self) -> str:
        """Get the currently configured model"""
        return settings.llm_model


# Convenience function for quick access
def get_default_llm():
    """Get default LLM instance based on settings"""
    processor = LLMProcessor()
    return processor.get_llm()


# Example usage and testing
if __name__ == "__main__":
    # Test singleton pattern
    processor1 = LLMProcessor()
    processor2 = LLMProcessor()

    print(f"Same instance? {processor1 is processor2}")  # Should be True
    print(f"Provider: {processor1.get_current_provider()}")
    print(f"Model: {processor1.get_current_model()}")

    # Test factory pattern
    llm1 = processor1.get_llm()
    llm2 = processor1.get_llm()

    print(f"Cached? {llm1 is llm2}")  # Should be True

    # Test different providers (if configured)
    try:
        llm_openai = processor1.get_llm(provider="openai", model="gpt-4o-mini")
        print(f"OpenAI LLM created: {type(llm_openai).__name__}")
    except Exception as e:
        print(f"OpenAI creation failed: {e}")

    print(f"Cached models: {processor1.get_cached_models()}")
