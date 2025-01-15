"""
NEAR Swarm Arbitrage Strategy Example
Demonstrates a plugin-based agent for DEX arbitrage opportunities.

This example shows:
1. How to create an advanced arbitrage plugin
2. Market data integration from multiple sources
3. LLM-powered opportunity analysis
4. Proper error handling and resource cleanup
5. Best practices for logging and monitoring

Usage:
1. Create plugin configuration:
   ```yaml
   # agent.yaml
   name: arbitrage-agent
   description: "DEX arbitrage agent with LLM analysis"
   version: "0.1.0"
   capabilities:
     - market_analysis
     - dex_integration
     - arbitrage
   
   llm:
     provider: ${LLM_PROVIDER}
     model: ${LLM_MODEL}
     temperature: 0.7
     system_prompt: |
       You are an arbitrage analysis expert.
       Evaluate DEX opportunities considering:
       1. Price differences
       2. Trading volumes
       3. Gas costs
       4. Slippage impact
       Always prioritize safety and profitability.
   
   near:
     network: ${NEAR_NETWORK:-testnet}
     account_id: ${NEAR_ACCOUNT_ID}
     private_key: ${NEAR_PRIVATE_KEY}
   
   market:
     min_profit_threshold: 0.02  # 2% minimum profit
     max_position_size: 1000     # Max NEAR per trade
     target_dexes:
       - ref_finance
       - jumbo
   ```

2. Install plugin:
   ```bash
   near-swarm plugins install ./arbitrage-agent
   ```

3. Run example:
   ```bash
   near-swarm execute arbitrage-agent --operation analyze --pair NEAR/USDC
   ```

Integration Patterns:
- Use environment variables for sensitive data
- Implement proper lifecycle methods
- Add comprehensive error handling
- Include detailed logging
- Cache market data efficiently

Testing:
1. Unit tests: Test arbitrage calculations
2. Integration tests: Test DEX interactions
3. End-to-end tests: Test full arbitrage flow
4. Market simulation tests
"""

import asyncio
import logging
from typing import Dict, Any, List
from near_swarm.plugins.base import AgentPlugin
from near_swarm.core.exceptions import AgentError, NEARError, LLMError
from near_swarm.core.market_data import MarketDataManager

# Configure logging
logger = logging.getLogger(__name__)

class ArbitragePlugin(AgentPlugin):
    """Plugin for identifying and executing DEX arbitrage opportunities."""
    
    async def initialize(self) -> None:
        """Initialize plugin resources."""
        try:
            # Initialize LLM provider
            self.llm = self.create_llm_provider(self.config.llm)
            
            # Initialize NEAR connection
            self.near = await self.create_near_connection(self.config.near)
            
            # Initialize market data manager
            self.market = MarketDataManager()
            
            logger.info("ArbitragePlugin initialized successfully")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise AgentError(f"Failed to initialize plugin: {e}")
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process arbitrage operations."""
        try:
            operation = context.get("operation")
            
            if operation == "analyze":
                return await self._analyze_opportunity(context)
            elif operation == "execute":
                return await self._execute_arbitrage(context)
            else:
                raise AgentError(f"Unknown operation: {operation}")
                
        except AgentError as e:
            logger.error(f"Operation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise AgentError(f"Operation failed: {e}")
    
    async def _analyze_opportunity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze arbitrage opportunities."""
        try:
            # Get parameters
            pair = context.get("pair")
            if not pair:
                raise AgentError("Missing required parameter: pair")
            
            # Get market data
            dex_prices = await self._get_dex_prices(pair)
            market_context = await self._get_market_context()
            
            # Analyze with LLM
            analysis = await self._analyze_with_llm(dex_prices, market_context)
            
            if analysis["is_opportunity"]:
                logger.info(f"Found arbitrage opportunity for {pair}")
                return {
                    "status": "opportunity_found",
                    "pair": pair,
                    "profit_potential": analysis["profit_potential"],
                    "recommended_action": analysis["action"],
                    "reasoning": analysis["reasoning"],
                    "risk_level": analysis["risk_level"]
                }
            else:
                logger.info(f"No profitable opportunity for {pair}")
                return {
                    "status": "no_opportunity",
                    "pair": pair,
                    "reason": analysis["reasoning"]
                }
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise AgentError(f"Failed to analyze opportunity: {e}")
    
    async def _execute_arbitrage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute arbitrage trade."""
        try:
            # Validate parameters
            if not all(k in context for k in ["pair", "amount", "route"]):
                raise AgentError("Missing required parameters")
            
            # Execute trades
            trades = []
            for step in context["route"]:
                result = await self.near.execute_swap(
                    dex=step["dex"],
                    pair=context["pair"],
                    amount=step["amount"],
                    direction=step["direction"]
                )
                trades.append(result)
            
            return {
                "status": "success",
                "trades": trades,
                "total_profit": sum(t["profit"] for t in trades)
            }
            
        except NEARError as e:
            logger.error(f"Trade execution failed: {e}")
            raise AgentError(f"Failed to execute arbitrage: {e}")
    
    async def _get_dex_prices(self, pair: str) -> List[Dict[str, Any]]:
        """Get prices from configured DEXes."""
        prices = []
        for dex in self.config.market.target_dexes:
            try:
                price = await self.market.get_dex_price(dex, pair)
                prices.append({
                    "dex": dex,
                    "price": price["price"],
                    "liquidity": price["liquidity"]
                })
            except Exception as e:
                logger.warning(f"Failed to get price from {dex}: {e}")
        return prices
    
    async def _get_market_context(self) -> Dict[str, Any]:
        """Get relevant market context."""
        try:
            return {
                "network": await self.near.get_network_stats(),
                "gas_price": await self.near.get_gas_price(),
                "market_volatility": await self.market.get_market_volatility()
            }
        except Exception as e:
            logger.error(f"Failed to get market context: {e}")
            raise
    
    async def _analyze_with_llm(
        self,
        dex_prices: List[Dict[str, Any]],
        market_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze opportunity using LLM."""
        try:
            prompt = f"""
            Analyze this arbitrage opportunity:
            
            DEX Prices:
            {dex_prices}
            
            Market Context:
            {market_context}
            
            Configuration:
            - Min Profit: {self.config.market.min_profit_threshold}
            - Max Position: {self.config.market.max_position_size}
            
            Return JSON with:
            - is_opportunity: boolean
            - profit_potential: float
            - action: string (execute/wait)
            - reasoning: string
            - risk_level: string (low/medium/high)
            """
            
            return await self.llm.query(prompt)
            
        except LLMError as e:
            logger.error(f"LLM analysis failed: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        try:
            if hasattr(self, 'near'):
                await self.near.close()
            if hasattr(self, 'market'):
                await self.market.close()
            logger.info("ArbitragePlugin cleaned up successfully")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise AgentError(f"Failed to cleanup plugin: {e}")

async def main():
    """Run the arbitrage strategy example."""
    from near_swarm.plugins import PluginLoader
    
    try:
        # Load plugin
        loader = PluginLoader()
        plugin = await loader.load_plugin("arbitrage-agent")
        
        # Analyze opportunity
        result = await plugin.evaluate({
            "operation": "analyze",
            "pair": "NEAR/USDC"
        })
        
        print("\n=== Analysis Result ===")
        print(f"Status: {result['status']}")
        
        if result['status'] == 'opportunity_found':
            print(f"\nProfit Potential: {result['profit_potential']:.2%}")
            print(f"Recommended Action: {result['recommended_action']}")
            print(f"Risk Level: {result['risk_level']}")
            print(f"\nReasoning: {result['reasoning']}")
        else:
            print(f"\nReason: {result['reason']}")
        
    except AgentError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if 'plugin' in locals():
            await loader.unload_plugin("arbitrage-agent")

if __name__ == "__main__":
    asyncio.run(main()) 