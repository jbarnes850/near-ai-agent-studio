"""Workshop environment verification script."""
import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from near_swarm.core.llm_provider import LLMConfig, create_llm_provider
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.near_integration import NEARConnection

async def verify_environment():
    """Verify all components needed for workshop."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Validate NEAR credentials
        network = os.getenv("NEAR_NETWORK", "testnet")
        account_id = os.getenv("NEAR_ACCOUNT_ID")
        private_key = os.getenv("NEAR_PRIVATE_KEY")
        
        if not account_id:
            raise ValueError("NEAR_ACCOUNT_ID environment variable is required")
        if not private_key:
            raise ValueError("NEAR_PRIVATE_KEY environment variable is required")

        # Validate LLM credentials
        llm_api_key = os.getenv("LLM_API_KEY")
        if not llm_api_key:
            raise ValueError("LLM_API_KEY environment variable is required")

        # 1. Test LLM
        config = LLMConfig(
            provider="hyperbolic",
            api_key=llm_api_key,
            model=os.getenv("LLM_MODEL", "meta-llama/Llama-3.3-70B-Instruct"),
            api_url=os.getenv("HYPERBOLIC_API_URL", "https://api.hyperbolic.xyz/v1/chat/completions")
        )
        provider = create_llm_provider(config)
        
        # 2. Test Market Data
        market = MarketDataManager()
        
        # 3. Test NEAR Connection
        near = NEARConnection(
            network=network,
            account_id=account_id,
            private_key=private_key
        )
        
        print("✅ All systems verified!")
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(verify_environment()) 