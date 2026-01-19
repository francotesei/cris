"""CRIS Configuration Module.

Configuration is controlled by:
  1. CRIS_ENV in .env → selects the environment (gemini, ollama, etc.)
  2. config/models.yml → defines what each environment contains
"""

from config.settings import Settings, get_settings
from config.model_config import (
    get_environment_config,
    get_current_environment,
    get_agent_config,
    get_available_models,
    list_environments,
)

__all__ = [
    "Settings",
    "get_settings",
    "get_environment_config",
    "get_current_environment",
    "get_agent_config",
    "get_available_models",
    "list_environments",
]
