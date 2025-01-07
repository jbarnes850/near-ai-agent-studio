# API Reference

## Core Components

### AgentConfig

Configuration for individual agents.

```python
class AgentConfig:
    def __init__(
        network: str,              # NEAR network (testnet/mainnet)
        account_id: str,           # NEAR account ID
        private_key: str,          # NEAR private key
        llm_provider: str,         # LLM provider (hyperbolic)
        llm_api_key: str,          # LLM API key
        llm_model: str = "deepseek-ai/DeepSeek-V3",  # LLM model
        debug: bool = False        # Enable debug mode
    )
```

### SwarmConfig

Configuration for swarm behavior.

```python
class SwarmConfig:
    def __init__(
        role: str,                # Agent role (market_analyzer, risk_manager, etc.)
        min_confidence: float,     # Minimum confidence for decisions (0.0-1.0)
        min_votes: int = 2,       # Minimum votes required for consensus
        timeout: float = 1.0      # Timeout for consensus (seconds)
    )
```

### SwarmAgent

Main agent class for swarm operations.

```python
class SwarmAgent:
    def __init__(
        config: AgentConfig,      # Agent configuration
        swarm_config: SwarmConfig # Swarm configuration
    )

    async def start(self) -> None:
        """Start the agent and initialize connections."""
        
    async def join_swarm(self, peers: List[SwarmAgent]) -> None:
        """Join a swarm with peer agents."""
        
    async def propose_action(
        self,
        action_type: str,         # Type of action to propose
        params: Dict[str, Any]    # Action parameters
    ) -> Dict[str, Any]:
        """Propose an action to the swarm."""
        
    async def evaluate_proposal(
        self,
        proposal: Dict[str, Any]  # Proposal to evaluate
    ) -> Dict[str, Any]:
        """Evaluate a proposal and return decision."""
        
    async def close(self) -> None:
        """Clean up resources and close connections."""
```

### MarketDataManager

Handles market data operations.

```python
class MarketDataManager:
    def __init__(
        cache_ttl: int = 300,     # Cache time-to-live (seconds)
        rate_limit: int = 10      # Rate limit (requests per minute)
    )
    
    async def get_price(
        self,
        symbol: str              # Token symbol
    ) -> float:
        """Get current price for token."""
        
    async def get_volume(
        self,
        symbol: str,             # Token symbol
        timeframe: str = "24h"   # Time period
    ) -> float:
        """Get trading volume for token."""
        
    async def get_market_context(
        self,
        symbol: str             # Token symbol
    ) -> Dict[str, Any]:
        """Get comprehensive market context."""
```

### SwarmChat

Interactive chat interface.

```python
class SwarmChat:
    def __init__(
        agent_type: str = "chat_assistant",  # Type of agent to use
        verbose: bool = False                # Enable verbose output
    )
    
    async def setup(self) -> None:
        """Initialize chat interface."""
        
    async def _process_input(
        self,
        user_input: str        # User's input text
    ) -> None:
        """Process user input and generate response."""
        
    async def cleanup(self) -> None:
        """Clean up resources."""
```

## Data Models

### MarketAnalysis

Structure for market analysis results.

```python
class MarketAnalysis(BaseModel):
    symbol: str                   # Token symbol
    price: float                  # Current price
    volume_24h: float            # 24-hour volume
    trend: str                   # Market trend
    confidence: float            # Analysis confidence
    reasoning: str               # Explanation of analysis
```

### RiskAssessment

Structure for risk assessment results.

```python
class RiskAssessment(BaseModel):
    risk_level: str              # High/Medium/Low
    factors: List[str]           # Risk factors identified
    mitigation: List[str]        # Suggested mitigations
    confidence: float            # Assessment confidence
```

### StrategyProposal

Structure for strategy proposals.

```python
class StrategyProposal(BaseModel):
    action: str                  # Buy/Sell/Hold
    target_price: float          # Target price
    stop_loss: float            # Stop loss price
    timeframe: str              # Strategy timeframe
    confidence: float           # Strategy confidence
    reasoning: str              # Strategy explanation
```

## Utility Functions

### Cache Management

```python
class Cache:
    async def get_or_set(
        key: str,               # Cache key
        func: Callable,         # Function to call if cache miss
        ttl: int = 300         # Time-to-live in seconds
    ) -> Any:
        """Get cached value or compute and cache new value."""
```

### Rate Limiting

```python
class RateLimiter:
    def __init__(
        max_calls: int,         # Maximum calls allowed
        time_window: int        # Time window in seconds
    )
    
    async def __aenter__(self) -> None:
        """Enter context and check rate limit."""
        
    async def __aexit__(self, *args) -> None:
        """Exit context and update rate limit."""
```

### Logging

```python
def setup_logging(
    level: str = "INFO",       # Logging level
    file_path: str = None      # Optional log file path
) -> None:
    """Configure logging for the application."""
```

## Constants

```python
# Agent Types
AGENT_TYPES = {
    "MARKET_ANALYZER": "market_analyzer",
    "RISK_MANAGER": "risk_manager",
    "STRATEGY_OPTIMIZER": "strategy_optimizer",
    "CHAT_ASSISTANT": "chat_assistant"
}

# Market Trends
MARKET_TRENDS = {
    "BULLISH": "bullish",
    "BEARISH": "bearish",
    "NEUTRAL": "neutral"
}

# Risk Levels
RISK_LEVELS = {
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low"
}

# Default Configuration
DEFAULT_CONFIG = {
    "MIN_CONFIDENCE": 0.7,
    "MIN_VOTES": 2,
    "CACHE_TTL": 300,
    "RATE_LIMIT": 10
}
```

## Error Types

```python
class SwarmError(Exception):
    """Base error for swarm operations."""
    pass

class ConsensusError(SwarmError):
    """Error in reaching consensus."""
    pass

class MarketDataError(SwarmError):
    """Error in fetching market data."""
    pass

class AgentConfigError(SwarmError):
    """Error in agent configuration."""
    pass
```

## Usage Examples

### Basic Agent Setup

```python
config = AgentConfig(
    network="testnet",
    account_id="your-account.testnet",
    private_key="your-private-key",
    llm_provider="hyperbolic",
    llm_api_key="your-api-key"
)

swarm_config = SwarmConfig(
    role="market_analyzer",
    min_confidence=0.7
)

agent = SwarmAgent(config, swarm_config)
await agent.start()
```

### Market Analysis

```python
market_data = MarketDataManager()
context = await market_data.get_market_context("NEAR")

result = await agent.evaluate_proposal({
    "type": "market_analysis",
    "params": {
        "symbol": "NEAR",
        "market_context": context
    }
})
```

### Multi-Agent System

```python
# Initialize agents
market_analyzer = SwarmAgent(config, SwarmConfig(role="market_analyzer"))
risk_manager = SwarmAgent(config, SwarmConfig(role="risk_manager"))
strategy_optimizer = SwarmAgent(config, SwarmConfig(role="strategy_optimizer"))

# Start agents
for agent in [market_analyzer, risk_manager, strategy_optimizer]:
    await agent.start()

# Form swarm
await market_analyzer.join_swarm([risk_manager, strategy_optimizer])

# Propose action
result = await market_analyzer.propose_action(
    action_type="market_trade",
    params={
        "symbol": "NEAR",
        "action": "buy",
        "amount": 100
    }
)
``` 