"""
Custom Agent Plugin Template
Use this template to create your own NEAR swarm agent plugin
"""

from typing import Dict, Any, Optional
from near_swarm.plugins.base import AgentPlugin
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig
import logging

logger = logging.getLogger(__name__)

class CustomAgentPlugin(AgentPlugin):
    """Custom agent implementation"""
    
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        # Initialize LLM provider
        llm_config = LLMConfig(
            provider=self.agent_config.llm_provider,
            api_key=self.agent_config.llm_api_key,
            model=self.agent_config.llm_model,
            temperature=0.7,
            max_tokens=1000,
            api_url=self.agent_config.api_url,
            system_prompt=self.plugin_config.system_prompt
        )
        self.llm_provider = create_llm_provider(llm_config)
        
        # Load custom settings
        self.min_confidence = self.plugin_config.settings.get(
            'min_confidence_threshold', 0.7
        )
        self.risk_tolerance = self.plugin_config.settings.get(
            'risk_tolerance', 'medium'
        )
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate based on your agent's logic"""
        if not self.llm_provider:
            raise RuntimeError("Plugin not initialized")
            
        # Extract data from context
        request = context.get('request', '')
        
        # Create role-specific prompts
        if self.plugin_config.role == "market_analyzer":
            current_price = context.get('price', 0)
            timestamp = context.get('timestamp', 0)
            
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
            
        elif self.plugin_config.role == "strategy_optimizer":
            market_analysis = context.get('market_analysis', {})
            current_price = context.get('current_price', 0)
            
            prompt = f"""Evaluate the following market opportunity:

Market Analysis:
- Observation: {market_analysis.get('observation', 'No observation provided')}
- Reasoning: {market_analysis.get('reasoning', 'No reasoning provided')}
- Conclusion: {market_analysis.get('conclusion', 'No conclusion provided')}
- Analysis Confidence: {market_analysis.get('confidence', 0):.0%}

Current Price: ${current_price:.2f}
Risk Tolerance: {self.risk_tolerance}

{request}

Provide your decision in JSON format with:
- context: Your understanding of the situation
- strategy: Your recommended approach
- rationale: Detailed explanation of your decision
- action: Specific steps to take
- confidence: Your confidence level (0-1)
"""
            
        else:
            prompt = f"""Analyze the following context:
{context}

Provide your analysis in JSON format with:
- observation: Your observations
- reasoning: Your analysis process
- conclusion: Clear summary
- confidence: Your confidence level (0-1)
"""
        
        # Get LLM analysis
        try:
            response = await self.llm_provider.query(prompt, expect_json=True)
            
            # Validate confidence threshold
            if response.get('confidence', 0) < self.min_confidence:
                if self.plugin_config.role == "market_analyzer":
                    response['conclusion'] = "Confidence too low for definitive recommendation. Need more data."
                elif self.plugin_config.role == "strategy_optimizer":
                    response['action'] = "Confidence too low for action. Monitoring situation."
                
            return response
            
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
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

# Register your plugin
from near_swarm.plugins import register_plugin
register_plugin("custom_agent", CustomAgentPlugin) 