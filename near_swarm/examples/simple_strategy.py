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

# Prevent duplicate logs
logger = colorlog.getLogger(__name__)
logger.propagate = False  # Prevent propagation to root logger
logger.handlers = []  # Clear any existing handlers

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(message)s',  # Simplified format without level/name
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))
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
        logger.info("\n🚀 Phase 1: Initialization")
        logger.info("Initializing market data and fetching current conditions...")
        
        # Initialize market data
        market_data = MarketDataManager()
        
        # Get market context
        near_data = await market_data.get_token_price("near")
        market_context = await market_data.get_market_context()
        
        logger.info("\n📊 Current Market Conditions:")
        logger.info(f"• NEAR Price: ${near_data['price']:.2f}")
        logger.info(f"• 24h Trading Volume: {near_data['24h_volume']}")
        logger.info(f"• Market Direction: {near_data['market_trend']}")
        logger.info(f"• Price Volatility: {near_data['volatility']}")
        
        # Load configuration
        config = load_config()
        
        logger.info("\n🤖 Phase 2: Agent Initialization")
        logger.info("Creating specialized AI agents with different roles...")
        
        # Market Analyzer: Evaluates market conditions and trends
        market_analyzer = SwarmAgent(
            config,
            SwarmConfig(
                role="market_analyzer",
                min_confidence=0.7,
                min_votes=2
            )
        )
        logger.info("✓ Market Analyzer: Evaluates price trends, volume, and market sentiment")

        # Risk Manager: Assesses transaction risks
        risk_manager = SwarmAgent(
            config,
            SwarmConfig(
                role="risk_manager",
                min_confidence=0.8,  # Higher threshold for risk management
                min_votes=2
            )
        )
        logger.info("✓ Risk Manager: Analyzes transaction risks and network conditions")

        # Strategy Optimizer: Optimizes execution parameters
        strategy_optimizer = SwarmAgent(
            config,
            SwarmConfig(
                role="strategy_optimizer",
                min_confidence=0.7,
                min_votes=2
            )
        )
        logger.info("✓ Strategy Optimizer: Fine-tunes transaction parameters")

        logger.info("\n🔄 Phase 3: Network Initialization")
        logger.info("Starting agents and establishing secure connections...")
        
        # Start all agents
        await market_analyzer.start()
        await risk_manager.start()
        await strategy_optimizer.start()
        logger.info("✓ All agents successfully connected to NEAR network")

        # Form swarm with all agents
        logger.info("\n🔗 Phase 4: Swarm Formation")
        logger.info("Connecting agents into a collaborative swarm network...")
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])
        logger.info("✓ Secure peer-to-peer connections established between agents")

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
                    "gas_price": "0.001",
                    "network_load": market_context["market"]["network_load"]
                }
            }
        }

        logger.info("\n🤔 Phase 5: Decision Making")
        logger.info("Analyzing proposed transaction...")
        logger.info(f"\n📝 Transaction Details:")
        logger.info(f"• Type: Transfer {proposal['params']['amount']} NEAR")
        logger.info(f"• To: {proposal['params']['recipient']}")
        logger.info(f"• Value: ${float(proposal['params']['amount']) * near_data['price']:.2f}")
        
        logger.info("\n💭 Agents are now evaluating the transaction...")
        logger.info("• Market Analyzer is checking market conditions")
        logger.info("• Risk Manager is assessing potential risks")
        logger.info("• Strategy Optimizer is evaluating execution parameters")

        # Get swarm consensus with LLM-powered evaluation
        result = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal["params"]
        )

        logger.info("\n🎯 Phase 6: Final Decision")
        logger.info(f"{'✅ Consensus reached' if result['consensus'] else '❌ Consensus not reached'}")
        logger.info(f"📊 Overall Approval Rate: {result['approval_rate']:.2%}")
        
        logger.info("\n💡 Agent Reasoning:")
        for i, reason in enumerate(result["reasons"], 1):
            logger.info(f"\nAgent {i} Analysis:")
            logger.info(f"• {reason}")

        if result["consensus"]:
            logger.info("\n✅ Transaction Approved")
            logger.info("All agents have approved with sufficient confidence")
            logger.info("Transaction is safe to execute")
        else:
            logger.info("\n❌ Transaction Rejected")
            logger.info("Insufficient consensus or confidence levels not met")
            logger.info("Transaction has been blocked for safety")

        return result

    except Exception as e:
        logger.error(f"❌ Strategy execution error: {str(e)}")
        raise
    finally:
        # Cleanup all agents
        logger.info("\n🧹 Phase 7: Cleanup")
        logger.info("Gracefully shutting down agents...")
        if market_data:
            await market_data.close()
        if market_analyzer:
            await market_analyzer.close()
        if risk_manager:
            await risk_manager.close()
        if strategy_optimizer:
            await strategy_optimizer.close()
        logger.info("✓ All agents successfully shut down")

if __name__ == "__main__":
    try:
        asyncio.run(run_simple_strategy())
    except KeyboardInterrupt:
        logger.info("\n👋 Strategy stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        raise 