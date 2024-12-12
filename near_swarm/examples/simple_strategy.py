"""
Simple Strategy Example
Demonstrates basic swarm intelligence with LLM-powered decision making
"""

import asyncio
import logging
from typing import List, Dict, Any

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.config import load_config

logger = logging.getLogger(__name__)

async def run_simple_strategy():
    """Run a simple strategy demonstrating swarm intelligence."""
    try:
        # Initialize agents with different roles using environment config
        config = load_config()

        market_analyzer = SwarmAgent(
            config,
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )

        risk_manager = SwarmAgent(
            config,
            SwarmConfig(role="risk_manager", min_confidence=0.8)
        )

        strategy_optimizer = SwarmAgent(
            config,
            SwarmConfig(role="strategy_optimizer", min_confidence=0.75)
        )

        # Form swarm
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])

        # Example transaction proposal
        proposal = {
            "type": "test_transaction",
            "params": {
                "action": "transfer",
                "recipient": "bob.testnet",
                "amount": "1",
                "token": "NEAR"
            }
        }

        print("\n=== Running Simple Strategy Example ===")
        print(f"Proposing transaction: {proposal}")

        # Get swarm consensus
        result = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal["params"]
        )

        print("\n=== Swarm Decision Analysis ===")
        print(f"Consensus reached: {result['consensus']}")
        print(f"Approval rate: {result['approval_rate']:.2%}")
        print(f"Total votes: {result['total_votes']}")
        print("\nAgent Reasoning:")
        for i, reason in enumerate(result['reasons'], 1):
            print(f"\nAgent {i}:")
            print(reason)

        if result["consensus"]:
            print("\n=== Executing Transaction ===")
            # Execute the transaction if consensus is reached
            # Note: In this example, we're just simulating the execution
            print("Transaction executed successfully!")
        else:
            print("\n=== Transaction Rejected ===")
            print("The swarm decided not to execute the transaction.")

    except Exception as e:
        logger.error(f"Error running simple strategy: {e}")
        raise
    finally:
        # Cleanup
        await market_analyzer.close()
        await risk_manager.close()
        await strategy_optimizer.close()

if __name__ == "__main__":
    asyncio.run(run_simple_strategy())
