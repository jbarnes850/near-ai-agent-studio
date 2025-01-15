"""
Plugin System for NEAR Swarm Intelligence
Provides extensibility for custom agents while maintaining core functionality
"""

from typing import Dict, Type
from .base import AgentPlugin
from .loader import PluginLoader

# Global plugin registry
_plugin_registry: Dict[str, Type[AgentPlugin]] = {}

def register_plugin(name: str, plugin_class: Type[AgentPlugin]) -> None:
    """Register a new agent plugin"""
    _plugin_registry[name] = plugin_class

def get_plugin(name: str) -> Type[AgentPlugin]:
    """Get a registered plugin by name"""
    if name not in _plugin_registry:
        raise ValueError(f"Plugin '{name}' not found")
    return _plugin_registry[name]

def list_plugins() -> Dict[str, Type[AgentPlugin]]:
    """List all registered plugins"""
    return dict(_plugin_registry)

__all__ = [
    'AgentPlugin',
    'PluginLoader',
    'register_plugin',
    'get_plugin',
    'list_plugins',
] 