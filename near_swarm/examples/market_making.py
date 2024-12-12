"""
Example Market Making Strategy using NEAR Swarm Intelligence
Demonstrates how to use the swarm for decentralized market making.
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from src.consensus import ConsensusEngine, ConsensusConfig, ConsensusStrategy, Vote
from src.market_data import MarketDataProvider
from src.memory_manager import SwarmMemory, AgentReputation, StrategyOutcome

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketMakingStrategy:
    """
    Decentralized market making strategy using swarm intelligence.
    Uses multiple agents to analyze market conditions and adjust positions.
    """
    
    def __init__(self,
                 token_pairs: List[str],
                 base_spread: float = 0.002,  # 0.2% base spread
                 min_liquidity: float = 1000,  # Minimum liquidity in USD
                 max_position: float = 10000,  # Maximum position size in USD
                 target_profit: float = 0.001): # 0.1% target profit per trade
        
        self.token_pairs = token_pairs
        self.base_spread = base_spread
        self.min_liquidity = min_liquidity
        self.max_position = max_position
        self.target_profit = target_profit
        
        # Initialize components
        self.market_data = MarketDataProvider()
        self.memory = SwarmMemory()
        self.consensus = ConsensusEngine(
            ConsensusConfig(
                strategy=ConsensusStrategy.HYBRID,
                min_participation=0.8,
                min_confidence=0.6
            )
        )
    
    async def analyze_opportunity(self, pair: str) -> Dict[str, Any]:
        """Analyze market making opportunity for a token pair."""
        try:
            # Get market data
            market_state = await self.market_data.analyze_market_conditions(
                protocols=['ref-finance'],
                tokens=[pair.split('/')[0], pair.split('/')[1]]
            )
            
            # Calculate metrics
            volatility = market_state.get('price_volatility', 0)
            liquidity = market_state.get('liquidity', 0)
            volume = market_state.get('volume_24h', 0)
            
            # Adjust spread based on conditions
            adjusted_spread = self.base_spread * (1 + volatility)
            
            return {
                'pair': pair,
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'volatility': volatility,
                    'liquidity': liquidity,
                    'volume': volume,
                    'adjusted_spread': adjusted_spread
                },
                'market_state': market_state
            }
            
        except Exception as e:
            logger.error(f"Error analyzing opportunity: {str(e)}")
            raise
    
    async def collect_agent_votes(self,
                                opportunity: Dict[str, Any]) -> List[Vote]:
        """Collect votes from different specialized agents."""
        try:
            votes = []
            
            # Market Analysis Agent
            market_vote = Vote(
                agent_id="market_analyzer",
                decision=self._evaluate_market_conditions(opportunity),
                confidence=self._calculate_market_confidence(opportunity),
                reasoning="Based on market volatility and liquidity"
            )
            votes.append(market_vote)
            
            # Risk Management Agent
            risk_vote = Vote(
                agent_id="risk_manager",
                decision=self._evaluate_risk_metrics(opportunity),
                confidence=self._calculate_risk_confidence(opportunity),
                reasoning="Based on position size and exposure"
            )
            votes.append(risk_vote)
            
            # Profit Optimization Agent
            profit_vote = Vote(
                agent_id="profit_optimizer",
                decision=self._evaluate_profit_potential(opportunity),
                confidence=self._calculate_profit_confidence(opportunity),
                reasoning="Based on spread and fee analysis"
            )
            votes.append(profit_vote)
            
            return votes
            
        except Exception as e:
            logger.error(f"Error collecting votes: {str(e)}")
            raise
    
    async def execute_strategy(self) -> None:
        """Execute the market making strategy."""
        try:
            for pair in self.token_pairs:
                # Analyze opportunity
                opportunity = await self.analyze_opportunity(pair)
                
                # Collect agent votes
                votes = await self.collect_agent_votes(opportunity)
                
                # Get agent reputations
                reputations = {
                    vote.agent_id: (await self.memory.get_agent_reputation(vote.agent_id) or AgentReputation(vote.agent_id, "unknown")).success_rate
                    for vote in votes
                }
                
                # Reach consensus
                consensus = await self.consensus.reach_consensus(
                    votes=votes,
                    reputations=reputations,
                    total_agents=len(votes)
                )
                
                # Record outcome
                if consensus['consensus_reached']:
                    logger.info(f"Consensus reached for {pair}: {consensus}")
                    
                    # Execute position adjustment
                    await self._adjust_position(pair, opportunity, consensus)
                    
                    # Record strategy outcome
                    await self.memory.record_strategy_outcome(
                        StrategyOutcome(
                            strategy_id=f"mm_{pair}_{datetime.now().isoformat()}",
                            timestamp=datetime.now().isoformat(),
                            success=True,
                            confidence_scores={v.agent_id: v.confidence for v in votes},
                            actual_profit=None,  # To be updated after execution
                            predicted_profit=opportunity['metrics'].get('expected_profit'),
                            execution_time=0.0,  # To be updated
                            agents_involved=[v.agent_id for v in votes]
                        )
                    )
                else:
                    logger.info(f"No consensus reached for {pair}: {consensus}")
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {str(e)}")
            raise
    
    def _evaluate_market_conditions(self, opportunity: Dict[str, Any]) -> bool:
        """Evaluate market conditions for favorable trading."""
        metrics = opportunity['metrics']
        return (
            metrics['liquidity'] >= self.min_liquidity and
            metrics['volume'] > 0 and
            metrics['volatility'] < 0.5  # 50% max volatility
        )
    
    def _calculate_market_confidence(self, opportunity: Dict[str, Any]) -> float:
        """Calculate confidence in market analysis."""
        metrics = opportunity['metrics']
        
        # Higher confidence with higher liquidity and lower volatility
        liquidity_score = min(metrics['liquidity'] / (self.min_liquidity * 10), 1.0)
        volatility_score = max(1 - metrics['volatility'], 0)
        
        return (liquidity_score + volatility_score) / 2
    
    def _evaluate_risk_metrics(self, opportunity: Dict[str, Any]) -> bool:
        """Evaluate risk metrics for position adjustment."""
        metrics = opportunity['metrics']
        return (
            metrics['adjusted_spread'] >= self.base_spread and
            metrics['liquidity'] >= self.min_liquidity * 2  # Extra safety margin
        )
    
    def _calculate_risk_confidence(self, opportunity: Dict[str, Any]) -> float:
        """Calculate confidence in risk assessment."""
        metrics = opportunity['metrics']
        
        # Higher confidence with larger spreads and higher liquidity
        spread_score = min(metrics['adjusted_spread'] / (self.base_spread * 2), 1.0)
        liquidity_score = min(metrics['liquidity'] / (self.min_liquidity * 5), 1.0)
        
        return (spread_score + liquidity_score) / 2
    
    def _evaluate_profit_potential(self, opportunity: Dict[str, Any]) -> bool:
        """Evaluate profit potential for the opportunity."""
        metrics = opportunity['metrics']
        expected_profit = metrics['adjusted_spread'] - 0.001  # Subtract fees
        return expected_profit >= self.target_profit
    
    def _calculate_profit_confidence(self, opportunity: Dict[str, Any]) -> float:
        """Calculate confidence in profit prediction."""
        metrics = opportunity['metrics']
        
        # Higher confidence with larger expected profit
        profit_score = min(
            (metrics['adjusted_spread'] - self.target_profit) / self.target_profit,
            1.0
        )
        volume_score = min(metrics['volume'] / (self.min_liquidity * 10), 1.0)
        
        return (profit_score + volume_score) / 2
    
    async def _adjust_position(self,
                             pair: str,
                             opportunity: Dict[str, Any],
                             consensus: Dict[str, Any]) -> None:
        """Adjust market making position based on consensus."""
        logger.info(f"Adjusting position for {pair}")
        # TODO: Implement actual position adjustment logic
        pass

async def main():
    """Run the market making strategy."""
    strategy = MarketMakingStrategy(
        token_pairs=['NEAR/USDC', 'ETH/NEAR'],
        base_spread=0.002,
        min_liquidity=1000,
        max_position=10000,
        target_profit=0.001
    )
    
    try:
        await strategy.execute_strategy()
    finally:
        await strategy.market_data.close()

if __name__ == "__main__":
    asyncio.run(main()) 