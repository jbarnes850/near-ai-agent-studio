"""
NEAR Portfolio Management Agent
Helps users understand their NEAR/USDC portfolio status and market position.
"""

import asyncio
import os
from decimal import Decimal
from typing import Dict, Any
from dataclasses import dataclass
from near_swarm.core.agent import Agent, AgentConfig
from near_swarm.core.market_data import MarketDataManager
from dotenv import load_dotenv

@dataclass
class PortfolioStatus:
    """Portfolio status information"""
    near_balance: Decimal
    usdc_balance: Decimal
    near_price_usd: Decimal
    total_value_usd: Decimal
    market_trend: str
    recommendations: list[str]

class PortfolioAgent:
    def __init__(self):
        load_dotenv()
        
        # Initialize market data manager
        self.market_data = MarketDataManager(
            cache_duration=300,  # 5 minutes
            max_requests_per_minute=60
        )
        
        # Initialize agent with portfolio-specific prompt
        self.agent = Agent(
            AgentConfig(
                network="testnet",
                account_id=os.getenv("NEAR_ACCOUNT_ID"),
                private_key=os.getenv("NEAR_PRIVATE_KEY"),
                llm_provider="hyperbolic",
                llm_api_key=os.getenv("LLM_API_KEY"),
                llm_model="deepseek-ai/DeepSeek-V3",
                system_prompt="""You are a portfolio management assistant for NEAR Protocol.
                Your role is to:
                1. Analyze portfolio composition
                2. Provide market insights
                3. Make simple portfolio recommendations
                4. Explain market trends
                
                Keep explanations clear and focused on the user's holdings.""",
                rpc_url=os.getenv("NEAR_RPC_URL")
            )
        )
    
    async def get_portfolio_status(self) -> PortfolioStatus:
        """Get current portfolio status including balances and market data."""
        try:
            # Start agent if not running
            if not self.agent.is_running():
                await self.agent.start()
            
            # Get NEAR balance
            near_balance = Decimal(await self.agent.check_balance())
            
            # Get USDC balance (assuming USDC contract)
            usdc_balance = Decimal(await self.agent.check_balance("usdc.testnet"))
            
            # Get NEAR price
            near_price = await self.market_data.get_price("NEAR/USD")
            near_price_usd = Decimal(str(near_price))
            
            # Calculate total value
            total_value = (near_balance * near_price_usd) + usdc_balance
            
            # Get market trend
            market_trend = await self._analyze_market_trend()
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                near_balance, usdc_balance, near_price_usd, market_trend
            )
            
            return PortfolioStatus(
                near_balance=near_balance,
                usdc_balance=usdc_balance,
                near_price_usd=near_price_usd,
                total_value_usd=total_value,
                market_trend=market_trend,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"Error getting portfolio status: {e}")
            raise
    
    async def _analyze_market_trend(self) -> str:
        """Analyze current market trend using recent price data."""
        try:
            # Get 24h price data
            price_24h = await self.market_data.get_price_history(
                "NEAR/USD",
                interval="1h",
                limit=24
            )
            
            # Simple trend analysis
            if price_24h[-1] > price_24h[0]:
                return "upward"
            elif price_24h[-1] < price_24h[0]:
                return "downward"
            return "stable"
            
        except Exception:
            return "unknown"
    
    async def _generate_recommendations(
        self,
        near_balance: Decimal,
        usdc_balance: Decimal,
        near_price: Decimal,
        trend: str
    ) -> list[str]:
        """Generate simple portfolio recommendations."""
        recommendations = []
        
        # Calculate portfolio composition
        total_value = (near_balance * near_price) + usdc_balance
        near_percentage = (near_balance * near_price) / total_value * 100
        
        # Basic recommendations based on composition and trend
        if near_percentage > 80:
            recommendations.append(
                "Consider reducing NEAR exposure to maintain a balanced portfolio"
            )
        elif near_percentage < 20:
            recommendations.append(
                "Consider increasing NEAR position while maintaining safe exposure"
            )
        
        if trend == "upward":
            recommendations.append(
                "Market showing positive momentum - monitor for profit taking opportunities"
            )
        elif trend == "downward":
            recommendations.append(
                "Market showing weakness - consider averaging in at lower prices"
            )
        
        return recommendations

    async def get_portfolio_summary(self) -> str:
        """Get a human-readable portfolio summary."""
        try:
            status = await self.get_portfolio_status()
            
            summary = f"""
Portfolio Summary:
-----------------
NEAR Balance: {status.near_balance:.2f} NEAR (${(status.near_balance * status.near_price_usd):.2f})
USDC Balance: ${status.usdc_balance:.2f}
Total Value: ${status.total_value_usd:.2f}
NEAR Price: ${status.near_price_usd:.2f}
Market Trend: {status.market_trend}

Recommendations:
"""
            
            for rec in status.recommendations:
                summary += f"- {rec}\n"
            
            return summary
            
        except Exception as e:
            return f"Error generating portfolio summary: {str(e)}"

async def main():
    # Initialize portfolio agent
    portfolio = PortfolioAgent()
    
    # Get and print portfolio summary
    summary = await portfolio.get_portfolio_summary()
    print(summary)

if __name__ == "__main__":
    asyncio.run(main()) 