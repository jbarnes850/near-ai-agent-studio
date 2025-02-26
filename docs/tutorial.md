# NEAR Swarm Intelligence Framework Tutorial

Welcome to the NEAR Swarm Intelligence Framework! This tutorial will guide you through building AI-powered agents that can interact with the NEAR blockchain using our plugin-based architecture.

## 🎯 What You'll Build

By the end of this tutorial, you'll have:

- Created a custom agent plugin
- Configured your agent using YAML
- Integrated with the NEAR blockchain
- Added LLM-powered decision making
- Deployed your agent to NEAR testnet

## 🔧 Prerequisites

- Python 3.12+
- Git
- An LLM API key (supports OpenAI, Anthropic, DeepSeek, or bring your own)
- Basic understanding of async Python
- NEAR testnet account (we'll help you create one)

## ⚙️ Setup and Configuration

### Quick Start (Recommended)

```bash
# Clone and setup
git clone https://github.com/jbarnes850/near-ai-agent-studio
cd near-ai-agent-studio
chmod +x scripts/quickstart.sh
./scripts/quickstart.sh
```

The quickstart script will automatically:

1. Set up your development environment
2. Create a NEAR testnet account
3. Install example agents
4. Verify all integrations
5. Launch an interactive assistant

### Manual Configuration

If you prefer manual setup, create a `.env` file:

```bash
# Required: NEAR Configuration
NEAR_NETWORK=testnet
NEAR_ACCOUNT_ID=your-account.testnet
NEAR_PRIVATE_KEY=your-private-key
NEAR_RPC_URL=https://rpc.testnet.fastnear.com/  # Optional

# Required: LLM Configuration
LLM_PROVIDER=hyperbolic  # hyperbolic, openai, anthropic, or deepseek
LLM_API_KEY=your-api-key
LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct  # Optional
LLM_TEMPERATURE=0.7  # Optional
LLM_MAX_TOKENS=2000  # Optional
```

### Plugin Configuration (agent.yaml)

```yaml
name: my-agent
description: "Agent description"
version: "0.1.0"
author: "Your Name"

# LLM Configuration
llm:
  provider: ${LLM_PROVIDER}
  model: ${LLM_MODEL}
  temperature: 0.7
  max_tokens: 2000
  system_prompt: |
    You are an AI agent specialized in NEAR operations.

# NEAR Configuration
near:
  network: ${NEAR_NETWORK:-testnet}
  account_id: ${NEAR_ACCOUNT_ID}
  private_key: ${NEAR_PRIVATE_KEY}
  rpc_url: ${NEAR_RPC_URL:-""}
  use_backup_rpc: true

# Agent capabilities
capabilities:
  - token_transfer
  - balance_check
  - transaction_validation

# Custom settings
settings:
  min_confidence_threshold: 0.7
  risk_tolerance: medium
  max_retries: 3
```

## 📚 Command Reference

```bash
# Create Components
near-swarm create agent my-agent     # Create new agent
near-swarm create project my-project # Create new project
near-swarm create strategy my-strategy # Create new strategy

# Manage Plugins
near-swarm plugins list              # List available plugins
near-swarm plugins install ./my-plugin # Install a plugin
near-swarm plugins update my-plugin  # Update a plugin

# Run Agents
near-swarm run my-agent             # Run single agent
near-swarm run price-monitor decision-maker # Run multiple agents
near-swarm execute my-agent --operation check_balance # Execute operation

# Configuration
near-swarm config init              # Initialize configuration
near-swarm config validate          # Validate configuration
near-swarm config show              # Show current configuration
```

## 🎓 Learning Paths

Choose your path based on your background:

### 🤖 For AI/ML Developers

- Focus on agent plugins and LLM integration
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

## 1. Your First Agent Plugin (10 minutes)

Let's create your first NEAR agent plugin! We'll build a simple token transfer agent named "TokenBot" that can:

1. Connect to NEAR testnet
2. Check its balance
3. Send NEAR tokens to other accounts

### Step 1: Create Plugin Structure

```bash
near-swarm create agent token-bot
cd token-bot
```

This creates:

```bash
token-bot/
├── __init__.py
├── agent.yaml     # Agent configuration
├── plugin.py      # Agent implementation
└── README.md      # Documentation
```

### Step 2: Configure Your Agent

Edit `agent.yaml`:

```yaml
name: token-bot
description: "A simple token transfer agent for NEAR blockchain"
version: "0.1.0"
author: "Your Name"

# LLM Configuration
llm:
  provider: ${LLM_PROVIDER}
  model: ${LLM_MODEL}
  temperature: 0.7
  max_tokens: 2000
  system_prompt: |
    You are TokenBot, a NEAR agent specialized in token transfers.
    Your responsibilities:
    1. Verify transaction parameters
    2. Ensure sufficient balance
    3. Execute transfers safely
    4. Maintain accurate records

# NEAR Configuration
near:
  network: ${NEAR_NETWORK:-testnet}
  account_id: ${NEAR_ACCOUNT_ID}
  private_key: ${NEAR_PRIVATE_KEY}
  rpc_url: ${NEAR_RPC_URL:-""}
  use_backup_rpc: true

# Agent capabilities
capabilities:
  - token_transfer
  - balance_check
  - transaction_validation
  - error_handling

# Custom settings
settings:
  min_confidence_threshold: 0.7
  risk_tolerance: medium
  max_retries: 3
  timeout: 30
  min_profit_threshold: 0.002  # 0.2% minimum profit
  max_position_size: 10000  # Maximum position size in USD
```

### Step 3: Implement Your Agent

Edit `plugin.py`:

```python
from typing import Dict, Any
from near_swarm.plugins.base import AgentPlugin
from near_swarm.core.exceptions import AgentError

class TokenBotPlugin(AgentPlugin):
    async def initialize(self) -> None:
        """Initialize resources for the agent."""
        # Create LLM provider
        self.llm = self.create_llm_provider(self.config.llm)
        
        # Initialize NEAR connection
        self.near = await self.create_near_connection(self.config.near)
        
        self.logger.info("TokenBot initialized successfully")
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming requests and execute operations."""
        try:
            operation = context.get("operation")
            if operation == "check_balance":
                balance = await self.near.get_balance()
                return {"balance": balance}
                
            elif operation == "send_tokens":
                recipient = context.get("recipient")
                amount = context.get("amount")
                
                # Validate parameters with LLM
                validation = await self.llm.validate_transfer(
                    recipient=recipient,
                    amount=amount
                )
                
                if not validation["is_valid"]:
                    raise AgentError(validation["reason"])
                
                # Execute transfer
                result = await self.near.send_tokens(
                    recipient_id=recipient,
                    amount=amount
                )
                return result
                
            else:
                raise AgentError(f"Unknown operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"Operation failed: {e}")
            raise AgentError(str(e))
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        await self.near.close()
        self.logger.info("TokenBot cleaned up successfully")
```

### Step 4: Environment Setup

Create a `.env` file in your project root:

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
```

### Step 5: Run Your Agent

1. Install your agent plugin:

```bash
near-swarm plugins install ./token-bot
```

2. Validate configuration:

```bash
near-swarm config validate
```

3. Start the agent:

```bash
near-swarm dev
```

You should see output like:

```bash
Loading plugin: token-bot
Initializing TokenBot...
TokenBot initialized successfully
Agent is running. Use Ctrl+C to stop.
```

### Step 6: Test Your Agent

Use the CLI to interact with your agent:

```bash
# Check balance
near-swarm execute token-bot --operation check_balance

# Send tokens
near-swarm execute token-bot \
  --operation send_tokens \
  --recipient recipient.testnet \
  --amount 1.5
```

### Error Handling

The plugin system provides built-in error handling:

- `AgentError`: For expected operational errors
- `PluginError`: For plugin lifecycle errors
- `ConfigError`: For configuration issues

Example error handling in your plugin:

```python
from near_swarm.core.exceptions import AgentError

async def evaluate(self, context):
    try:
        # Your logic here
        pass
    except ValueError as e:
        raise AgentError(f"Invalid input: {e}")
    except Exception as e:
        self.logger.error(f"Unexpected error: {e}")
        raise AgentError("Internal error occurred")
```

Now that you have your first agent plugin running, let's move on to more advanced features!

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
near-swarm run simple-strategy
```

2. Arbitrage Strategy

```bash
near-swarm run arbitrage-strategy
```

3. Swarm Trading

```bash
near-swarm run swarm-trading
```

4. Token Transfer Strategy

```bash
near-swarm run token-transfer
```

## 📚 Next Steps

1. Explore [Core Concepts](core-concepts.md)
2. Try example implementations in `examples/`
3. Join our [Discord Community](https://discord.gg/near)
4. Contribute to the framework
5. Deploy your first agent to mainnet

### Transaction Handling and Error Recovery

When executing transactions through your agent, the framework provides built-in retry logic and error handling:

```python
# Example transaction execution with automatic retry
async def execute_transfer(self, recipient: str, amount: float) -> dict:
    """Execute a token transfer with built-in retry logic."""
    try:
        result = await self.near.send_transaction(
            receiver_id=recipient,
            amount=amount
        )
        return {
            "status": "success",
            "transaction_id": result["transaction_id"],
            "explorer_url": result["explorer_url"]
        }
    except Exception as e:
        self.logger.error(f"Transaction failed: {str(e)}")
        raise AgentError(f"Transfer failed: {str(e)}")
```

The framework automatically handles:

- Nonce management and retries
- Transaction status tracking
- Error reporting and logging
- Explorer URL generation

Key transaction behaviors:

- Maximum 3 retry attempts for failed transactions
- Exponential backoff between retries
- Automatic nonce handling through near-api-py
- Clear status reporting and error messages

### Common Transaction Issues

When implementing transaction logic, be aware of these common scenarios:

1. **Nonce Errors**
   - The framework automatically handles nonce conflicts
   - Retries with exponential backoff
   - No manual nonce management needed

2. **Transaction Timing**
   - Transactions require >75% confidence to execute
   - Initial runs typically suggest "Hold" positions
   - Clear logging indicates transaction status

3. **Error Recovery**
   - Automatic retry for recoverable errors
   - Clear error messages for debugging
   - Transaction status available in explorer

Example agent output during transaction:

```bash
✨ High Confidence Decision:
• Action: Buy NEAR tokens
• Confidence: 85%

🔄 Preparing to execute transaction...
✅ Transaction Successfully Executed!
• Transaction Hash: HbP7yJMfGfHKWxV5FjHtu2Vk5TZ3eJKPDXvW9YfR1Wk3
• Explorer URL: https://testnet.nearblocks.io/txns/HbP7yJMfGfHKWxV5FjHtu2Vk5TZ3eJKPDXvW9YfR1Wk3
```
