"""
LLM Processor - Factory Pattern + Singleton
Dynamically connects to different LLM providers
"""
import threading
from enum import Enum
from typing import Optional, Any
import logging

from langchain_openai import ChatOpenAI
from utils.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  # Future implementation


class LLMProcessor:
    """
    LLM Processor using Factory Pattern + Singleton

    This class ensures only one instance exists (Singleton)
    and provides a factory method to create different LLM instances.

    Usage:
        processor = LLMProcessor()
        llm = processor.get_llm(LLMProvider.OPENAI, model="gpt-4o-mini")
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
        logger.info("LLMProcessor initialized")

    def get_llm(
        self,
        provider: LLMProvider = LLMProvider.OPENAI,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any
    ):
        """
        Factory method to get an LLM instance

        Args:
            provider: LLM provider (OPENAI, ANTHROPIC, etc.)
            model: Model name (defaults to settings)
            temperature: Temperature parameter (defaults to settings)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLM instance from the specified provider

        Example:
            >>> processor = LLMProcessor()
            >>> llm = processor.get_llm(LLMProvider.OPENAI, model="gpt-4")
            >>> response = llm.invoke("Hello!")
        """
        # Use defaults from settings if not provided
        model = model or settings.llm_model
        temperature = temperature if temperature is not None else settings.openai_temperature

        # Create cache key
        cache_key = f"{provider}_{model}_{temperature}"

        # Return cached instance if exists
        if cache_key in self._cache:
            logger.debug(f"Returning cached LLM: {cache_key}")
            return self._cache[cache_key]

        # Create new instance based on provider
        logger.info(f"Creating new LLM instance: {provider} - {model}")

        if provider == LLMProvider.OPENAI:
            llm = self._create_openai_llm(model, temperature, **kwargs)
        elif provider == LLMProvider.ANTHROPIC:
            llm = self._create_anthropic_llm(model, temperature, **kwargs)
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
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=settings.openai_api_key,
            **kwargs
        )

    def _create_anthropic_llm(
        self,
        model: str,
        temperature: float,
        **kwargs: Any
    ):
        """Create Anthropic LLM instance (future implementation)"""
        # TODO: Implement Anthropic support
        raise NotImplementedError("Anthropic support coming soon")

    def clear_cache(self):
        """Clear cached LLM instances"""
        logger.info("Clearing LLM cache")
        self._cache.clear()

    def get_cached_models(self) -> list:
        """Get list of cached model keys"""
        return list(self._cache.keys())


# Convenience function for quick access
def get_default_llm():
    """Get default LLM instance"""
    processor = LLMProcessor()
    return processor.get_llm()


# Example usage
if __name__ == "__main__":
    # Test singleton pattern
    processor1 = LLMProcessor()
    processor2 = LLMProcessor()

    print(f"Same instance? {processor1 is processor2}")  # Should be True

    # Test factory pattern
    llm1 = processor1.get_llm(LLMProvider.OPENAI, model="gpt-4o-mini")
    llm2 = processor1.get_llm(LLMProvider.OPENAI, model="gpt-4o-mini")

    print(f"Cached? {llm1 is llm2}")  # Should be True

    # Test different models
    llm3 = processor1.get_llm(LLMProvider.OPENAI, model="gpt-4")
    print(f"Different model cached separately? {llm1 is not llm3}")  # Should be True

    print(f"Cached models: {processor1.get_cached_models()}")
