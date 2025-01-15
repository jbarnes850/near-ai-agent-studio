"""
Example Market Analyzer Plugin
Demonstrates how to implement a custom agent plugin
"""

from typing import Dict, Any
from near_swarm.plugins.base import AgentPlugin, PluginConfig
from near_swarm.core.agent import AgentConfig
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig

class MarketAnalyzerPlugin(AgentPlugin):
    """Market analysis plugin implementation"""
    
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        # Initialize LLM provider
        llm_config = LLMConfig(
            provider=self.agent_config.llm_provider,
            api_key=self.agent_config.llm_api_key,
            model=self.agent_config.llm_model,
            temperature=self.agent_config.llm_temperature,
            max_tokens=self.agent_config.llm_max_tokens,
            api_url=self.agent_config.api_url,
            system_prompt=self.plugin_config.system_prompt or """You are a specialized market analysis agent.
Your role is to analyze market conditions and provide insights."""
        )
        self.llm_provider = create_llm_provider(llm_config)
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate market conditions"""
        if not self.llm_provider:
            raise RuntimeError("Plugin not initialized")
            
        # Create evaluation prompt
        prompt = f"""Analyze the following market conditions:
Market Context:
{context.get('market_context', {})}

Provide your analysis in JSON format with:
- trend: Current market trend
- confidence: Your confidence level (0-1)
- reasoning: Detailed explanation
- recommendations: List of actionable items
"""
        
        # Get LLM analysis
        response = await self.llm_provider.query(prompt, expect_json=True)
        return response
    
    async def cleanup(self) -> None:
        """Clean up plugin resources"""
        if self.llm_provider:
            await self.llm_provider.close()
            self.llm_provider = None

# Register the plugin
from near_swarm.plugins import register_plugin
register_plugin("market_analyzer", MarketAnalyzerPlugin) 