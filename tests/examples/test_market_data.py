"""
Tests for market data integration.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import aiohttp

from near_swarm.core.market_data import MarketDataManager


class MockResponse:
    """Mock aiohttp response."""
    def __init__(self, data):
        self.data = data

    async def json(self):
        return self.data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
async def mock_session():
    """Create a mock aiohttp session."""
    session = AsyncMock()

    # Mock price response
    session.get.return_value = MockResponse({
        "near": {"usd": 3.50},
        "usdc": {"usd": 1.00},
        "eth": {"usd": 3000.00}
    })

    return session


@pytest.fixture
async def market_data(mock_session):
    """Create a test market data manager."""
    with patch('aiohttp.ClientSession', return_value=mock_session):
        manager = MarketDataManager()
        await manager.initialize()
        yield manager
        await manager.close()


@pytest.mark.asyncio
async def test_token_price(market_data):
    """Test getting token prices."""
    # Test getting NEAR price
    price = await market_data.get_token_price("NEAR", "USD")
    assert price == 3.50

    # Test getting USDC price
    price = await market_data.get_token_price("USDC", "USD")
    assert price == 1.00

    # Test getting ETH price
    price = await market_data.get_token_price("ETH", "USD")
    assert price == 3000.00


@pytest.mark.asyncio
async def test_market_opportunity_analysis(market_data):
    """Test market opportunity analysis."""
    # Test analyzing opportunities
    analysis = await market_data.analyze_market_opportunity(
        tokens=["NEAR", "USDC", "ETH"],
        amount=1000.0
    )

    assert "timestamp" in analysis
    assert "opportunities" in analysis
    assert "market_state" in analysis
    assert isinstance(analysis["opportunities"], list)


@pytest.mark.asyncio
async def test_market_state(market_data):
    """Test getting market state."""
    # Test getting market state
    state = await market_data._get_market_state(
        tokens=["NEAR", "USDC"]
    )

    assert "timestamp" in state
    assert "prices" in state
    assert "volumes" in state
    assert "liquidity" in state
    assert all(token in state["prices"] for token in ["NEAR", "USDC"])


@pytest.mark.asyncio
async def test_trading_volumes(market_data):
    """Test getting trading volumes."""
    # Test getting volumes
    volumes = await market_data._get_trading_volumes(
        tokens=["NEAR", "USDC"]
    )

    assert "NEAR" in volumes
    assert "USDC" in volumes
    assert all(isinstance(v, float) for v in volumes.values())


@pytest.mark.asyncio
async def test_liquidity_data(market_data):
    """Test getting liquidity data."""
    # Test getting liquidity
    liquidity = await market_data._get_liquidity_data(
        tokens=["NEAR", "USDC"]
    )

    assert "NEAR" in liquidity
    assert "USDC" in liquidity
    assert all(
        "total_liquidity" in data and "available_liquidity" in data
        for data in liquidity.values()
    )


@pytest.mark.asyncio
async def test_opportunity_finding(market_data):
    """Test finding opportunities."""
    # Test market state
    market_state = {
        "prices": {
            "NEAR": 3.50,
            "USDC": 1.00,
            "ETH": 3000.00
        },
        "liquidity": {
            "NEAR": {
                "total_liquidity": 1000000.0,
                "available_liquidity": 500000.0
            },
            "USDC": {
                "total_liquidity": 2000000.0,
                "available_liquidity": 1000000.0
            },
            "ETH": {
                "total_liquidity": 5000000.0,
                "available_liquidity": 2500000.0
            }
        }
    }

    # Find opportunities
    opportunities = await market_data._find_opportunities(
        market_state,
        amount=1000.0
    )

    assert isinstance(opportunities, list)
    assert all(
        "token" in opp and "type" in opp and "price" in opp
        for opp in opportunities
    )


@pytest.mark.asyncio
async def test_profit_estimation(market_data):
    """Test profit estimation."""
    # Test profit calculation
    profit = market_data._estimate_profit(
        price=3.50,
        amount=1000.0,
        liquidity={
            "total_liquidity": 1000000.0,
            "available_liquidity": 500000.0
        }
    )

    assert isinstance(profit, float)
    assert profit >= 0


@pytest.mark.asyncio
async def test_error_handling(market_data):
    """Test error handling."""
    # Test invalid token
    with pytest.raises(Exception):
        await market_data.get_token_price("INVALID_TOKEN")

    # Test invalid amount
    with pytest.raises(ValueError):  # Specify the exact exception we expect
        await market_data.analyze_market_opportunity(
            tokens=["NEAR"],
            amount=-1000.0  # Invalid negative amount should raise ValueError
        )


@pytest.mark.asyncio
async def test_resource_cleanup(market_data):
    """Test resource cleanup."""
    # Test session cleanup
    await market_data.close()
    assert market_data.session is None
