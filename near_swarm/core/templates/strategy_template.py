"""
NEAR Swarm Strategy Template
Demonstrates multi-agent swarm decision making with market data integration.
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_agent_config() -> AgentConfig:
    """Get agent configuration from environment."""
    # Get required values with defaults
    account_id = os.getenv('NEAR_ACCOUNT_ID')
    private_key = os.getenv('NEAR_PRIVATE_KEY')
    llm_api_key = os.getenv('LLM_API_KEY')

    # Validate required environment variables
    if not account_id:
        raise ValueError("NEAR_ACCOUNT_ID environment variable is required")
    if not private_key:
        raise ValueError("NEAR_PRIVATE_KEY environment variable is required")
    if not llm_api_key:
        raise ValueError("LLM_API_KEY environment variable is required")

    return AgentConfig(
        network=os.getenv('NEAR_NETWORK', 'testnet'),
        account_id=account_id,
        private_key=private_key,
        llm_provider=os.getenv('LLM_PROVIDER', 'hyperbolic'),
        llm_api_key=llm_api_key,
        llm_model=os.getenv('LLM_MODEL', 'meta-llama/Llama-3.3-70B-Instruct')
    )

async def run_strategy():
    """Run a multi-agent swarm strategy."""
    # Initialize market data
    market = MarketDataManager()
    agents = []
    
    try:
        # 1. Get market data
        near_data = await market.get_token_price('near')
        logger.info(f"NEAR Price: ${near_data['price']}")
        
        dex_data = await market.get_dex_data('ref-finance')
        logger.info(f"REF Finance TVL: ${dex_data['tvl']:,.2f}")
        
        # 2. Initialize swarm agents with different roles
        config = get_agent_config()
        
        market_analyzer = SwarmAgent(
            config=config,
            swarm_config=SwarmConfig(
                role="market_analyzer",
                min_confidence=0.7
            )
        )
        agents.append(market_analyzer)

        risk_manager = SwarmAgent(
            config=config,
            swarm_config=SwarmConfig(
                role="risk_manager",
                min_confidence=0.8
            )
        )
        agents.append(risk_manager)

        # 3. Analyze trading opportunity
        opportunity = await market.analyze_market_opportunity(
            token_pair='NEAR/USDC',
            amount=100,
            max_slippage=0.01
        )
        
        # 4. Create trading proposal
        proposal = {
            "type": "market_trade",
            "pair": "NEAR/USDC",
            "action": "buy" if opportunity["analysis"]["is_opportunity"] else "skip",
            "amount": 100,
            "price_impact": opportunity["analysis"]["price_impact"],
            "market_data": {
                "near_price": near_data["price"],
                "dex_tvl": dex_data["tvl"]
            }
        }

        # 5. Get swarm consensus
        logger.info("\n🤖 Getting swarm consensus...")
        consensus = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal
        )

        # 6. Display results
        logger.info("\n=== Swarm Decision ===")
        logger.info(f"Action: {proposal['action'].upper()}")
        logger.info(f"Confidence: {consensus.get('confidence', 0):.2%}")
        logger.info(f"Reasoning: {consensus.get('reasoning', 'No reasoning provided')}")
        
    finally:
        # Cleanup
        await market.close()
        for agent in agents:
            await agent.close()

if __name__ == "__main__":
    asyncio.run(run_strategy())
