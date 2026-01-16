# CRIS Plugins

Custom plugins to extend CRIS functionality.

## Creating a Plugin

```
plugins/
└── my_plugin/
    ├── __init__.py
    └── agent.py
```

### agent.py

```python
from core.adk_agent import CRISADKAgent, CRISToolResult

class MyAgent(CRISADKAgent):
    name = "my_agent"
    description = "Custom analysis"
    
    def get_tools(self):
        return [self.analyze]
    
    async def analyze(self, data: str) -> CRISToolResult:
        """Analyze data."""
        return CRISToolResult(success=True, data={})
```

### __init__.py

```python
from .agent import MyAgent
__all__ = ["MyAgent"]
```

## Enable Plugin

In `.env`:

```env
ENABLED_PLUGINS=my_plugin
```

## Example

See `example_agent/` for a complete implementation.
