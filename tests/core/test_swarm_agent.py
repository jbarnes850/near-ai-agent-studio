"""
Core Swarm Agent Tests
Tests essential functionality for NEAR Swarm Intelligence
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio
import json
import requests

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig


class MockKeyPair:
    def __init__(self):
        self.public_key = "ed25519:test_public_key"
        self.secret_key = "ed25519:test_secret_key"

    def encoded_public_key(self):
        return self.public_key


class MockSigner:
    def __init__(self, account_id: str, key_pair: MockKeyPair):
        self.account_id = account_id
        self._key_pair = key_pair


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.ok = status_code == 200
        self.content = json.dumps(json_data).encode('utf-8')

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if not self.ok:
            raise requests.HTTPError(f"{self.status_code} Error")


@pytest.fixture
def mock_near_provider():
    """Create a mock NEAR provider."""
    with patch('near_api.providers.JsonProvider') as mock_provider:
        mock_provider.return_value.get_account = Mock(return_value={
            "amount": "100000000000000000000000000",
            "locked": "0",
            "code_hash": "11111111111111111111111111111111",
            "storage_usage": 100,
            "storage_paid_at": 0,
            "block_height": 1234567,
            "block_hash": "11111111111111111111111111111111"
        })
        mock_provider.return_value.json_rpc = Mock(return_value={
            "result": {
                "amount": "100000000000000000000000000",
                "locked": "0",
                "code_hash": "11111111111111111111111111111111",
                "storage_usage": 100,
                "storage_paid_at": 0,
                "block_height": 1234567,
                "block_hash": "11111111111111111111111111111111"
            }
        })
        mock_provider.return_value.get_access_key = Mock(return_value={
            "nonce": 1,
            "permission": "FullAccess"
        })
        yield mock_provider


@pytest.fixture
def mock_requests():
    """Create a mock requests module."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MockResponse({
            "result": {
                "amount": "100000000000000000000000000",
                "locked": "0",
                "code_hash": "11111111111111111111111111111111",
                "storage_usage": 100,
                "storage_paid_at": 0,
                "block_height": 1234567,
                "block_hash": "11111111111111111111111111111111"
            }
        })
        yield mock_post


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    with patch('logging.getLogger') as mock_get_logger:
        mock_logger = Mock()
        mock_logger.error = Mock()
        mock_logger.info = Mock()
        mock_logger.warning = Mock()
        mock_logger.debug = Mock()
        mock_get_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def mock_signer():
    """Create a mock signer."""
    with patch('near_api.signer.Signer') as mock_signer:
        mock_signer.return_value = MockSigner("test.testnet", MockKeyPair())
        yield mock_signer


@pytest.fixture
def agent_config():
    """Create test agent configuration."""
    return AgentConfig(
        near_network="testnet",
        account_id="test.testnet",
        private_key="ed25519:test_key",
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


@pytest.fixture
async def swarm_agent(agent_config, swarm_config, mock_near_provider, mock_requests, mock_logger, mock_signer):
    """Create a test swarm agent."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('logging.getLogger', return_value=mock_logger), \
         patch('near_api.signer.Signer', mock_signer):
        agent = SwarmAgent(agent_config, swarm_config)
        yield agent
        await agent.close()


@pytest.mark.asyncio
async def test_swarm_formation(swarm_agent, agent_config, swarm_config, mock_near_provider, mock_requests, mock_logger, mock_signer):
    """Test basic swarm formation."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('logging.getLogger', return_value=mock_logger), \
         patch('near_api.signer.Signer', mock_signer):
        # Create peer agents
        peers = [
            SwarmAgent(
                agent_config,
                SwarmConfig(role="risk_manager")
            ),
            SwarmAgent(
                agent_config,
                SwarmConfig(role="strategy_optimizer")
            )
        ]
        
        # Join swarm
        await swarm_agent.join_swarm(peers)
        assert len(swarm_agent.swarm_peers) == 2
        
        # Verify peer connections
        for peer in peers:
            assert peer in swarm_agent.swarm_peers
            assert swarm_agent in peer.swarm_peers
            await peer.close()


@pytest.mark.asyncio
async def test_basic_proposal(swarm_agent, agent_config, swarm_config, mock_near_provider, mock_requests, mock_logger, mock_signer):
    """Test basic proposal mechanism."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('logging.getLogger', return_value=mock_logger), \
         patch('near_api.signer.Signer', mock_signer):
        # Create peer agents
        peers = [
            SwarmAgent(
                agent_config,
                SwarmConfig(role="risk_manager")
            ),
            SwarmAgent(
                agent_config,
                SwarmConfig(role="strategy_optimizer")
            )
        ]
        await swarm_agent.join_swarm(peers)
        
        # Make proposal
        result = await swarm_agent.propose_action(
            action_type="trade",
            params={
                "token": "NEAR",
                "action": "buy",
                "amount": 1.0
            }
        )
        
        # Verify result structure
        assert "consensus" in result
        assert "approval_rate" in result
        assert "total_votes" in result
        assert isinstance(result["reasons"], list)
        
        # Cleanup
        for peer in peers:
            await peer.close()


@pytest.mark.asyncio
async def test_simple_consensus(swarm_agent, agent_config, swarm_config, mock_near_provider, mock_requests, mock_logger, mock_signer):
    """Test basic consensus reaching."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('logging.getLogger', return_value=mock_logger), \
         patch('near_api.signer.Signer', mock_signer):
        # Create agents with different confidence thresholds
        agents = [
            SwarmAgent(
                agent_config,
                SwarmConfig(
                    role="market_analyzer",
                    min_confidence=0.6
                )
            ),
            SwarmAgent(
                agent_config,
                SwarmConfig(
                    role="risk_manager",
                    min_confidence=0.8
                )
            )
        ]
        
        # Connect agents
        for agent in agents:
            await agent.join_swarm([a for a in agents if a != agent])
        
        # Make proposal
        result = await agents[0].propose_action(
            action_type="trade",
            params={
                "token": "NEAR",
                "action": "buy",
                "amount": 1.0
            }
        )
        
        # Verify consensus
        assert "consensus" in result
        assert "approval_rate" in result
        assert result["total_votes"] == len(agents) - 1
        
        # Cleanup
        for agent in agents:
            await agent.close()


@pytest.mark.asyncio
async def test_error_handling(swarm_agent):
    """Test error handling in swarm operations."""
    # Test invalid proposal
    invalid_proposal = {
        "type": "invalid",
        "params": {}
    }
    
    result = await swarm_agent.evaluate_proposal(invalid_proposal)
    assert not result["decision"]
    assert result["confidence"] == 0.0
    assert "failed" in result["reasoning"].lower() 