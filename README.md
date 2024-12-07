<div align="center">

# NEAR Swarm Intelligence Framework

A production-ready starter kit for building AI-powered trading strategies on NEAR using multi-agent swarm intelligence.

## 🧠 What is Swarm Intelligence?

Swarm intelligence is a collaborative decision-making approach where multiple specialized agents work together to achieve better outcomes than any single agent could alone. In this framework:

- **Market Analyzer** agents evaluate price data and trading volumes
- **Risk Manager** agents assess potential risks and exposure
- **Strategy Optimizer** agents fine-tune execution parameters

These agents collaborate through a consensus mechanism, where each agent:

1. Evaluates proposals based on its expertise
2. Provides a confidence score with its decision
3. Explains its reasoning

## ⚡️ Quick Start

```bash
# Clone the repository
git clone https://github.com/jbarnes850/near-swarm-intelligence
cd near-swarm-intelligence

# Run the quickstart script
./scripts/quickstart.sh
```

The quickstart script will:

- Set up your Python environment
- Install dependencies
- Create a NEAR testnet account
- Configure your environment
- Create an example strategy
- Guide you through using the CLI

> **Note**: This template runs on NEAR testnet by default for safe development.
> Always test thoroughly before deploying to mainnet.

# Run example strategy
```bash
python examples/swarm_trading.py
```

## 🎯 Key Features

### Multi-Agent Framework

- **Specialized Agents**: Each agent has a specific role and expertise
- **Consensus Mechanism**: Weighted voting system based on agent confidence
- **Collaborative Decisions**: Agents work together to evaluate opportunities
- **Transparent Reasoning**: Each agent explains its decision rationale

### NEAR Integration

- **Automated Setup**: Quick wallet creation and configuration
- **Transaction Safety**: Built-in validation and error handling
- **Market Access**: Ready-to-use interfaces for DEX interactions

### Starter Kit Features

- **Simple Interface**: Clear APIs for agent creation and interaction
- **Working Examples**: Production-ready trading strategy templates
- **Comprehensive Tests**: Reliable test suite for core components
- **Clear Documentation**: Step-by-step guides and best practices

## 🚀 Basic Usage

```python
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

# Create specialized agents
market_analyzer = SwarmAgent(
    config=AgentConfig(...),
    swarm_config=SwarmConfig(
        role="market_analyzer",
        min_confidence=0.6  # Lower threshold for market signals
    )
)

risk_manager = SwarmAgent(
    config=AgentConfig(...),
    swarm_config=SwarmConfig(
        role="risk_manager",
        min_confidence=0.8  # Higher threshold for risk assessment
    )
)

# Form the swarm
swarm = [market_analyzer, risk_manager]
for agent in swarm:
    await agent.join_swarm([a for a in swarm if a != agent])

# Propose a trade
result = await market_analyzer.propose_action(
    action_type="trade",
    params={
        "token": "NEAR",
        "action": "buy",
        "amount": 10.0
    }
)

# Check consensus
if result["consensus"]:
    print(f"Trade approved with {result['approval_rate']:.0%} confidence")
    for reason in result["reasons"]:
        print(f"- {reason}")
```

## 📦 Project Structure

```bash
near-swarm/
├── near_swarm/          # Core Framework
│   └── core/           
│       ├── agent.py         # Base Agent
│       ├── swarm_agent.py   # Swarm Implementation
│       ├── consensus.py     # Voting System
│       └── near_integration.py
├── examples/            # Working Examples
│   ├── swarm_trading.py    # Basic Trading Strategy
│   └── market_making.py    # Market Making Strategy
├── tests/              # Test Suite
└── docs/               # Documentation
```

## 🛠 Configuration

Copy `.env.example` to `.env` and configure:

```env
# NEAR Configuration
NEAR_NETWORK=testnet
NEAR_ACCOUNT_ID=your-account.testnet
NEAR_PRIVATE_KEY=your-private-key

# AI Provider (optional)
HYPERBOLIC_API_KEY=your-api-key

# Swarm Settings
CONSENSUS_THRESHOLD=0.7  # Required agreement among agents
MIN_VOTES=2             # Minimum votes needed
```

## 📚 CLI Commands

The `near-swarm` CLI helps manage your strategies:

```bash
# Create new strategy
./scripts/near-swarm init arbitrage --name my-strategy

# List strategies
./scripts/near-swarm list

# Run strategy
./scripts/near-swarm run

# Monitor performance
./scripts/near-swarm monitor
```

## 📚 Documentation

- [Getting Started](docs/getting-started.md) - First steps and basic concepts
- [First Strategy](docs/first-strategy.md) - Build your first swarm strategy
- [Core Concepts](docs/core-concepts.md) - Deep dive into swarm intelligence
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details

---

<div align="center">

Built with ❤️ by the NEAR Community

[Join us on Discord](https://discord.gg/near) • [Follow us on Twitter](https://twitter.com/NEARProtocol)

</div>
