"""
Tests for NEAR AI Agent implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from near_swarm.core.agent import NEARAgent, AgentConfig, create_agent


@pytest.fixture
def mock_provider():
    """Create a mock NEAR provider."""
    provider = Mock()
    provider.get_account = Mock(return_value={
        "amount": "100000000000000000000000000",  # 100 NEAR
        "locked": "0",
        "code_hash": "11111111111111111111111111111111",
        "storage_usage": 100,
        "storage_paid_at": 0,
        "block_height": 1234567,
        "block_hash": "11111111111111111111111111111111"
    })
    return provider


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
async def agent(agent_config, mock_provider):
    """Create a test agent."""
    with patch('near_api.providers.JsonProvider', return_value=mock_provider):
        agent = NEARAgent(agent_config)
        yield agent
        await agent.close()


@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initialization."""
    assert agent.config.near_network == "testnet"
    assert agent.config.account_id == "test.testnet"
    assert agent.near_account is not None


@pytest.mark.asyncio
async def test_process_message(agent):
    """Test message processing."""
    message = "Test message"
    with patch.object(agent.llm.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value.choices = [Mock(message=Mock(content="Test response"))]
        response = await agent.process_message(message)
        assert response == "Test response"
        mock_create.assert_called_once()


@pytest.mark.asyncio
async def test_check_balance(agent):
    """Test balance checking."""
    with patch.object(agent.near_account, 'get_account_balance', new_callable=AsyncMock) as mock_balance:
        mock_balance.return_value = {
            'available': '100000000000000000000000000',  # 100 NEAR
            'staked': '0',
            'total': '100000000000000000000000000'
        }
        balance = await agent.check_balance()
        assert balance == 100.0
        mock_balance.assert_called_once()


@pytest.mark.asyncio
async def test_execute_transaction(agent):
    """Test transaction execution."""
    with patch.object(agent.near_account, 'send_money', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {
            'transaction': {
                'hash': '11111111111111111111111111111111'
            }
        }
        result = await agent.execute_transaction("recipient.testnet", 1.0)
        assert result["status"] == "success"
        assert result["transaction_hash"] == "11111111111111111111111111111111"
        mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_error_handling(agent):
    """Test error handling."""
    with patch.object(agent.near_account, 'send_money', new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = Exception("Test error")
        result = await agent.execute_transaction("recipient.testnet", 1.0)
        assert result["status"] == "error"
        assert result["error"] == "Test error"


@pytest.mark.asyncio
async def test_resource_cleanup(agent):
    """Test resource cleanup."""
    await agent.close()
    assert agent.session.closed


@pytest.mark.asyncio
async def test_create_agent():
    """Test agent creation helper."""
    config = {
        "near_network": "testnet",
        "account_id": "test.testnet",
        "private_key": "ed25519:test_key",
        "llm_provider": "hyperbolic",
        "llm_api_key": "test_key"
    }
    
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
        agent = create_agent(config)
        assert isinstance(agent, NEARAgent)
        assert agent.config.near_network == "testnet"
        assert agent.config.account_id == "test.testnet"
        await agent.close() 