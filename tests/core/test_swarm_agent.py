"""
Core Swarm Agent Tests
Tests essential functionality for NEAR Swarm Intelligence
"""

import pytest
from unittest.mock import Mock, patch

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig


@pytest.fixture
def agent_config():
    """Create test agent configuration."""
    return AgentConfig(
        near_network="testnet",
        account_id="test.testnet",
        private_key="ed25519:3D4YudUQRE39Lc4JHghuB5WM8kbgDDa34mnrEP5DdTApVH81af3e7MvFronz1F2u9wsnS4jx4nX4UNqm8M2n8acG",
        llm_provider="hyperbolic",
        llm_api_key="test_key"
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