"""
Swarm Agent Module
Implements swarm intelligence for NEAR agents
"""

import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from near_swarm.core.agent import NEARAgent, AgentConfig

logger = logging.getLogger(__name__)


@dataclass
class SwarmConfig:
    """Swarm agent configuration."""
    role: str
    min_confidence: float = 0.7
    min_votes: int = 2
    timeout: float = 1.0

    def __post_init__(self):
        """Validate configuration."""
        if not self.role:
            raise ValueError("role is required")
        if self.min_confidence < 0 or self.min_confidence > 1:
            raise ValueError("min_confidence must be between 0 and 1")
        if self.min_votes < 1:
            raise ValueError("min_votes must be at least 1")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")


class SwarmAgent(NEARAgent):
    """NEAR agent with swarm intelligence capabilities."""

    def __init__(self, config: AgentConfig, swarm_config: SwarmConfig):
        """Initialize swarm agent."""
        super().__init__(config)
        self.swarm_config = swarm_config
        self.swarm_peers: List[SwarmAgent] = []
        logger.info(f"Initialized swarm agent with role: {swarm_config.role}")

    async def join_swarm(self, peers: List['SwarmAgent']):
        """Join a swarm of agents."""
        self.swarm_peers = peers
        for peer in peers:
            if self not in peer.swarm_peers:
                peer.swarm_peers.append(self)
        logger.info(f"Joined swarm with {len(peers)} peers")

    async def propose_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Propose an action to the swarm."""
        proposal = {
            "type": action_type,
            "params": params,
            "proposer": self.config.account_id
        }

        # Collect votes from peers
        votes = []
        for peer in self.swarm_peers:
            vote = await peer.evaluate_proposal(proposal)
            votes.append(vote)

        # Calculate consensus
        total_votes = len(votes)
        positive_votes = sum(1 for v in votes if v["decision"])
        approval_rate = positive_votes / total_votes if total_votes > 0 else 0

        # Check if consensus is reached
        consensus = (
            approval_rate >= self.swarm_config.min_confidence and
            positive_votes >= self.swarm_config.min_votes
        )

        result = {
            "consensus": consensus,
            "approval_rate": approval_rate,
            "total_votes": total_votes,
            "reasons": [v["reasoning"] for v in votes]
        }

        logger.info(f"Proposal result: consensus={consensus}, approval_rate={approval_rate}")
        return result

    async def evaluate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a proposal based on agent's role and expertise."""
        try:
            # Basic validation
            if not proposal.get("type") or not proposal.get("params"):
                return {
                    "decision": False,
                    "confidence": 0.0,
                    "reasoning": "Invalid proposal format"
                }

            # Role-specific evaluation
            if self.swarm_config.role == "risk_manager":
                return await self._evaluate_risk(proposal)
            elif self.swarm_config.role == "market_analyzer":
                return await self._evaluate_market(proposal)
            elif self.swarm_config.role == "strategy_optimizer":
                return await self._evaluate_strategy(proposal)
            else:
                return {
                    "decision": False,
                    "confidence": 0.0,
                    "reasoning": f"Unsupported role: {self.swarm_config.role}"
                }

        except Exception as e:
            logger.error(f"Error evaluating proposal: {str(e)}")
            return {
                "decision": False,
                "confidence": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}"
            }

    async def _evaluate_risk(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from risk management perspective."""
        # Implement risk evaluation logic
        return {
            "decision": True,
            "confidence": 0.8,
            "reasoning": "Risk levels acceptable"
        }

    async def _evaluate_market(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from market analysis perspective."""
        # Implement market analysis logic
        return {
            "decision": True,
            "confidence": 0.9,
            "reasoning": "Market conditions favorable"
        }

    async def _evaluate_strategy(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from strategy optimization perspective."""
        # Implement strategy evaluation logic
        return {
            "decision": True,
            "confidence": 0.85,
            "reasoning": "Strategy aligns with objectives"
        }