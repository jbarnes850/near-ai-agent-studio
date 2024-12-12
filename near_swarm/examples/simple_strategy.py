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
from near_swarm.core.near_integration import NEARConnection

logger = logging.getLogger(__name__)

async def run_simple_strategy():
    """Run a simple strategy demonstrating swarm intelligence."""
    agents = []
    agent = None
    try:
        # Initialize agents with different roles using environment config
        config = load_config()

        # Initialize NEAR connection first
        near = NEARConnection(
            network=config.network,
            account_id=config.account_id,
            private_key=config.private_key
        )
        await near.check_account(config.account_id)

        # Initialize agents with different roles
        agent = SwarmAgent(
            config,
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )
        agents.append(agent)

        risk_manager = SwarmAgent(
            config,
            SwarmConfig(role="risk_manager", min_confidence=0.8)
        )
        agents.append(risk_manager)

        strategy_optimizer = SwarmAgent(
            config,
            SwarmConfig(role="strategy_optimizer", min_confidence=0.75)
        )
        agents.append(strategy_optimizer)

        # Create a test proposal
        proposal = {
            "receiver_id": "bob.testnet",
            "actions": [{
                "Transfer": {
                    "deposit": str(int(1 * 10**24))  # 1 NEAR in yoctoNEAR
                }
            }]
        }

        print("\n=== Running Simple Strategy Example ===")
        print(f"Proposing transaction: {proposal}")

        # Get consensus from all agents
        decisions = []
        for agent in agents:
            decision = await agent.evaluate_proposal(proposal)
            decisions.append(decision)

        # Calculate consensus
        total_votes = len([d for d in decisions if d["decision"]])
        approval_rate = (total_votes / len(decisions)) * 100

        print("\n=== Swarm Decision Analysis ===")
        print(f"Consensus reached: {total_votes >= 2}")
        print(f"Approval rate: {approval_rate:.2f}%")
        print(f"Total votes: {total_votes}")

        print("\nAgent Reasoning:\n")
        for i, decision in enumerate(decisions, 1):
            print(f"Agent {i}:")
            print(decision.get("reasoning", "No reasoning provided"))
            print()

        if total_votes >= 2:
            print("=== Executing Transaction ===")
            # Execute the transaction using NEAR connection
            await near.send_transaction(proposal)
            print("Transaction executed successfully!")

    finally:
        # Close all agent connections
        for agent in agents:
            await agent.close()

if __name__ == "__main__":
    asyncio.run(run_simple_strategy())
