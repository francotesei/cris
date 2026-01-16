# Plugin System

CRIS is designed as an open-source platform where the community can share new capabilities through plugins.

## 📁 Plugin Structure

Plugins live in the `plugins/` directory. Each plugin is a Python package.

```
plugins/
└── my_special_plugin/
    ├── __init__.py
    ├── agent.py          # Custom agents
    ├── processor.py      # Custom document processors
    └── provider.py       # Custom LLM providers
```

## 🔌 How it Works

1. **Discovery**: At startup, CRIS scans the `plugins/` folder for any subdirectories containing an `__init__.py`.
2. **Loading**: It imports each package, which triggers any decorators (`@ComponentRegistry.register_...`).
3. **Availability**: Once loaded, these components are indistinguishable from built-in ones.

## 🛠️ Creating a Plugin

See the [Plugin Development Guide](../plugins/README.md) for a detailed technical walkthrough.

## 📦 Sharing Plugins

To share a plugin, simply zip your plugin directory. Other users can install it by dropping it into their `plugins/` folder and restarting CRIS.

## 🔒 Security Note

Only install plugins from trusted sources. Since plugins are regular Python code, they have the same permissions as the main CRIS application.
