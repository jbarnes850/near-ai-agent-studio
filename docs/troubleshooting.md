# Troubleshooting Guide

## Common Issues and Solutions

### Setup Issues

#### Python Environment

```bash
❌ Error: Python 3 is required but not found
```

**Solution:**

1. Install Python 3:

   - macOS: `brew install python3`
   - Ubuntu: `sudo apt install python3`
   - Windows: Download from python.org

#### NEAR CLI

```bash
❌ Error: near command not found
```

**Solution:**

1. Install Node.js first:

   ```bash
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

2. Install NEAR CLI:

   ```bash
   npm install -g near-cli
   ```

#### Wallet Creation

```bash
❌ Error: Failed to create NEAR account
```

**Solution:**

1. Check internet connection
2. Verify testnet is operational: https://explorer.testnet.near.org
3. Try manual creation:

   ```bash
   near create-account your-account.testnet --masterAccount testnet
   ```

### Runtime Issues

#### Market Data

```bash
❌ Error: Failed to fetch market data
```

**Solution:**

1. Check API endpoints in `.env`
2. Verify internet connection
3. Try with backup data source:

   ```python
   # In your strategy
   try:
       price = await self.market.get_token_price("NEAR")
   except:
       price = await self.market.get_backup_price("NEAR")
   ```

#### Memory Management

```bash
❌ Error: Memory limit exceeded
```

**Solution:**

1. Adjust memory settings in `.env`:

   ```env
   MAX_MEMORY_ENTRIES=500
   MEMORY_PRUNING_THRESHOLD=0.7
   ```

2. Implement custom pruning:

   ```python
   await memory.prune(
       category="market_data",
       older_than_hours=24
   )
   ```

#### Gas Issues

```bash
❌ Error: Insufficient gas
```

**Solution:**

1. Adjust gas settings:

   ```python
   await near.call_contract(
       contract_id="contract.testnet",
       method_name="method",
       args={},
       gas=300_000_000_000_000  # 300 TGas
   )
   ```

2. Use gas estimation:

   ```python
   gas = await near.estimate_gas(
       contract_id="contract.testnet",
       method_name="method",
       args={}
   )
   gas = int(gas * 1.2)  # Add 20% buffer
   ```

## Customization Examples

### 1. Custom Market Data Source

```python
from src.market_data import MarketDataManager

class CustomMarketData(MarketDataManager):
    async def get_token_price(self, token: str) -> float:
        # Your custom implementation
        price = await self.fetch_from_custom_source(token)
        await self.cache.set(f"price_{token}", price)
        return price
        
    async def fetch_from_custom_source(self, token: str) -> float:
        # Implement your data fetching logic
        pass
```

### 2. Custom Strategy Template

```python
from near_swarm.core.agent import BaseAgent

class CustomStrategy(BaseAgent):
    async def analyze_opportunity(self, pair: str):
        # Get market data
        price_data = await self.market.get_market_stats(pair)
        
        # Your custom analysis
        if self._is_profitable(price_data):
            return {
                "action": "execute",
                "params": self._prepare_execution(price_data)
            }
        return None
        
    def _is_profitable(self, data: dict) -> bool:
        # Your profitability logic
        return data['profit_potential'] > self.config.min_profit
        
    def _prepare_execution(self, data: dict) -> dict:
        # Your execution preparation
        return {
            "amount": self.calculate_position_size(data['profit_potential']),
            "params": data['execution_params']
        }
```

### 3. Custom Memory Storage

```python
from near_swarm.core.memory_manager import MemoryManager
import redis

class RedisMemoryManager(MemoryManager):
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        
    async def store(self, category: str, data: dict):
        key = f"{category}:{data['timestamp']}"
        await self.redis.set(key, json.dumps(data))
        
    async def retrieve(self, category: str, limit: int = 10):
        keys = await self.redis.keys(f"{category}:*")
        data = []
        for key in keys[:limit]:
            value = await self.redis.get(key)
            data.append(json.loads(value))
        return data
```

## Best Practices

### 1. Error Handling

```python
try:
    result = await self.execute_trade(params)
except NEARException as e:
    logger.error(f"NEAR error: {str(e)}")
    await self.handle_near_error(e)
except MarketDataException as e:
    logger.error(f"Market data error: {str(e)}")
    await self.use_backup_data()
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    await self.emergency_shutdown()
```

### 2. Logging

```python
import structlog

logger = structlog.get_logger()

logger.info("strategy_started", 
    strategy="arbitrage",
    pairs=["NEAR/USDC"],
    timestamp=datetime.now().isoformat()
)
```

### 3. Testing

```python
# test_strategy.py
async def test_opportunity_analysis():
    strategy = CustomStrategy(config)
    opportunity = await strategy.analyze_opportunity("NEAR/USDC")
    
    assert opportunity is not None
    assert opportunity['action'] == "execute"
    assert 0 < opportunity['params']['amount'] <= config.max_position
```

## Getting Help

1. Check the logs:

   ```bash
   tail -f logs/strategy.log
   ```

2. Run diagnostics:

   ```bash
   ./scripts/verify_all.sh
   ```
3. Join our Discord community: https://discord.gg/near

4. Open an issue: https://github.com/jbarnes850/near-swarm-intelligence/issues
