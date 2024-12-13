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
    """Run a simple strategy example."""
    try:
        logger.info("Initializing simple strategy...")
        
        # Load configuration
        config = load_config()
        
        # Initialize agents
        market_analyzer = SwarmAgent(
            config,
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )

        risk_manager = SwarmAgent(
            config,
            SwarmConfig(role="risk_manager", min_confidence=0.8)
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

        print("\n=== Running Simple Strategy Example ===")
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

        return result

    except Exception as e:
        logger.error(f"Error in simple strategy: {str(e)}")
        raise
    finally:
        # Cleanup
        await market_analyzer.close()
        await risk_manager.close()

if __name__ == "__main__":
    asyncio.run(run_simple_strategy()) 