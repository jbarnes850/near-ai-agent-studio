"""
Core Agent Tests
Tests essential functionality for NEAR AI Agent
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
import requests

from near_swarm.core.agent import NEARAgent, AgentConfig


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


@pytest.mark.asyncio
async def test_agent_initialization(agent_config, mock_near_provider, mock_requests, mock_logger, mock_signer):
    """Test basic agent initialization."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('logging.getLogger', return_value=mock_logger), \
         patch('near_api.signer.Signer', mock_signer):
        agent = NEARAgent(agent_config)
        assert agent.config.near_network == "testnet"
        assert agent.config.account_id == "test.testnet"
        assert agent.config.llm_provider == "hyperbolic"


@pytest.mark.asyncio
async def test_config_validation():
    """Test configuration validation."""
    # Test missing required fields
    with pytest.raises(ValueError):
        AgentConfig(
            near_network="",  # Empty network
            account_id="test.testnet",
            private_key="ed25519:test_key",
            llm_provider="hyperbolic",
            llm_api_key="test_key"
        )
    
    # Test invalid network
    with pytest.raises(ValueError):
        AgentConfig(
            near_network="invalid_network",
            account_id="test.testnet",
            private_key="ed25519:test_key",
            llm_provider="hyperbolic",
            llm_api_key="test_key"
        )
    
    # Test invalid account ID format
    with pytest.raises(ValueError):
        AgentConfig(
            near_network="testnet",
            account_id="invalid@account",  # Invalid format
            private_key="ed25519:test_key",
            llm_provider="hyperbolic",
            llm_api_key="test_key"
        )


@pytest.mark.asyncio
async def test_basic_lifecycle(agent_config, mock_near_provider, mock_requests, mock_logger, mock_signer):
    """Test agent lifecycle (start, stop)."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('logging.getLogger', return_value=mock_logger), \
         patch('near_api.signer.Signer', mock_signer):
        agent = NEARAgent(agent_config)
        
        # Test start
        await agent.start()
        assert agent.is_running() is True
        
        # Test stop
        await agent.stop()
        assert agent.is_running() is False


@pytest.mark.asyncio
async def test_error_recovery(agent_config, mock_near_provider, mock_requests, mock_logger, mock_signer):
    """Test agent error recovery."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('logging.getLogger', return_value=mock_logger), \
         patch('near_api.signer.Signer', mock_signer):
        agent = NEARAgent(agent_config)
        
        # Simulate network error during start
        mock_near_provider.return_value.get_account.side_effect = Exception("Network error")
        
        # Agent should handle error gracefully
        with pytest.raises(Exception) as exc_info:
            await agent.start()
        assert "Network error" in str(exc_info.value)
        assert agent.is_running() is False
        
        # Reset mock and try again
        mock_near_provider.return_value.get_account.side_effect = None
        await agent.start()
        assert agent.is_running() is True 