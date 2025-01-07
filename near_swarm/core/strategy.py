"""Base strategy class for NEAR Swarm Intelligence."""
import abc
from typing import Dict, Any, List

from near_swarm.core.swarm_agent import SwarmAgent

class Strategy(abc.ABC):
    """Abstract base class for swarm strategies."""

    def __init__(self, agents: List[SwarmAgent]):
        """Initialize the strategy with a list of agents."""
        self.agents = agents

    @abc.abstractmethod
    async def start(self):
        """Start the strategy."""
        pass

    @abc.abstractmethod
    async def stop(self):
        """Stop the strategy."""
        pass

    @abc.abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """Execute the strategy.
        
        Returns:
            Dict[str, Any]: The execution result containing:
                - decision (bool): Whether the strategy execution was successful
                - confidence (float): Confidence level in the decision (0.0 to 1.0)
                - reasoning (str): Explanation of the decision
        """
        pass 