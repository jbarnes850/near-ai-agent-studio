# Core Concepts

## Overview

NEAR Swarm Intelligence is a framework for building AI-powered multi-agent systems that can collaborate to make intelligent decisions. The framework leverages large language models (LLMs) through the Hyperbolic API and integrates with the NEAR blockchain for secure and transparent operations.

## Key Components

### 1. Plugin System

The plugin system is the core of agent extensibility:
- Plugins define agent behavior and capabilities
- Easy to create custom agents
- Hot-reloadable during runtime
- Configurable through YAML

#### Plugin Structure
```
my_agent/
├── __init__.py
├── agent.yaml     # Agent configuration
├── plugin.py      # Agent implementation
└── README.md      # Documentation
```

#### Example Plugin
```python
from near_swarm.plugins.base import AgentPlugin

class CustomAgent(AgentPlugin):
    async def initialize(self) -> None:
        # Initialize resources
        self.llm_provider = create_llm_provider(self.config.llm)
        
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Implement agent logic
        response = await self.llm_provider.query(your_prompt)
        return self.process_response(response)
```

### 2. Configuration System

The framework uses a flexible configuration system:
- Multiple configuration sources
- Environment variable support
- Variable substitution
- Validation through Pydantic

#### Configuration Precedence
1. CLI arguments
2. Environment variables
3. Configuration file
4. Default values

#### Example Configuration
```yaml
name: my_agent
role: market_analysis
capabilities:
  - price_analysis
  - trend_detection
llm:
  provider: ${LLM_PROVIDER}
  model: ${LLM_MODEL}
  temperature: 0.7
```

### 3. Built-in Agents

The framework includes specialized agents:

1. **Market Analyzer**
   ```python
   # Example market analysis
   async def evaluate(self, context):
       market_data = context.get('market_data', {})
       sentiment_data = context.get('sentiment_data', {})
       return await self.analyze_market(market_data, sentiment_data)
   ```

2. **Risk Manager**
   ```python
   # Example risk assessment
   async def evaluate(self, context):
       portfolio = context.get('portfolio', {})
       proposed_trades = context.get('proposed_trades', [])
       return await self.assess_risk(portfolio, proposed_trades)
   ```

### 4. CLI Tools

Comprehensive CLI for development:
```bash
# Create new components
near-swarm create agent my-agent
near-swarm create strategy my-strategy

# Manage plugins
near-swarm plugins install my-plugin
near-swarm plugins list
near-swarm plugins update my-plugin

# Configuration
near-swarm config init
near-swarm config validate
near-swarm config show
```

## Architecture

```
near_swarm/
├── core/                    # Core system
├── templates/              # Templates for new components
├── plugins/               # Plugin system
│   ├── base.py           # Plugin base classes
│   └── loader.py         # Plugin loading logic
├── agents/                # Built-in agents
│   ├── market_analyzer/   # Market analysis
│   ├── risk_manager/     # Risk management
│   └── custom/           # User agents
├── config/               # Configuration
│   ├── schema.py        # Config schemas
│   └── loader.py        # Config loading
└── cli/                  # CLI tools
    ├── create.py        # Creation commands
    └── plugins.py       # Plugin management
```

## Best Practices

1. **Plugin Development**
   - Use the plugin template
   - Follow type hints
   - Add comprehensive docstrings
   - Include plugin documentation

2. **Configuration Management**
   - Use environment variables for secrets
   - Validate configurations
   - Keep settings modular
   - Use variable substitution

3. **Agent Design**
   - Focus on single responsibility
   - Handle errors gracefully
   - Clean up resources properly
   - Log important decisions

4. **Development Workflow**
   - Start with example agents
   - Test on testnet first
   - Use the CLI tools
   - Follow the plugin structure

## Security Considerations

1. **API Keys**
   - Use environment variables
   - Never commit secrets
   - Rotate regularly
   - Validate in config

2. **Plugin Safety**
   - Validate plugin sources
   - Review third-party plugins
   - Test in isolation
   - Monitor resource usage

3. **Error Handling**
   - Graceful degradation
   - Resource cleanup
   - Comprehensive logging
   - Alert mechanisms

## Next Steps

1. Follow the [Tutorial](tutorial.md)
2. Create your first plugin
3. Join the developer community
4. Contribute to the framework
