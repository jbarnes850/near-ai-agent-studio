"""Simple strategy implementation for NEAR Swarm Intelligence."""
import asyncio
import json
import logging
from typing import Dict, Any, List

from near_swarm.core.swarm_agent import SwarmAgent
from near_swarm.core.strategy import Strategy

logger = logging.getLogger(__name__)

class SimpleStrategy(Strategy):
    """A simple strategy that demonstrates LLM-powered multi-agent decision making."""

    def __init__(self, agents: List[SwarmAgent]):
        """Initialize the strategy with a list of agents."""
        super().__init__(agents)
        self._is_running = False

    async def start(self):
        """Start the strategy."""
        if self._is_running:
            return

        logger.info("Starting simple strategy")
        self._is_running = True

        # Start all agents
        await asyncio.gather(*[agent.start() for agent in self.agents])

    async def stop(self):
        """Stop the strategy."""
        if not self._is_running:
            return

        logger.info("Stopping simple strategy")
        self._is_running = False

        # Stop all agents
        await asyncio.gather(*[agent.stop() for agent in self.agents])

    async def execute(self) -> Dict[str, Any]:
        """Execute the strategy with LLM-powered decision making."""
        if not self._is_running:
            raise RuntimeError("Strategy must be started before execution")

        try:
            # Simulate getting market data (in a real implementation, this would come from external sources)
            market_context = {
                "current_price": "3.45",
                "24h_volume": "15.2M",
                "volatility": "Medium",
                "market_trend": "Bullish",
                "gas_price": "2.5 Gwei",
                "network_load": "Moderate"
            }

            # Create a sample proposal with market context
            proposal = {
                "type": "transfer",
                "params": {
                    "amount": "10",
                    "token": "NEAR",
                    "recipient": "example.near",
                    "market_context": market_context
                }
            }

            # Collect evaluations from all agents
            evaluations = await asyncio.gather(*[
                agent.evaluate_proposal(proposal)
                for agent in self.agents
            ])

            # Aggregate decisions with confidence weighting
            total_confidence = sum(eval["confidence"] for eval in evaluations)
            if total_confidence == 0:
                return {
                    "decision": False,
                    "confidence": 0.0,
                    "reasoning": "No agent provided a confident evaluation"
                }

            # Weight each decision by its confidence
            weighted_decision = sum(
                eval["confidence"] * (1.0 if eval["decision"] else 0.0)
                for eval in evaluations
            ) / total_confidence

            # Final decision requires >66% confidence-weighted consensus
            final_decision = weighted_decision > 0.66

            # Combine reasoning from all agents
            combined_reasoning = "\n\nAgent Evaluations:\n" + "\n".join([
                f"- {self.agents[i].swarm_config.role}: {eval['reasoning']} (Confidence: {eval['confidence']:.2f})"
                for i, eval in enumerate(evaluations)
            ])

            return {
                "decision": final_decision,
                "confidence": weighted_decision,
                "reasoning": f"Consensus Decision: {'Approved' if final_decision else 'Rejected'} with {weighted_decision:.2%} confidence.{combined_reasoning}"
            }

        except Exception as e:
            logger.error(f"Strategy execution failed: {str(e)}")
            return {
                "decision": False,
                "confidence": 0.0,
                "reasoning": f"Strategy execution failed: {str(e)}"
            } 