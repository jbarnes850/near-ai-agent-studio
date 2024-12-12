"""
NEAR Swarm Intelligence Framework
A multi-agent framework for building AI-powered trading strategies on NEAR Protocol.
"""

__version__ = "0.1.0"

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.consensus import ConsensusManager, Vote

__all__ = [
    "AgentConfig",
    "SwarmAgent",
    "SwarmConfig",
    "ConsensusManager",
    "Vote",
]
