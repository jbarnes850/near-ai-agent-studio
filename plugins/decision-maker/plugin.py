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
        """Evaluate market data and make strategic decisions"""
        try:
            if not context.get('price_data'):
                return {'error': 'No price data provided'}
                
            price_data = context['price_data']
            price_change = price_data.get('change_24h', 0)
            current_price = price_data.get('price', 0)
            
            decision = self._evaluate_market_conditions(price_change, current_price)
            decision['context'] = context
            
            return decision
            
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