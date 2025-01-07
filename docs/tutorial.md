# Developer Tutorial

This tutorial will guide you through building your first AI-powered trading agent using the NEAR Swarm Intelligence framework.

## Prerequisites

- Python 3.12+
- [Hyperbolic API Key](https://hyperbolic.ai)
- Basic understanding of NEAR Protocol

## 1. Basic Setup

```bash
# Install the framework
pip install near-swarm

# Create a new project
mkdir my-trading-bot
cd my-trading-bot

# Initialize environment
cp .env.example .env
# Edit .env with your credentials
```

## 2. Your First Agent

Create `simple_agent.py`:

```python
import asyncio
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

async def main():
    # Configure agent
    config = AgentConfig(
        network="testnet",
        account_id="your-account.testnet",
        private_key="your-private-key",
        llm_provider="hyperbolic",
        llm_api_key="your-api-key",
        llm_model="deepseek-ai/DeepSeek-V3"
    )
    
    # Create market analyzer
    agent = SwarmAgent(
        config,
        SwarmConfig(
            role="market_analyzer",
            min_confidence=0.7
        )
    )
    
    # Start agent
    await agent.start()
    
    try:
        # Example: Analyze NEAR market
        result = await agent.evaluate_proposal({
            "type": "market_analysis",
            "params": {
                "symbol": "NEAR",
                "market_context": {
                    "current_price": 5.45,
                    "24h_volume": "2.1M",
                    "market_trend": "upward"
                }
            }
        })
        
        print(f"Decision: {'Yes' if result['decision'] else 'No'}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Reasoning: {result['reasoning']}")
        
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Natural Language Interface

Create `chat_bot.py`:

```python
from near_swarm.cli.chat import SwarmChat
import asyncio

async def main():
    # Initialize chat interface
    chat = SwarmChat(
        agent_type="chat_assistant",
        verbose=True
    )
    
    # Setup and start
    await chat.setup()
    
    try:
        # Example: Process natural language query
        await chat._process_input(
            "What's the current market sentiment for NEAR?"
        )
    finally:
        await chat.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

## 4. Multi-Agent System

Create `swarm_system.py`:

```python
import asyncio
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

async def main():
    # Create base config
    config = AgentConfig(
        network="testnet",
        account_id="your-account.testnet",
        private_key="your-private-key",
        llm_provider="hyperbolic",
        llm_api_key="your-api-key",
        llm_model="deepseek-ai/DeepSeek-V3"
    )
    
    # Initialize specialized agents
    market_analyzer = SwarmAgent(
        config,
        SwarmConfig(role="market_analyzer", min_confidence=0.7)
    )
    
    risk_manager = SwarmAgent(
        config,
        SwarmConfig(role="risk_manager", min_confidence=0.8)
    )
    
    strategy_optimizer = SwarmAgent(
        config,
        SwarmConfig(role="strategy_optimizer", min_confidence=0.7)
    )
    
    # Start all agents
    for agent in [market_analyzer, risk_manager, strategy_optimizer]:
        await agent.start()
    
    # Form swarm
    await market_analyzer.join_swarm([risk_manager, strategy_optimizer])
    
    try:
        # Example: Get swarm consensus on a trade
        result = await market_analyzer.propose_action(
            action_type="market_trade",
            params={
                "symbol": "NEAR",
                "action": "buy",
                "amount": 100,
                "market_context": {
                    "current_price": 5.45,
                    "24h_volume": "2.1M",
                    "market_trend": "upward"
                }
            }
        )
        
        print("\nSwarm Decision:")
        print(f"Consensus: {'Reached' if result['consensus'] else 'Not Reached'}")
        print(f"Approval Rate: {result['approval_rate']:.2%}")
        print("\nReasoning from each agent:")
        for reason in result['reasons']:
            print(f"- {reason}")
            
    finally:
        # Cleanup
        for agent in [market_analyzer, risk_manager, strategy_optimizer]:
            await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. Production Considerations

### Error Handling

```python
try:
    result = await agent.evaluate_proposal(proposal)
except Exception as e:
    logger.error(f"Evaluation failed: {str(e)}")
    # Implement fallback strategy
    result = await fallback_strategy(proposal)
```

### Rate Limiting

```python
from near_swarm.core.market_data import MarketDataManager

market_data = MarketDataManager(
    cache_ttl=300,  # Cache for 5 minutes
    rate_limit=10   # Max 10 requests per minute
)
```

### Monitoring

```python
# In .env
LOG_LEVEL=INFO
ENABLE_TELEMETRY=true
PROMETHEUS_PORT=9090
```

### Security

1. Never commit `.env` files
2. Use environment variables for secrets
3. Implement proper error handling
4. Set reasonable limits:
```python
MAX_POSITION_SIZE=10000
EMERGENCY_SHUTDOWN_THRESHOLD=0.05
```

## Next Steps

1. Review [Core Concepts](core-concepts.md)
2. Explore example implementations in `near_swarm/examples/`
3. Join our developer community
4. Contribute to the framework 