"""OpenAI LLM Provider.

Implementation of BaseLLMProvider using OpenAI's API.
"""

import json
from typing import Any, Optional, Type, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from core.base_llm_provider import BaseLLMProvider
from core.registry import ComponentRegistry
from config.settings import get_settings
from utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)


@ComponentRegistry.register_llm_provider("openai")
class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI GPT models."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs: Any) -> None:
        super().__init__(model, temperature, max_tokens, **kwargs)
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.logger = get_logger("provider.openai")

    async def generate(self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any) -> str:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    async def generate_structured(self, prompt: str, schema: Type[T], system_instruction: Optional[str] = None, **kwargs: Any) -> T:
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        # Enforce JSON mode for OpenAI
        prompt_plus = f"{prompt}\n\nReturn JSON according to schema: {schema.model_json_schema()}"
        messages.append({"role": "user", "content": prompt_plus})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs
        )
        
        data = json.loads(response.choices[0].message.content)
        return schema.model_validate(data)
