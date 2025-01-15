"""
NEAR Swarm Agent Core
Provides the base agent functionality and plugin integration
"""

from typing import Dict, Any, Optional, List
import logging

from ..config.schema import AgentConfig, LLMSettings
from ..config.loader import ConfigLoader
from ..plugins.loader import PluginLoader

logger = logging.getLogger(__name__)

class SwarmAgent:
    """Core swarm agent with plugin support"""
    
    def __init__(self, config: Optional[AgentConfig] = None, config_path: Optional[str] = None):
        """Initialize swarm agent"""
        # Load configuration
        if config:
            self.config = config
        else:
            loader = ConfigLoader()
            if config_path:
                loader.load_config_file(config_path)
            self.config = loader.get_config()
        
        self.plugin_loader = PluginLoader()
        self._plugins = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize agent and load plugins"""
        if self._initialized:
            return
            
        try:
            # Load configured plugins
            if self.config.plugins:
                for plugin_config in self.config.plugins:
                    plugin = await self.plugin_loader.load_plugin(
                        plugin_config.name,
                        self.config,
                        plugin_config
                    )
                    self._plugins[plugin_config.name] = plugin
                    
            logger.info(f"Initialized SwarmAgent with plugins: {list(self._plugins.keys())}")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing SwarmAgent: {str(e)}")
            raise
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate using loaded plugins"""
        if not self._initialized:
            await self.initialize()
        
        results = {}
        for name, plugin in self._plugins.items():
            try:
                result = await plugin.evaluate(context)
                results[name] = result
            except Exception as e:
                logger.error(f"Error in plugin {name}: {str(e)}")
                results[name] = {"error": str(e)}
        
        return results
    
    async def cleanup(self) -> None:
        """Clean up agent and plugins"""
        if self._initialized:
            await self.plugin_loader.cleanup()
            self._plugins = {}
            self._initialized = False
    
    def get_plugin(self, name: str) -> Optional[Any]:
        """Get a loaded plugin by name"""
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List names of loaded plugins"""
        return list(self._plugins.keys())
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        return None
