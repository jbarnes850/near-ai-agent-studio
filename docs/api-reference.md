# API Reference

## Core Components

### AgentPlugin

Base class for implementing agent plugins.

```python
class AgentPlugin:
    def __init__(
        config: Dict[str, Any]    # Plugin configuration from agent.yaml
    )

    async def initialize(self) -> None:
        """Initialize plugin resources."""
        
    async def evaluate(
        self,
        context: Dict[str, Any]  # Evaluation context
    ) -> Dict[str, Any]:
        """Process requests and return results."""
        
    async def cleanup(self) -> None:
        """Clean up plugin resources."""
```

### PluginLoader

Manages plugin lifecycle and registration.

```python
class PluginLoader:
    def __init__(
        plugin_dir: str = None,   # Custom plugin directory
        cache_plugins: bool = True # Enable plugin caching
    )
    
    async def load_plugin(
        self,
        name: str               # Plugin name
    ) -> AgentPlugin:
        """Load and initialize a plugin."""
        
    async def unload_plugin(
        self,
        name: str              # Plugin name
    ) -> None:
        """Unload and cleanup a plugin."""
        
    def get_plugin(
        self,
        name: str             # Plugin name
    ) -> Optional[AgentPlugin]:
        """Get a loaded plugin instance."""
        
    def list_loaded_plugins(self) -> List[str]:
        """List all currently loaded plugins."""
```

### ConfigurationManager

Handles configuration loading and validation.

```python
class ConfigurationManager:
    def __init__(
        config_dir: str = None,   # Custom config directory
        env_prefix: str = "NEAR_" # Environment variable prefix
    )
    
    def load_config(
        self,
        name: str,               # Config name
        schema: Type[BaseModel]  # Pydantic schema
    ) -> BaseModel:
        """Load and validate configuration."""
        
    def save_config(
        self,
        name: str,              # Config name
        config: BaseModel       # Configuration to save
    ) -> None:
        """Save configuration to file."""
```

### LLMProvider

Interface for LLM integration.

```python
class LLMProvider:
    def __init__(
        config: LLMConfig       # LLM configuration
    )
    
    async def query(
        self,
        prompt: str,           # Prompt text
        **kwargs               # Additional parameters
    ) -> Dict[str, Any]:
        """Send query to LLM and get response."""
        
    async def validate_action(
        self,
        action: Dict[str, Any], # Action to validate
        context: Dict[str, Any] # Validation context
    ) -> Dict[str, Any]:
        """Validate action using LLM."""
```

### NEARConnection

Manages NEAR blockchain interaction.

```python
class NEARConnection:
    def __init__(
        config: NEARConfig     # NEAR configuration
    )
    
    async def get_balance(
        self,
        account_id: str = None # Optional account ID
    ) -> float:
        """Get account balance."""
        
    async def send_tokens(
        self,
        recipient_id: str,     # Recipient account
        amount: str,           # Amount to send
        memo: str = None       # Optional memo
    ) -> Dict[str, Any]:
        """Send NEAR tokens."""
```

## Configuration Models

### LLMConfig

Configuration for LLM providers.

```python
class LLMConfig(BaseModel):
    provider: str              # LLM provider name
    model: str                 # Model identifier
    api_key: str              # API key
    temperature: float = 0.7   # Sampling temperature
    max_tokens: int = 2000     # Maximum tokens
    system_prompt: str         # System prompt
```

### NEARConfig

Configuration for NEAR blockchain.

```python
class NEARConfig(BaseModel):
    network: str              # Network (testnet/mainnet)
    account_id: str           # Account ID
    private_key: str          # Private key
    rpc_url: Optional[str]    # Custom RPC URL
    use_backup_rpc: bool      # Use backup RPC
```

### AgentConfig

Configuration for agent plugins.

```python
class AgentConfig(BaseModel):
    name: str                 # Agent name
    description: str          # Agent description
    version: str             # Version number
    author: str              # Author name
    capabilities: List[str]   # Agent capabilities
    llm: LLMConfig           # LLM configuration
    near: NEARConfig         # NEAR configuration
```

## CLI Commands

### Plugin Management

```bash
# Create new plugin
near-swarm create agent my-agent

# Install plugin
near-swarm plugins install ./my-agent

# List plugins
near-swarm plugins list

# Update plugin
near-swarm plugins update my-agent

# Remove plugin
near-swarm plugins remove my-agent
```

### Configuration

```bash
# Initialize config
near-swarm config init

# Validate config
near-swarm config validate

# Show current config
near-swarm config show

# Set config value
near-swarm config set key value
```

### Agent Control

```bash
# Start agent
near-swarm start my-agent

# Stop agent
near-swarm stop my-agent

# Execute operation
near-swarm execute my-agent --operation check_balance
```

## Error Types

```python
class AgentError(Exception):
    """Error in agent operations."""
    pass

class PluginError(Exception):
    """Error in plugin lifecycle."""
    pass

class ConfigError(Exception):
    """Error in configuration."""
    pass

class LLMError(Exception):
    """Error in LLM operations."""
    pass

class NEARError(Exception):
    """Error in NEAR operations."""
    pass
```

## Constants

```python
# Plugin States
PLUGIN_STATES = {
    "LOADED": "loaded",
    "INITIALIZED": "initialized",
    "RUNNING": "running",
    "STOPPED": "stopped",
    "ERROR": "error"
}

# Configuration Sources
CONFIG_SOURCES = {
    "CLI": "cli",
    "ENV": "env",
    "FILE": "file",
    "DEFAULT": "default"
}

# Default Settings
DEFAULT_SETTINGS = {
    "PLUGIN_CACHE_TTL": 3600,
    "CONFIG_ENV_PREFIX": "NEAR_",
    "LLM_TEMPERATURE": 0.7,
    "LLM_MAX_TOKENS": 2000
}
``` 