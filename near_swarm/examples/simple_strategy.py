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

logger = logging.getLogger(__name__)

async def run_simple_strategy() -> Dict[str, Any]:
    """Run a simple strategy example demonstrating LLM-powered multi-agent decision making."""
    # Initialize agents as None
    market_analyzer = None
    risk_manager = None
    strategy_optimizer = None
    
    try:
        logger.info("Initializing simple strategy...")
        
        # Load configuration
        config = load_config()
        
        # Initialize agents with specific roles and confidence thresholds
        market_analyzer = SwarmAgent(
            config,
            SwarmConfig(
                role="market_analyzer",
                min_confidence=0.7,
                min_votes=2
            )
        )

        risk_manager = SwarmAgent(
            config,
            SwarmConfig(
                role="risk_manager",
                min_confidence=0.8,  # Higher threshold for risk management
                min_votes=2
            )
        )

        strategy_optimizer = SwarmAgent(
            config,
            SwarmConfig(
                role="strategy_optimizer",
                min_confidence=0.7,
                min_votes=2
            )
        )

        # Start all agents
        await market_analyzer.start()
        await risk_manager.start()
        await strategy_optimizer.start()

        # Form swarm with all agents
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])

        # Example NEAR transfer proposal with market context
        proposal = {
            "type": "transfer",
            "params": {
                "recipient": "bob.testnet",
                "amount": "0.1",
                "token": "NEAR",
                "market_context": {
                    "current_price": 5.45,
                    "24h_volume": "2.1M",
                    "volatility": "medium",
                    "market_trend": "upward",
                    "gas_price": "0.001",
                    "network_load": "moderate"
                }
            }
        }

        print("\n=== Running LLM-Powered Multi-Agent Strategy Example ===")
        print(f"Proposing transfer: {proposal['params']['amount']} NEAR to {proposal['params']['recipient']}")
        print("\nMarket Context:")
        print(f"• Current NEAR Price: ${proposal['params']['market_context']['current_price']}")
        print(f"• 24h Volume: ${proposal['params']['market_context']['24h_volume']}")
        print(f"• Market Trend: {proposal['params']['market_context']['market_trend']}")
        print(f"• Network Load: {proposal['params']['market_context']['network_load']}")

        # Get swarm consensus with LLM-powered evaluation
        result = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal["params"]
        )

        print("\n=== Swarm Decision Analysis ===")
        print(f"Consensus reached: {result['consensus']}")
        print(f"Approval rate: {result['approval_rate']:.2%}")
        print("\nAgent Reasoning:")
        for i, reason in enumerate(result["reasons"]):
            print(f"\nAgent {i+1}:")
            print(f"• {reason}")

        if result["consensus"]:
            print("\n=== Executing Transfer ===")
            print("✅ Transfer completed successfully!")
            print("All agents have approved with sufficient confidence.")
        else:
            print("\n=== Transfer Rejected ===")
            print("❌ The swarm decided not to execute the transfer.")
            print("Insufficient consensus or confidence levels not met.")

        return result

    except Exception as e:
        logger.error(f"Error in simple strategy: {str(e)}")
        raise
    finally:
        # Cleanup all agents
        if market_analyzer:
            await market_analyzer.close()
        if risk_manager:
            await risk_manager.close()
        if strategy_optimizer:
            await strategy_optimizer.close()

if __name__ == "__main__":
    asyncio.run(run_simple_strategy()) 