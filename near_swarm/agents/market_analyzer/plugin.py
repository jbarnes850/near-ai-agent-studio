"""
Market Analyzer Agent
Analyzes market conditions and provides trading insights
"""

from typing import Dict, Any, List
from near_swarm.plugins.base import AgentPlugin, PluginConfig
from near_swarm.core.agent import AgentConfig
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig

class MarketAnalyzerPlugin(AgentPlugin):
    """Market analysis agent implementation"""
    
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
            system_prompt=self.plugin_config.system_prompt
        )
        self.llm_provider = create_llm_provider(llm_config)
        
        # Load custom settings
        self.min_confidence = self.plugin_config.custom_settings.get(
            'min_confidence_threshold', 0.7
        )
        self.max_lookback = self.plugin_config.custom_settings.get(
            'max_lookback_periods', 30
        )
        self.risk_tolerance = self.plugin_config.custom_settings.get(
            'risk_tolerance', 'medium'
        )
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate market conditions"""
        if not self.llm_provider:
            raise RuntimeError("Plugin not initialized")
            
        # Extract market data from context
        market_data = context.get('market_data', {})
        sentiment_data = context.get('sentiment_data', {})
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(market_data, sentiment_data)
        
        # Get LLM analysis
        response = await self.llm_provider.query(prompt, expect_json=True)
        
        # Apply risk adjustments based on confidence
        if response.get('confidence', 0) < self.min_confidence:
            response['recommendations'] = self._adjust_recommendations(
                response['recommendations'],
                response['confidence']
            )
            
        return response
    
    def _create_analysis_prompt(
        self,
        market_data: Dict[str, Any],
        sentiment_data: Dict[str, Any]
    ) -> str:
        """Create the analysis prompt"""
        return f"""Analyze the following market conditions:

Market Data:
{self._format_market_data(market_data)}

Sentiment Data:
{self._format_sentiment_data(sentiment_data)}

Risk Tolerance: {self.risk_tolerance}

Provide your analysis in JSON format with:
- trend: Current market trend (bullish/bearish/neutral)
- confidence: Your confidence level (0-1)
- evidence: List of supporting evidence
- risks: List of risk factors
- recommendations: List of actionable recommendations
"""
    
    def _format_market_data(self, data: Dict[str, Any]) -> str:
        """Format market data for prompt"""
        if not data:
            return "No market data available"
            
        return "\n".join([
            f"- {key}: {value}"
            for key, value in data.items()
        ])
    
    def _format_sentiment_data(self, data: Dict[str, Any]) -> str:
        """Format sentiment data for prompt"""
        if not data:
            return "No sentiment data available"
            
        return "\n".join([
            f"- {key}: {value}"
            for key, value in data.items()
        ])
    
    def _adjust_recommendations(
        self,
        recommendations: List[str],
        confidence: float
    ) -> List[str]:
        """Adjust recommendations based on confidence"""
        if confidence < 0.5:
            return ["Insufficient confidence for trading recommendations"]
            
        # Add risk warnings
        adjusted = []
        for rec in recommendations:
            adjusted.append(f"{rec} (Confidence: {confidence:.2f})")
        
        return adjusted
    
    async def cleanup(self) -> None:
        """Clean up plugin resources"""
        if self.llm_provider:
            await self.llm_provider.close()
            self.llm_provider = None

# Register the plugin
from near_swarm.plugins import register_plugin
register_plugin("market_analyzer", MarketAnalyzerPlugin) 