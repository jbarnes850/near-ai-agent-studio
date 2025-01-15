"""
Price Monitoring Agent Plugin
Analyzes NEAR market conditions and price movements
"""

from typing import Dict, Any, Optional
from near_swarm.plugins.base import AgentPlugin
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig
from near_swarm.plugins import register_plugin
import logging

logger = logging.getLogger(__name__)

class PriceMonitorPlugin(AgentPlugin):
    """Price monitoring agent implementation"""
    
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        # Initialize LLM provider
        llm_config = LLMConfig(
            provider=self.agent_config.llm.provider,
            api_key=self.agent_config.llm.api_key,
            model=self.agent_config.llm.model,
            temperature=self.agent_config.llm.temperature,
            max_tokens=self.agent_config.llm.max_tokens,
            api_url=self.agent_config.llm.api_url,
            system_prompt="""You are a specialized market analysis agent in the NEAR ecosystem.
Your role is to analyze market conditions, identify trends, and provide trading insights.

Key responsibilities:
1. Analyze price movements and market trends
2. Assess market sentiment and volatility
3. Identify potential trading opportunities
4. Provide risk-adjusted recommendations

Always provide your analysis in a structured format with:
- Observation: Current market conditions and notable patterns
- Reasoning: Your analysis process and key factors considered
- Conclusion: Clear summary of findings
- Confidence: Your confidence level (0-1)"""
        )
        self.llm_provider = create_llm_provider(llm_config)
        
        # Load custom settings
        self.min_confidence = self.plugin_config.settings.get(
            'min_confidence_threshold', 0.7
        )
        self.max_lookback = self.plugin_config.settings.get(
            'max_lookback_periods', 30
        )
        self.risk_tolerance = self.plugin_config.settings.get(
            'risk_tolerance', 'medium'
        )
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate market conditions"""
        if not self.llm_provider:
            raise RuntimeError("Plugin not initialized")
            
        # Extract data from context
        current_price = context.get('price', 0)
        timestamp = context.get('timestamp', 0)
        request = context.get('request', '')
        
        # Create analysis prompt
        prompt = f"""Analyze the current NEAR market conditions:

Current Price: ${current_price:.2f}
Timestamp: {timestamp}
Risk Tolerance: {self.risk_tolerance}

{request}

Provide your analysis in JSON format with:
- observation: Your observations of current conditions
- reasoning: Your detailed analysis process
- conclusion: Clear summary and recommendations
- confidence: Your confidence level (0-1)
"""
        
        # Get LLM analysis
        try:
            response = await self.llm_provider.query(prompt, expect_json=True)
            
            # Validate confidence threshold
            if response.get('confidence', 0) < self.min_confidence:
                response['conclusion'] = "Confidence too low for definitive recommendation. Need more data."
                
            return response
            
        except Exception as e:
            logger.error(f"Error during market analysis: {e}")
            return {
                "observation": "Error during analysis",
                "reasoning": str(e),
                "conclusion": "Analysis failed",
                "confidence": 0
            }
    
    async def execute(self, operation: Optional[str] = None, **kwargs) -> Any:
        """Execute plugin operation"""
        if operation == "analyze":
            return await self.evaluate(kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        if self.llm_provider:
            await self.llm_provider.close()

# Register the plugin
register_plugin("price-monitor", PriceMonitorPlugin) 