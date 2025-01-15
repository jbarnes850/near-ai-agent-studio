"""
Decision Making Agent Plugin
Makes strategic decisions based on market analysis
"""

from typing import Dict, Any, Optional
from near_swarm.plugins.base import AgentPlugin
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig
from near_swarm.plugins import register_plugin
import logging

logger = logging.getLogger(__name__)

class DecisionMakerPlugin(AgentPlugin):
    """Decision making agent implementation"""
    
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
            system_prompt="""You are a strategic decision-making agent in the NEAR ecosystem.
Your role is to evaluate market opportunities and make risk-managed decisions.

Key responsibilities:
1. Evaluate market analysis and opportunities
2. Calculate optimal position sizes
3. Manage risk exposure
4. Make strategic recommendations

Always provide your decisions in a structured format with:
- Analysis: Your evaluation of the situation
- Strategy: Your recommended course of action
- Rationale: Detailed reasoning behind the decision
- Risk: Assessment of potential risks
- Confidence: Your confidence level (0-1)"""
        )
        self.llm_provider = create_llm_provider(llm_config)
        
        # Load custom settings
        self.min_confidence = self.plugin_config.settings.get(
            'min_confidence_threshold', 0.7
        )
        self.risk_tolerance = self.plugin_config.settings.get(
            'risk_tolerance', 'medium'
        )
        self.max_position_size = self.plugin_config.settings.get(
            'max_position_size', 100000
        )
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate and make strategic decisions"""
        if not self.llm_provider:
            raise RuntimeError("Plugin not initialized")
            
        # Extract data from context
        market_analysis = context.get('market_analysis', {})
        current_positions = context.get('positions', [])
        request = context.get('request', '')
        
        # Create decision prompt
        prompt = f"""Evaluate the current market situation and make strategic decisions:

Market Analysis: {market_analysis}
Current Positions: {current_positions}
Risk Tolerance: {self.risk_tolerance}
Max Position Size: {self.max_position_size}

{request}

Provide your decision in JSON format with:
- analysis: Your evaluation of the situation
- strategy: Recommended course of action
- rationale: Detailed reasoning
- risk: Risk assessment
- confidence: Your confidence level (0-1)
"""
        
        # Get LLM decision
        try:
            response = await self.llm_provider.query(prompt, expect_json=True)
            
            # Validate confidence threshold
            if response.get('confidence', 0) < self.min_confidence:
                response['strategy'] = "Hold - Confidence too low for action"
                
            return response
            
        except Exception as e:
            logger.error(f"Error during decision making: {e}")
            return {
                "analysis": "Error during analysis",
                "strategy": "Unable to make decision",
                "rationale": str(e),
                "risk": "Unknown - Analysis failed",
                "confidence": 0
            }
    
    async def execute(self, operation: Optional[str] = None, **kwargs) -> Any:
        """Execute plugin operation"""
        if operation == "decide":
            return await self.evaluate(kwargs)
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        if self.llm_provider:
            await self.llm_provider.close()

# Register the plugin
register_plugin("decision-maker", DecisionMakerPlugin) 