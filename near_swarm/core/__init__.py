"""
Core components of the NEAR Swarm Intelligence Framework.
"""

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.consensus import ConsensusManager, Vote
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.memory_manager import MemoryManager, StrategyOutcome
from near_swarm.core.near_integration import NEARConnection
from near_swarm.core.exceptions import (
    AgentError,
    NEARError,
    LLMError,
    ConfigError,
    MarketDataError,
    PluginError,
)

__all__ = [
    "AgentConfig",
    "SwarmAgent",
    "SwarmConfig",
    "ConsensusManager",
    "Vote",
    "MarketDataManager",
    "MemoryManager",
    "StrategyOutcome",
    "NEARConnection",
    # Exceptions
    "AgentError",
    "NEARError",
    "LLMError",
    "ConfigError",
    "MarketDataError",
    "PluginError",
] 