"""
Consensus mechanism for NEAR AI Agents.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import asyncio
import time


@dataclass
class Vote:
    """Vote from an agent."""
    agent_id: str
    decision: bool
    confidence: float
    reasoning: str


class ConsensusManager:
    """Manages consensus between multiple agents."""
    
    def __init__(
        self,
        min_confidence: float = 0.7,
        min_votes: int = 3,
        timeout: float = 5.0
    ):
        """Initialize consensus manager."""
        self.min_confidence = min_confidence
        self.min_votes = min_votes
        self.timeout = timeout
        self.votes: Dict[str, List[Vote]] = {}
    
    async def collect_votes(
        self,
        proposal_id: str,
        agents: List,
        proposal: Dict
    ) -> List[Vote]:
        """Collect votes from agents."""
        votes = []
        tasks = []
        
        # Create tasks for each agent
        for agent in agents:
            task = asyncio.create_task(
                self._get_agent_vote(agent, proposal)
            )
            tasks.append(task)
        
        # Wait for all votes or timeout
        try:
            results = await asyncio.gather(*tasks)
            votes.extend([vote for vote in results if vote])
        except asyncio.TimeoutError:
            pass
        
        # Store votes
        self.votes[proposal_id] = votes
        return votes
    
    async def _get_agent_vote(self, agent, proposal) -> Optional[Vote]:
        """Get vote from a single agent."""
        try:
            result = await agent.evaluate_proposal(proposal)
            return Vote(
                agent_id=agent.id,
                decision=result["decision"],
                confidence=result["confidence"],
                reasoning=result["reasoning"]
            )
        except Exception:
            return None
    
    def reach_consensus(self, votes: List[Vote]) -> Dict:
        """Determine if consensus is reached."""
        if len(votes) < self.min_votes:
            return {
                "consensus": False,
                "reason": "Insufficient votes",
                "total_votes": len(votes),
                "approval_rate": 0.0,
                "confidence_scores": [],
                "reasons": []
            }
        
        # Calculate weighted approval rate
        total_confidence = sum(vote.confidence for vote in votes)
        if total_confidence == 0:
            weighted_approval = 0.0
        else:
            weighted_approval = sum(
                vote.confidence for vote in votes if vote.decision
            ) / total_confidence
        
        # Collect confidence scores and reasons
        confidence_scores = [vote.confidence for vote in votes]
        reasons = [vote.reasoning for vote in votes]
        
        return {
            "consensus": weighted_approval >= self.min_confidence,
            "approval_rate": weighted_approval,
            "total_votes": len(votes),
            "confidence_scores": confidence_scores,
            "reasons": reasons
        }
    
    async def get_vote_history(
        self,
        proposal_id: Optional[str] = None
    ) -> Dict[str, List[Vote]]:
        """Get voting history."""
        if proposal_id:
            return {proposal_id: self.votes.get(proposal_id, [])}
        return self.votes
    
    def analyze_agent_performance(self, agent_id: str) -> Dict:
        """Analyze agent's voting performance."""
        agent_votes = []
        for votes in self.votes.values():
            agent_votes.extend(
                vote for vote in votes if vote.agent_id == agent_id
            )
        
        if not agent_votes:
            return {
                "total_votes": 0,
                "average_confidence": 0.0,
                "approval_rate": 0.0
            }
        
        total_votes = len(agent_votes)
        avg_confidence = sum(
            vote.confidence for vote in agent_votes
        ) / total_votes
        approval_rate = sum(
            1 for vote in agent_votes if vote.decision
        ) / total_votes
        
        return {
            "total_votes": total_votes,
            "average_confidence": avg_confidence,
            "approval_rate": approval_rate
        }
    
    def clear_history(self):
        """Clear voting history."""
        self.votes.clear()
