#!/usr/bin/env python3
"""
NEAR Swarm Intelligence Example
Demonstrates LLM-powered multi-agent decision making
"""

import asyncio
import logging
import os
from typing import Dict, Any
from dotenv import load_dotenv

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.market_data import MarketDataManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_example() -> Dict[str, Any]:
    """Run an example demonstrating LLM-powered multi-agent decision making."""
    market_analyzer = None
    risk_manager = None
    strategy_optimizer = None
    market_data = None
    
    try:
        print("\n🚀 Initializing NEAR Swarm Intelligence Example")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Load configuration
        load_dotenv()
        
        # Validate environment
        required_vars = ["NEAR_ACCOUNT_ID", "NEAR_PRIVATE_KEY", "LLM_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Initialize market data
        print("\n📊 Fetching Market Data...")
        market_data = MarketDataManager()
        near_data = await market_data.get_token_price("near")
        print(f"• Current NEAR Price: ${near_data['price']:.2f}")
        
        # Initialize agents with specific roles
        print("\n🤖 Initializing Swarm Agents...")
        
        config = AgentConfig(
            network=os.getenv("NEAR_NETWORK", "testnet"),
            account_id=os.getenv("NEAR_ACCOUNT_ID"),
            private_key=os.getenv("NEAR_PRIVATE_KEY"),
            llm_provider=os.getenv("LLM_PROVIDER", "hyperbolic"),
            llm_api_key=os.getenv("LLM_API_KEY"),
            llm_model=os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct"),
            api_url=os.getenv("LLM_API_URL", "https://api.hyperbolic.xyz/v1")
        )
        
        market_analyzer = SwarmAgent(
            config,
            SwarmConfig(
                role="market_analyzer",
                min_confidence=0.7,
                min_votes=2
            )
        )
        print("✓ Market Analyzer initialized")

        risk_manager = SwarmAgent(
            config,
            SwarmConfig(
                role="risk_manager",
                min_confidence=0.8,  # Higher threshold for risk management
                min_votes=2
            )
        )
        print("✓ Risk Manager initialized")

        strategy_optimizer = SwarmAgent(
            config,
            SwarmConfig(
                role="strategy_optimizer",
                min_confidence=0.7,
                min_votes=2
            )
        )
        print("✓ Strategy Optimizer initialized")

        # Start all agents
        print("\n🔄 Starting Agents...")
        await market_analyzer.start()
        await risk_manager.start()
        await strategy_optimizer.start()
        print("✓ All agents started")

        # Form swarm
        print("\n🔗 Forming Swarm Network...")
        await market_analyzer.join_swarm([risk_manager, strategy_optimizer])
        print("✓ Swarm network established")

        # Example NEAR transfer proposal with market context
        proposal = {
            "type": "transfer",
            "params": {
                "recipient": "bob.testnet",
                "amount": "0.1",
                "token": "NEAR",
                "market_context": {
                    "current_price": near_data["price"],
                    "24h_volume": "2.1M",
                    "volatility": "medium",
                    "market_trend": "upward",
                    "gas_price": "0.001",
                    "network_load": "moderate"
                }
            }
        }

        print("\n=== Running LLM-Powered Multi-Agent Strategy Example ===")
        print(f"Proposing transfer: {proposal['params']['amount']} NEAR to {proposal['params']['recipient']}")
        print("\nMarket Context:")
        print(f"• Current NEAR Price: ${proposal['params']['market_context']['current_price']:.2f}")
        print(f"• 24h Volume: ${proposal['params']['market_context']['24h_volume']}")
        print(f"• Market Trend: {proposal['params']['market_context']['market_trend']}")
        print(f"• Network Load: {proposal['params']['market_context']['network_load']}")

        # Get swarm consensus with LLM-powered evaluation
        result = await market_analyzer.propose_action(
            action_type=proposal["type"],
            params=proposal["params"]
        )

        print("\n=== Swarm Decision Analysis ===")
        print(f"Consensus reached: {result['consensus']}")
        print(f"Approval rate: {result['approval_rate']:.2%}")
        print("\nAgent Reasoning:")
        for i, reason in enumerate(result["reasons"]):
            print(f"\nAgent {i+1}:")
            print(f"• {reason}")

        if result["consensus"]:
            print("\n=== Executing Transfer ===")
            print("✅ Transfer completed successfully!")
            print("All agents have approved with sufficient confidence.")
        else:
            print("\n=== Transfer Rejected ===")
            print("❌ The swarm decided not to execute the transfer.")
            print("Insufficient consensus or confidence levels not met.")

        return result

    except Exception as e:
        logger.error(f"Error in example: {str(e)}")
        raise
    finally:
        # Cleanup
        if market_data:
            await market_data.close()
        if market_analyzer:
            await market_analyzer.close()
        if risk_manager:
            await risk_manager.close()
        if strategy_optimizer:
            await strategy_optimizer.close()

if __name__ == "__main__":
    asyncio.run(run_example()) 