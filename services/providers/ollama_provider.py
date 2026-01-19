"""Ollama LLM Provider.

Implementation of BaseLLMProvider using Ollama's OpenAI-compatible API.
Allows running local LLM models without API costs.

Supported models (run `ollama list` to see installed):
- llama3.2: General purpose, good reasoning
- mistral: Fast, good for analysis
- qwen2.5: Excellent reasoning and multilingual
- gemma2: Google's open model
- codellama: Code-focused tasks
- deepseek-r1: Advanced reasoning (requires more RAM)
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


@ComponentRegistry.register_llm_provider("ollama")
class OllamaProvider(BaseLLMProvider):
    """Provider for local Ollama models.
    
    Ollama exposes an OpenAI-compatible API at http://localhost:11434/v1,
    so we can reuse the OpenAI client with a custom base_url.
    
    Usage:
        1. Install Ollama: https://ollama.ai
        2. Pull a model: `ollama pull llama3.2`
        3. Start server: `ollama serve`
        4. Set LLM_PROVIDER=ollama in .env
    """
    
    def __init__(
        self,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs: Any
    ) -> None:
        """Initialize the Ollama provider.
        
        Args:
            model: Model name (e.g., 'llama3.2', 'mistral'). Defaults to settings.
            temperature: Sampling temperature.
            max_tokens: Maximum response tokens.
            **kwargs: Additional configuration.
        """
        settings = get_settings()
        
        # Use settings if model not specified
        model = model or settings.ollama_model
        
        super().__init__(model, temperature, max_tokens, **kwargs)
        
        self.logger = get_logger("provider.ollama")
        
        # Create OpenAI client pointing to Ollama's local server
        self.client = AsyncOpenAI(
            base_url=settings.ollama_base_url,
            api_key="ollama"  # Ollama doesn't require a real API key
        )
        
        self.logger.info(
            f"Initialized Ollama provider with model '{self.model}' "
            f"at {settings.ollama_base_url}"
        )

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate text using local Ollama model.
        
        Args:
            prompt: The user prompt.
            system_instruction: Optional system message.
            **kwargs: Additional generation parameters.
            
        Returns:
            Generated text response.
        """
        messages = []
        
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Ollama generation failed: {str(e)}")
            
            # Provide helpful error message for common issues
            if "Connection refused" in str(e):
                raise ConnectionError(
                    "Cannot connect to Ollama. Make sure Ollama is running:\n"
                    "  1. Start Ollama: `ollama serve`\n"
                    "  2. Or check if it's running: `curl http://localhost:11434/api/tags`"
                ) from e
            elif "model" in str(e).lower() and "not found" in str(e).lower():
                raise ValueError(
                    f"Model '{self.model}' not found. Pull it first:\n"
                    f"  `ollama pull {self.model}`\n"
                    f"  Available models: llama3.2, mistral, qwen2.5, gemma2"
                ) from e
            raise

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        **kwargs: Any
    ) -> T:
        """Generate structured JSON response matching a Pydantic schema.
        
        Args:
            prompt: The user prompt.
            schema: Pydantic model class to validate against.
            system_instruction: Optional system message.
            **kwargs: Additional generation parameters.
            
        Returns:
            Instance of the schema model populated with generated data.
        """
        messages = []
        
        # Add system instruction with JSON enforcement
        json_system = (
            "You are a helpful assistant that always responds with valid JSON. "
            "Never include markdown code blocks or explanations, only pure JSON."
        )
        if system_instruction:
            json_system = f"{system_instruction}\n\n{json_system}"
        
        messages.append({"role": "system", "content": json_system})
        
        # Add schema to prompt
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        prompt_with_schema = (
            f"{prompt}\n\n"
            f"Respond with valid JSON matching this exact schema:\n"
            f"```json\n{schema_json}\n```\n\n"
            f"Return ONLY the JSON object, no other text."
        )
        
        messages.append({"role": "user", "content": prompt_with_schema})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            
            # Clean up response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            # Parse and validate
            data = json.loads(content)
            return schema.model_validate(data)
            
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Failed to parse Ollama JSON response: {str(e)}\n"
                f"Response was: {content[:500]}..."
            )
            raise ValueError(
                f"Ollama returned invalid JSON. Try a more capable model "
                f"like 'qwen2.5' or 'llama3.2' for structured output."
            ) from e
        except Exception as e:
            self.logger.error(f"Ollama structured generation failed: {str(e)}")
            raise

    async def health_check(self) -> bool:
        """Check if Ollama is running and the model is available.
        
        Returns:
            True if healthy, False otherwise.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=10
            )
            return "OK" in response.choices[0].message.content.upper()
        except Exception as e:
            self.logger.warning(f"Ollama health check failed: {str(e)}")
            return False
