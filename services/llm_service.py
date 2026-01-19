"""LLM Orchestration Service.

Manages LLM generation using pluggable providers.
Configuration is loaded from CRIS_ENV + models.yml.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from core.base_llm_provider import BaseLLMProvider
from core.registry import ComponentRegistry
from config.settings import get_settings
from config.model_config import get_current_environment
from utils.logger import get_logger

# Import providers to ensure they register themselves
# This must happen before any LLMService is instantiated
import services.providers  # noqa: F401

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """Orchestrator for LLM operations.
    
    Configuration is loaded from:
      1. CRIS_ENV in .env → selects environment (gemini, ollama, etc.)
      2. config/models.yml → defines what each environment contains
    """
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the service using current environment config."""
        self.logger = get_logger("service.llm")
        settings = get_settings()
        
        # Load config from current environment (CRIS_ENV)
        env_config = get_current_environment()
        
        self.provider_name = env_config.get("provider", "gemini")
        model = env_config.get("model", "gemini-3-pro")
        temperature = env_config.get("temperature", 0.7)
        max_tokens = env_config.get("max_tokens", 8192)
        
        self.logger.info(f"CRIS_ENV={settings.cris_env} → provider={self.provider_name}, model={model}")
        
        provider_class = ComponentRegistry.get_llm_provider_class(self.provider_name)
        if not provider_class:
            available = ComponentRegistry.list_llm_providers()
            raise ValueError(
                f"LLM Provider '{self.provider_name}' not found in registry. "
                f"Available: {available}. Check CRIS_ENV in your .env file."
            )
            
        self.provider: BaseLLMProvider = provider_class(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        self.logger.info(f"Initialized LLM service: {self.provider_name}/{model}")

    async def generate(self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any) -> str:
        """Text generation."""
        return await self.provider.generate(prompt, system_instruction, **kwargs)

    async def generate_structured(self, prompt: str, schema: Type[T], system_instruction: Optional[str] = None, **kwargs: Any) -> T:
        """Structured generation."""
        return await self.provider.generate_structured(prompt, schema, system_instruction, **kwargs)
