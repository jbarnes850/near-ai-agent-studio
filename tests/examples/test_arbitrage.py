"""
Tests for arbitrage strategy implementation.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from near_swarm.examples.arbitrage import ArbitrageStrategy


@pytest.fixture
def arbitrage_strategy():
    """Create a test arbitrage strategy."""
    return ArbitrageStrategy(
        token_pairs=["NEAR/USDC", "NEAR/USDT", "ETH/NEAR"],
        exchanges=["ref-finance", "jumbo"],
        min_profit=0.002,
        max_position=10000,
        gas_threshold=0.001
    )


@pytest.mark.asyncio
async def test_find_arbitrage(arbitrage_strategy):
    """Test finding arbitrage opportunities."""
    # Test finding opportunities
    opportunities = await arbitrage_strategy.find_arbitrage("NEAR/USDC")
    
    assert isinstance(opportunities, dict)
    assert "pair" in opportunities
    assert "opportunities" in opportunities
    assert "prices" in opportunities


@pytest.mark.asyncio
async def test_collect_agent_votes(arbitrage_strategy):
    """Test collecting agent votes."""
    # Test collecting votes
    opportunity = {
        "opportunity": {
            "buy_exchange": "ref-finance",
            "sell_exchange": "jumbo",
            "buy_price": 3.50,
            "sell_price": 3.52,
            "profit_pct": 0.005
        }
    }
    
    votes = await arbitrage_strategy.collect_agent_votes(opportunity)
    
    assert len(votes) == 3  # Three agents voting
    assert all(hasattr(vote, "agent_id") for vote in votes)
    assert all(hasattr(vote, "decision") for vote in votes)
    assert all(hasattr(vote, "confidence") for vote in votes)


@pytest.mark.asyncio
async def test_position_size_calculation(arbitrage_strategy):
    """Test position size calculation."""
    # Test position calculation
    opportunity = {
        "profit_pct": 0.005,
        "buy_exchange": "ref-finance",
        "sell_exchange": "jumbo"
    }
    
    gas_cost = 0.1
    position = arbitrage_strategy._calculate_position_size(opportunity, gas_cost)
    
    assert position > 0
    assert position <= arbitrage_strategy.max_position


@pytest.mark.asyncio
async def test_gas_cost_estimation(arbitrage_strategy):
    """Test gas cost estimation."""
    # Test gas estimation
    pair = "NEAR/USDC"
    opportunity = {
        "buy_exchange": "ref-finance",
        "sell_exchange": "jumbo"
    }
    
    gas_cost = await arbitrage_strategy._estimate_gas_costs(pair, opportunity)
    
    assert gas_cost > 0
    assert isinstance(gas_cost, float)


@pytest.mark.asyncio
async def test_profit_calculation(arbitrage_strategy):
    """Test profit calculation."""
    # Test profit calculation
    buy_result = {
        "status": "success",
        "amount": 1000,
        "price": 3.50
    }
    
    sell_result = {
        "status": "success",
        "amount": 1000,
        "price": 3.52
    }
    
    gas_cost = 0.1
    profit = arbitrage_strategy._calculate_actual_profit(
        buy_result,
        sell_result,
        gas_cost
    )
    
    assert profit > 0
    assert isinstance(profit, float)


@pytest.mark.asyncio
async def test_liquidity_evaluation(arbitrage_strategy):
    """Test liquidity evaluation."""
    # Test liquidity check
    opportunity = {
        "opportunity": {
            "buy_exchange": "ref-finance",
            "sell_exchange": "jumbo",
            "buy_price": 3.50,
            "sell_price": 3.52,
            "profit_pct": 0.005
        }
    }
    
    has_liquidity = arbitrage_strategy._evaluate_liquidity(opportunity)
    assert isinstance(has_liquidity, bool)


@pytest.mark.asyncio
async def test_error_handling(arbitrage_strategy):
    """Test error handling."""
    # Test invalid pair
    with pytest.raises(Exception):
        await arbitrage_strategy.find_arbitrage("INVALID/PAIR")


@pytest.mark.asyncio
async def test_memory_integration(arbitrage_strategy):
    """Test memory system integration."""
    # Test memory manager
    assert hasattr(arbitrage_strategy, "memory")
    assert arbitrage_strategy.memory is not None