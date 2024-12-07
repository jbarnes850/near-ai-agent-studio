"""
Tests for memory management system.
"""

import pytest
from datetime import datetime

from near_swarm.core.memory_manager import MemoryManager, StrategyOutcome


@pytest.fixture
def memory_manager():
    """Create a test memory manager."""
    return MemoryManager()


@pytest.mark.asyncio
async def test_store_and_retrieve(memory_manager):
    """Test storing and retrieving data."""
    # Test data
    test_data = {
        "key": "value",
        "number": 42
    }
    
    test_context = {
        "category": "test",
        "timestamp": datetime.now().isoformat()
    }
    
    # Store data
    success = await memory_manager.store(
        "test_category",
        test_data,
        test_context
    )
    assert success
    
    # Retrieve data
    results = await memory_manager.retrieve(
        "test_category",
        context={"category": "test"}
    )
    
    assert len(results) == 1
    assert results[0]["data"] == test_data
    assert results[0]["context"] == test_context


@pytest.mark.asyncio
async def test_strategy_outcome_recording(memory_manager):
    """Test recording strategy outcomes."""
    # Create test outcome
    outcome = StrategyOutcome(
        strategy_id="test_strategy",
        timestamp=datetime.now().isoformat(),
        success=True,
        confidence_scores={"agent1": 0.9, "agent2": 0.8},
        actual_profit=100.0,
        predicted_profit=95.0,
        execution_time=1.5,
        agents_involved=["agent1", "agent2"]
    )
    
    # Record outcome
    success = await memory_manager.record_strategy_outcome(outcome)
    assert success
    
    # Check performance metrics
    performance = await memory_manager.get_strategy_performance("test_strategy")
    
    assert performance["total_executions"] == 1
    assert performance["success_rate"] == 1.0
    assert performance["average_profit"] == 100.0
    assert 0 <= performance["prediction_accuracy"] <= 1.0


@pytest.mark.asyncio
async def test_context_filtering(memory_manager):
    """Test context-based filtering."""
    # Store multiple entries
    await memory_manager.store(
        "test_category",
        {"value": 1},
        {"type": "A"}
    )
    
    await memory_manager.store(
        "test_category",
        {"value": 2},
        {"type": "B"}
    )
    
    await memory_manager.store(
        "test_category",
        {"value": 3},
        {"type": "A"}
    )
    
    # Retrieve with context filter
    results = await memory_manager.retrieve(
        "test_category",
        context={"type": "A"}
    )
    
    assert len(results) == 2
    assert all(r["context"]["type"] == "A" for r in results)


@pytest.mark.asyncio
async def test_memory_clearing(memory_manager):
    """Test memory clearing functionality."""
    # Store test data
    await memory_manager.store(
        "category1",
        {"test": "data1"}
    )
    
    await memory_manager.store(
        "category2",
        {"test": "data2"}
    )
    
    # Clear specific category
    success = await memory_manager.clear_category("category1")
    assert success
    
    # Verify category1 is empty
    results = await memory_manager.retrieve("category1")
    assert len(results) == 0
    
    # Verify category2 still has data
    results = await memory_manager.retrieve("category2")
    assert len(results) == 1
    
    # Clear all memory
    success = await memory_manager.clear_all()
    assert success
    
    # Verify all categories are empty
    results1 = await memory_manager.retrieve("category1")
    results2 = await memory_manager.retrieve("category2")
    assert len(results1) == 0
    assert len(results2) == 0


@pytest.mark.asyncio
async def test_performance_metrics(memory_manager):
    """Test strategy performance metrics."""
    # Record multiple outcomes
    outcomes = [
        StrategyOutcome(
            strategy_id="test_strategy",
            timestamp=datetime.now().isoformat(),
            success=True,
            confidence_scores={"agent1": 0.9},
            actual_profit=100.0,
            predicted_profit=95.0,
            execution_time=1.0,
            agents_involved=["agent1"]
        ),
        StrategyOutcome(
            strategy_id="test_strategy",
            timestamp=datetime.now().isoformat(),
            success=False,
            confidence_scores={"agent1": 0.7},
            actual_profit=0.0,
            predicted_profit=90.0,
            execution_time=1.0,
            agents_involved=["agent1"]
        )
    ]
    
    for outcome in outcomes:
        await memory_manager.record_strategy_outcome(outcome)
    
    # Get performance metrics
    performance = await memory_manager.get_strategy_performance("test_strategy")
    
    assert performance["total_executions"] == 2
    assert performance["success_rate"] == 0.5
    assert performance["average_profit"] == 50.0
    assert 0 <= performance["prediction_accuracy"] <= 1.0


@pytest.mark.asyncio
async def test_error_handling(memory_manager):
    """Test error handling in memory operations."""
    # Test retrieving from non-existent category
    results = await memory_manager.retrieve("non_existent")
    assert len(results) == 0
    
    # Test clearing non-existent category
    success = await memory_manager.clear_category("non_existent")
    assert success  # Should succeed silently
    
    # Test getting performance for non-existent strategy
    performance = await memory_manager.get_strategy_performance("non_existent")
    assert performance["total_executions"] == 0
    assert performance["success_rate"] == 0.0
    assert performance["average_profit"] == 0.0
    assert performance["prediction_accuracy"] == 0.0 