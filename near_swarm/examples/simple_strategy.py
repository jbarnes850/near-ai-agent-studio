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
            "type": "test_transaction",
            "params": {
                "action": "transfer",
                "recipient": "bob.testnet",
                "amount": "1",
                "token": "NEAR"
            },
            "proposer": config.account_id
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
            try:
                # Convert the proposal to NEAR transaction format
                near_tx = {
                    "receiver_id": proposal["params"]["recipient"],
                    "actions": [{
                        "Transfer": {
                            "deposit": str(int(float(proposal["params"]["amount"]) * 10**24))  # Convert to yoctoNEAR
                        }
                    }]
                }
                result = await near.send_transaction(near_tx)

                # Validate transaction result
                if isinstance(result, dict):
                    if "result" in result and "transaction_outcome" in result["result"]:
                        print("Transaction executed successfully!")
                        print(f"Transaction ID: {result['result']['transaction_outcome']['id']}")
                    elif "transaction_outcome" in result:
                        print("Transaction executed successfully!")
                        print(f"Transaction ID: {result['transaction_outcome']['id']}")
                    else:
                        raise ValueError("Invalid transaction response format")
                else:
                    raise ValueError("Invalid transaction response type")
            except Exception as e:
                logger.error(f"Failed to execute transaction: {str(e)}")
                raise

    finally:
        # Close all agent connections
        for agent in agents:
            await agent.close()

if __name__ == "__main__":
    asyncio.run(run_simple_strategy())
