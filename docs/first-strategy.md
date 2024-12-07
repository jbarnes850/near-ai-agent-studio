# Building Your First Swarm Strategy

This guide will walk you through creating a simple trading strategy using the NEAR Swarm Intelligence framework. You'll learn how to use multiple agents to make collaborative trading decisions.

## Prerequisites

- NEAR testnet account (created via `create_near_wallet.sh`)
- Python 3.8+
- Basic understanding of async/await in Python

## 1. Basic Setup (2 minutes)

```bash
# Clone and setup
git clone https://github.com/jbarnes850/near-swarm-intelligence
cd near-swarm-intelligence
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your NEAR credentials
```

## 2. Understanding Swarm Components (3 minutes)

A swarm strategy has three key components:

1. **Specialized Agents**
   - Market Analyzer: Evaluates prices and volumes
   - Risk Manager: Assesses trading risks
   - Strategy Optimizer: Fine-tunes parameters

2. **Consensus Mechanism**
   - Agents vote on proposals
   - Each vote includes confidence level
   - Weighted decisions based on expertise

3. **Action Execution**
   - Validated by consensus
   - Safe transaction handling
   - Automatic error recovery

## 3. Creating Your Strategy (5 minutes)

Create `my_strategy.py`:

```python
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

async def run_strategy():
    # 1. Create agent configurations
    config = AgentConfig(
        near_network="testnet",
        account_id="your-account.testnet",  # From .env
        private_key="your-private-key",     # From .env
        llm_provider="hyperbolic"
    )

    # 2. Create specialized agents
    market = SwarmAgent(
        config=config,
        swarm_config=SwarmConfig(
            role="market_analyzer",
            min_confidence=0.6  # More sensitive to opportunities
        )
    )
    
    risk = SwarmAgent(
        config=config,
        swarm_config=SwarmConfig(
            role="risk_manager",
            min_confidence=0.8  # More conservative
        )
    )

    # 3. Form the swarm
    swarm = [market, risk]
    for agent in swarm:
        await agent.join_swarm([a for a in swarm if a != agent])

    # 4. Define trading logic
    async def check_opportunity(token: str, amount: float):
        return await market.propose_action(
            action_type="trade",
            params={
                "token": token,
                "action": "buy",
                "amount": amount
            }
        )

    # 5. Main loop
    while True:
        # Check NEAR trading opportunity
        result = await check_opportunity("NEAR", 10.0)
        
        if result["consensus"]:
            print(f"Trade approved ({result['approval_rate']:.0%} confidence)")
            print("\nReasons:")
            for reason in result["reasons"]:
                print(f"- {reason}")
            # Execute trade here
            break
        
        await asyncio.sleep(60)  # Wait before next check

if __name__ == "__main__":
    asyncio.run(run_strategy())
```

## 4. Running Your Strategy (2 minutes)

```bash
# Option 1: Direct execution
python my_strategy.py

# Option 2: Using CLI tool
./scripts/near-swarm init custom --name my-strategy
./scripts/near-swarm run
```

## 5. Understanding the Output

Your strategy will output decisions like:

```
🤖 Swarm Trading Decision
━━━━━━━━━━━━━━━━━━━━━━━
Consensus Reached: ✅
Approval Rate: 85%
Total Votes: 2

📝 Agent Reasoning:
1. Market conditions favorable: Price=$3.25, Volume=$50K
2. Risk assessment passed: Volatility within bounds
```

## Next Steps

1. **Add More Agents**: Create specialized agents for different aspects of your strategy
2. **Custom Evaluation**: Implement your own market analysis and risk assessment logic
3. **Production Deployment**: Add monitoring and automated recovery
4. **Strategy Optimization**: Use the memory system to track and improve performance

## Common Pitfalls

- Always test with small amounts first
- Monitor agent confidence levels
- Handle network errors gracefully
- Keep track of gas costs

## Resources

- [Core Concepts](core-concepts.md) - Detailed framework documentation
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Examples](../examples/) - More strategy examples 