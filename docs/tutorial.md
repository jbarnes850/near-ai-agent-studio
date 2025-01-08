# NEAR Swarm Intelligence Framework Tutorial

Welcome to the NEAR Swarm Intelligence Framework! This tutorial will guide you through building AI-powered agents that can interact with the NEAR blockchain. Whether you're an AI researcher, a Web3 developer, or a crypto-native builder, this guide will help you get started.

## 🎯 What You'll Build

By the end of this tutorial, you'll have:
- Created an AI agent that can interact with NEAR blockchain
- Built a multi-agent swarm system with specialized roles
- Implemented LLM-powered decision making
- Deployed your agents to NEAR testnet
- Added production-ready features

## 🧠 System Prompts

The framework uses role-specific system prompts to guide agent behavior. Here are the core roles:

### Risk Manager
```python
RISK_MANAGER_PROMPT = """As a Risk Manager, evaluate proposals focusing on:
1. Position Size Analysis
2. Security Assessment
3. Risk Metrics
4. Compliance and Limits

Your primary responsibility is protecting assets and maintaining risk parameters."""
```

### Market Analyzer
```python
MARKET_ANALYZER_PROMPT = """As a Market Analyzer, evaluate proposals focusing on:
1. Price Analysis
2. Market Conditions
3. Technical Indicators
4. Cross-market Analysis

Your primary responsibility is market analysis and trend identification."""
```

### Strategy Optimizer
```python
STRATEGY_OPTIMIZER_PROMPT = """As a Strategy Optimizer, evaluate proposals focusing on:
1. Execution Optimization
2. Cost Analysis
3. Performance Metrics
4. Technical Efficiency

Your primary responsibility is optimizing execution and performance."""
```

## 🚀 Quick Start (5 minutes)

```bash
# Install the framework
pip install near-swarm

# Create a new project with interactive wizard
near-swarm create my-first-swarm --interactive

# Start the development environment
cd my-first-swarm
near-swarm dev
```

## 🔧 Prerequisites

- Python 3.12+
- An LLM API key (supports OpenAI, Anthropic, DeepSeek, or bring your own)
- Basic understanding of async Python
- NEAR testnet account (we'll help you create one)

## 🎓 Learning Paths

Choose your path based on your background:

### 🤖 For AI/ML Developers
- Focus on agent architecture and LLM integration
- Skip to the "Customizing Agent Behavior" section
- See examples of different LLM providers

### 🌐 For Web3 Developers
- Focus on NEAR blockchain integration
- Skip to the "NEAR Integration" section
- Learn about transaction handling and smart contracts

### 🏗️ For Full-Stack Developers
- Follow the tutorial sequentially
- Learn both AI and blockchain concepts
- Build end-to-end applications

## 1. Your First Agent (10 minutes)

Let's create your first NEAR agent! We'll build a simple token transfer agent named "TokenBot" that can:
1. Connect to NEAR testnet
2. Check its balance
3. Send NEAR tokens to other accounts

Here's the complete code with line-by-line explanations:

```python
from near_swarm.core.agent import Agent, AgentConfig
import asyncio
import os
from dotenv import load_dotenv

# Define your agent's behavior
TOKENBOT_PROMPT = """You are TokenBot, a NEAR agent specialized in token transfers.
Your responsibilities:
1. Verify transaction parameters
2. Ensure sufficient balance
3. Execute transfers safely
4. Maintain accurate records

Always prioritize security and accuracy in your operations."""

async def main():
    # 1. Load environment variables
    load_dotenv()
    
    # 2. Configure your TokenBot agent
    config = AgentConfig(
        name="TokenBot",
        network="testnet",
        account_id=os.getenv("NEAR_ACCOUNT_ID"),
        private_key=os.getenv("NEAR_PRIVATE_KEY"),
        llm_provider="hyperbolic",
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_model="deepseek-ai/DeepSeek-V3",
        llm_temperature=0.7,
        llm_max_tokens=2000,
        system_prompt=TOKENBOT_PROMPT,
        rpc_url=os.getenv("NEAR_RPC_URL"),  # Optional custom RPC
        use_backup_rpc=True  # Use backup RPC if primary fails
    )
    
    # 3. Create and initialize agent
    async with Agent(config) as token_bot:
        try:
            # 4. Check our balance
            balance = await token_bot.check_balance()
            print(f"TokenBot's balance: {balance} NEAR")
            
            # 5. Send some NEAR tokens
            print("Sending 1.5 NEAR to recipient.testnet...")
            result = await token_bot.send_tokens(
                recipient_id="recipient.testnet",
                amount="1.5"  # 1.5 NEAR
            )
            print(f"Success! Transaction hash: {result['transaction_hash']}")
            
            # 6. Check our new balance
            new_balance = await token_bot.check_balance()
            print(f"New balance after transfer: {new_balance} NEAR")
            
        except RuntimeError as e:
            print(f"Failed to execute operation: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Understanding Each Step

1. **Imports**: We import the necessary classes and utilities
   - `Agent`: The core class for creating NEAR agents
   - `AgentConfig`: Configuration class for setting up the agent
   - `load_dotenv`: Helps load environment variables safely

2. **Configuration**: We set up TokenBot with essential parameters
   - `name`: Identifies your agent in logs and monitoring
   - `network`: Choose between "testnet" (for development) or "mainnet"
   - `account_id`: Your NEAR account that the agent will use
   - `private_key`: The account's private key for signing transactions
   - `llm_*`: AI model configuration for intelligent decision-making

3. **Agent Creation**: We create the TokenBot instance with our config

4. **Starting Up**: The `start()` method:
   - Verifies your NEAR account exists
   - Establishes connection to the network
   - Prepares the agent for operations

5. **Basic Operations**: TokenBot can:
   - Check its balance with `check_balance()`
   - Send tokens with `send_tokens()`
   - Handle errors gracefully

6. **Cleanup**: Always use `close()` to shut down properly

### Environment Setup

Create a `.env` file in your project root with these variables:

```bash
# Required: NEAR account details
NEAR_NETWORK=testnet
NEAR_ACCOUNT_ID=your-account.testnet
NEAR_PRIVATE_KEY=your-private-key

# Required: AI provider details
LLM_PROVIDER=hyperbolic
LLM_API_KEY=your-llm-api-key

# Optional: AI model settings
LLM_MODEL=deepseek-ai/DeepSeek-V3
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

### Running Your Agent

1. Save the code as `token_bot.py`
2. Create and fill your `.env` file
3. Run your agent:
```bash
python token_bot.py
```

You should see output like:
```
Starting TokenBot...
TokenBot's balance: 10.5 NEAR
Sending 1.5 NEAR to recipient.testnet...
Success! Transaction hash: HZBpK...
New balance after transfer: 9.0 NEAR
Shutting down TokenBot...
```

### Error Handling

TokenBot includes built-in error handling:
```python
try:
    await token_bot.start()
except RuntimeError as e:
    print(f"Failed to start TokenBot: {e}")
    # Handle initialization error
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other errors
finally:
    await token_bot.close()
```

Now that you have your first agent running, let's move on to more advanced features!

## 2. NEAR Integration (15 minutes)

Now let's make our agent interact with NEAR blockchain.

```python
from near_swarm import Agent, Config, near
import asyncio

async def main():
    agent = Agent(
        Config(
            name="defi_trader",
            chain="testnet",
            near={
                "account_id": "your-account.testnet",
                "private_key": "${NEAR_PRIVATE_KEY}"  # Use env var
            }
        )
    )

    # Handle blockchain transactions
    @agent.on_transaction
    async def handle_trade(tx):
        """Execute trades on NEAR"""
        # Verify transaction first
        if not await agent.verify_transaction(tx):
            return {"status": "rejected", "reason": "verification_failed"}

        # Execute the trade
        result = await near.execute_transaction(
            tx,
            gas=300_000_000_000_000,  # 300 TGas
            deposit=near.parse_near_amount("1")  # 1 NEAR
        )

        return {"status": "success", "tx_hash": result.transaction_hash}

    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Concepts
- Transaction verification
- Gas management
- Error handling
- Security best practices

## 3. Building a Swarm (20 minutes)

Now let's create a collaborative swarm of specialized agents. Each agent has a specific role and expertise:

```python
from near_swarm.core.agent import Agent, AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
import asyncio
import os
from dotenv import load_dotenv

async def main():
    load_dotenv()
    
    # Base configuration for all agents
    base_config = AgentConfig(
        network="testnet",
        account_id=os.getenv("NEAR_ACCOUNT_ID"),
        private_key=os.getenv("NEAR_PRIVATE_KEY"),
        llm_provider="hyperbolic",
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_model="deepseek-ai/DeepSeek-V3"
    )
    
    # Create specialized agents with their roles
    risk_manager = SwarmAgent(
        config=base_config,
        swarm_config=SwarmConfig(
            role="risk_manager",
            min_confidence=0.8,  # Higher threshold for risk decisions
            min_votes=2
        )
    )
    
    market_analyzer = SwarmAgent(
        config=base_config,
        swarm_config=SwarmConfig(
            role="market_analyzer",
            min_confidence=0.7
        )
    )
    
    strategy_optimizer = SwarmAgent(
        config=base_config,
        swarm_config=SwarmConfig(
            role="strategy_optimizer",
            min_confidence=0.7
        )
    )
    
    # Start all agents
    async with risk_manager, market_analyzer, strategy_optimizer:
        # Form the swarm
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])
        
        try:
            # Example: Propose a trade to the swarm
            proposal_result = await market_analyzer.propose_action(
                action_type="market_trade",
                params={
                    "symbol": "NEAR",
                    "action": "buy",
                    "amount": 100,
                    "market_context": {
                        "current_price": 5.45,
                        "24h_volume": "2.1M",
                        "market_trend": "upward",
                        "volatility": "medium",
                        "gas_price": "low",
                        "network_load": "normal"
                    }
                }
            )
            
            # Check the swarm's decision
            if proposal_result["consensus"]:
                print("\nSwarm approved the trade!")
                print(f"Approval rate: {proposal_result['approval_rate']:.1%}")
                print("\nReasoning from each agent:")
                for reason in proposal_result["reasons"]:
                    print(f"- {reason}")
            else:
                print("\nSwarm rejected the trade")
                print(f"Approval rate: {proposal_result['approval_rate']:.1%}")
                print("\nConcerns raised:")
                for reason in proposal_result["reasons"]:
                    print(f"- {reason}")
                    
        except Exception as e:
            print(f"Error during swarm operation: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Understanding Swarm Behavior

1. **Role-Based Evaluation**
   - Each agent evaluates proposals based on their expertise
   - Risk managers focus on security and exposure
   - Market analyzers assess price and trends
   - Strategy optimizers handle execution details

2. **Consensus Mechanism**
   - Proposals need minimum confidence and votes
   - Each agent provides reasoning for their decision
   - Higher thresholds for critical operations

3. **Market Context**
   - Agents consider current market conditions
   - Includes price, volume, volatility, etc.
   - Network conditions affect decisions

4. **Error Handling**
   - Built-in validation at each step
   - Graceful handling of timeouts
   - Detailed error reporting

### Example Swarm Output

```
Swarm approved the trade!
Approval rate: 83.3%

Reasoning from each agent:
- Risk Manager: Position size within limits, volatility acceptable, no security concerns
- Market Analyzer: Strong upward trend, good volume, favorable entry point
- Strategy Optimizer: Low gas fees, optimal execution route identified
```

## 4. Production Readiness (15 minutes)

Essential features for production deployment.

### Monitoring and Logging

```python
from near_swarm.core.agent import Agent
from near_swarm.core.config import Config
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    config = Config(
        name="production_agent",
        chain="mainnet",
        log_level="INFO"
    )
    
    agent = Agent(config)
    
    # Add health checks
    @agent.on_heartbeat(interval_seconds=60)
    async def health_check():
        """Regular health check for the agent"""
        metrics = await agent.get_metrics()
        logging.info(f"Agent metrics: {metrics}")
        
        if metrics['memory_usage'] > 85:
            logging.warning("High memory usage detected")
            await agent.optimize_memory()

    await agent.start()
```

### Market Data Management

```python
from near_swarm.core.market_data import MarketDataManager

# Initialize market data manager with caching
market_data = MarketDataManager(
    cache_duration=300,  # 5 minutes
    max_requests_per_minute=60
)

# Use in your agent
@agent.on_message
async def handle_market_data(message):
    """Handle market data requests with rate limiting"""
    try:
        data = await market_data.get_price("NEAR/USD")
        return {"status": "success", "data": data}
    except Exception as e:
        logging.error(f"Market data error: {e}")
        return {"status": "error", "message": str(e)}
```

### Transaction Security

```python
from near_swarm.core.near_integration import NEARIntegration
from decimal import Decimal

class TransactionValidator:
    def __init__(self):
        self.max_amount = Decimal("1000")  # Max 1000 NEAR
        self.allowed_tokens = {"NEAR", "USDC.near"}
        
    def validate_transaction(self, tx):
        """Validate transaction parameters"""
        if Decimal(tx.amount) > self.max_amount:
            return False, "Amount exceeds maximum allowed"
            
        if tx.token_id not in self.allowed_tokens:
            return False, "Token not in allowed list"
            
        return True, "Transaction validated"

# Use in your agent
validator = TransactionValidator()

@agent.on_transaction
async def handle_transaction(tx):
    """Handle transaction with validation"""
    is_valid, reason = validator.validate_transaction(tx)
    
    if not is_valid:
        logging.warning(f"Transaction rejected: {reason}")
        return {"status": "rejected", "reason": reason}
        
    # Process valid transaction
    near = NEARIntegration(config.near)
    result = await near.execute_transaction(tx)
    
    return {"status": "success", "tx_hash": result.transaction_hash}
```

## 🎮 Interactive Examples

Try these examples in your development environment:

1. Simple Trading Strategy
```bash
near-swarm run examples/simple_strategy.py
```

2. Arbitrage Strategy
```bash
near-swarm run examples/arbitrage_strategy.py
```

3. Swarm Trading
```bash
near-swarm run examples/swarm_trading.py
```

4. Token Transfer Strategy
```bash
near-swarm run examples/token_transfer_strategy.py
```

## 📚 Next Steps

1. Explore [Core Concepts](core-concepts.md)
2. Try example implementations in `examples/`
3. Join our [Discord Community](https://discord.gg/near)
4. Contribute to the framework
5. Deploy your first agent to mainnet

## 🤝 Need Help?

- Check our [Troubleshooting Guide](troubleshooting.md)
- Join our Discord community
- Open an issue on GitHub
- Read our [API Reference](api-reference.md) 