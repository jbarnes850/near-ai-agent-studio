"""
Custom exceptions for the NEAR Swarm Intelligence Framework.
"""

class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass

class NEARError(Exception):
    """Exception for NEAR blockchain interaction errors."""
    pass

class LLMError(Exception):
    """Exception for LLM-related errors."""
    pass

class ConfigError(Exception):
    """Exception for configuration-related errors."""
    pass

class MarketDataError(Exception):
    """Exception for market data-related errors."""
    pass

class PluginError(Exception):
    """Exception for plugin-related errors."""
    pass 