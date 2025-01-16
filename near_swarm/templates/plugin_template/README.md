# NEAR Agent Template

This template helps you create specialized agents for the NEAR ecosystem. It includes built-in support for market analysis, strategy optimization, and custom agent roles.

## Available Roles

### Market Analyzer
The market analyzer role focuses on monitoring NEAR token prices and market conditions. It provides:
- Real-time price analysis
- Market sentiment evaluation
- Risk assessment
- Trend identification

Example configuration:
```yaml
name: price-monitor
role: market_analyzer
market_data:
  update_interval: 300  # 5 minutes
  confidence_threshold: 0.7
  risk_threshold: 0.8
```

### Strategy Optimizer
The strategy optimizer role evaluates market opportunities and makes strategic decisions. It provides:
- Trading strategy recommendations
- Risk mitigation steps
- Confidence-based decisions
- Performance optimization

Example configuration:
```yaml
name: decision-maker
role: strategy_optimizer
strategy:
  min_confidence: 0.8
  max_exposure: 0.2
  risk_tolerance: medium
```

## Configuration

### Required Environment Variables
```bash
# LLM Provider (required)
export LLM_PROVIDER=hyperbolic
export LLM_API_KEY=your_api_key
export LLM_MODEL=meta-llama/llama-3.3-70B-instruct

# NEAR Network (optional)
export NEAR_NETWORK=testnet
export NEAR_ACCOUNT_ID=your.testnet
export NEAR_PRIVATE_KEY=your_private_key
```

### Agent Configuration (agent.yaml)
The `agent.yaml` file defines your agent's behavior:
```yaml
name: your_agent_name
role: market_analyzer  # or strategy_optimizer

# LLM Settings
llm_provider: ${LLM_PROVIDER}
llm_api_key: ${LLM_API_KEY}
llm_model: ${LLM_MODEL}
llm_temperature: 0.7
llm_max_tokens: 1000

# Role-specific settings...
```

## Usage

### Creating an Agent
```bash
# Create a market analyzer
near-swarm create agent price-monitor --role market_analyzer

# Create a strategy optimizer
near-swarm create agent decision-maker --role strategy_optimizer
```

### Running Agents
```bash
# Run a single agent
near-swarm run price-monitor

# Run multiple agents together
near-swarm run price-monitor decision-maker
```

### Development

1. Implement your agent logic in `plugin.py`
2. Configure settings in `agent.yaml`
3. Test your agent:
```bash
# Run with debug logging
RUST_LOG=debug near-swarm run your-agent

# Run with a specific operation
near-swarm execute your-agent --operation custom_action
```

## Best Practices

1. **Error Handling**
   - Always handle API errors gracefully
   - Provide meaningful error messages
   - Implement retry logic for transient failures

2. **Resource Management**
   - Clean up resources in the `cleanup()` method
   - Use async context managers for external connections
   - Monitor memory usage for long-running agents

3. **Configuration**
   - Use environment variables for sensitive data
   - Document all configuration options
   - Provide sensible defaults

4. **Testing**
   - Write unit tests for your agent logic
   - Test with different market conditions
   - Validate error handling and edge cases 