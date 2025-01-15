"""
Decision Maker Plugin for NEAR Swarm Intelligence
Evaluates market analysis and makes strategic decisions
"""

import logging
from typing import Dict, Any, Optional
from near_swarm.plugins.base import AgentPlugin, PluginConfig
from near_swarm.core.agent import AgentConfig

logger = logging.getLogger(__name__)

class DecisionMakerPlugin(AgentPlugin):
    """Strategic decision making plugin"""
    
    def __init__(self, agent_config: AgentConfig, plugin_config: PluginConfig):
        super().__init__(agent_config, plugin_config)
        self.min_confidence = float(self.plugin_config.custom_settings.get('min_confidence_threshold', 0.8))
        self.risk_tolerance = self.plugin_config.custom_settings.get('risk_tolerance', 'medium')
        self.decision_interval = int(self.plugin_config.custom_settings.get('decision_interval', 300))
        self.logger = logger
        
    async def initialize(self) -> None:
        """Initialize decision maker"""
        self.logger.info("Decision maker initialized successfully")
        
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process market analysis and make decisions"""
        try:
            if message.get('type') != 'price_update':
                return None
                
            price_data = message.get('data', {})
            if not price_data or price_data.get('confidence', 0) < self.min_confidence:
                return None
                
            # Analyze price movement
            price_change = price_data.get('change_24h', 0)
            current_price = price_data.get('price', 0)
            
            decision = self._evaluate_market_conditions(price_change, current_price)
            
            return {
                'type': 'trading_decision',
                'data': {
                    'action': decision['action'],
                    'confidence': decision['confidence'],
                    'reasoning': decision['reasoning'],
                    'risk_level': decision['risk_level']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return None
            
    def _evaluate_market_conditions(self, price_change: float, current_price: float) -> Dict[str, Any]:
        """Evaluate market conditions and generate decision"""
        # Define risk thresholds based on risk tolerance
        risk_thresholds = {
            'low': {'change': 0.03, 'confidence': 0.9},
            'medium': {'change': 0.05, 'confidence': 0.8},
            'high': {'change': 0.08, 'confidence': 0.7}
        }
        
        threshold = risk_thresholds[self.risk_tolerance]
        
        if abs(price_change) < threshold['change']:
            return {
                'action': 'hold',
                'confidence': 0.85,
                'reasoning': 'Price movement within normal range',
                'risk_level': 'low'
            }
            
        # Determine action based on price movement and risk tolerance
        if price_change > threshold['change']:
            return {
                'action': 'sell' if self.risk_tolerance != 'high' else 'hold',
                'confidence': threshold['confidence'],
                'reasoning': f'Significant price increase of {price_change}%',
                'risk_level': 'medium'
            }
        else:
            return {
                'action': 'buy' if self.risk_tolerance != 'low' else 'hold',
                'confidence': threshold['confidence'],
                'reasoning': f'Significant price decrease of {price_change}%',
                'risk_level': 'medium'
            }
            
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate market analysis and provide strategic decisions with detailed reasoning"""
        try:
            market_analysis = context.get('market_analysis', {})
            current_price = context.get('current_price', 0)
            
            # Extract market insights
            price_change = market_analysis.get('change_24h', 0)
            risk_level = market_analysis.get('risk_level', 'medium')
            market_confidence = market_analysis.get('confidence', 0)
            
            # Detailed strategic analysis
            context_analysis = f"I'm analyzing the NEAR market at ${current_price:.2f}. The price monitor indicates a {abs(price_change):.1f}% {'increase' if price_change > 0 else 'decrease'} "
            context_analysis += f"with {market_confidence*100:.0f}% confidence. Market risk is assessed as {risk_level}. "
            
            strategy = "Given these conditions, "
            if risk_level == 'high':
                strategy += "I recommend a cautious approach. High market volatility requires strict risk management and smaller position sizes. "
            elif risk_level == 'medium':
                strategy += "a balanced strategy is appropriate. We can explore opportunities while maintaining moderate risk controls. "
            else:
                strategy += "we can be more opportunistic. Lower risk levels allow for larger positions with appropriate stops. "
                
            rationale = f"My reasoning is based on: 1) The significant {'upward' if price_change > 0 else 'downward'} price movement, "
            rationale += f"2) The {risk_level} risk assessment from market analysis, and "
            rationale += f"3) Our {'conservative' if self.risk_tolerance == 'low' else 'balanced' if self.risk_tolerance == 'medium' else 'aggressive'} risk tolerance setting. "
            
            action = "Recommended Action: "
            confidence = 0.0
            
            if abs(price_change) >= 0.1 and market_confidence >= 0.9:
                action += f"{'Take profit' if price_change > 0 else 'Buy the dip'} with tight stops. "
                confidence = 0.85
            elif abs(price_change) >= 0.05 and market_confidence >= 0.8:
                action += f"{'Scale out' if price_change > 0 else 'Scale in'} gradually. "
                confidence = 0.75
            else:
                action += "Hold current positions and monitor for clearer signals. "
                confidence = 0.65
                
            action += f"Set stops at {abs(price_change)*1.5:.1f}% {'below entry' if price_change > 0 else 'above entry'} for risk management."
            
            return {
                'context': context_analysis,
                'strategy': strategy,
                'rationale': rationale,
                'action': action,
                'confidence': confidence,
                'risk_level': risk_level
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating market data: {str(e)}")
            return {'error': str(e)}
            
    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trading decisions"""
        try:
            if action.get('type') == 'evaluate_market':
                return await self.evaluate(action.get('data', {}))
            return {'error': 'Unsupported action type'}
            
        except Exception as e:
            self.logger.error(f"Error executing action: {str(e)}")
            return {'error': str(e)}
            
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass 