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

2. Install in development mode:
```bash
pip install -e .
```

## Plugin Issues

### Plugin Loading Errors

**Problem**: "Plugin not found" or loading errors.

**Solution**:
1. Check plugin structure:
```
my-agent/
├── __init__.py
├── agent.yaml     # Must exist
├── plugin.py      # Must exist
└── README.md
```

2. Verify plugin is installed:
```bash
near-swarm plugins list
```

3. Try reinstalling:
```bash
near-swarm plugins remove my-agent
near-swarm plugins install ./my-agent
```

### Plugin Configuration

**Problem**: Invalid plugin configuration.

**Solution**:
1. Validate configuration:
```bash
near-swarm config validate
```

2. Check YAML syntax:
```yaml
# agent.yaml
name: my-agent
description: "Agent description"
version: "0.1.0"
author: "Your Name"

capabilities:
  - capability_one
  - capability_two

llm:
  provider: ${LLM_PROVIDER}
  model: ${LLM_MODEL}
  temperature: 0.7

near:
  network: ${NEAR_NETWORK:-testnet}
  account_id: ${NEAR_ACCOUNT_ID}
  private_key: ${NEAR_PRIVATE_KEY}
```

3. Debug configuration loading:
```bash
near-swarm config show --debug
```

### Plugin Lifecycle

**Problem**: Plugin initialization or cleanup failures.

**Solution**:
1. Implement proper lifecycle methods:
```python
class MyPlugin(AgentPlugin):
    async def initialize(self) -> None:
        try:
            # Initialize resources
            self.llm = self.create_llm_provider(self.config.llm)
            self.near = await self.create_near_connection(self.config.near)
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise PluginError(str(e))
    
    async def cleanup(self) -> None:
        try:
            # Clean up resources
            await self.near.close()
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
```

2. Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
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

3. Load variables:
```bash
source .env
```

### Configuration Validation

**Problem**: Configuration validation errors.

**Solution**:
1. Use configuration models:
```python
from pydantic import BaseModel, Field

class MyConfig(BaseModel):
    name: str
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    temperature: float = Field(ge=0, le=1)
```

2. Validate during loading:
```python
from near_swarm.config import ConfigurationManager

config_manager = ConfigurationManager()
try:
    config = config_manager.load_config("my-agent", MyConfig)
except ConfigError as e:
    print(f"Configuration error: {e}")
```

## Runtime Issues

### LLM Integration

**Problem**: LLM API errors or unexpected responses.

**Solution**:
1. Verify API key:
```python
from near_swarm.llm import LLMProvider

provider = LLMProvider(config.llm)
try:
    await provider.validate_connection()
except LLMError as e:
    print(f"LLM error: {e}")
```

2. Handle API errors:
```python
async def safe_llm_call(self, prompt: str) -> Dict[str, Any]:
    try:
        return await self.llm.query(prompt)
    except LLMError as e:
        self.logger.error(f"LLM call failed: {e}")
        return {"error": str(e)}
```

### NEAR Integration

**Problem**: NEAR blockchain interaction errors.

**Solution**:
1. Test connection:
```python
from near_swarm.near import NEARConnection

near = NEARConnection(config.near)
try:
    await near.validate_connection()
except NEARError as e:
    print(f"NEAR error: {e}")
```

2. Handle transaction errors:
```python
async def safe_transfer(self, recipient: str, amount: str) -> Dict[str, Any]:
    try:
        return await self.near.send_tokens(recipient, amount)
    except NEARError as e:
        self.logger.error(f"Transfer failed: {e}")
        return {"error": str(e)}
```

## Common Error Messages

### "Plugin directory not found"

**Solution**:
1. Check directory structure:
```bash
ls -R my-agent/
```

2. Create plugin with CLI:
```bash
near-swarm create agent my-agent
```

### "Invalid plugin configuration"

**Solution**:
1. Validate YAML syntax
2. Check variable substitution
3. Run validation:
```bash
near-swarm config validate my-agent
```

### "Plugin initialization failed"

**Solution**:
1. Check resource initialization
2. Verify dependencies
3. Enable debug mode:
```bash
near-swarm start my-agent --debug
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
```
