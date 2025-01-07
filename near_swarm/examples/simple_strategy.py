"""
Simple Strategy Example
Demonstrates basic swarm intelligence with LLM-powered decision making
"""

import asyncio
import logging
from typing import Dict, Any
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.config import load_config
from near_swarm.core.market_data import MarketDataManager

# Configure logging with colors
import colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))
logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

async def run_simple_strategy() -> Dict[str, Any]:
    """Run a simple strategy example demonstrating LLM-powered multi-agent decision making."""
    # Initialize components
    market_analyzer = None
    risk_manager = None
    strategy_optimizer = None
    market_data = None
    
    try:
        logger.info("🚀 Initializing simple strategy...")
        
        # Initialize market data
        logger.info("📊 Fetching market data...")
        market_data = MarketDataManager()
        near_data = await market_data.get_token_price("near")
        dex_data = await market_data.get_dex_data("ref-finance")
        
        logger.info(f"• Current NEAR Price: ${near_data['price']:.2f}")
        logger.info(f"• 24h Volume: {near_data['24h_volume']}")
        logger.info(f"• Market Trend: {near_data['market_trend']}")
        logger.info(f"• Volatility: {near_data['volatility']}")
        
        # Load configuration
        config = load_config()
        
        # Initialize agents with specific roles and confidence thresholds
        logger.info("\n🤖 Creating agents...")
        
        market_analyzer = SwarmAgent(
            config,
            SwarmConfig(
                role="market_analyzer",
                min_confidence=0.7,
                min_votes=2
            )
        )
        logger.info("✓ Market Analyzer ready")

        risk_manager = SwarmAgent(
            config,
            SwarmConfig(
                role="risk_manager",
                min_confidence=0.8,  # Higher threshold for risk management
                min_votes=2
            )
        )
        logger.info("✓ Risk Manager ready")

        strategy_optimizer = SwarmAgent(
            config,
            SwarmConfig(
                role="strategy_optimizer",
                min_confidence=0.7,
                min_votes=2
            )
        )
        logger.info("✓ Strategy Optimizer ready")

        # Start all agents
        logger.info("\n🔄 Starting agents...")
        await market_analyzer.start()
        await risk_manager.start()
        await strategy_optimizer.start()
        logger.info("✓ All agents started")

        # Form swarm with all agents
        logger.info("\n🔗 Forming swarm network...")
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])
        logger.info("✓ Swarm network established")

        # Example NEAR transfer proposal with real market context
        proposal = {
            "type": "transfer",
            "params": {
                "recipient": "bob.testnet",
                "amount": "0.1",
                "token": "NEAR",
                "market_context": {
                    "current_price": near_data["price"],
                    "24h_volume": near_data["24h_volume"],
                    "volatility": near_data["volatility"],
                    "market_trend": near_data["market_trend"],
                    "gas_price": "0.001",  # TODO: Get from RPC
                    "network_load": "moderate"  # TODO: Calculate from block stats
                }
            }
        }

        logger.info("\n=== Running LLM-Powered Multi-Agent Strategy Example ===")
        logger.info(f"📝 Proposal: Transfer {proposal['params']['amount']} NEAR to {proposal['params']['recipient']}")
        logger.info("\n📊 Market Context:")
        logger.info(f"• Current NEAR Price: ${proposal['params']['market_context']['current_price']:.2f}")
        logger.info(f"• 24h Volume: {proposal['params']['market_context']['24h_volume']}")
        logger.info(f"• Market Trend: {proposal['params']['market_context']['market_trend']}")
        logger.info(f"• Volatility: {proposal['params']['market_context']['volatility']}")

        # Get swarm consensus with LLM-powered evaluation
        logger.info("\n🤔 Getting swarm consensus...")
        result = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal["params"]
        )

        logger.info("\n=== Swarm Decision Analysis ===")
        logger.info(f"{'✅ Consensus reached' if result['consensus'] else '❌ Consensus not reached'}")
        logger.info(f"📊 Approval rate: {result['approval_rate']:.2%}")
        logger.info("\n💭 Agent Reasoning:")
        for i, reason in enumerate(result["reasons"]):
            logger.info(f"\nAgent {i+1}:")
            logger.info(f"• {reason}")

        if result["consensus"]:
            logger.info("\n=== Executing Transfer ===")
            logger.info("✅ Transfer completed successfully!")
            logger.info("All agents have approved with sufficient confidence.")
        else:
            logger.info("\n=== Transfer Rejected ===")
            logger.info("❌ The swarm decided not to execute the transfer.")
            logger.info("Insufficient consensus or confidence levels not met.")

        return result

    except Exception as e:
        logger.error(f"❌ Error in simple strategy: {str(e)}")
        raise
    finally:
        # Cleanup all agents
        logger.info("\n🧹 Cleaning up...")
        if market_data:
            await market_data.close()
        if market_analyzer:
            await market_analyzer.close()
        if risk_manager:
            await risk_manager.close()
        if strategy_optimizer:
            await strategy_optimizer.close()
        logger.info("✓ Cleanup complete")

if __name__ == "__main__":
    try:
        asyncio.run(run_simple_strategy())
    except KeyboardInterrupt:
        logger.info("\n👋 Strategy stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        raise 