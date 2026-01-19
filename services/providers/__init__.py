"""CRIS LLM Providers.

Pluggable LLM provider implementations.

Available providers:
- gemini: Google Gemini (requires GOOGLE_API_KEY)
- openai: OpenAI GPT models (requires OPENAI_API_KEY)
- anthropic: Anthropic Claude (requires ANTHROPIC_API_KEY)
- ollama: Local models via Ollama (free, no API key needed)
"""

from services.providers.gemini_provider import GeminiProvider
from services.providers.openai_provider import OpenAIProvider
from services.providers.anthropic_provider import AnthropicProvider
from services.providers.ollama_provider import OllamaProvider

__all__ = ["GeminiProvider", "OpenAIProvider", "AnthropicProvider", "OllamaProvider"]
