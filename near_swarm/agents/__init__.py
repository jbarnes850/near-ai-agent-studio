"""
NEAR Swarm Agent Implementations
Contains built-in and custom agent implementations
"""

from typing import Dict, Type
from ..plugins.base import AgentPlugin

# Registry of built-in agents
_agent_registry: Dict[str, Type[AgentPlugin]] = {}

def register_agent(name: str, agent_class: Type[AgentPlugin]) -> None:
    """Register a built-in agent"""
    _agent_registry[name] = agent_class

def get_agent(name: str) -> Type[AgentPlugin]:
    """Get a registered agent by name"""
    if name not in _agent_registry:
        raise ValueError(f"Agent '{name}' not found")
    return _agent_registry[name]

def list_agents() -> Dict[str, Type[AgentPlugin]]:
    """List all registered agents"""
    return dict(_agent_registry) 