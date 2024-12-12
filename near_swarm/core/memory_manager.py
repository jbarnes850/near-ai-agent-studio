"""
Memory Management System
Core functionality for storing and retrieving agent memory
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class StrategyOutcome:
    """Record of a strategy execution outcome"""
    strategy_id: str
    timestamp: str
    success: bool
    confidence_scores: Dict[str, float]
    actual_profit: float
    predicted_profit: float
    execution_time: float
    agents_involved: List[str]


class MemoryManager:
    """Memory management system for storing and retrieving agent data"""
    
    def __init__(self):
        """Initialize memory manager"""
        self.memory: Dict[str, List[Dict[str, Any]]] = {}
        self.outcomes: List[StrategyOutcome] = []
    
    async def store(
        self,
        category: str,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Store data in memory with context"""
        try:
            if category not in self.memory:
                self.memory[category] = []
            
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "context": context or {}
            }
            
            self.memory[category].append(memory_entry)
            return True
            
        except Exception as e:
            raise Exception(f"Error storing memory: {str(e)}")
    
    async def retrieve(
        self,
        category: str,
        context: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve data from memory with optional context filtering"""
        try:
            if category not in self.memory:
                return []
            
            results = self.memory[category]
            
            # Filter by context if provided
            if context:
                results = [
                    entry for entry in results
                    if self._match_context(entry["context"], context)
                ]
            
            # Sort by timestamp (newest first) and limit results
            results.sort(
                key=lambda x: x["timestamp"],
                reverse=True
            )
            return results[:limit]
            
        except Exception as e:
            raise Exception(f"Error retrieving memory: {str(e)}")
    
    def _match_context(
        self,
        entry_context: Dict[str, Any],
        query_context: Dict[str, Any]
    ) -> bool:
        """Check if entry context matches query context"""
        return all(
            entry_context.get(k) == v
            for k, v in query_context.items()
        )
    
    async def record_strategy_outcome(
        self,
        outcome: StrategyOutcome
    ) -> bool:
        """Record the outcome of a strategy execution"""
        try:
            self.outcomes.append(outcome)
            
            # Store in regular memory too
            await self.store(
                "strategy_outcomes",
                {
                    "strategy_id": outcome.strategy_id,
                    "success": outcome.success,
                    "actual_profit": outcome.actual_profit,
                    "predicted_profit": outcome.predicted_profit
                },
                {
                    "timestamp": outcome.timestamp,
                    "agents": outcome.agents_involved
                }
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Error recording strategy outcome: {str(e)}")
    
    async def get_strategy_performance(
        self,
        strategy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get performance metrics for strategies"""
        try:
            # Filter outcomes
            relevant_outcomes = self.outcomes
            if strategy_id:
                relevant_outcomes = [
                    o for o in relevant_outcomes
                    if o.strategy_id == strategy_id
                ]
            
            # Calculate metrics
            total_executions = len(relevant_outcomes)
            successful_executions = len([o for o in relevant_outcomes if o.success])
            
            if total_executions == 0:
                return {
                    "total_executions": 0,
                    "success_rate": 0.0,
                    "average_profit": 0.0,
                    "prediction_accuracy": 0.0
                }
            
            # Calculate metrics
            success_rate = successful_executions / total_executions
            average_profit = sum(o.actual_profit for o in relevant_outcomes) / total_executions
            
            # Calculate prediction accuracy
            prediction_errors = [
                abs(o.predicted_profit - o.actual_profit)
                for o in relevant_outcomes
            ]
            average_prediction_error = sum(prediction_errors) / total_executions
            prediction_accuracy = max(0, 1 - average_prediction_error)
            
            return {
                "total_executions": total_executions,
                "success_rate": success_rate,
                "average_profit": average_profit,
                "prediction_accuracy": prediction_accuracy
            }
            
        except Exception as e:
            raise Exception(f"Error getting strategy performance: {str(e)}")
    
    async def clear_category(self, category: str) -> bool:
        """Clear all entries in a category"""
        try:
            if category in self.memory:
                self.memory[category] = []
            return True
        except Exception as e:
            raise Exception(f"Error clearing category: {str(e)}")
    
    async def clear_all(self) -> bool:
        """Clear all memory"""
        try:
            self.memory.clear()
            self.outcomes.clear()
            return True
        except Exception as e:
            raise Exception(f"Error clearing memory: {str(e)}")