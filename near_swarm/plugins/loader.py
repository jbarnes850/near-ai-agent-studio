"""
Plugin Loader for NEAR Swarm Intelligence
Manages plugin lifecycle and integration with SwarmAgent
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, Type
import yaml

from near_swarm.core.agent import AgentConfig
from .base import AgentPlugin, PluginConfig

logger = logging.getLogger(__name__)

class PluginLoader:
    """Manages plugin loading and lifecycle"""
    
    def __init__(self):
        self._loaded_plugins: Dict[str, AgentPlugin] = {}
    
    async def load_plugin(
        self,
        name: str,
        agent_config: Optional[AgentConfig] = None,
        plugin_config: Optional[PluginConfig] = None
    ) -> AgentPlugin:
        """Load and initialize a plugin"""
        try:
            # Check if plugin is already loaded
            if name in self._loaded_plugins:
                return self._loaded_plugins[name]
            
            # Import plugin module
            module_path = f"near_swarm.plugins.{name}"
            try:
                module = importlib.import_module(module_path)
            except ImportError:
                # Try loading from examples directory first
                example_path = os.path.join("near_swarm", "examples", f"{name.replace('-', '_')}_strategy.py")
                if os.path.exists(example_path):
                    spec = importlib.util.spec_from_file_location(name, example_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                    else:
                        raise ImportError(f"Could not load plugin: {name}")
                else:
                    # Try loading from custom plugins directory
                    custom_path = os.path.join("plugins", f"{name}.py")
                    if os.path.exists(custom_path):
                        spec = importlib.util.spec_from_file_location(name, custom_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                        else:
                            raise ImportError(f"Could not load plugin: {name}")
                    else:
                        raise ImportError(f"Plugin not found: {name}")
            
            # Load plugin configuration
            if not plugin_config:
                config_path = os.path.join("plugins", name, "agent.yaml")
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                        plugin_config = PluginConfig(**config_data)
                else:
                    # Use default configuration
                    plugin_config = PluginConfig(
                        name=name,
                        role=name,
                        capabilities=[],
                        system_prompt=None,
                        custom_settings={}
                    )
                    
            # Create default agent config if not provided
            if not agent_config:
                # Create agent config with required fields
                agent_config = AgentConfig(
                    name=name,
                    environment="development",
                    log_level="INFO"
                )
            
            # Create plugin instance
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, AgentPlugin) and attr != AgentPlugin:
                    plugin_class = attr
                    break
                    
            if not plugin_class:
                raise ImportError(f"No plugin class found in module: {name}")
                
            plugin = plugin_class(agent_config, plugin_config)
            
            # Initialize plugin
            await plugin.initialize()
            
            # Store loaded plugin
            self._loaded_plugins[name] = plugin
            
            logger.info(f"Loaded plugin: {name}")
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin {name}: {str(e)}")
            raise
    
    async def unload_plugin(self, name: str) -> None:
        """Unload and cleanup a plugin"""
        if name in self._loaded_plugins:
            plugin = self._loaded_plugins[name]
            await plugin.cleanup()
            del self._loaded_plugins[name]
            logger.info(f"Unloaded plugin: {name}")
    
    def get_plugin(self, name: str) -> Optional[AgentPlugin]:
        """Get a loaded plugin by name"""
        return self._loaded_plugins.get(name)
    
    def list_loaded_plugins(self) -> Dict[str, AgentPlugin]:
        """List all loaded plugins"""
        return dict(self._loaded_plugins)
    
    async def cleanup(self) -> None:
        """Clean up all loaded plugins"""
        for name in list(self._loaded_plugins.keys()):
            await self.unload_plugin(name) 