"""
Base Plugin System for NEAR Swarm Intelligence
Defines the interface that all agent plugins must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from near_swarm.core.agent import AgentConfig
from near_swarm.core.llm_provider import LLMProvider

@dataclass
class PluginConfig:
    """Configuration for agent plugins"""
    name: str
    role: str
    capabilities: List[str]
    system_prompt: Optional[str] = None
    custom_settings: Dict[str, Any] = None

class AgentPlugin(ABC):
    """Base class for all agent plugins"""
    
    def __init__(self, agent_config: AgentConfig, plugin_config: PluginConfig):
        """Initialize plugin with configurations"""
        self.agent_config = agent_config
        self.plugin_config = plugin_config
        self.llm_provider: Optional[LLMProvider] = None
        self._is_initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        pass
    
    @abstractmethod
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a proposal or context"""
        pass
    
    @abstractmethod
    async def execute(self, operation: Optional[str] = None, **kwargs) -> Any:
        """Execute plugin operation"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up plugin resources"""
        pass
    
    @property
    def capabilities(self) -> List[str]:
        """List plugin capabilities"""
        return self.plugin_config.capabilities
    
    @property
    def role(self) -> str:
        """Get plugin role"""
        return self.plugin_config.role
    
    @property
    def name(self) -> str:
        """Get plugin name"""
        return self.plugin_config.name
    
    async def __aenter__(self):
        """Async context manager entry"""
        if not self._is_initialized:
            await self.initialize()
            self._is_initialized = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        self._is_initialized = False
        return None 