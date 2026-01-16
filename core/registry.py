"""Component Registry.

Centralizes the registration and discovery of pluggable components
(agents, providers, processors).
"""

from typing import Dict, Type, TypeVar, Optional, List

T = TypeVar("T")


class ComponentRegistry:
    """Registry for pluggable CRIS components."""
    
    _agents: Dict[str, Type[Any]] = {}
    _llm_providers: Dict[str, Type[Any]] = {}
    _processors: Dict[str, Type[Any]] = {}
    _vector_stores: Dict[str, Type[Any]] = {}

    @classmethod
    def register_agent(cls, name: str):
        """Decorator to register an agent class."""
        def decorator(subclass: Type[T]) -> Type[T]:
            cls._agents[name] = subclass
            return subclass
        return decorator

    @classmethod
    def register_llm_provider(cls, name: str):
        """Decorator to register an LLM provider class."""
        def decorator(subclass: Type[T]) -> Type[T]:
            cls._llm_providers[name] = subclass
            return subclass
        return decorator

    @classmethod
    def register_processor(cls, name: str):
        """Decorator to register a processor class."""
        def decorator(subclass: Type[T]) -> Type[T]:
            cls._processors[name] = subclass
            return subclass
        return decorator

    @classmethod
    def get_agent_class(cls, name: str) -> Optional[Type[Any]]:
        """Retrieve an agent class by name."""
        return cls._agents.get(name)

    @classmethod
    def get_llm_provider_class(cls, name: str) -> Optional[Type[Any]]:
        """Retrieve an LLM provider class by name."""
        return cls._llm_providers.get(name)

    @classmethod
    def get_processor_class(cls, name: str) -> Optional[Type[Any]]:
        """Retrieve a processor class by name."""
        return cls._processors.get(name)

    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent names."""
        return list(cls._agents.keys())

    @classmethod
    def list_llm_providers(cls) -> List[str]:
        """List all registered LLM provider names."""
        return list(cls._llm_providers.keys())
