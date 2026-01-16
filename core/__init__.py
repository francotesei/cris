"""CRIS Core Module - Powered by Gemini 3 + ADK + A2A.

This module contains the core abstractions and base classes that enable
CRIS's extensible architecture. Includes both legacy base classes and
new ADK/A2A infrastructure.

New Architecture (Gemini 3 + ADK + A2A):
- CRISADKAgent: Base class for ADK-powered agents
- CRISOrchestratorAgent: Orchestrator with A2A delegation
- A2AHandler/A2AClient: A2A protocol implementation
- AgentCard: A2A capability advertisement

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

# New ADK + A2A infrastructure
from core.adk_agent import (
    CRISADKAgent,
    CRISOrchestratorAgent,
    AgentRole,
    AgentCard,
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
    # New ADK infrastructure
    "CRISADKAgent",
    "CRISOrchestratorAgent",
    "AgentRole",
    "AgentCard",
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
