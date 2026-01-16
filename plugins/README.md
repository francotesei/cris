# CRIS Plugin Development Guide

This directory contains custom plugins that extend CRIS functionality.

## Creating a Plugin

1. Create a new directory for your plugin:
   ```
   plugins/
   └── my_custom_agent/
       ├── __init__.py
       └── agent.py
   ```

2. Implement your plugin by extending the appropriate base class:

```python
# plugins/my_custom_agent/agent.py
from core.base_agent import BaseAgent, AgentInput, AgentOutput
from core.registry import ComponentRegistry

@ComponentRegistry.register_agent("my_custom")
class MyCustomAgent(BaseAgent):
    """Custom agent implementation."""
    
    name = "my_custom"
    description = "Description of what this agent does"
    
    async def process(self, input: AgentInput) -> AgentOutput:
        # Your implementation here
        pass
    
    def get_capabilities(self) -> list[str]:
        return ["capability1", "capability2"]
```

3. Export your plugin in `__init__.py`:

```python
# plugins/my_custom_agent/__init__.py
from .agent import MyCustomAgent

__all__ = ["MyCustomAgent"]
```

4. Enable your plugin in `.env`:
   ```
   ENABLED_PLUGINS=my_custom_agent
   ```

## Plugin Types

You can create plugins for:

- **Agents**: Extend `BaseAgent` for new analysis capabilities
- **Processors**: Extend `BaseProcessor` for new document types
- **LLM Providers**: Extend `BaseLLMProvider` for new LLM backends
- **Vector Stores**: Extend `BaseVectorStore` for new vector databases

## Best Practices

1. **Type Hints**: Always use type hints for better IDE support
2. **Documentation**: Document your plugin with docstrings
3. **Error Handling**: Handle errors gracefully with proper logging
4. **Testing**: Include tests in a `tests/` subdirectory
5. **Dependencies**: If your plugin needs extra dependencies, document them

## Example Plugins

See `example_agent/` for a complete example implementation.
