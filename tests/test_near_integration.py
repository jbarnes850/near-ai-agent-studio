"""
Tests for NEAR Protocol integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from near_swarm.core.near_integration import NEARConnection


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
async def near_connection(mock_provider):
    """Create a test NEAR connection."""
    with patch('near_api.providers.JsonProvider', return_value=mock_provider):
        connection = NEARConnection(
            network="testnet",
            account_id="test.testnet",
            private_key="ed25519:test_key"
        )
        yield connection
        await connection.close()


@pytest.mark.asyncio
async def test_near_connection(near_connection):
    """Test NEAR connection initialization."""
    assert near_connection.network == "testnet"
    assert near_connection.account_id == "test.testnet"
    assert near_connection.account is not None


@pytest.mark.asyncio
async def test_ref_finance_integration(near_connection):
    """Test Ref Finance integration."""
    with patch.object(near_connection.account, 'function_call', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = {
            'transaction': {
                'hash': '11111111111111111111111111111111'
            }
        }
        
        result = await near_connection.swap_tokens(
            "wrap.testnet",
            "usdc.testnet",
            1.0
        )
        
        assert result["status"] == "success"
        assert result["transaction_hash"] == "11111111111111111111111111111111"
        mock_call.assert_called_once()


@pytest.mark.asyncio
async def test_gas_estimation(near_connection):
    """Test gas estimation."""
    with patch.object(near_connection.account, 'view_function', new_callable=AsyncMock) as mock_view:
        mock_view.return_value = {
            'gas': '30000000000000'  # 0.03 NEAR
        }
        
        gas = await near_connection.estimate_swap_gas(
            "wrap.testnet",
            "usdc.testnet",
            1.0
        )
        
        assert gas > 0
        assert isinstance(gas, float)
        mock_view.assert_called_once()


@pytest.mark.asyncio
async def test_market_data_integration(near_connection):
    """Test market data integration."""
    with patch.object(near_connection.account, 'view_function', new_callable=AsyncMock) as mock_view:
        mock_view.return_value = {
            'price': '3500000000000000000000000',  # 3.5 NEAR per token
            'liquidity': '1000000000000000000000000000'  # 1000 NEAR
        }
        
        data = await near_connection.get_pool_data(
            "wrap.testnet",
            "usdc.testnet"
        )
        
        assert "price" in data
        assert "liquidity" in data
        assert isinstance(data["price"], float)
        assert isinstance(data["liquidity"], float)
        mock_view.assert_called_once()


@pytest.mark.asyncio
async def test_strategy_execution(near_connection):
    """Test strategy execution."""
    with patch.object(near_connection.account, 'function_call', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = {
            'transaction': {
                'hash': '11111111111111111111111111111111'
            }
        }
        
        result = await near_connection.execute_strategy({
            "action": "swap",
            "params": {
                "from_token": "wrap.testnet",
                "to_token": "usdc.testnet",
                "amount": 1.0
            }
        })
        
        assert result["status"] == "success"
        assert result["transaction_hash"] == "11111111111111111111111111111111"
        mock_call.assert_called_once()


@pytest.mark.asyncio
async def test_error_handling(near_connection):
    """Test error handling."""
    with patch.object(near_connection.account, 'function_call', new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("Test error")
        
        result = await near_connection.swap_tokens(
            "wrap.testnet",
            "usdc.testnet",
            1.0
        )
        
        assert result["status"] == "error"
        assert result["error"] == "Test error"


@pytest.mark.asyncio
async def test_transaction_monitoring(near_connection):
    """Test transaction monitoring."""
    with patch.object(near_connection.account, 'get_transaction_result', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            'status': {
                'SuccessValue': ''
            }
        }
        
        status = await near_connection.check_transaction(
            "11111111111111111111111111111111"
        )
        
        assert status["success"] is True
        mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_network_conditions(near_connection):
    """Test network conditions check."""
    with patch.object(near_connection.account, 'view_function', new_callable=AsyncMock) as mock_view:
        mock_view.return_value = {
            'block_height': '12345678',
            'gas_price': '100000000'
        }
        
        conditions = await near_connection.check_network_conditions()
        
        assert "block_height" in conditions
        assert "gas_price" in conditions
        assert isinstance(conditions["block_height"], int)
        assert isinstance(conditions["gas_price"], int)
        mock_view.assert_called_once() 