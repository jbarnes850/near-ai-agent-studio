# Core Concepts

This document explains the fundamental concepts behind the NEAR Swarm Intelligence framework.

## Swarm Intelligence Overview

Swarm intelligence is a collective behavior of decentralized, self-organized agents working together to make decisions. In our framework, this concept is applied to DeFi operations where multiple specialized agents collaborate to:

1. Analyze market conditions
2. Assess risks
3. Identify opportunities
4. Execute strategies

## Agent System

### Agent Roles

Each agent in the swarm has a specialized role:

1. **Market Analyzer**
   - Analyzes market conditions
   - Monitors liquidity and volume
   - Tracks price movements
   - Confidence based on market stability

2. **Risk Manager**
   - Evaluates position risks
   - Monitors exposure limits
   - Assesses market risks
   - Confidence based on risk metrics

3. **Strategy Optimizer**
   - Optimizes execution parameters
   - Adjusts to market conditions
   - Fine-tunes strategies
   - Confidence based on historical performance

### Agent Properties

Each agent has:

```python
@dataclass
class AgentReputation:
    agent_id: str
    role: str
    success_rate: float
    total_operations: int
    successful_operations: int
    average_confidence: float
```

## Consensus Mechanism

### Voting Process

1. **Vote Collection**

```python
@dataclass
class Vote:
    agent_id: str
    decision: bool
    confidence: float  # 0.0 to 1.0
    reasoning: str
```

2. **Consensus Strategies**

- **Simple Majority**
  - Basic voting with confidence threshold
  - Each agent gets equal weight
  - Requires minimum participation

- **Reputation Weighted**
  - Weights votes by agent reputation
  - Better performing agents have more influence
  - Adapts over time

- **Confidence Weighted**
  - Weights votes by confidence scores
  - Higher confidence = more influence
  - Rewards careful decision making

- **Hybrid**
  - Combines reputation and confidence
  - Balanced influence model
  - Most sophisticated approach

### Consensus Formula

For hybrid consensus:

```python
weight = (reputation_weight * reputation + 
         confidence_weight * confidence)
```

## Memory Management

### Storage System

1. **File-based Storage**

```python
class FileStorage:
    def save(self, key: str, value: Any) -> bool
    def load(self, key: str) -> Optional[Any]
    def delete(self, key: str) -> bool
```

2. **Data Categories**

- Agent reputations
- Strategy outcomes
- Market data cache
- Performance metrics

### Learning System

1. **Reputation Updates**

```python
async def update_reputation(
    agent_id: str,
    success: bool,
    confidence: float
) -> AgentReputation
```

2. **Outcome Recording**

```python
async def record_outcome(
    strategy_id: str,
    success: bool,
    metrics: Dict[str, Any]
) -> None
```

## Market Data Integration

### DeFi Llama Integration

1. **Data Points**

- TVL (Total Value Locked)
- Volume data
- Price information
- Protocol metrics

2. **Caching System**

```python
class MarketDataProvider:
    def __init__(self, cache_duration: int = 300):
        self.cache: Dict[str, Any] = {}
```

### Market Analysis

1. **Metrics Calculation**

```python
async def analyze_market_conditions(
    protocols: List[str],
    tokens: List[str]
) -> Dict[str, Any]
```

2. **Risk Assessment**

```python
async def analyze_risk(
    token: str,
    position_size: float
) -> Dict[str, Any]
```

## Strategy Development

### Strategy Lifecycle

1. **Initialization**
   - Configure parameters
   - Initialize components
   - Set up monitoring

2. **Execution Loop**
   - Analyze opportunities
   - Collect votes
   - Reach consensus
   - Execute actions
   - Record outcomes

3. **Learning Loop**
   - Update reputations
   - Adjust parameters
   - Optimize performance

### Example Strategy Structure

```python
class Strategy:
    def __init__(self):
        self.market_data = MarketDataProvider()
        self.memory = SwarmMemory()
        self.consensus = ConsensusEngine(
            ConsensusConfig(
                strategy=ConsensusStrategy.HYBRID
            )
        )
    
    async def execute(self):
        opportunity = await self.analyze()
        votes = await self.collect_votes()
        consensus = await self.reach_consensus()
        if consensus['consensus_reached']:
            await self.execute_action()
```

## Best Practices

### Agent Design

1. **Specialization**
   - Single responsibility
   - Clear decision criteria
   - Well-defined confidence calculation

2. **Confidence Scoring**
   - Based on concrete metrics
   - Normalized (0.0 to 1.0)
   - Conservative estimates

### Risk Management

1. **Position Limits**
   - Per-token limits
   - Total exposure limits
   - Dynamic adjustments

2. **Emergency Conditions**
   - Market circuit breakers
   - Volatility limits
   - Loss thresholds

### Performance Optimization

1. **Monitoring**
   - Agent performance
   - Strategy outcomes
   - System health

2. **Adjustment**
   - Parameter tuning
   - Agent weighting
   - Strategy evolution

## Advanced Topics

For more advanced topics, see:

- [Advanced Features](advanced-features.md)
- [Performance Tuning](performance-tuning.md)
- [Custom Agents](custom-agents.md)
