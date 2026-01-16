"""Plugin Loader.

Handles dynamic discovery and loading of custom plugins from the plugins directory.
"""

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import List

from utils.logger import get_logger


class PluginLoader:
    """Discovers and loads external CRIS plugins."""
    
    def __init__(self, plugins_dir: str = "./plugins") -> None:
        """Initialize the loader.
        
        Args:
            plugins_dir: Path to the directory containing plugins.
        """
        self.plugins_dir = Path(plugins_dir)
        self.logger = get_logger("core.plugin_loader")

    def load_all(self, enabled_plugins: List[str] = None) -> None:
        """Discover and load all enabled plugins.
        
        Args:
            enabled_plugins: Optional list of plugin folder names to load.
                             If None, loads all subdirectories with __init__.py.
        """
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return

        self.logger.info(f"Loading plugins from {self.plugins_dir.absolute()}")

        # Ensure plugins dir is in path
        if str(self.plugins_dir.absolute()) not in sys.path:
            sys.path.append(str(self.plugins_dir.absolute()))

        for item in self.plugins_dir.iterdir():
            if not item.is_dir():
                continue
                
            plugin_name = item.name
            
            # Skip if explicitly disabled
            if enabled_plugins is not None and plugin_name not in enabled_plugins:
                continue
                
            # Skip hidden or special dirs
            if plugin_name.startswith((".", "_")):
                continue

            init_file = item / "__init__.py"
            if not init_file.exists():
                self.logger.debug(f"Skipping directory {plugin_name}: no __init__.py")
                continue

            try:
                self.logger.info(f"Loading plugin: {plugin_name}")
                # Import the plugin package which should trigger registration
                importlib.import_module(f"plugins.{plugin_name}")
                self.logger.info(f"Successfully loaded plugin: {plugin_name}")
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_name}: {str(e)}", exc_info=True)
