"""
Simple Strategy Example
Demonstrates basic swarm intelligence with LLM-powered decision making
"""

import logging
import os
import base58
from typing import Dict, Any, Optional

from near_swarm.core.agent import Agent
from near_swarm.core.config import AgentConfig
from near_swarm.core.near_integration import NEARConnection, NEARConnectionError
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

logger = logging.getLogger(__name__)

async def run_simple_strategy(near_connection: Optional[NEARConnection] = None) -> Dict[str, Any]:
    """Run a simple strategy example that demonstrates swarm intelligence with LLM-powered decision making."""
    try:
        logger.info("Initializing simple strategy...")

        # Initialize NEAR connection if not provided
        if not near_connection:
            network = os.getenv("NEAR_NETWORK", "testnet")
            account_id = os.getenv("NEAR_ACCOUNT_ID")
            private_key = os.getenv("NEAR_PRIVATE_KEY")

            if not all([network, account_id, private_key]):
                raise RuntimeError("Missing required environment variables: NEAR_NETWORK, NEAR_ACCOUNT_ID, NEAR_PRIVATE_KEY")

            near_connection = NEARConnection(
                network=network,
                account_id=account_id,
                private_key=private_key
            )

        # Create agent configuration
        try:
            logger.debug("Attempting to access private key from key pair")
            # Access private key and encode it properly
            private_key_bytes = near_connection.signer.key_pair._secret_key  # Already in bytes
            private_key = f"ed25519:{base58.b58encode(private_key_bytes).decode('utf-8')}"
            logger.debug(f"Successfully accessed private key: {private_key[:16]}...")
        except AttributeError as e:
            logger.error(f"Failed to access private key: {str(e)}")
            raise RuntimeError(f"Failed to access private key: {str(e)}")

        config = AgentConfig(
            network=near_connection.network,
            account_id=near_connection.account_id,
            private_key=private_key,
            llm_provider=os.getenv("LLM_PROVIDER", "hyperbolic"),
            llm_api_key=os.getenv("LLM_API_KEY"),
            llm_model=os.getenv("LLM_MODEL", "meta-llama/Llama-3.3-70B-Instruct"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            api_url=os.getenv("HYPERBOLIC_API_URL")
        )

        # Initialize the agent with a specific role
        agent = Agent(config=config)
        swarm_config = SwarmConfig(
            role="market_analyzer",
            min_confidence=0.7,
            min_votes=1,
            timeout=1.0
        )

        # Create and use SwarmAgent with async context manager
        async with SwarmAgent(config=config, swarm_config=swarm_config) as swarm_agent:
            # Example: Evaluate a test proposal for a transfer transaction
            test_proposal = {
                "type": "transfer",
                "params": {
                    "amount": 0.1,  # Amount in NEAR
                    "recipient": "recipient-test.testnet",
                    "reason": "Test transaction for demonstration"
                },
                "proposer": near_connection.account_id  # Add proposer field
            }

            # Get swarm decision
            try:
                logger.info("Evaluating proposal with swarm agent...")
                swarm_decision = await swarm_agent.evaluate_proposal(test_proposal)
                logger.info(f"Swarm decision: {swarm_decision}")

                # Check if proposal was approved
                if swarm_decision.get("decision", False):
                    logger.info("Proposal approved by swarm. Executing transaction...")
                    try:
                        # Execute the transaction
                        result = await near_connection.send_transaction(
                            receiver_id=test_proposal["params"]["recipient"],
                            amount=test_proposal["params"]["amount"]
                        )
                        logger.info(f"Transaction executed successfully: {result}")
                        return {
                            "status": "success",
                            "message": "Strategy executed successfully",
                            "transaction": result,
                            "swarm_decision": swarm_decision
                        }
                    except Exception as e:
                        error_msg = f"Failed to execute transaction: {str(e)}"
                        logger.error(error_msg)
                        return {
                            "status": "error",
                            "message": error_msg,
                            "swarm_decision": swarm_decision
                        }
                else:
                    message = f"Proposal rejected by swarm. Reason: {swarm_decision.get('reasoning', 'No reason provided')}"
                    logger.info(message)
                    return {
                        "status": "rejected",
                        "message": message,
                        "swarm_decision": swarm_decision
                    }
            except Exception as e:
                error_msg = f"Error in swarm decision making: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    except Exception as e:
        logger.error(f"Error in simple strategy: {str(e)}")
        raise RuntimeError(f"Error in simple strategy: {str(e)}")
