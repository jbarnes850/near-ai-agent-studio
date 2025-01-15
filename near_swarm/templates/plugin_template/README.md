# NEAR Swarm Agent Plugin Template

This template helps you create custom agents for the NEAR Swarm Intelligence framework.

## Getting Started

1. Copy this template directory:
```bash
near-swarm create agent my-agent
```

2. Configure your agent in `agent.yaml`:
- Set your agent's name and role
- Define capabilities
- Configure LLM settings
- Add custom settings

3. Implement your agent logic in `plugin.py`:
- Customize the evaluation logic
- Add your own methods
- Configure LLM prompts
- Add custom initialization

## Plugin Structure
```
my-agent/
├── __init__.py
├── agent.yaml     # Agent configuration
├── plugin.py      # Agent implementation
└── README.md      # Documentation
```

## Configuration (agent.yaml)
```yaml
name: my_agent
role: custom_role
capabilities:
  - capability_1
  - capability_2
llm:
  system_prompt: |
    Your custom prompt here
settings:
  your_setting: value
```

## Implementation (plugin.py)
Key methods to implement:
- `initialize()`: Set up your agent
- `evaluate()`: Main logic
- `cleanup()`: Resource cleanup

Example:
```python
async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """Your custom evaluation logic"""
    # Get LLM analysis
    response = await self.llm_provider.query(your_prompt)
    
    # Add custom processing
    result = process_response(response)
    
    return result
```

## Usage
```python
from near_swarm.plugins import get_plugin
from near_swarm.core.agent import AgentConfig

# Create configuration
config = AgentConfig(...)

# Load your plugin
plugin = await plugin_loader.load_plugin("my_agent", config)

# Use your plugin
result = await plugin.evaluate(context)
```

## Best Practices
1. Keep your agent focused on a specific role
2. Use clear, descriptive prompts
3. Handle errors gracefully
4. Clean up resources properly
5. Document your agent's capabilities
6. Add type hints and docstrings
7. Follow NEAR's coding standards

## Testing
Create tests in `tests/`:
```python
async def test_my_agent():
    plugin = MyAgentPlugin(config)
    result = await plugin.evaluate(test_context)
    assert result["decision"] is not None
```

## Contributing
Share your agent with the community:
1. Fork the repository
2. Create your agent
3. Add documentation
4. Submit a pull request

## Support
- Documentation: [docs.near.org](https://docs.near.org)
- Discord: [NEAR Discord](https://near.chat)
- GitHub: [NEAR Protocol](https://github.com/near) 