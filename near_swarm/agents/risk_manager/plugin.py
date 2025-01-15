"""
Risk Manager Agent
Manages risk exposure and provides risk assessments
"""

from typing import Dict, Any, List
from decimal import Decimal
from near_swarm.plugins.base import AgentPlugin, PluginConfig
from near_swarm.core.agent import AgentConfig
from near_swarm.core.llm_provider import create_llm_provider, LLMConfig

class RiskManagerPlugin(AgentPlugin):
    """Risk management agent implementation"""
    
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
        
        # Load risk settings
        settings = self.plugin_config.custom_settings
        self.max_position_size = Decimal(str(settings.get('max_position_size', 0.1)))
        self.max_total_exposure = Decimal(str(settings.get('max_total_exposure', 0.5)))
        self.stop_loss_multiplier = Decimal(str(settings.get('stop_loss_multiplier', 2.0)))
        self.risk_per_trade = Decimal(str(settings.get('risk_per_trade', 0.02)))
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate risk metrics and provide recommendations"""
        if not self.llm_provider:
            raise RuntimeError("Plugin not initialized")
            
        # Extract data from context
        portfolio = context.get('portfolio', {})
        market_data = context.get('market_data', {})
        proposed_trades = context.get('proposed_trades', [])
        
        # Calculate current risk metrics
        risk_metrics = self._calculate_risk_metrics(portfolio, proposed_trades)
        
        # Create risk assessment prompt
        prompt = self._create_risk_prompt(risk_metrics, market_data, proposed_trades)
        
        # Get LLM analysis
        response = await self.llm_provider.query(prompt, expect_json=True)
        
        # Add calculated metrics to response
        response['metrics'] = risk_metrics
        
        return response
    
    def _calculate_risk_metrics(
        self,
        portfolio: Dict[str, Any],
        proposed_trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate current risk metrics"""
        total_value = Decimal(str(portfolio.get('total_value', 0)))
        current_exposure = Decimal(str(portfolio.get('current_exposure', 0)))
        
        # Calculate exposure from proposed trades
        proposed_exposure = sum(
            Decimal(str(trade.get('size', 0)))
            for trade in proposed_trades
        )
        
        return {
            'current_exposure_ratio': float(current_exposure / total_value),
            'proposed_exposure_ratio': float(proposed_exposure / total_value),
            'total_exposure_ratio': float((current_exposure + proposed_exposure) / total_value),
            'available_risk': float(self.max_total_exposure - (current_exposure / total_value)),
            'max_trade_size': float(total_value * self.max_position_size)
        }
    
    def _create_risk_prompt(
        self,
        risk_metrics: Dict[str, Any],
        market_data: Dict[str, Any],
        proposed_trades: List[Dict[str, Any]]
    ) -> str:
        """Create the risk assessment prompt"""
        return f"""Assess the following risk scenario:

Risk Metrics:
{self._format_metrics(risk_metrics)}

Market Conditions:
{self._format_market_data(market_data)}

Proposed Trades:
{self._format_trades(proposed_trades)}

Risk Limits:
- Maximum position size: {float(self.max_position_size * 100)}% of portfolio
- Maximum total exposure: {float(self.max_total_exposure * 100)}% of portfolio
- Risk per trade: {float(self.risk_per_trade * 100)}% of portfolio

Provide your assessment in JSON format with:
- risk_level: Overall risk level (low/medium/high)
- exposure_assessment: Analysis of current and proposed exposure
- position_recommendations: List of position size adjustments
- risk_mitigations: List of risk mitigation strategies
- stop_losses: Recommended stop-loss levels
"""
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format risk metrics for prompt"""
        return "\n".join([
            f"- {key}: {value:.2%}"
            for key, value in metrics.items()
        ])
    
    def _format_market_data(self, data: Dict[str, Any]) -> str:
        """Format market data for prompt"""
        if not data:
            return "No market data available"
            
        return "\n".join([
            f"- {key}: {value}"
            for key, value in data.items()
        ])
    
    def _format_trades(self, trades: List[Dict[str, Any]]) -> str:
        """Format proposed trades for prompt"""
        if not trades:
            return "No proposed trades"
            
        return "\n".join([
            f"- Trade {i+1}: {trade.get('asset')} "
            f"Size: {trade.get('size')} "
            f"Type: {trade.get('type')}"
            for i, trade in enumerate(trades)
        ])
    
    async def cleanup(self) -> None:
        """Clean up plugin resources"""
        if self.llm_provider:
            await self.llm_provider.close()
            self.llm_provider = None

# Register the plugin
from near_swarm.plugins import register_plugin
register_plugin("risk_manager", RiskManagerPlugin) 