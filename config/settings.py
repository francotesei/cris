"""CRIS Settings Configuration.

This module uses Pydantic Settings to manage application configuration
via environment variables and .env files.

Built for the Google Gemini 3 Hackathon 🚀

Configuration:
  - CRIS_ENV: Select environment (gemini, ollama, openai, anthropic)
  - config/models.yml: Defines what each environment contains
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """CRIS Application Settings."""

    # ==========================================================================
    # ENVIRONMENT SELECTION (main config switch)
    # ==========================================================================
    # Set this to switch between environments defined in config/models.yml
    # Options: gemini (default), ollama, openai, anthropic
    cris_env: str = "gemini"
    
    # ==========================================================================
    # API Keys (required based on CRIS_ENV)
    # ==========================================================================
    google_api_key: Optional[str] = None      # Required for: gemini
    openai_api_key: Optional[str] = None      # Required for: openai
    anthropic_api_key: Optional[str] = None   # Required for: anthropic
    # ollama: no API key required
    
    # ==========================================================================
    # Ollama Configuration (only used when CRIS_ENV=ollama)
    # ==========================================================================
    ollama_base_url: str = "http://localhost:11434/v1"
    
    # ==========================================================================
    # ADK Configuration (Google Agent Development Kit)
    # ==========================================================================
    adk_enable_tracing: bool = True
    adk_session_timeout: int = 3600
    adk_max_tool_calls: int = 10
    
    # ==========================================================================
    # A2A Protocol Configuration
    # ==========================================================================
    a2a_enable: bool = True
    a2a_server_port: int = 8080
    a2a_protocol_version: str = "0.2"
    a2a_enable_streaming: bool = True

    # Neo4j Configuration
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "crispassword"
    neo4j_max_connection_lifetime: int = 3600
    neo4j_max_connection_pool_size: int = 50
    neo4j_max_path_depth: int = 6

    # Vector Store Configuration
    vector_store_type: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"
    chroma_default_collection: str = "evidence"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Application Configuration
    app_name: str = "CRIS"
    app_version: str = "0.1.0-alpha"
    app_title: str = "CRIS - Criminal Reasoning Intelligence System"
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
    geocoding_user_agent: str = "cris_investigative_system"
    google_maps_api_key: Optional[str] = None
    mapbox_api_key: Optional[str] = None
    
    # Map Defaults
    default_map_center_lat: float = 40.7128
    default_map_center_lon: float = -74.0060
    default_map_zoom: int = 12

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
