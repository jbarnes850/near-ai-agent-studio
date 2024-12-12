"""
Core Swarm Agent Tests
Tests essential functionality for NEAR Swarm Intelligence
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig


@pytest.fixture
def agent_config():
    """Create test agent configuration."""
    return AgentConfig(
        network="testnet",
        account_id="test.testnet",
        private_key="ed25519:3D4YudUQRE39Lc4JHghuB5WM8kbgDDa34mnrEP5DdTApVH81af3e7MvFronz1F2u9wsnS4jx4nX4UNqm8M2n8acG",
        llm_provider="hyperbolic",
        llm_api_key="test_key",
        api_url="https://api.hyperbolic.ai/v1"
    )


@pytest.fixture
def swarm_config():
    """Create test swarm configuration."""
    return SwarmConfig(
        role="market_analyzer",
        min_confidence=0.7,
        min_votes=2,
        timeout=1.0
    )


@pytest.mark.asyncio
async def test_swarm_config_validation():
    """Test swarm configuration validation."""
    # Test valid config
    config = SwarmConfig(
        role="market_analyzer",
        min_confidence=0.7,
        min_votes=2,
        timeout=1.0
    )
    assert config.role == "market_analyzer"
    assert config.min_confidence == 0.7

    # Test invalid confidence
    with pytest.raises(ValueError):
        SwarmConfig(
            role="market_analyzer",
            min_confidence=1.5,  # Invalid confidence
            min_votes=2,
            timeout=1.0
        )


@pytest.mark.asyncio
async def test_swarm_formation(agent_config, swarm_config):
    """Test basic swarm formation."""
    with patch('near_swarm.core.near_integration.NEARConnection') as mock_connection:
        mock_connection.return_value.check_account = Mock(return_value=True)

        # Create agents
        main_agent = SwarmAgent(agent_config, swarm_config)
        peer_agent = SwarmAgent(agent_config, SwarmConfig(role="risk_manager"))

        # Join swarm
        await main_agent.join_swarm([peer_agent])

        # Verify connections
        assert len(main_agent.swarm_peers) == 1
        assert peer_agent in main_agent.swarm_peers
        assert main_agent in peer_agent.swarm_peers

        # Cleanup
        await main_agent.close()
        await peer_agent.close()


@pytest.mark.asyncio
async def test_llm_evaluation(agent_config, swarm_config):
    """Test LLM-based proposal evaluation."""
    with patch('near_swarm.core.near_integration.NEARConnection') as mock_connection, \
         patch('near_swarm.core.llm_provider.HyperbolicProvider.query', new_callable=AsyncMock) as mock_query:

        mock_connection.return_value.check_account = Mock(return_value=True)
        mock_query.return_value = '{"decision": true, "confidence": 0.85, "reasoning": "Test reasoning"}'

        # Create agent
        agent = SwarmAgent(agent_config, swarm_config)

        # Test proposal
        proposal = {
            "type": "market_trade",
            "params": {
                "asset": "near",
                "action": "buy",
                "amount": 100
            },
            "proposer": "test.testnet"
        }

        # Test evaluation using async context manager
        async with agent as active_agent:
            result = await active_agent.evaluate_proposal(proposal)
            assert result["decision"] == True
            assert result["confidence"] == 0.85
            assert "Test reasoning" in result["reasoning"]

            # Verify LLM was called with correct role
            mock_query.assert_called_once()
            call_args = mock_query.call_args[0][0]
            assert swarm_config.role in call_args
            assert "market_trade" in call_args


@pytest.mark.asyncio
async def test_llm_evaluation_error_handling(agent_config, swarm_config):
    """Test LLM evaluation error handling."""
    with patch('near_swarm.core.near_integration.NEARConnection') as mock_connection, \
         patch('near_swarm.core.llm_provider.HyperbolicProvider.query', new_callable=AsyncMock) as mock_query:

        mock_connection.return_value.check_account = Mock(return_value=True)
        mock_query.side_effect = Exception("LLM API error")

        # Create agent
        agent = SwarmAgent(agent_config, swarm_config)

        # Test proposal
        proposal = {
            "type": "market_trade",
            "params": {
                "asset": "near",
                "action": "buy",
                "amount": 100
            },
            "proposer": "test.testnet"
        }

        # Test evaluation with error using async context manager
        async with agent as active_agent:
            result = await active_agent.evaluate_proposal(proposal)
            assert result["decision"] == False
            assert result["confidence"] == 0.0
            assert "LLM API error" in result["reasoning"]
