"""
Custom Agent Plugin Template
Use this template to create your own NEAR swarm agent plugin
"""

from typing import Dict, Any
from near_swarm.plugins.base import AgentPlugin, PluginConfig
from near_swarm.core.agent import AgentConfig
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig

class CustomAgentPlugin(AgentPlugin):
    """Custom agent implementation"""
    
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        # Initialize LLM provider with your custom configuration
        llm_config = LLMConfig(
            provider=self.agent_config.llm_provider,
            api_key=self.agent_config.llm_api_key,
            model=self.agent_config.llm_model,
            temperature=self.agent_config.llm_temperature,
            max_tokens=self.agent_config.llm_max_tokens,
            api_url=self.agent_config.api_url,
            system_prompt=self.plugin_config.system_prompt
        )
        self.llm_provider = create_llm_provider(llm_config)
        
        # Add any custom initialization here
        self.confidence_threshold = self.plugin_config.custom_settings.get(
            'confidence_threshold', 0.7
        )
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate based on your agent's logic"""
        if not self.llm_provider:
            raise RuntimeError("Plugin not initialized")
            
        # Create your custom evaluation prompt
        prompt = f"""[Your custom prompt here]
Context:
{context}

Provide your analysis in JSON format with:
- decision: Your decision (true/false)
- confidence: Your confidence level (0-1)
- reasoning: Detailed explanation
- recommendations: List of actionable items
"""
        
        # Get LLM analysis
        response = await self.llm_provider.query(prompt, expect_json=True)
        
        # Add your custom logic here
        # Example: Filter low confidence responses
        if response.get('confidence', 0) < self.confidence_threshold:
            response['decision'] = False
            response['reasoning'] += "\nConfidence below threshold."
        
        return response
    
    async def cleanup(self) -> None:
        """Clean up plugin resources"""
        if self.llm_provider:
            await self.llm_provider.close()
            self.llm_provider = None
        # Add any custom cleanup here

# Register your plugin
from near_swarm.plugins import register_plugin
register_plugin("custom_agent", CustomAgentPlugin) 