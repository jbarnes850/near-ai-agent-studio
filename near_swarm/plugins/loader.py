"""
Plugin Loader for NEAR Swarm Intelligence
Manages plugin lifecycle and integration with SwarmAgent
"""

import os
import logging
import importlib
from typing import Dict, Any, Optional, Type, List
import yaml

from near_swarm.core.agent import AgentConfig
from .base import AgentPlugin, PluginConfig

logger = logging.getLogger(__name__)

class PluginLoader:
    """Manages plugin loading and lifecycle"""
    
    def __init__(self):
        self._loaded_plugins: Dict[str, AgentPlugin] = {}
        
    async def load_all_plugins(self) -> Dict[str, AgentPlugin]:
        """Scan and load all available plugins."""
        # Search paths for plugins
        search_paths = [
            ("near_swarm/agents", "plugin.py"),  # Look for plugin.py in subdirectories
            ("agents/custom", "plugin.py"),
            ("near_swarm/examples", "*_strategy.py"),
            ("plugins", "plugin.py")  # Look for plugin.py in subdirectories
        ]
        
        # Track found plugins
        found_plugins = set()
        
        # Scan each search path
        for base_path, pattern in search_paths:
            if os.path.exists(base_path):
                for root, _, files in os.walk(base_path):
                    if pattern == "plugin.py" and pattern in files:
                        # Extract plugin name from directory
                        plugin_name = os.path.basename(root)
                        found_plugins.add(plugin_name)
                    elif pattern.endswith("_strategy.py"):
                        # Extract plugin name from strategy files
                        for file in files:
                            if file.endswith("_strategy.py"):
                                plugin_name = file.replace("_strategy.py", "").replace("_", "-")
                                found_plugins.add(plugin_name)
        
        # Load each found plugin
        for plugin_name in found_plugins:
            try:
                await self.load_plugin(plugin_name)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {str(e)}")
        
        return self._loaded_plugins
        
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
            module_path = None
            module = None
            
            # Try loading from plugins directory first
            plugin_path = os.path.join("plugins", name, "plugin.py")
            if os.path.exists(plugin_path):
                spec = importlib.util.spec_from_file_location(name, plugin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
            
            # If not found, try other locations
            if not module:
                try:
                    module_path = f"near_swarm.plugins.{name}"
                    module = importlib.import_module(module_path)
                except ImportError:
                    # Try loading from agents directory
                    agent_path = os.path.join("near_swarm", "agents", name, "plugin.py")
                    if os.path.exists(agent_path):
                        spec = importlib.util.spec_from_file_location(name, agent_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                    else:
                        # Try loading from custom agents directory
                        custom_agent_path = os.path.join("agents", "custom", name, "plugin.py")
                        if os.path.exists(custom_agent_path):
                            spec = importlib.util.spec_from_file_location(name, custom_agent_path)
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                        else:
                            raise ImportError(f"Agent/plugin not found: {name}")
                
            # Load configuration
            if not plugin_config:
                # Try loading from agents directory first
                config_path = os.path.join("agents", f"{name}.yaml")
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                        
                        # Extract plugin configuration
                        plugin_data = next((p for p in config_data.get('plugins', []) if p.get('name') == name), {})
                        if not plugin_data:
                            plugin_data = {
                                'name': name,
                                'role': name,
                                'capabilities': [],
                                'custom_settings': {}
                            }
                        
                        plugin_config = PluginConfig(**plugin_data)
                else:
                    # Use default configuration
                    plugin_config = PluginConfig(
                        name=name,
                        role=name,
                        capabilities=[],
                        custom_settings={}
                    )
                    
            # Create default agent config if not provided
            if not agent_config:
                # Load from agent.yaml if it exists
                config_path = os.path.join("agents", f"{name}.yaml")
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                        # Remove plugin-specific fields
                        if 'plugins' in config_data:
                            del config_data['plugins']
                        agent_config = AgentConfig(**config_data)
                else:
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
                raise ImportError(f"No agent/plugin class found in module: {name}")
                
            plugin = plugin_class(agent_config, plugin_config)
            
            # Initialize plugin
            await plugin.initialize()
            
            # Store loaded plugin
            self._loaded_plugins[name] = plugin
            
            logger.info(f"Loaded agent/plugin: {name}")
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading {name}: {str(e)}")
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