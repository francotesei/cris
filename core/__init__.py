"""CRIS Core Module.

This module contains the core abstractions and base classes that enable
CRIS's extensible plugin architecture. All agents, processors, and
providers inherit from these base classes.
"""

from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.base_processor import BaseProcessor
from core.base_llm_provider import BaseLLMProvider
from core.base_vector_store import BaseVectorStore
from core.base_graph_db import BaseGraphDB
from core.registry import ComponentRegistry
from core.plugin_loader import PluginLoader

__all__ = [
    "BaseAgent",
    "AgentInput",
    "AgentOutput",
    "AgentCapability",
    "BaseProcessor",
    "BaseLLMProvider",
    "BaseVectorStore",
    "BaseGraphDB",
    "ComponentRegistry",
    "PluginLoader",
]
