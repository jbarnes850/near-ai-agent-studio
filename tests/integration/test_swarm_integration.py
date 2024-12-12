"""
Integration tests for NEAR Swarm Intelligence core functionality
"""

import pytest
from unittest.mock import AsyncMock, patch

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

@pytest.fixture
def agent_config():
    """Create test agent configuration."""
    return AgentConfig(
        network="testnet",
        account_id="test.testnet",
        private_key="ed25519:3D4YudUQRE39Lc4JHghuB5WM8kbgDDa34mnrEP5DdTApVH81af3e7MvFrog1CMNn67PCQmNkxQLPoacMuZydf2hL",
        llm_provider="hyperbolic",
        llm_api_key="test_key",
        llm_model="meta-llama/Llama-3.3-70B-Instruct",
        llm_temperature=0.7,
        llm_max_tokens=2000,
        api_url="https://api.hyperbolic.ai/v1"
    )

@pytest.mark.asyncio
async def test_swarm_consensus(agent_config):
    """Test swarm consensus with multiple agents."""
    with patch('near_swarm.core.near_integration.NEARConnection') as mock_connection, \
         patch('near_swarm.core.llm_provider.HyperbolicProvider.query', new_callable=AsyncMock) as mock_query:

        mock_connection.return_value.check_account = AsyncMock(return_value=True)
        mock_query.return_value = '{"decision": true, "confidence": 0.85, "reasoning": "Test reasoning"}'

        # Create agents with different roles
        market_analyzer = SwarmAgent(
            agent_config,
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )

        risk_manager = SwarmAgent(
            agent_config,
            SwarmConfig(role="risk_manager", min_confidence=0.8)
        )

        strategy_optimizer = SwarmAgent(
            agent_config,
            SwarmConfig(role="strategy_optimizer", min_confidence=0.75)
        )

        # Form swarm
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])

        # Test proposal
        proposal = {
            "type": "test_transaction",
            "params": {
                "action": "transfer",
                "recipient": "bob.testnet",
                "amount": "1",
                "token": "NEAR"
            },
            "proposer": agent_config.account_id
        }

        # Use agents within context managers
        async with market_analyzer as active_analyzer, \
                  risk_manager as active_risk_manager, \
                  strategy_optimizer as active_optimizer:

            # Get consensus
            result = await active_analyzer.propose_action(
                action_type=proposal["type"],
                params=proposal["params"]
            )

            # Verify consensus
            assert result["consensus"] == True
            assert result["approval_rate"] >= 0.7
            assert len(result["reasons"]) == 2  # Two peer agents

            # Verify LLM was queried for each agent
            assert mock_query.call_count == 2  # Two peer evaluations

        # Cleanup
        await market_analyzer.close()
        await risk_manager.close()
        await strategy_optimizer.close()

@pytest.mark.asyncio
async def test_swarm_transaction_execution(agent_config):
    """Test end-to-end transaction execution in swarm."""
    with patch('near_swarm.core.near_integration.NEARConnection') as mock_connection, \
         patch('near_swarm.core.llm_provider.HyperbolicProvider.query', new_callable=AsyncMock) as mock_query:

        mock_connection.return_value.check_account = AsyncMock(return_value=True)
        mock_query.return_value = '{"decision": true, "confidence": 0.9, "reasoning": "Test reasoning"}'

        # Create swarm
        agent = SwarmAgent(
            agent_config,
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )

        # Test transaction
        proposal = {
            "type": "transfer",
            "params": {
                "recipient": "bob.testnet",
                "amount": "1"
            },
            "proposer": agent_config.account_id
        }

        # Evaluate proposal
        async with agent as active_agent:
            result = await active_agent.evaluate_proposal(proposal)

            # Verify evaluation
            assert result["decision"] == True
            assert result["confidence"] >= 0.7
            assert "reasoning" in result

            # Verify LLM was queried
            assert mock_query.called

        # Cleanup
        await agent.close()
