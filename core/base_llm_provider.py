"""Base LLM Provider Abstractions.

Defines the interface for pluggable LLM backends (Gemini, OpenAI, etc).
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs: Any) -> None:
        """Initialize the provider.
        
        Args:
            model: The model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum response length.
            **kwargs: Provider-specific configuration.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.config = kwargs

    @abstractmethod
    async def generate(self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any) -> str:
        """Generate a text response for a prompt.
        
        Args:
            prompt: The user prompt.
            system_instruction: Optional system message/context.
            **kwargs: Overrides for generation parameters.
            
        Returns:
            The generated text.
        """
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, schema: Type[T], system_instruction: Optional[str] = None, **kwargs: Any) -> T:
        """Generate a structured response matching a Pydantic schema.
        
        Args:
            prompt: The user prompt.
            schema: The Pydantic model to populate.
            system_instruction: Optional system message/context.
            **kwargs: Overrides for generation parameters.
            
        Returns:
            An instance of the schema model.
        """
        pass
