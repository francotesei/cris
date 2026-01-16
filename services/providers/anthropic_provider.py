"""Anthropic LLM Provider.

Implementation of BaseLLMProvider using Anthropic's Claude API.
"""

import json
import re
from typing import Any, Optional, Type, TypeVar

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from core.base_llm_provider import BaseLLMProvider
from core.registry import ComponentRegistry
from config.settings import get_settings
from utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)


@ComponentRegistry.register_llm_provider("anthropic")
class AnthropicProvider(BaseLLMProvider):
    """Provider for Anthropic Claude models."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs: Any) -> None:
        super().__init__(model, temperature, max_tokens, **kwargs)
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.logger = get_logger("provider.anthropic")

    async def generate(self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_instruction or "",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def generate_structured(self, prompt: str, schema: Type[T], system_instruction: Optional[str] = None, **kwargs: Any) -> T:
        # Anthropic doesn't have a strict JSON mode like OpenAI/Gemini yet, 
        # so we use a very descriptive prompt and regex extraction.
        prompt_plus = f"""
        {prompt}
        
        You MUST respond with a valid JSON object matching this schema:
        {schema.model_json_schema()}
        
        Ensure the JSON is wrapped in ```json tags.
        """
        
        text = await self.generate(prompt_plus, system_instruction, **kwargs)
        
        # Extract JSON from code blocks
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Fallback to finding the first { and last }
            json_str = text[text.find("{"):text.rfind("}")+1]
            
        try:
            data = json.loads(json_str)
            return schema.model_validate(data)
        except Exception as e:
            self.logger.error(f"Failed to parse Claude JSON: {str(e)}\nRaw Response: {text}")
            raise
