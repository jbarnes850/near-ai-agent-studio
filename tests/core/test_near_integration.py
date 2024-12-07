"""
Core NEAR Protocol Integration Tests
Tests essential functionality for interacting with NEAR Protocol
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
import requests

from near_swarm.core.near_integration import NEARConnection


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
def mock_signer():
    """Create a mock signer."""
    with patch('near_api.signer.Signer') as mock_signer:
        mock_signer.return_value = MockSigner("test.testnet", MockKeyPair())
        yield mock_signer


@pytest.mark.asyncio
async def test_connection_initialization(mock_near_provider, mock_requests, mock_signer):
    """Test basic NEAR connection initialization."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('near_api.signer.Signer', mock_signer):
        connection = NEARConnection(
            network="testnet",
            account_id="test.testnet",
            private_key="ed25519:test_key"
        )
        assert connection.network == "testnet"
        assert connection.account_id == "test.testnet"
        assert connection.provider is not None


@pytest.mark.asyncio
async def test_basic_transaction(mock_near_provider, mock_requests, mock_signer):
    """Test basic transaction functionality."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('near_api.signer.Signer', mock_signer):
        connection = NEARConnection(
            network="testnet",
            account_id="test.testnet",
            private_key="ed25519:test_key"
        )
        
        # Test sending a simple transaction
        result = await connection.send_transaction({
            "receiver_id": "receiver.testnet",
            "actions": [{"type": "Transfer", "amount": "1000000000000000000000000"}]
        })
        
        assert result is not None
        assert "transaction_outcome" in result


@pytest.mark.asyncio
async def test_error_handling(mock_near_provider, mock_requests, mock_signer):
    """Test error handling for common failure scenarios."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('near_api.signer.Signer', mock_signer):
        connection = NEARConnection(
            network="testnet",
            account_id="test.testnet",
            private_key="ed25519:test_key"
        )
        
        # Test invalid transaction
        with pytest.raises(ValueError):
            await connection.send_transaction({
                "receiver_id": "",  # Invalid receiver
                "actions": []  # No actions
            })
        
        # Test network error
        mock_near_provider.return_value.get_account.side_effect = Exception("Network error")
        with pytest.raises(Exception) as exc_info:
            await connection.check_account("test.testnet")
        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_account_validation(mock_near_provider, mock_requests, mock_signer):
    """Test account validation and balance checking."""
    with patch('near_api.providers.JsonProvider', mock_near_provider), \
         patch('requests.post', mock_requests), \
         patch('near_api.signer.Signer', mock_signer):
        connection = NEARConnection(
            network="testnet",
            account_id="test.testnet",
            private_key="ed25519:test_key"
        )
        
        # Test account exists
        exists = await connection.check_account("test.testnet")
        assert exists is True
        
        # Test balance check
        balance = await connection.get_account_balance()
        assert float(balance) > 0
        assert "available" in balance 