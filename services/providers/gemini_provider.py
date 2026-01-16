"""Google Gemini LLM Provider.

Implementation of BaseLLMProvider using Google's Generative AI SDK.
"""

import json
from typing import Any, Optional, Type, TypeVar

import google.generativeai as genai
from pydantic import BaseModel

from core.base_llm_provider import BaseLLMProvider
from core.registry import ComponentRegistry
from config.settings import get_settings
from utils.logger import get_logger

T = TypeVar("T", bound=BaseModel)


@ComponentRegistry.register_llm_provider("gemini")
class GeminiProvider(BaseLLMProvider):
    """Provider for Google Gemini models."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, **kwargs: Any) -> None:
        super().__init__(model, temperature, max_tokens, **kwargs)
        settings = get_settings()
        genai.configure(api_key=settings.google_api_key)
        self.logger = get_logger("provider.gemini")
        
        self.client = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            }
        )

    async def generate(self, prompt: str, system_instruction: Optional[str] = None, **kwargs: Any) -> str:
        """Generate text using Gemini."""
        # Note: In real production, use async calls if available in SDK
        # Currently the SDK is synchronous for simple generation
        chat = self.client.start_chat()
        if system_instruction:
            prompt = f"SYSTEM: {system_instruction}\n\nUSER: {prompt}"
            
        response = chat.send_message(prompt)
        return response.text

    async def generate_structured(self, prompt: str, schema: Type[T], system_instruction: Optional[str] = None, **kwargs: Any) -> T:
        """Generate structured data using Gemini's JSON mode."""
        prompt_with_schema = f"""
        {prompt}
        
        Respond with valid JSON matching this schema:
        {schema.model_json_schema()}
        """
        
        if system_instruction:
            prompt_with_schema = f"SYSTEM: {system_instruction}\n\nUSER: {prompt_with_schema}"
            
        response = self.client.generate_content(
            prompt_with_schema,
            generation_config={"response_mime_type": "application/json"}
        )
        
        try:
            data = json.loads(response.text)
            return schema.model_validate(data)
        except Exception as e:
            self.logger.error(f"Failed to parse Gemini JSON: {str(e)}\nResponse: {response.text}")
            raise
