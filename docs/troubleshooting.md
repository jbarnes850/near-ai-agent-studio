# Troubleshooting Guide

This guide helps you resolve common issues when working with the NEAR Swarm Intelligence framework.

## Installation Issues

### Python Version Error

**Problem**: Error about Python version compatibility.

**Solution**:
1. Check your Python version:
```bash
python --version
```

2. Install Python 3.12+:
```bash
# macOS
brew install python@3.12

# Ubuntu
sudo apt update
sudo apt install python3.12
```

### Package Dependencies

**Problem**: Missing dependencies or version conflicts.

**Solution**:
1. Update pip:
```bash
python -m pip install --upgrade pip
```

2. Install with dependencies:
```bash
pip install near-swarm[all]
```

## Configuration Issues

### Environment Variables

**Problem**: "Environment variable not set" errors.

**Solution**:
1. Check `.env` file exists:
```bash
ls -la .env
```

2. Verify required variables:
```bash
NEAR_NETWORK=testnet
NEAR_ACCOUNT_ID=your-account.testnet
NEAR_PRIVATE_KEY=your-private-key
LLM_PROVIDER=hyperbolic
LLM_API_KEY=your-api-key
LLM_MODEL=deepseek-ai/DeepSeek-V3
```

3. Load variables:
```bash
source .env
```

### API Key Issues

**Problem**: "Invalid API key" or authentication errors.

**Solution**:
1. Verify API key format
2. Check key permissions
3. Ensure key is active
4. Try regenerating key

## Runtime Issues

### Connection Errors

**Problem**: Cannot connect to NEAR network or API services.

**Solution**:
1. Check network connection
2. Verify NEAR RPC endpoint:
```python
# In your code
from near_swarm.core.near import NearConnection

connection = NearConnection(network="testnet")
await connection.health_check()
```

3. Test API connectivity:
```python
from near_swarm.core.llm_provider import LLMProvider

provider = LLMProvider()
await provider.test_connection()
```

### Memory Issues

**Problem**: Out of memory errors during agent operations.

**Solution**:
1. Reduce batch sizes
2. Implement pagination
3. Clear cache regularly:
```python
from near_swarm.core.market_data import MarketDataManager

market_data = MarketDataManager()
await market_data.clear_cache()
```

### Performance Issues

**Problem**: Slow response times or high latency.

**Solution**:
1. Enable caching:
```python
market_data = MarketDataManager(
    cache_ttl=300,  # 5 minutes
    rate_limit=10   # 10 requests/minute
)
```

2. Optimize batch sizes:
```python
# Process in smaller batches
async def process_batch(items, batch_size=10):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        await process_items(batch)
```

## Agent Issues

### Consensus Failures

**Problem**: Agents cannot reach consensus.

**Solution**:
1. Check confidence thresholds:
```python
swarm_config = SwarmConfig(
    min_confidence=0.7,  # Adjust as needed
    min_votes=2
)
```

2. Review agent logs:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

3. Monitor agent states:
```python
async def monitor_agents(swarm):
    states = await swarm.get_agent_states()
    for agent_id, state in states.items():
        print(f"Agent {agent_id}: {state}")
```

### Invalid Responses

**Problem**: Agents return unexpected or invalid responses.

**Solution**:
1. Validate inputs:
```python
from pydantic import BaseModel, Field

class MarketAnalysis(BaseModel):
    symbol: str
    price: float = Field(gt=0)
    confidence: float = Field(ge=0, le=1)
```

2. Add error handling:
```python
try:
    result = await agent.analyze_market(symbol)
except ValueError as e:
    logger.error(f"Invalid market data: {e}")
    result = None
```

## Common Error Messages

### "No module named 'near_swarm'"

**Solution**:
1. Check installation:
```bash
pip list | grep near-swarm
```

2. Install in development mode:
```bash
pip install -e .
```

### "LLM API rate limit exceeded"

**Solution**:
1. Implement rate limiting:
```python
from near_swarm.core.utils import RateLimiter

limiter = RateLimiter(max_calls=10, time_window=60)
async with limiter:
    result = await llm.generate(prompt)
```

2. Use caching:
```python
from near_swarm.core.cache import Cache

cache = Cache()
result = await cache.get_or_set(
    key="market_analysis",
    func=analyze_market,
    ttl=300
)
```

## Getting Help

1. Check documentation:
   - [Tutorial](tutorial.md)
   - [Core Concepts](core-concepts.md)
   - [API Reference](api-reference.md)

2. Search issues:
   - [GitHub Issues](https://github.com/jbarnes850/near_swarm_intelligence/issues)

3. Join community:
   - [Discord](https://discord.gg/near)
   - [Forum](https://gov.near.org)

4. Debug tools:
```python
# Enable debug logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use debug mode
agent = SwarmAgent(config, debug=True)
```
