"""LLM Orchestration Service.

Manages LLM generation using pluggable providers and centralized prompts.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from core.base_llm_provider import BaseLLMProvider
from core.registry import ComponentRegistry
from config.settings import get_settings
from utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)


class LLMService:
    """Orchestrator for LLM operations."""
    
    def __init__(self, provider_name: str = None, **kwargs: Any) -> None:
        """Initialize the service.
        
        Args:
            provider_name: Override for the configured provider.
            **kwargs: Generation parameter overrides.
        """
        settings = get_settings()
        self.provider_name = provider_name or settings.llm_provider
        self.logger = get_logger("service.llm")
        
        provider_class = ComponentRegistry.get_llm_provider_class(self.provider_name)
        if not provider_class:
            raise ValueError(f"LLM Provider '{self.provider_name}' not found in registry")
            
        self.provider: BaseLLMProvider = provider_class(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            **kwargs
        )
        self.logger.info(f"Initialized LLM service with provider: {self.provider_name}")

    async def generate(self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any) -> str:
        """Text generation."""
        return await self.provider.generate(prompt, system_instruction, **kwargs)

    async def generate_structured(self, prompt: str, schema: Type[T], system_instruction: Optional[str] = None, **kwargs: Any) -> T:
        """Structured generation."""
        return await self.provider.generate_structured(prompt, schema, system_instruction, **kwargs)
