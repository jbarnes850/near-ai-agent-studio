"""
Example of using SwarmAgent for trading decisions.

This example demonstrates how to:
1. Create specialized agents with different roles
2. Form a swarm for collaborative decision making
3. Propose and evaluate trading actions
4. Reach consensus among agents

Key concepts:
- Each agent has a specific role (market analysis, risk, strategy)
- Agents work together to evaluate trading decisions
- Consensus is reached based on weighted votes
- Decisions include confidence levels and reasoning
"""

import asyncio
import os
from dotenv import load_dotenv
import logging

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config() -> AgentConfig:
    """Load configuration from environment variables."""
    load_dotenv()
    
    # Verify required environment variables
    required_vars = ['NEAR_ACCOUNT_ID', 'NEAR_PRIVATE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            f"Please copy .env.example to .env and configure your credentials."
        )
    
    return AgentConfig(
        near_network=os.getenv('NEAR_NETWORK', 'testnet'),
        account_id=os.getenv('NEAR_ACCOUNT_ID'),
        private_key=os.getenv('NEAR_PRIVATE_KEY'),
        llm_provider=os.getenv('LLM_PROVIDER', 'hyperbolic'),
        llm_api_key=os.getenv('LLM_API_KEY', '')
    )


async def create_swarm() -> list[SwarmAgent]:
    """Create a swarm of specialized agents."""
    config = load_config()
    
    # Create agents with different roles
    agents = [
        SwarmAgent(
            config=config,
            swarm_config=SwarmConfig(
                role="market_analyzer",
                min_confidence=0.6
            )
        ),
        SwarmAgent(
            config=config,
            swarm_config=SwarmConfig(
                role="risk_manager",
                min_confidence=0.7
            )
        ),
        SwarmAgent(
            config=config,
            swarm_config=SwarmConfig(
                role="strategy_optimizer",
                min_confidence=0.8
            )
        )
    ]
    
    # Connect agents into a swarm
    logger.info("Forming swarm with %d agents...", len(agents))
    for agent in agents:
        peers = [a for a in agents if a != agent]
        await agent.join_swarm(peers)
    
    return agents


async def propose_trade(swarm: list[SwarmAgent], token: str):
    """Propose a trade to the swarm."""
    # Use market analyzer as the proposing agent
    market_analyzer = next(
        agent for agent in swarm 
        if agent.swarm_config.role == "market_analyzer"
    )
    
    # Create trade proposal
    proposal = {
        "token": token,
        "action": "buy",
        "amount": 10.0,
        "max_price": 3.50
    }
    
    logger.info("Proposing trade: %s", proposal)
    
    # Get swarm consensus
    result = await market_analyzer.propose_action(
        action_type="trade",
        params=proposal
    )
    
    # Print detailed results
    print("\n🤖 Swarm Trading Decision")
    print("━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Consensus Reached: {'✅' if result['consensus'] else '❌'}")
    print(f"Approval Rate: {result['approval_rate']:.1%}")
    print(f"Total Votes: {result['total_votes']}")
    
    print("\n📝 Agent Reasoning:")
    for i, reason in enumerate(result["reasons"], 1):
        print(f"{i}. {reason}")
    
    return result


async def main():
    """Run the swarm trading example."""
    try:
        # Create and initialize swarm
        swarm = await create_swarm()
        
        # Propose a NEAR trade
        await propose_trade(swarm, "NEAR")
        
        # Cleanup
        for agent in swarm:
            await agent.close()
            
    except ValueError as e:
        logger.error("Configuration error: %s", str(e))
    except Exception as e:
        logger.error("Error running example: %s", str(e))


if __name__ == "__main__":
    asyncio.run(main()) 