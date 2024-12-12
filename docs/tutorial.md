# NEAR Swarm Intelligence Tutorial

This tutorial guides you through creating and managing AI-powered swarm agents on NEAR testnet, leveraging LLM-based decision making for intelligent consensus.

## Quick Start

1. Clone and setup the repository:
```bash
git clone https://github.com/jbarnes850/near_swarm_intelligence
cd near_swarm_intelligence
./scripts/quickstart.sh
```

2. The quickstart script will:
   - Set up your Python environment
   - Install dependencies
   - Create a NEAR testnet account
   - Configure environment variables
   - Set up LLM integration

## Environment Configuration

The framework requires two sets of environment variables:

### NEAR Configuration
```env
NEAR_NETWORK=testnet
NEAR_ACCOUNT_ID=your-account.testnet
NEAR_PRIVATE_KEY=your-private-key
```

### LLM Configuration
```env
LLM_PROVIDER=hyperbolic
LLM_API_KEY=your-api-key
LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

## CLI Commands

The `near-swarm` CLI provides several commands for managing your swarm:

### Initialize a Strategy
```bash
near-swarm init my-strategy
```
Creates a new strategy directory with:
- `config.json`: Strategy configuration
- `my-strategy.py`: Strategy implementation

### Create an Agent
```bash
near-swarm create-agent market_analyzer --min-confidence 0.7
```
Available roles:
- market_analyzer: Analyzes market conditions and opportunities
- risk_manager: Evaluates transaction safety and risk levels
- strategy_optimizer: Optimizes execution parameters

### Run Strategies
Run the example strategy:
```bash
near-swarm run --example simple_strategy
```

Run your custom strategy:
```bash
near-swarm run --config my-strategy/config.json
```

### Interactive Mode
```bash
near-swarm interactive
```

## Understanding Swarm Intelligence

### Agent Roles

1. **Market Analyzer**
   - Analyzes market conditions
   - Identifies opportunities
   - Initiates swarm proposals

2. **Risk Manager**
   - Evaluates transaction safety
   - Assesses risk levels
   - Validates proposals

3. **Strategy Optimizer**
   - Optimizes execution timing
   - Adjusts parameters
   - Improves efficiency

### LLM-Powered Decision Making

Agents use LLM integration for intelligent decision making:

```python
# Example agent evaluation
result = await agent.evaluate_proposal({
    "type": "transaction",
    "params": {
        "action": "transfer",
        "amount": "1.5",
        "recipient": "bob.testnet"
    }
})

print(f"Decision: {result['decision']}")
print(f"Confidence: {result['confidence']}")
print(f"Reasoning: {result['reasoning']}")
```

### Swarm Consensus

Agents work together to reach consensus:

```python
# Form swarm
await market_analyzer.join_swarm([risk_manager, strategy_optimizer])

# Propose action
result = await market_analyzer.propose_action(
    action_type="transaction",
    params={"amount": "1.5", "recipient": "bob.testnet"}
)

if result["consensus"]:
    print("Executing approved action...")
```

## Creating Your First Strategy

1. Initialize the strategy:
```bash
near-swarm init my-strategy
```

2. Review generated files:
```
my-strategy/
├── config.json     # Strategy configuration
└── my-strategy.py  # Strategy implementation
```

3. Configure in `config.json`:
```json
{
  "name": "my-strategy",
  "roles": ["market_analyzer", "risk_manager"],
  "min_confidence": 0.7,
  "min_votes": 2
}
```

4. Implement your strategy:
```python
import asyncio
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

async def run_strategy():
    # Initialize agents
    market_analyzer = SwarmAgent(
        AgentConfig(),  # Configured by quickstart.sh
        SwarmConfig(role="market_analyzer", min_confidence=0.7)
    )

    risk_manager = SwarmAgent(
        AgentConfig(),
        SwarmConfig(role="risk_manager", min_confidence=0.8)
    )

    # Form swarm
    await market_analyzer.join_swarm([risk_manager])

    # Define your strategy logic
    proposal = {
        "type": "transaction",
        "params": {
            "action": "transfer",
            "amount": "1.5",
            "recipient": "bob.testnet"
        }
    }

    # Get swarm consensus
    result = await market_analyzer.propose_action(
        action_type=proposal["type"],
        params=proposal["params"]
    )

    if result["consensus"]:
        print("Executing approved transaction...")
        # Implement your execution logic
```

5. Run your strategy:
```bash
near-swarm run --config my-strategy/config.json
```

## Testing

Run integration tests:
```bash
pytest tests/integration -v
```

This verifies:
- CLI functionality
- Swarm consensus
- Transaction execution
- LLM integration

## Best Practices

1. **Start Simple**
   - Begin with simple_strategy example
   - Gradually add complexity
   - Test thoroughly before deployment

2. **Error Handling**
   - Handle LLM API errors gracefully
   - Implement proper cleanup
   - Log important decisions

3. **Configuration**
   - Use environment variables for credentials
   - Keep strategy settings in config.json
   - Start with default configurations

4. **Testing**
   - Test on testnet first
   - Write integration tests
   - Monitor agent decisions

## Next Steps

1. Explore example strategies in `examples/`
2. Customize agent roles and evaluation logic
3. Implement advanced consensus mechanisms
4. Create your own strategy templates

## Links

- [NEAR Documentation](https://docs.near.org)
- [Project README](../README.md)
- [Example Strategies](../near_swarm/examples/)
- [Integration Tests](../tests/integration/)

Remember: Always test thoroughly on testnet before deploying to mainnet. 