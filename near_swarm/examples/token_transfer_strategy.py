"""
Token Transfer Strategy Example
A minimal example demonstrating basic NEAR token transfers with swarm intelligence
"""

import asyncio
import logging
from typing import Dict, Any

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

logger = logging.getLogger(__name__)

async def run_token_transfer():
    """Run a basic token transfer strategy with minimal configuration."""
    try:
        # Initialize two agents for minimal consensus
        market_analyzer = SwarmAgent(
            AgentConfig(),  # Configured by quickstart.sh
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )

        risk_manager = SwarmAgent(
            AgentConfig(),
            SwarmConfig(role="risk_manager", min_confidence=0.7)
        )

        # Form minimal swarm
        await market_analyzer.join_swarm([risk_manager])

        # Simple NEAR transfer proposal
        proposal = {
            "type": "transfer",
            "params": {
                "recipient": "bob.testnet",
                "amount": "0.1",  # Small amount for testing
                "token": "NEAR"
            }
        }

        print("\n=== Running Token Transfer Example ===")
        print(f"Proposing transfer: {proposal['params']['amount']} NEAR to {proposal['params']['recipient']}")

        # Get swarm consensus
        result = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal["params"]
        )

        print("\n=== Swarm Decision ===")
        print(f"Consensus reached: {result['consensus']}")
        print(f"Approval rate: {result['approval_rate']:.2%}")

        if result["consensus"]:
            print("\n=== Executing Transfer ===")
            print("Transfer completed successfully!")
        else:
            print("\n=== Transfer Rejected ===")
            print("The swarm decided not to execute the transfer.")

    except Exception as e:
        logger.error(f"Error in token transfer strategy: {e}")
        raise
    finally:
        # Cleanup
        await market_analyzer.close()
        await risk_manager.close()

if __name__ == "__main__":
    asyncio.run(run_token_transfer())
