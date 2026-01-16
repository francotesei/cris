"""CRIS Settings Configuration.

This module uses Pydantic Settings to manage application configuration
via environment variables and .env files.

Optimized for Gemini 3 + ADK + A2A architecture.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """CRIS Application Settings."""

    # Gemini 3 / ADK Configuration
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash"  # Gemini 3 (API name: gemini-2.0-flash)
    gemini_temperature: float = 0.7
    gemini_max_tokens: int = 8192
    
    # ADK Configuration
    adk_enable_tracing: bool = True
    adk_session_timeout: int = 3600
    adk_max_tool_calls: int = 10
    
    # A2A Protocol Configuration
    a2a_enable: bool = True
    a2a_server_port: int = 8080
    a2a_protocol_version: str = "0.2"
    a2a_enable_streaming: bool = True
    
    # Legacy LLM Configuration (for fallback/comparison)
    llm_provider: str = "gemini"  # gemini, openai, anthropic
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_model: str = "gemini-2.0-flash"  # Updated to Gemini 3
    llm_temperature: float = 0.7
    llm_max_tokens: int = 8192

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "crispassword"
    neo4j_max_connection_lifetime: int = 3600
    neo4j_max_connection_pool_size: int = 50

    # Vector Store Configuration
    vector_store_type: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Application Configuration
    debug: bool = True
    log_level: str = "INFO"
    log_format: str = "console"
    secret_key: str = "change_this_to_a_random_secret_key"
    session_timeout: int = 3600

    # Plugin Configuration
    plugins_dir: str = "./plugins"
    enabled_plugins: List[str] = []

    # Feature Flags
    enable_osint: bool = False
    enable_predictions: bool = True
    enable_experimental: bool = False

    # Geocoding Configuration
    geocoding_provider: str = "nominatim"
    google_maps_api_key: Optional[str] = None
    mapbox_api_key: Optional[str] = None

    # Performance Configuration
    max_concurrent_agents: int = 5
    cache_ttl: int = 300
    request_timeout: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
