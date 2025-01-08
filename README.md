# NEAR AI Agent Studio

A production-ready starter kit for building AI-powered agents and multi-agent swarms on NEAR. This template provides the essential building blocks for creating autonomous agents that can interact with the NEAR blockchain, make decisions using LLMs, and collaborate in swarms.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NEAR](https://img.shields.io/badge/NEAR-Protocol-blue.svg)](https://near.org)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](https://github.com/near/near-ai-agent-template/actions)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/badge/PyPI-0.1.0-blue.svg)](https://pypi.org/project/near-swarm/)
[![Hyperbolic](https://img.shields.io/badge/LLM-Hyperbolic-purple.svg)](https://hyperbolic.xyz)

[![Lava Network](https://img.shields.io/badge/RPC-Lava%20Network-orange.svg)](https://www.lavanet.xyz/get-started/near)

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
   - [Swarm Intelligence](#-swarm-intelligence)
   - [Interactive Voice Assistant](#-interactive-voice-assistant)
   - [Multi-Agent Strategy](#-multi-agent-strategy)
   - [Chat Interface](#-chat-interface)
3. [Getting Started](#-getting-started)
   - [Prerequisites](#prerequisites)
   - [Quick Start](#quick-start)
   - [Environment Setup](#environment-setup)
   - [Running Demos](#running-demos)
4. [Core Components](#-core-components)
   - [System Architecture](#system-architecture)
   - [Agent Types](#agent-types)
   - [Integration Points](#integration-points)
5. [Interactive Features](#-interactive-features)
   - [Voice Commands](#voice-commands)
   - [Chat Commands](#chat-commands)
   - [Strategy Development](#strategy-development)
6. [Development Guide](#-development-guide)
   - [Creating Agents](#creating-agents)
   - [Building Strategies](#building-strategies)
   - [Testing](#testing)
7. [Examples](#-examples)
8. [Documentation](#-documentation)
9. [Contributing](#-contributing)

## Overview

The NEAR AI Agent Studio is an educational and interactive starter kit designed for developers looking to build AI-powered applications on NEAR. It combines three powerful paradigms:
- 🧠 Multi-agent swarm intelligence for collaborative decision-making
- 🗣️ Voice-powered agents for portfolio management and market analysis
- 💬 Interactive chat with autonomous agents for onchain actions

## 🔥 Features

### 🧠 Swarm Intelligence

Swarm intelligence enables multiple specialized agents to collaborate for better outcomes:

- **Market Analyzer** agents evaluate price data and trading volumes
- **Risk Manager** agents assess potential risks and exposure
- **Strategy Optimizer** agents fine-tune execution parameters

These agents work together through:
1. Expertise-based evaluation
2. Confidence scoring
3. Transparent reasoning
4. Consensus building

### 🎙️ Interactive Voice Assistant

Natural language interaction with your NEAR portfolio:
- Real-time market analysis and insights
- Portfolio balance monitoring
- Transaction history tracking
- Voice-powered trading suggestions
- Market sentiment analysis

### 🤖 Multi-Agent Strategy

Watch specialized AI agents collaborate in real-time:

1. **Market Analysis Phase**
   - Price trend evaluation
   - Volume analysis
   - Market sentiment assessment
   - Network monitoring

2. **Risk Management Phase**
   - Transaction risk assessment
   - Portfolio exposure analysis
   - Network security validation
   - Gas optimization

3. **Strategy Optimization Phase**
   - Parameter fine-tuning
   - Execution timing
   - Slippage prediction
   - Cost-benefit analysis

4. **Consensus Building**
   - Multi-agent voting
   - Confidence scoring
   - Detailed reasoning
   - Transparent decisions

### 💬 Chat Interface

Powerful interactive development environment:
```bash
# Start chatting with your AI assistant
./scripts/chat

# Available modes:
./scripts/chat --agent market_analyzer  # Market analysis
./scripts/chat --multi-agent            # Multi-agent mode
./scripts/chat --verbose                # Detailed reasoning
```

Features:
- Natural language interaction
- Market analysis and insights
- Risk assessment
- Portfolio management
- Strategy optimization
- Development tools

## ⚡️ Getting Started

### Prerequisites

Before you begin, ensure you have:

#### System Requirements
- Python 3.12 or higher
- Operating System:
  - macOS 12.0+
  - Ubuntu 20.04+ / Debian 11+
  - Windows 10/11 with WSL2

#### NEAR Account
- NEAR testnet account (created automatically by [quickstart](./scripts/quickstart.sh) script)
- Or existing account with:
  - Account ID
  - Full access key
  - Test NEAR tokens (available from [NEAR Faucet](https://near-faucet.io))

#### API Keys
- Hyperbolic API key for LLM capabilities
  - Sign up at [hyperbolic.xyz](https://hyperbolic.xyz)
  - Free tier available for development
- ElevenLabs API key for voice features (optional)
  - Register at [elevenlabs.io](https://elevenlabs.io)
  - Free tier includes basic voice synthesis

#### Development Tools
- Git
- Node.js 18+ (for web interface)
- Rust toolchain (optional, for contract development)

### Quick Start
```bash
# Install from PyPI
pip install near-swarm

# Or clone the repository
git clone https://github.com/jbarnes850/near-swarm-intelligence
cd near-swarm-intelligence

# Run the quickstart script
./scripts/quickstart.sh
```

### Environment Setup
```bash
# Copy and edit environment variables
cp .env.example .env
```

### Running Demos
```bash
# Run all demos
python near_swarm/examples/demo.py all

# Run specific components
python near_swarm/examples/demo.py voice    # Voice assistant
python near_swarm/examples/demo.py strategy # Multi-agent strategy
```

## 🔧 Core Components

> **Tip**: Start with modifying the examples in `near_swarm/examples/` to understand the framework.

> **Note**: This template runs on NEAR testnet by default for safe development.
> Always test thoroughly before deploying to mainnet.

### System Architecture

```mermaid
graph TB
    %% Core Components
    Core[Agent Core]
    style Core fill:black,stroke:#00C1DE,stroke-width:3px,color:white

    %% Agent Capabilities
    OnChain[Onchain Actions]
    AI[AI Reasoning]
    Memory[Agent Memory]
    style OnChain fill:black,stroke:#00C1DE,stroke-width:2px,color:white
    style AI fill:black,stroke:#00C1DE,stroke-width:2px,color:white
    style Memory fill:black,stroke:#00C1DE,stroke-width:2px,color:white

    %% External Systems
    Blockchain[NEAR Protocol]
    LLM[Language Models]
    Storage[Persistent State]
    style Blockchain fill:#00C1DE,stroke:black,stroke-width:2px,color:black
    style LLM fill:#00C1DE,stroke:black,stroke-width:2px,color:black
    style Storage fill:#00C1DE,stroke:black,stroke-width:2px,color:black

    %% Swarm Intelligence Layer
    subgraph Swarm[AI Swarm]
        direction TB
        Analyzer[Market Analyzer<br/>Identifies Opportunities]
        Risk[Risk Manager<br/>Validates Safety]
        Strategy[Strategy Optimizer<br/>Improves Performance]

        style Analyzer fill:black,stroke:#00C1DE,stroke-width:2px,color:white
        style Risk fill:black,stroke:#00C1DE,stroke-width:2px,color:white
        style Strategy fill:black,stroke:#00C1DE,stroke-width:2px,color:white
    end
    style Swarm fill:none,stroke:#00C1DE,stroke-width:3px,color:white

    %% Consensus Layer
    subgraph Consensus[Consensus System]
        direction TB
        Voting[Voting Mechanism]
        Confidence[Confidence Scoring]
        
        style Voting fill:black,stroke:#00C1DE,stroke-width:2px,color:white
        style Confidence fill:black,stroke:#00C1DE,stroke-width:2px,color:white
    end
    style Consensus fill:none,stroke:#00C1DE,stroke-width:3px,color:white

    %% Core Connections
    Core --> OnChain
    Core --> AI
    Core --> Memory
    Core --> Swarm
    Core --> Consensus

    %% External Connections
    OnChain <--> Blockchain
    AI <--> LLM
    Memory <--> Storage

    %% Swarm Connections
    Analyzer <--> Risk
    Risk <--> Strategy
    Strategy <--> Analyzer

    %% Consensus Connections
    Swarm <--> Consensus
    
    %% Labels
    classDef label fill:none,stroke:none,color:white
    class Core,OnChain,AI,Memory,Blockchain,LLM,Storage,Analyzer,Risk,Strategy,Voting,Confidence label

    %% Title
    classDef title fill:none,stroke:none,color:#00C1DE,font-size:18px
    class Title title
```

### Project Structure
```bash
near-swarm-intelligence/
├── near_swarm/              
│   ├── core/               
│   │   ├── agent.py       
│   │   ├── swarm_agent.py 
│   │   ├── llm_provider.py 
│   │   ├── near_integration.py 
│   │   └── config/        
│   │       ├── agent_roles.json 
│   │       └── swarm_config.json 
│   └── examples/         
│       ├── simple_strategy.py 
│       └── arbitrage_strategy.py 
├── scripts/              
├── tests/               
└── docs/                
```

## 🛠️ Development Guide

### Creating Your First Agent

```python
from near_swarm.core.agent import Agent, AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

# Configure your agent
config = AgentConfig(
    near_network="testnet",
    account_id="your-account.testnet",
    private_key="your-private-key",
    llm_provider="hyperbolic",
    llm_api_key="your-api-key"
)

# Create and start agent
agent = Agent(config)
await agent.start()

# Execute actions
result = await agent.execute_action({
    "type": "transaction",
    "params": {
        "receiver_id": "receiver.testnet",
        "amount": "1.5"
    }
})
```

### Creating a Swarm

```python
# Create swarm configuration
swarm_config = SwarmConfig(
    role="market_analyzer",
    min_confidence=0.7,
    min_votes=2,
    timeout=1.0
)

# Initialize swarm agents
main_agent = SwarmAgent(config, swarm_config)
peer_agent = SwarmAgent(config, SwarmConfig(role="risk_manager"))

# Form swarm
await main_agent.join_swarm([peer_agent])
```

## 📚 Interactive Features

### Voice Commands
- Portfolio queries
- Market analysis
- Transaction requests
- Strategy suggestions

### Chat Commands
- Market Analysis
  ```bash
  /market [symbol]  # Get market analysis
  /trend [timeframe]  # Get trend analysis
  /volume [symbol]  # Volume analysis
  ```

- Risk Management
  ```bash
  /risk [action]  # Risk assessment
  /balance  # Check portfolio balance
  /positions  # List open positions
  ```

- Strategy
  ```bash
  /strategy [action]  # Strategy suggestions
  /portfolio  # Portfolio overview
  ```

- Development Tools
  ```bash
  /ws  # Manage workspace
  /env  # Configure environment
  /config  # View/modify settings
  ```

## 📄 Examples

For more examples and reference implementations, check out our [examples directory](near_swarm/examples/):

- [`simple_strategy.py`](near_swarm/examples/simple_strategy.py) - Basic multi-agent decision making
- [`arbitrage_strategy.py`](near_swarm/examples/arbitrage_strategy.py) - Advanced DEX arbitrage
- [`portfolio_advisor.py`](near_swarm/examples/portfolio_advisor.py) - Voice-powered portfolio management
- [`demo.py`](near_swarm/examples/demo.py) - Interactive demo of all features

Each example includes detailed comments and demonstrates different aspects of the framework.
See our [Examples Guide](docs/examples.md) for detailed walkthroughs.

## 📖 Documentation

- [Core Concepts](docs/core-concepts.md)
- [First Strategy](docs/first-strategy.md)
- [Tutorial](docs/tutorial.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ by the NEAR community
