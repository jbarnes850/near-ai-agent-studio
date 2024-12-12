"""
Core Agent Tests
Tests essential functionality for NEAR AI Agent
"""

import pytest
from unittest.mock import Mock, patch

from near_swarm.core.agent import Agent, AgentConfig


@pytest.fixture
def agent_config():
    """Create test agent configuration."""
    return AgentConfig(
        network="testnet",
        account_id="test.testnet",
        private_key="ed25519:3D4YudUQRE39Lc4JHghuB5WM8kbgDDa34mnrEP5DdTApVH81af3e7MvFronz1F2u9wsnS4jx4nX4UNqm8M2n8acG",
        llm_provider="hyperbolic",
        llm_api_key="test_key"
    )


@pytest.mark.asyncio
async def test_config_validation():
    """Test configuration validation."""
    # Test valid config
    config = AgentConfig(
        network="testnet",
        account_id="test.testnet",
        private_key="ed25519:3D4YudUQRE39Lc4JHghuB5WM8kbgDDa34mnrEP5DdTApVH81af3e7MvFronz1F2u9wsnS4jx4nX4UNqm8M2n8acG",
        llm_provider="hyperbolic",
        llm_api_key="test_key"
    )
    assert config.network == "testnet"
    assert config.account_id == "test.testnet"

    # Test invalid network
    with pytest.raises(ValueError):
        AgentConfig(
            network="invalid_network",
            account_id="test.testnet",
            private_key="ed25519:3D4YudUQRE39Lc4JHghuB5WM8kbgDDa34mnrEP5DdTApVH81af3e7MvFronz1F2u9wsnS4jx4nX4UNqm8M2n8acG",
            llm_provider="hyperbolic",
            llm_api_key="test_key"
        )


@pytest.mark.asyncio
async def test_agent_lifecycle(agent_config):
    """Test basic agent lifecycle."""
    with patch('near_swarm.core.near_integration.NEARConnection') as mock_connection:
        mock_connection.return_value.check_account = Mock(return_value=True)
        agent = Agent(agent_config)

        # Test start
        await agent.start()
        assert agent.is_running() is True

        # Test stop
        await agent.stop()
        assert agent.is_running() is False 