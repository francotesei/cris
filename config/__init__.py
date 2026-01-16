"""CRIS Configuration Module.

This module provides centralized configuration management for CRIS,
including environment variables, settings, and LLM prompts.
"""

from config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
