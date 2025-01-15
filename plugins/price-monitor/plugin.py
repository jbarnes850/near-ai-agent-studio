"""
Price Monitor Plugin for NEAR Swarm Intelligence
Monitors NEAR token prices and market conditions
"""

import logging
from typing import Dict, Any, Optional
from near_swarm.plugins.base import AgentPlugin, PluginConfig
from near_swarm.core.agent import AgentConfig
from near_swarm.core.market_data import MarketDataManager

logger = logging.getLogger(__name__)

class PriceMonitorPlugin(AgentPlugin):
    """Price monitoring plugin for market analysis"""
    
    def __init__(self, agent_config: AgentConfig, plugin_config: PluginConfig):
        super().__init__(agent_config, plugin_config)
        self.market_data = None
        self.update_interval = int(self.plugin_config.custom_settings.get('update_interval', 60))
        self.alert_threshold = float(self.plugin_config.custom_settings.get('alert_threshold', 0.05))
        self.logger = logger
        
    async def initialize(self) -> None:
        """Initialize market data connection"""
        self.market_data = MarketDataManager()
        self.logger.info("Price monitor initialized successfully")
        
    async def get_price_data(self) -> Dict[str, Any]:
        """Get NEAR price data using available method"""
        try:
            # Get price data using get_token_price
            return await self.market_data.get_token_price('near')
        except Exception as e:
            self.logger.error(f"Error getting price data: {str(e)}")
            return {}
        
    async def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process incoming messages and monitor price changes"""
        try:
            # Get current NEAR price
            price_data = await self.get_price_data()
            if not price_data:
                return None
            
            response = {
                'type': 'price_update',
                'data': {
                    'price': price_data['price'],
                    'timestamp': price_data['timestamp'],
                    'change_24h': price_data.get('24h_change', 0),
                    'confidence': 0.95
                }
            }
            
            # Check for significant price changes
            if abs(price_data.get('24h_change', 0)) >= self.alert_threshold:
                response['alert'] = {
                    'type': 'price_movement',
                    'severity': 'high' if abs(price_data['24h_change']) >= 0.1 else 'medium',
                    'message': f"Significant price movement detected: {price_data['24h_change']}%"
                }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return None
            
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate market conditions with detailed natural language analysis"""
        try:
            price_data = await self.get_price_data()
            if not price_data:
                return {'error': 'Failed to get price data'}
            
            price = price_data['price']
            change_24h = price_data.get('24h_change', 0)
            
            # Detailed market analysis
            observation = f"I observe that NEAR is currently trading at ${price:.2f}, with a {change_24h:.1f}% change in the last 24 hours. "
            if abs(change_24h) >= self.alert_threshold:
                observation += f"This represents a significant {'increase' if change_24h > 0 else 'decrease'} in price, exceeding our alert threshold of {self.alert_threshold*100}%."
            else:
                observation += "The price movement is within normal trading ranges."
                
            reasoning = f"Analyzing this price action: The {abs(change_24h):.1f}% {'upward' if change_24h > 0 else 'downward'} movement "
            if abs(change_24h) >= 0.1:
                reasoning += "indicates high market volatility. This could be due to significant market events, news, or large trading volumes. "
            elif abs(change_24h) >= 0.05:
                reasoning += "suggests moderate market activity. This might be normal market dynamics or early signs of a trend forming. "
            else:
                reasoning += "shows relatively stable market conditions. This could indicate a period of consolidation or low trading activity. "
                
            conclusion = "Based on the analysis, "
            if abs(change_24h) >= 0.1:
                conclusion += f"the market is showing {'bullish' if change_24h > 0 else 'bearish'} momentum with high volatility. Traders should exercise caution and consider risk management strategies."
            elif abs(change_24h) >= 0.05:
                conclusion += f"there's a moderate {'upward' if change_24h > 0 else 'downward'} trend developing. This might present opportunities while maintaining reasonable risk levels."
            else:
                conclusion += "the market appears stable. This could be a good time for accumulation or position adjustment with lower risk."
            
            return {
                'observation': observation,
                'reasoning': reasoning,
                'conclusion': conclusion,
                'price': price,
                'change_24h': change_24h,
                'confidence': 0.95,
                'risk_level': 'high' if abs(change_24h) >= 0.1 else 'medium' if abs(change_24h) >= 0.05 else 'low'
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating market conditions: {str(e)}")
            return {'error': str(e)}
            
    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute monitoring actions"""
        try:
            if action.get('type') == 'monitor_price':
                return await self.evaluate({'type': 'price_check'})
            return {'error': 'Unsupported action type'}
            
        except Exception as e:
            self.logger.error(f"Error executing action: {str(e)}")
            return {'error': str(e)}
            
    async def cleanup(self) -> None:
        """Cleanup market data connection"""
        if self.market_data:
            try:
                await self.market_data.close()
            except:
                pass 