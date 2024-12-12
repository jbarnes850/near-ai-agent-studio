"""
NEAR Swarm Intelligence Strategy Template
"""

import asyncio
import logging
from typing import Dict, Any

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

logger = logging.getLogger(__name__)

async def run_strategy():
    """Run the strategy."""
    try:
        # Initialize agents with different roles
        market_analyzer = SwarmAgent(
            AgentConfig(),  # Will be configured by quickstart.sh
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )

        risk_manager = SwarmAgent(
            AgentConfig(),
            SwarmConfig(role="risk_manager", min_confidence=0.8)
        )

        strategy_optimizer = SwarmAgent(
            AgentConfig(),
            SwarmConfig(role="strategy_optimizer", min_confidence=0.75)
        )

        # Form swarm
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])

        # Define your strategy logic here
        proposal = {
            "type": "your_action_type",
            "params": {
                # Add your parameters here
            }
        }

        # Get swarm consensus
        result = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal["params"]
        )

        # Process result
        if result["consensus"]:
            logger.info("Consensus reached, executing action...")
            # Implement your action execution here
        else:
            logger.info("Consensus not reached, skipping action")

    except Exception as e:
        logger.error(f"Strategy execution failed: {str(e)}")
        raise
    finally:
        # Cleanup
        await market_analyzer.close()
        await risk_manager.close()
        await strategy_optimizer.close()

if __name__ == "__main__":
    asyncio.run(run_strategy())
