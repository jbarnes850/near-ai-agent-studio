"""
Swarm Agent Module
Implements swarm intelligence for NEAR agents with LLM-powered decision making
"""

import logging
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from near_swarm.core.agent import SwarmAgent, AgentConfig
from near_swarm.core.llm_provider import LLMProvider, create_llm_provider, LLMConfig
from near_swarm.plugins.base import AgentPlugin

logger = logging.getLogger(__name__)


@dataclass
class SwarmConfig:
    """Swarm agent configuration."""
    role: str
    min_confidence: float = 0.7
    min_votes: int = 2
    timeout: float = 1.0
    max_retries: int = 3
    llm: Optional[LLMConfig] = None

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


class SwarmAgent(AgentPlugin):
    """Swarm agent with plugin support and LLM-powered decision making."""

    def __init__(self, config: SwarmConfig):
        """Initialize swarm agent."""
        self.config = config
        self.llm = None
        self.swarm_peers: List['SwarmAgent'] = []
        self._initialized = False
        self._is_running = False
        logger.info(f"Initialized swarm agent with role: {config.role}")

    async def initialize(self) -> None:
        """Initialize agent resources."""
        if self._initialized:
            return

        try:
            # Initialize LLM if configured
            if self.config.llm:
                self.llm = create_llm_provider(self.config.llm)

            self._initialized = True
            self._is_running = True
            logger.info(f"Initialized SwarmAgent with role: {self.config.role}")

        except Exception as e:
            logger.error(f"Error initializing SwarmAgent: {str(e)}")
            raise

    async def join_swarm(self, peers: List['SwarmAgent']):
        """Join a swarm of agents."""
        self.swarm_peers = peers
        for peer in peers:
            if self not in peer.swarm_peers:
                peer.swarm_peers.append(self)
        logger.info(f"Joined swarm with {len(peers)} peers")

    async def propose_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Propose an action to the swarm."""
        if not self._is_running:
            raise RuntimeError("Cannot propose action - Agent is not running")

        proposal = {
            "type": action_type,
            "params": params,
            "proposer": self.config.role
        }

        # Collect votes from peers
        votes = []
        for peer in self.swarm_peers:
            vote = await peer.evaluate_proposal(proposal)
            votes.append(vote)

        # Calculate consensus
        total_votes = len(votes)
        positive_votes = sum(1 for v in votes if v["decision"] == "approve")
        approval_rate = positive_votes / total_votes if total_votes > 0 else 0

        # Check if consensus is reached
        consensus = (
            approval_rate >= self.config.min_confidence and
            positive_votes >= self.config.min_votes
        )

        result = {
            "consensus": consensus,
            "approval_rate": approval_rate,
            "total_votes": total_votes,
            "votes": votes,
            "reasons": [v["reasoning"] for v in votes]
        }

        logger.info(f"Proposal result: consensus={consensus}, approval_rate={approval_rate}")
        return result

    async def evaluate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a proposal using role-specific expertise."""
        if not self._is_running:
            return {"decision": "reject", "confidence": 0.0, "reasoning": "Agent is not running"}

        try:
            # Get role-specific evaluation prompt
            role_prompt = self._get_role_prompt()
            
            # Add proposal context
            context = {
                "proposal": proposal,
                "role": self.config.role,
                "role_prompt": role_prompt
            }

            # Use plugin's evaluate method
            result = await self.evaluate(context)

            # Ensure proper response format
            if "error" in result:
                return {
                    "decision": "reject",
                    "confidence": 0.0,
                    "reasoning": f"Evaluation error: {result['error']}"
                }

            return result

        except Exception as e:
            logger.error(f"Error evaluating proposal: {str(e)}")
            return {
                "decision": "reject",
                "confidence": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}"
            }

    def _get_role_prompt(self) -> str:
        """Get role-specific evaluation prompt."""
        if self.config.role == "risk_manager":
            return """As a Risk Manager, evaluate this proposal focusing on:
1. Position Size Analysis
2. Security Assessment
3. Risk Metrics
4. Compliance and Limits

Your primary responsibility is protecting assets and maintaining risk parameters."""

        elif self.config.role == "market_analyzer":
            return """As a Market Analyzer, evaluate this proposal focusing on:
1. Price Analysis
2. Market Conditions
3. Technical Indicators
4. Cross-market Analysis

Your primary responsibility is market analysis and trend identification."""

        elif self.config.role == "strategy_optimizer":
            return """As a Strategy Optimizer, evaluate this proposal focusing on:
1. Execution Optimization
2. Cost Analysis
3. Performance Metrics
4. Technical Efficiency

Your primary responsibility is optimizing execution and performance."""

        return f"As a {self.config.role}, evaluate this proposal based on your expertise."

    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate using LLM and return decision."""
        if not self._initialized:
            await self.initialize()

        try:
            # Format context for LLM
            prompt = self._format_prompt(context)

            # Get LLM response
            response = await self.llm.query(prompt)

            # Parse and validate response
            result = self._parse_response(response)

            if result["confidence"] < self.config.min_confidence:
                logger.warning(f"Low confidence decision: {result['confidence']}")
                return {"decision": "abstain", "reason": "Low confidence"}

            return result

        except Exception as e:
            logger.error(f"Error in evaluation: {str(e)}")
            return {"error": str(e)}

    def _format_prompt(self, context: Dict[str, Any]) -> str:
        """Format context into LLM prompt."""
        proposal = context.get("proposal", {})
        role_prompt = context.get("role_prompt", "")

        return f"""
        {role_prompt}

        Proposal to Evaluate:
        Type: {proposal.get('type')}
        Parameters: {json.dumps(proposal.get('params', {}), indent=2)}
        Proposer: {proposal.get('proposer')}

        Provide your analysis and decision in JSON format with:
        - decision: string (approve/reject/abstain)
        - confidence: float (0-1)
        - reasoning: string
        """

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        try:
            result = json.loads(response)
            required_fields = ["decision", "confidence", "reasoning"]

            if not all(field in result for field in required_fields):
                raise ValueError("Missing required fields in response")

            # Validate decision values
            if result["decision"] not in ["approve", "reject", "abstain"]:
                raise ValueError("Invalid decision value")

            # Validate confidence range
            if not isinstance(result["confidence"], (int, float)) or not 0 <= result["confidence"] <= 1:
                raise ValueError("Confidence must be a float between 0 and 1")

            return result

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")

    async def cleanup(self) -> None:
        """Clean up agent resources."""
        self._initialized = False
        self._is_running = False
        self.swarm_peers = []
        logger.info("SwarmAgent cleaned up")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
        return None
