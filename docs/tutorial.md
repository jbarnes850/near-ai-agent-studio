# NEAR Swarm Intelligence Tutorial

This tutorial will guide you through creating your first NEAR swarm intelligence strategy. We'll focus on practical examples that showcase NEAR Protocol's unique capabilities.

## Quick Start

1. Clone and setup the repository:
```bash
git clone https://github.com/your-org/near-swarm-template
cd near-swarm-template
./scripts/quickstart.sh
```

2. The quickstart script will:
   - Set up your Python environment
   - Install dependencies
   - Create a NEAR testnet account
   - Configure your environment
   - Create an example strategy
   - Guide you through using the CLI

## Core Components

### 1. NEAR Integration
The template provides seamless integration with NEAR Protocol:
```python
from near_swarm.core.near_integration import NEARConnection

# Initialize connection
near = NEARConnection(
    network='testnet',
    account_id='your-account.testnet',
    private_key='your-private-key'
)

# Execute transaction
result = await near.execute_transaction(
    receiver_id='app.ref-finance.testnet',
    amount=1.5  # in NEAR
)
```

### 2. Market Data
Built-in market data integration:
```python
from near_swarm.core.market_data import MarketDataManager

# Initialize market data
market = MarketDataManager()

# Get token price
price = await market.get_token_price('NEAR/USDC')
```

### 3. Memory Management
Persistent storage for strategy data:
```python
from near_swarm.core.memory_manager import MemoryManager

# Initialize memory
memory = MemoryManager()

# Store and retrieve data
await memory.store('last_trade', {'price': 3.50, 'volume': 1000})
data = await memory.retrieve('last_trade')
```

## Creating Your First Strategy

1. Initialize a new strategy:
```bash
./scripts/near-swarm init arbitrage --name my-strategy
```

2. Review the generated files:
```
my-strategy/
├── strategy.py      # Main strategy logic
├── config.json     # Strategy configuration
└── .env           # Environment variables
```

3. Configure your strategy in `config.json`:
```json
{
  "strategy_type": "arbitrage",
  "name": "my-strategy",
  "parameters": {
    "token_pairs": ["NEAR/USDC"],
    "exchanges": ["ref-finance", "jumbo"],
    "min_profit": 0.002,
    "max_position": 1000
  }
}
```

4. Run your strategy:
```bash
cd my-strategy
./scripts/near-swarm run
```

## Example: Simple Arbitrage Strategy

Here's a complete example of an arbitrage strategy:

```python
from near_swarm.core.agent import BaseAgent
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.memory_manager import MemoryManager

class ArbitrageStrategy(BaseAgent):
    def __init__(self, config):
        self.config = config
        self.market = MarketDataManager()
        self.memory = MemoryManager()
    
    async def find_opportunity(self, pair):
        # Get prices from exchanges
        prices = await self.market.get_prices(
            pair=pair,
            exchanges=self.config.exchanges
        )
        
        # Find best prices
        best_bid = max(prices, key=lambda x: x['bid'])
        best_ask = min(prices, key=lambda x: x['ask'])
        
        # Calculate profit
        profit_pct = (best_bid['bid'] - best_ask['ask']) / best_ask['ask']
        
        if profit_pct > self.config.min_profit:
            return {
                'buy_exchange': best_ask['exchange'],
                'sell_exchange': best_bid['exchange'],
                'profit_pct': profit_pct,
                'amount': min(
                    self.config.max_position,
                    best_ask['liquidity'],
                    best_bid['liquidity']
                )
            }
        return None
    
    async def execute_trade(self, opportunity):
        try:
            # Record start of trade
            await self.memory.store('trade_start', {
                'timestamp': time.time(),
                'opportunity': opportunity
            })
            
            # Execute trades
            buy_result = await self.near.swap_tokens(
                exchange=opportunity['buy_exchange'],
                token_in='USDC',
                token_out='NEAR',
                amount=opportunity['amount']
            )
            
            sell_result = await self.near.swap_tokens(
                exchange=opportunity['sell_exchange'],
                token_in='NEAR',
                token_out='USDC',
                amount=buy_result['received_amount']
            )
            
            # Record results
            await self.memory.store('trade_result', {
                'success': True,
                'profit': sell_result['received_amount'] - opportunity['amount'],
                'gas_used': buy_result['gas_used'] + sell_result['gas_used']
            })
            
            return True
            
        except Exception as e:
            await self.memory.store('trade_error', {
                'error': str(e),
                'opportunity': opportunity
            })
            return False
```

## CLI Commands

The `near-swarm` CLI provides several commands:

```bash
# Create new strategy
near-swarm init arbitrage --name my-strategy

# List available strategies
near-swarm list

# Run a strategy
near-swarm run

# Run strategy tests
near-swarm test

# Monitor performance
near-swarm monitor
```

## Best Practices

1. **Error Handling**
   - Always use try/except blocks for network operations
   - Store error information for analysis
   - Implement proper cleanup on errors

2. **Gas Management**
   - Set reasonable gas limits
   - Include gas costs in profit calculations
   - Monitor gas usage patterns

3. **Testing**
   - Test on testnet first
   - Use the built-in test framework
   - Monitor initial trades closely

## Next Steps

1. Review example strategies in `examples/`
2. Customize strategy parameters
3. Add additional token pairs
4. Implement your own strategy logic

Remember: Always test thoroughly on testnet before deploying to mainnet with real funds. 