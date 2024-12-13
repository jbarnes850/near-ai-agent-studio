# Building Multi-Agent Systems with NEAR Swarm Intelligence

This tutorial guides you through creating and managing AI-powered swarm agents on NEAR testnet. You'll learn how to build collaborative multi-agent systems that leverage LLM-based decision making for intelligent consensus.

## Prerequisites

- Python 3.12+
- Basic understanding of NEAR Protocol
- Familiarity with async Python

## Quick Start

1. Clone and setup the repository:

```bash
git clone https://github.com/jbarnes850/near_swarm_intelligence
cd near_swarm_intelligence
./scripts/quickstart.sh
```

2. The quickstart script will:
   - Set up your Python virtual environment
   - Install dependencies from requirements.txt
   - Create a NEAR testnet account using create_near_wallet.sh
   - Configure environment variables
   - Set up Hyperbolic AI LLM integration

## Core Concepts

### What is Swarm Intelligence?

Swarm intelligence in this framework represents collaborative decision-making where multiple specialized agents work together to achieve better outcomes than any single agent could alone.

Key components:
- Multiple agents with different expertise
- Consensus-based decision making
- LLM-powered reasoning
- Blockchain integration

### Agent Types

1. **Market Analyzer**
   - Analyzes market conditions and price data
   - Identifies trading opportunities
   - Initiates swarm proposals

2. **Risk Manager**
   - Evaluates transaction safety
   - Assesses potential risks and exposure
   - Validates proposals against risk parameters

3. **Strategy Optimizer**
   - Fine-tunes execution parameters
   - Optimizes timing and efficiency
   - Improves overall strategy performance

## Building Your First Agent

Let's create a simple market analyzer agent:

```python
from near_swarm.core.agent import Agent, AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

async def create_market_analyzer():
    # Basic configuration
    config = AgentConfig(
        near_network="testnet",
        account_id="your-account.testnet",
        private_key="your-private-key",
        llm_provider="hyperbolic",
        llm_api_key="your-api-key"
    )

    # Swarm-specific configuration
    swarm_config = SwarmConfig(
        role="market_analyzer",
        min_confidence=0.7,
        min_votes=2,
        timeout=1.0
    )

    # Create the agent
    agent = SwarmAgent(config, swarm_config)
    await agent.start()
    
    return agent
```

## Creating a Swarm

Now let's create a simple swarm with multiple agents:

```python
async def create_swarm():
    # Create agents
    market_analyzer = await create_market_analyzer()
    
    risk_manager = SwarmAgent(
        AgentConfig(),  # Using default config
        SwarmConfig(role="risk_manager", min_confidence=0.8)
    )
    
    strategy_optimizer = SwarmAgent(
        AgentConfig(),
        SwarmConfig(role="strategy_optimizer", min_confidence=0.7)
    )

    # Form swarm
    await market_analyzer.join_swarm([risk_manager, strategy_optimizer])
    
    return market_analyzer
```

## Implementing a Strategy

Let's implement a simple trading strategy:

```python
async def run_trading_strategy(market_analyzer):
    # Define a trading proposal
    proposal = {
        "type": "transaction",
        "params": {
            "action": "swap",
            "token_in": "NEAR",
            "token_out": "USDC",
            "amount": "10",
            "min_output": "9.5"
        }
    }

    # Get swarm consensus
    result = await market_analyzer.propose_action(
        action_type=proposal["type"],
        params=proposal["params"]
    )

    if result["consensus"]:
        print("Executing approved transaction...")
        print(f"Confidence: {result['confidence']}")
        print(f"Supporting agents: {result['supporting_agents']}")
        
        # Execute the transaction
        tx_result = await market_analyzer.execute_action(proposal)
        print(f"Transaction result: {tx_result}")
```

## Advanced Features

### Memory Management

Agents can maintain state and learn from past decisions:

```python
from near_swarm.core.memory_manager import MemoryManager

memory = MemoryManager()
await memory.store_decision(
    agent_id="market_analyzer_1",
    decision={
        "type": "swap",
        "confidence": 0.85,
        "outcome": "success"
    }
)

# Retrieve past decisions
past_decisions = await memory.get_decisions("market_analyzer_1")
```

### Market Data Integration

Access real-time market data:

```python
from near_swarm.core.market_data import MarketDataProvider

market_data = MarketDataProvider()
price_data = await market_data.get_price("NEAR/USDC")
volume_data = await market_data.get_volume("NEAR/USDC", timeframe="1h")
```

## Example Strategies

The repository includes several example strategies:

1. Simple Strategy (examples/simple_strategy.py)
2. Arbitrage Strategy (examples/arbitrage.py)
3. Swarm Trading Strategy (examples/swarm_trading.py)

Review these examples to understand different approaches to multi-agent system design.

## Testing Your Agents

Run the test suite:

```bash
pytest tests/ -v
```

Key test areas:
- Agent initialization
- Swarm consensus
- Transaction execution
- Market data integration

## Best Practices

1. **Start Simple**
   - Begin with the simple_strategy example
   - Add complexity gradually
   - Test thoroughly on testnet

2. **Error Handling**
   - Handle API failures gracefully
   - Implement proper cleanup
   - Log important decisions

3. **Security**
   - Never commit private keys
   - Use environment variables
   - Implement transaction limits

4. **Testing**
   - Write comprehensive tests
   - Use testnet for development
   - Monitor agent performance

## Next Steps

1. Explore the example strategies in `examples/`
2. Customize agent roles and evaluation logic
3. Implement your own consensus mechanisms
4. Create advanced trading strategies

## Resources

- [NEAR Documentation](https://docs.near.org)
- [Project README](../README.md)
- [Core Concepts](core-concepts.md)
- [Troubleshooting Guide](troubleshooting.md)

Remember: Always test thoroughly on testnet before deploying to mainnet. 