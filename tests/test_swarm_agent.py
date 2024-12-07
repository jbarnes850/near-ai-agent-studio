"""
Tests for SwarmAgent implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig


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
async def swarm_agent(agent_config, swarm_config):
    """Create a test swarm agent."""
    agent = SwarmAgent(agent_config, swarm_config)
    yield agent
    await agent.close()


@pytest.mark.asyncio
async def test_swarm_agent_initialization(swarm_agent):
    """Test swarm agent initialization."""
    assert swarm_agent.config.near_network == "testnet"
    assert swarm_agent.swarm_config.role == "market_analyzer"
    assert swarm_agent.swarm_peers == []
    assert swarm_agent.consensus_manager is not None


@pytest.mark.asyncio
async def test_join_swarm(swarm_agent, agent_config):
    """Test joining a swarm."""
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
async def test_propose_action(swarm_agent, agent_config):
    """Test proposing an action to the swarm."""
    # Create mock peers
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
    
    # Propose action
    result = await swarm_agent.propose_action(
        action_type="trade",
        params={
            "token": "NEAR",
            "action": "buy",
            "amount": 10.0
        }
    )
    
    # Verify result structure
    assert "consensus" in result
    assert "approval_rate" in result
    assert "total_votes" in result
    assert "reasons" in result
    assert isinstance(result["reasons"], list)
    
    # Cleanup
    for peer in peers:
        await peer.close()


@pytest.mark.asyncio
async def test_evaluate_proposal_market_analyzer(swarm_agent):
    """Test market analyzer role evaluation."""
    proposal = {
        "type": "trade",
        "params": {
            "token": "NEAR",
            "action": "buy",
            "amount": 10.0
        }
    }
    
    result = await swarm_agent.evaluate_proposal(proposal)
    assert "decision" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert isinstance(result["confidence"], float)
    assert 0 <= result["confidence"] <= 1


@pytest.mark.asyncio
async def test_evaluate_proposal_risk_manager(agent_config):
    """Test risk manager role evaluation."""
    agent = SwarmAgent(
        agent_config,
        SwarmConfig(role="risk_manager")
    )
    
    proposal = {
        "type": "trade",
        "params": {
            "token": "NEAR",
            "action": "buy",
            "amount": 10.0
        }
    }
    
    result = await agent.evaluate_proposal(proposal)
    assert "decision" in result
    assert "confidence" in result
    assert "reasoning" in result
    assert isinstance(result["confidence"], float)
    assert 0 <= result["confidence"] <= 1
    
    await agent.close()


@pytest.mark.asyncio
async def test_error_handling(swarm_agent):
    """Test error handling in proposal evaluation."""
    # Test with invalid proposal
    invalid_proposal = {
        "type": "invalid",
        "params": {}
    }
    
    result = await swarm_agent.evaluate_proposal(invalid_proposal)
    assert not result["decision"]
    assert result["confidence"] == 0.0
    assert "failed" in result["reasoning"].lower()


@pytest.mark.asyncio
async def test_consensus_threshold(agent_config):
    """Test consensus threshold behavior."""
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
    
    # Propose action
    result = await agents[0].propose_action(
        action_type="trade",
        params={
            "token": "NEAR",
            "action": "buy",
            "amount": 1.0  # Small amount for safer test
        }
    )
    
    # Verify consensus behavior
    assert "consensus" in result
    assert "approval_rate" in result
    assert result["total_votes"] == len(agents) - 1  # Excluding proposer
    
    # Cleanup
    for agent in agents:
        await agent.close()


@pytest.mark.asyncio
async def test_concurrent_proposals(agent_config):
    """Test handling multiple concurrent proposals."""
    # Create a swarm of agents
    agents = [
        SwarmAgent(
            agent_config,
            SwarmConfig(role=role)
        )
        for role in ["market_analyzer", "risk_manager", "strategy_optimizer"]
    ]
    
    # Connect agents
    for agent in agents:
        await agent.join_swarm([a for a in agents if a != agent])
    
    # Make concurrent proposals
    proposals = [
        agent.propose_action(
            action_type="trade",
            params={
                "token": "NEAR",
                "action": "buy",
                "amount": 1.0 * (i + 1)
            }
        )
        for i, agent in enumerate(agents)
    ]
    
    # Wait for all proposals
    results = await asyncio.gather(*proposals)
    
    # Verify all results are valid
    for result in results:
        assert "consensus" in result
        assert "approval_rate" in result
        assert "reasons" in result
    
    # Cleanup
    for agent in agents:
        await agent.close() 