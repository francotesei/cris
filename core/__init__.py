"""CRIS Core Module - Multi-Provider AI Agents.

This module contains the core abstractions and base classes that enable
CRIS's extensible architecture. Supports multiple LLM providers:
- Gemini (cloud)
- Ollama (local, free)
- OpenAI (cloud)
- Anthropic (cloud)

Agent Base Classes:
- MultiProviderAgent: Works with any LLM provider (recommended)
- CRISADKAgent: Google ADK-powered agents (requires Gemini)

Legacy Architecture (still supported):
- BaseAgent: Original agent abstraction
- BaseLLMProvider: Pluggable LLM backends
"""

# Legacy base classes (still supported)
from core.base_agent import BaseAgent, AgentInput, AgentOutput, AgentCapability
from core.base_processor import BaseProcessor
from core.base_llm_provider import BaseLLMProvider
from core.base_vector_store import BaseVectorStore
from core.base_graph_db import BaseGraphDB
from core.registry import ComponentRegistry
from core.plugin_loader import PluginLoader

# Multi-provider agent infrastructure (works with Ollama, Gemini, OpenAI, etc.)
from core.multi_provider_agent import (
    MultiProviderAgent,
    MultiProviderOrchestrator,
    AgentRole,
    AgentCard,
    ToolResult,
)

# ADK + A2A infrastructure (requires Gemini)
from core.adk_agent import (
    CRISADKAgent,
    CRISOrchestratorAgent,
    CRISToolResult,
    create_tool,
)
from core.a2a_server import (
    A2AHandler,
    A2AClient,
    A2ARegistry,
    A2AAgentCard,
    A2ASkill,
    Task,
    TaskState,
    Message,
    MessageRole,
    ContentPart,
    Artifact,
)

__all__ = [
    # Legacy base classes
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
    # Multi-provider agents (recommended)
    "MultiProviderAgent",
    "MultiProviderOrchestrator",
    "AgentRole",
    "AgentCard",
    "ToolResult",
    # ADK infrastructure (Gemini only)
    "CRISADKAgent",
    "CRISOrchestratorAgent",
    "CRISToolResult",
    "create_tool",
    # A2A Protocol
    "A2AHandler",
    "A2AClient",
    "A2ARegistry",
    "A2AAgentCard",
    "A2ASkill",
    "Task",
    "TaskState",
    "Message",
    "MessageRole",
    "ContentPart",
    "Artifact",
]
