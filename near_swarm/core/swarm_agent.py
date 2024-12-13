"""
Swarm Agent Module
Implements swarm intelligence for NEAR agents with LLM-powered decision making
"""

import logging
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from near_swarm.core.agent import Agent, AgentConfig
from near_swarm.core.llm_provider import LLMProvider, create_llm_provider, LLMConfig

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


class SwarmAgent(Agent):
    """NEAR agent with swarm intelligence and LLM-powered decision making capabilities."""

    def __init__(self, config: AgentConfig, swarm_config: SwarmConfig):
        """Initialize swarm agent."""
        super().__init__(config)
        self.swarm_config = swarm_config
        self.swarm_peers: List[SwarmAgent] = []

        # Handle optional api_url with default
        api_url = config.api_url or "https://api.hyperbolic.ai/v1"

        # Initialize LLM provider with validated config
        self.llm_provider = create_llm_provider(LLMConfig(
            provider=config.llm_provider,
            api_key=config.llm_api_key,
            model=config.llm_model,
            temperature=config.llm_temperature,
            max_tokens=config.llm_max_tokens,
            api_url=api_url  # Now we know this is not None
        ))
        self._is_running = False
        logger.info(f"Initialized swarm agent with role: {swarm_config.role}")

    async def __aenter__(self):
        """Async context manager entry."""
        self._is_running = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._is_running = False
        await self.close()
        return None

    def is_running(self) -> bool:
        """Check if the agent is running."""
        return self._is_running

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
        """Evaluate a proposal based on agent's role and expertise using LLM."""
        try:
            if not self._is_running:
                raise RuntimeError("transaction_outcome rejected - Agent is not running")

            # Basic validation
            if not proposal.get("type") or not proposal.get("params"):
                raise RuntimeError("transaction_outcome rejected - Invalid proposal format")

            # Role-specific evaluation using LLM
            role_prompt = ""
            if self.swarm_config.role == "risk_manager":
                role_prompt = """As a Risk Manager, your expertise is in:
- Position size optimization
- Exposure management
- Slippage calculation
- Smart contract risk assessment
- Network security evaluation

Key Metrics to Consider:
1. Current portfolio exposure
2. Historical volatility patterns
3. Smart contract security status
4. Network congestion levels
5. Liquidity depth impact"""
            elif self.swarm_config.role == "market_analyzer":
                role_prompt = """As a Market Analyzer, your expertise is in:
- Price trend analysis and pattern recognition
- Volume and liquidity assessment
- Market sentiment evaluation
- Technical indicator interpretation
- Cross-chain market comparison

Key Metrics to Consider:
1. Price momentum and volatility
2. Trading volume trends
3. Market depth and liquidity
4. Order book imbalances
5. Cross-exchange price differentials"""
            elif self.swarm_config.role == "strategy_optimizer":
                role_prompt = """As a Strategy Optimizer, your expertise is in:
- Gas optimization
- Execution timing
- Route optimization
- Fee minimization
- Performance analysis

Key Metrics to Consider:
1. Historical gas prices
2. Network congestion patterns
3. DEX routing efficiency
4. Fee structures across venues
5. Historical strategy performance"""
            else:
                raise RuntimeError(f"transaction_outcome rejected - Unsupported role: {self.swarm_config.role}")

            result = await self._evaluate_with_llm(proposal, role_prompt)
            return result

        except Exception as e:
            if "transaction_outcome" not in str(e):
                return {
                    "decision": False,
                    "confidence": 0.0,
                    "reasoning": f"Error evaluating proposal: {str(e)}"
                }
            raise

    async def _evaluate_with_llm(self, proposal: Dict[str, Any], role_prompt: str) -> Dict[str, Any]:
        """Evaluate proposal using LLM with role-specific prompt."""
        try:
            prompt = f"""You are a specialized AI agent in a NEAR Protocol trading swarm with the role of {self.swarm_config.role}.

{role_prompt}

Current Proposal:
{json.dumps(proposal, indent=2)}

Based on your role and expertise, evaluate this proposal and provide your decision in JSON format:
{{
    "decision": boolean,      // Whether to approve the proposal
    "confidence": float,      // Your confidence level (0.0 to 1.0)
    "reasoning": string       // Detailed explanation of your decision
}}

Focus on:
1. Risk assessment and market conditions
2. Technical analysis and price trends
3. Historical performance and patterns
4. Network activity and on-chain metrics
5. Liquidity and volume analysis

Response:"""

            # Query LLM provider
            response = await self.llm_provider.query(prompt)

            # Parse and validate response
            return self._parse_llm_response(response)

        except Exception as e:
            logger.error(f"LLM evaluation failed: {str(e)}")
            # Return failure response instead of raising error
            return {
                "decision": False,
                "confidence": 0.0,
                "reasoning": f"LLM evaluation failed: {str(e)}"
            }

    def _generate_evaluation_prompt(self, proposal: Dict[str, Any], role_prompt: str) -> str:
        """Generate a prompt for LLM evaluation."""
        prompt = f"""
As a {self.swarm_config.role}, evaluate the following proposal:

{role_prompt}

Proposal Details:
Type: {proposal.get('type')}
Parameters: {json.dumps(proposal.get('params', {}), indent=2)}
Proposer: {proposal.get('proposer', 'Unknown')}

Provide your evaluation in JSON format with the following fields:
- decision (boolean): Whether to approve the proposal
- confidence (float): Confidence level between 0 and 1
- reasoning (string): Detailed explanation of your decision

Response:"""
        return prompt

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate LLM response."""
        try:
            # Handle string-based decision values
            result = json.loads(response)
            
            # Convert string decision to boolean if needed
            if isinstance(result['decision'], str):
                result['decision'] = result['decision'].lower() != 'hold'
            
            # Validate required fields
            if not all(key in result for key in ['decision', 'confidence', 'reasoning']):
                raise ValueError("Missing required fields in LLM response")

            # Convert reasoning list to string if needed
            if isinstance(result['reasoning'], list):
                result['reasoning'] = ' '.join(result['reasoning'])

            # Validate types and ranges
            if not isinstance(result['confidence'], (int, float)) or not 0 <= result['confidence'] <= 1:
                raise ValueError("Confidence must be a float between 0 and 1")

            return result
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")

    async def _evaluate_risk(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from risk management perspective using LLM."""
        role_prompt = """Evaluate the proposal from a risk management perspective. Consider:
1. Transaction safety and security
2. Asset exposure and potential losses
3. Smart contract risks
4. Market volatility impact
5. Compliance and regulatory concerns"""
        return await self._evaluate_with_llm(proposal, role_prompt)

    async def _evaluate_market(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from market analysis perspective using LLM."""
        role_prompt = """Evaluate the proposal from a market analysis perspective. Consider:
1. Current market conditions
2. Price trends and volatility
3. Trading volume and liquidity
4. Market sentiment
5. Potential market impact"""
        return await self._evaluate_with_llm(proposal, role_prompt)

    async def _evaluate_strategy(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate proposal from strategy optimization perspective using LLM."""
        role_prompt = """Evaluate the proposal from a strategy optimization perspective. Consider:
1. Strategy effectiveness
2. Resource utilization
3. Expected returns
4. Risk-reward ratio
5. Alignment with objectives"""
        return await self._evaluate_with_llm(proposal, role_prompt)
