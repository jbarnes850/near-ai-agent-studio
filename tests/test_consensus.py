"""
Tests for consensus mechanism.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from near_swarm.core.consensus import ConsensusManager, Vote


@pytest.fixture
def consensus_manager():
    """Create a test consensus manager."""
    return ConsensusManager(
        min_confidence=0.7,
        min_votes=3,
        timeout=5.0
    )


@pytest.mark.asyncio
async def test_vote_collection(consensus_manager):
    """Test collecting votes from agents."""
    # Create mock agents
    mock_agents = [
        AsyncMock(
            id=f"agent{i}",
            evaluate_proposal=AsyncMock(
                return_value={
                    "decision": True,
                    "confidence": 0.8,
                    "reasoning": "Test reasoning"
                }
            )
        )
        for i in range(3)
    ]
    
    # Test proposal
    proposal = {
        "action": "test_action",
        "parameters": {"param1": "value1"}
    }
    
    # Collect votes
    votes = await consensus_manager.collect_votes(
        "test_proposal",
        mock_agents,
        proposal
    )
    
    assert len(votes) == 3
    assert all(isinstance(vote, Vote) for vote in votes)
    assert all(vote.decision for vote in votes)
    assert all(vote.confidence == 0.8 for vote in votes)


@pytest.mark.asyncio
async def test_consensus_reaching(consensus_manager):
    """Test reaching consensus."""
    # Create test votes
    votes = [
        Vote(
            agent_id="agent1",
            decision=True,
            confidence=0.9,
            reasoning="High confidence approval"
        ),
        Vote(
            agent_id="agent2",
            decision=True,
            confidence=0.8,
            reasoning="Medium confidence approval"
        ),
        Vote(
            agent_id="agent3",
            decision=False,
            confidence=0.6,
            reasoning="Low confidence rejection"
        )
    ]
    
    # Test consensus
    result = consensus_manager.reach_consensus(votes)
    
    assert "consensus" in result
    assert "approval_rate" in result
    assert "total_votes" in result
    assert "confidence_scores" in result
    assert "reasons" in result
    assert result["total_votes"] == 3


@pytest.mark.asyncio
async def test_vote_history(consensus_manager):
    """Test vote history tracking."""
    # Create test votes
    votes = [
        Vote(
            agent_id="agent1",
            decision=True,
            confidence=0.9,
            reasoning="Test reasoning"
        )
    ]
    
    # Store votes
    proposal_id = "test_proposal"
    consensus_manager.votes[proposal_id] = votes
    
    # Get history
    history = await consensus_manager.get_vote_history(proposal_id)
    
    assert proposal_id in history
    assert len(history[proposal_id]) == 1
    assert history[proposal_id][0].agent_id == "agent1"


@pytest.mark.asyncio
async def test_agent_performance(consensus_manager):
    """Test agent performance analysis."""
    # Create test votes
    agent_id = "test_agent"
    votes = [
        Vote(
            agent_id=agent_id,
            decision=True,
            confidence=0.9,
            reasoning="First vote"
        ),
        Vote(
            agent_id=agent_id,
            decision=False,
            confidence=0.8,
            reasoning="Second vote"
        )
    ]
    
    # Store votes
    consensus_manager.votes["proposal1"] = [votes[0]]
    consensus_manager.votes["proposal2"] = [votes[1]]
    
    # Analyze performance
    performance = consensus_manager.analyze_agent_performance(agent_id)
    
    assert performance["total_votes"] == 2
    assert 0.8 <= performance["average_confidence"] <= 0.9
    assert performance["approval_rate"] == 0.5


@pytest.mark.asyncio
async def test_minimum_votes(consensus_manager):
    """Test minimum votes requirement."""
    # Create insufficient votes
    votes = [
        Vote(
            agent_id="agent1",
            decision=True,
            confidence=0.9,
            reasoning="Test reasoning"
        )
    ]
    
    # Test consensus with insufficient votes
    result = consensus_manager.reach_consensus(votes)
    
    assert result["consensus"] is False
    assert "Insufficient votes" in result["reason"]


@pytest.mark.asyncio
async def test_confidence_threshold(consensus_manager):
    """Test confidence threshold."""
    # Create low confidence votes
    votes = [
        Vote(
            agent_id=f"agent{i}",
            decision=True,
            confidence=0.5,  # Below threshold
            reasoning="Low confidence vote"
        )
        for i in range(3)
    ]
    
    # Test consensus with low confidence
    result = consensus_manager.reach_consensus(votes)
    
    # With all votes having confidence 0.5, weighted approval should be 0.5
    # which is below the min_confidence threshold of 0.7
    assert result["consensus"] is False
    assert result["approval_rate"] == 0.5


@pytest.mark.asyncio
async def test_clear_history(consensus_manager):
    """Test clearing vote history."""
    # Store some votes
    consensus_manager.votes["test_proposal"] = [
        Vote(
            agent_id="agent1",
            decision=True,
            confidence=0.9,
            reasoning="Test vote"
        )
    ]
    
    # Clear history
    consensus_manager.clear_history()
    
    # Verify history is cleared
    assert len(consensus_manager.votes) == 0
    
    # Get history should return empty
    history = await consensus_manager.get_vote_history()
    assert len(history) == 0 