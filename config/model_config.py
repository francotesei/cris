"""Model Configuration Loader.

Loads model configuration from models.yml based on CRIS_ENV.

Usage:
    1. Set CRIS_ENV in .env (e.g., CRIS_ENV=gemini or CRIS_ENV=ollama)
    2. models.yml defines what each environment contains
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from utils.logger import get_logger

_model_config: Optional[Dict[str, Any]] = None
_logger = get_logger("config.models")


def _load_yaml() -> Dict[str, Any]:
    """Load the models.yml file."""
    global _model_config
    
    if _model_config is None:
        config_path = Path(__file__).parent / "models.yml"
        
        if config_path.exists():
            with open(config_path, "r") as f:
                _model_config = yaml.safe_load(f)
        else:
            _logger.warning("models.yml not found, using defaults")
            _model_config = {
                "environments": {
                    "gemini": {
                        "provider": "gemini",
                        "model": "gemini-3-pro",
                        "temperature": 0.7,
                        "max_tokens": 8192,
                    }
                },
                "agents": {}
            }
    
    return _model_config


def get_environment_config(env_name: str) -> Dict[str, Any]:
    """Get configuration for a specific environment.
    
    Args:
        env_name: Environment name (gemini, ollama, openai, anthropic)
        
    Returns:
        Dictionary with provider, model, temperature, max_tokens, etc.
    """
    config = _load_yaml()
    environments = config.get("environments", {})
    
    if env_name not in environments:
        _logger.warning(f"Environment '{env_name}' not found, falling back to 'gemini'")
        env_name = "gemini"
    
    return environments.get(env_name, {})


def get_current_environment() -> Dict[str, Any]:
    """Get configuration for the current CRIS_ENV.
    
    Returns:
        Dictionary with provider, model, temperature, max_tokens, etc.
    """
    # Import here to avoid circular dependency
    from config.settings import get_settings
    settings = get_settings()
    
    return get_environment_config(settings.cris_env)


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Get configuration for a specific agent.
    
    Merges environment defaults with agent-specific overrides.
    
    Args:
        agent_name: Name of the agent (e.g., 'orchestrator', 'link_agent')
        
    Returns:
        Dictionary with provider, model, temperature, max_tokens
    """
    # Get base config from current environment
    env_config = get_current_environment()
    
    result = {
        "provider": env_config.get("provider", "gemini"),
        "model": env_config.get("model", "gemini-3-pro"),
        "temperature": env_config.get("temperature", 0.7),
        "max_tokens": env_config.get("max_tokens", 8192),
    }
    
    # Apply agent-specific overrides (mainly temperature)
    config = _load_yaml()
    agents = config.get("agents", {})
    agent_config = agents.get(agent_name, {})
    
    if agent_config.get("temperature") is not None:
        result["temperature"] = agent_config["temperature"]
    
    return result


def get_available_models(provider: str) -> list:
    """Get available models for a provider.
    
    Args:
        provider: Provider name (gemini, ollama, openai, anthropic)
        
    Returns:
        List of model configurations
    """
    config = _load_yaml()
    models = config.get("models", {})
    return models.get(provider, [])


def list_environments() -> Dict[str, str]:
    """List all available environments with descriptions.
    
    Returns:
        Dictionary mapping environment names to descriptions
    """
    config = _load_yaml()
    environments = config.get("environments", {})
    
    return {
        name: env.get("description", "")
        for name, env in environments.items()
    }
