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
            api_url=api_url,  # Now we know this is not None
            system_prompt=config.system_prompt
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

    async def evaluate_proposal(self, proposal: Dict[str, Any], stream: bool = False) -> Dict[str, Any]:
        """Evaluate a proposal based on agent's role and expertise using LLM."""
        try:
            if not self._is_running:
                raise RuntimeError("transaction_outcome rejected - Agent is not running")

            # Basic validation
            if not proposal.get("type") or not proposal.get("params"):
                raise RuntimeError("transaction_outcome rejected - Invalid proposal format")

            # Handle general chat interactions
            if proposal["type"] == "general_chat" and self.swarm_config.role == "chat_assistant":
                query = proposal["params"]["query"]
                context = proposal["params"].get("context", {})
                
                prompt = f"""You are a helpful AI assistant for the NEAR Protocol ecosystem.
Your role is to help users understand and interact with NEAR's features and capabilities.

User Query: {query}

Please provide a helpful, informative response that:
1. Directly addresses the user's question
2. Includes relevant NEAR Protocol information
3. Suggests useful commands or next steps if applicable
4. Maintains a friendly, conversational tone

Current Context:
{json.dumps(context, indent=2)}

Response should be clear, accurate, and engaging.
Do not include any JSON formatting in your response.
Just provide the natural language response directly."""

                if stream:
                    # For streaming, return an async generator
                    async def response_stream():
                        async for chunk in self.llm_provider.stream(prompt):
                            yield chunk
                    return {
                        "type": "chat_response",
                        "stream": response_stream(),
                        "confidence": 0.95
                    }
                else:
                    # For non-streaming, return the complete response
                    response = await self.llm_provider.query(prompt, expect_json=False)
                    return {
                        "content": response,
                        "type": "chat_response",
                        "confidence": 0.95
                    }

            # For other proposal types, expect JSON responses
            role_prompt = ""
            if self.swarm_config.role == "risk_manager":
                role_prompt = """As a Risk Manager, evaluate this proposal focusing on:
1. Position Size Analysis:
   - Check if the transaction amount is within safe limits
   - Evaluate total portfolio exposure
   - Consider historical volatility impact

2. Security Assessment:
   - Analyze smart contract risks
   - Evaluate network security status
   - Check for any recent security incidents

3. Risk Metrics:
   - Calculate potential downside risk
   - Assess slippage impact
   - Evaluate market depth and liquidity

4. Compliance and Limits:
   - Verify transaction limits
   - Check for any regulatory concerns
   - Ensure compliance with portfolio guidelines

Your primary responsibility is protecting assets and maintaining risk parameters."""

            elif self.swarm_config.role == "market_analyzer":
                role_prompt = """As a Market Analyzer, evaluate this proposal focusing on:
1. Price Analysis:
   - Current price trends and momentum
   - Support and resistance levels
   - Volume profile and patterns

2. Market Conditions:
   - Overall market sentiment
   - Trading volume analysis
   - Market depth assessment

3. Technical Indicators:
   - Moving averages and trends
   - Volatility metrics
   - Momentum indicators

4. Cross-market Analysis:
   - Price correlations
   - Arbitrage opportunities
   - Market inefficiencies

Your primary responsibility is market analysis and trend identification."""

            elif self.swarm_config.role == "strategy_optimizer":
                role_prompt = """As a Strategy Optimizer, evaluate this proposal focusing on:
1. Execution Optimization:
   - Gas price analysis
   - Network congestion assessment
   - Timing optimization

2. Cost Analysis:
   - Transaction fee evaluation
   - Slippage estimation
   - Total cost impact

3. Performance Metrics:
   - Historical strategy performance
   - Success rate analysis
   - Optimization opportunities

4. Technical Efficiency:
   - Route optimization
   - Protocol efficiency
   - Implementation improvements

Your primary responsibility is optimizing execution and performance."""

            elif self.swarm_config.role == "chat_assistant":
                role_prompt = """As a Chat Assistant, evaluate this interaction focusing on:
1. User Intent Analysis:
   - Understand the user's question or request
   - Identify key topics and concepts
   - Determine required information or actions

2. Response Planning:
   - Structure clear and helpful responses
   - Include relevant NEAR ecosystem information
   - Suggest appropriate commands or tools

3. Knowledge Integration:
   - Incorporate NEAR Protocol expertise
   - Reference relevant documentation
   - Provide practical examples

4. Interaction Quality:
   - Maintain conversational tone
   - Ensure accuracy and clarity
   - Guide users effectively

Your primary responsibility is helping users understand and interact with the NEAR ecosystem."""

            else:
                raise RuntimeError(f"transaction_outcome rejected - Unsupported role: {self.swarm_config.role}")

            # Add market context analysis
            if "market_context" in proposal["params"]:
                context = proposal["params"]["market_context"]
                role_prompt += f"""

Current Market Context:
• NEAR Price: ${context.get('current_price', 'N/A')}
• 24h Volume: {context.get('24h_volume', 'N/A')}
• Volatility: {context.get('volatility', 'N/A')}
• Market Trend: {context.get('market_trend', 'N/A')}
• Gas Price: {context.get('gas_price', 'N/A')}
• Network Load: {context.get('network_load', 'N/A')}

Consider these market conditions in your evaluation."""

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
Type: {proposal['type']}
Amount: {proposal['params'].get('amount', '0.1')} NEAR
Recipient: {proposal['params'].get('recipient', 'bob.testnet')}
Market Context:
- Price: ${proposal['params'].get('market_context', {}).get('current_price', '4.91')}
- Volume: ${proposal['params'].get('market_context', {}).get('24h_volume', '401M')}
- Trend: {proposal['params'].get('market_context', {}).get('market_trend', 'neutral')}
- Network Load: {proposal['params'].get('market_context', {}).get('network_load', 'moderate')}

Evaluate this proposal based on your role and expertise. Consider all market conditions and risk factors.
Provide a thorough analysis with clear reasoning for your decision.

You must respond with a valid JSON object containing exactly these fields:
{{
    "decision": boolean,      // true to approve, false to reject
    "confidence": number,     // between 0.0 and 1.0
    "reasoning": string      // detailed explanation
}}

Example response:
{{
    "decision": true,
    "confidence": 0.85,
    "reasoning": "Market conditions are favorable with low volatility..."
}}"""

            response = await self.llm_provider.query(prompt, expect_json=True)
            return json.loads(response)

        except Exception as e:
            return {
                "decision": False,
                "confidence": 0.0,
                "reasoning": f"Error evaluating proposal: {str(e)}"
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
