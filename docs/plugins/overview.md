# Plugin System

Extend CRIS with custom plugins.

## Structure

```
plugins/
└── my_plugin/
    ├── __init__.py
    └── agent.py
```

## Creating a Plugin

```python
# plugins/my_plugin/agent.py
from core.adk_agent import CRISADKAgent, CRISToolResult

class MyPluginAgent(CRISADKAgent):
    name = "my_plugin_agent"
    description = "Custom analysis"
    
    def get_tools(self):
        return [self.analyze]
    
    async def analyze(self, data: str) -> CRISToolResult:
        return CRISToolResult(success=True, data={})
```

```python
# plugins/my_plugin/__init__.py
from .agent import MyPluginAgent
__all__ = ["MyPluginAgent"]
```

## Loading

Plugins are auto-discovered from `plugins/` at startup.

Enable specific plugins in `.env`:

```env
ENABLED_PLUGINS=my_plugin
```

## Security

Only install plugins from trusted sources.
