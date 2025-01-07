"""Workshop environment verification script."""
import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from near_swarm.core.llm_provider import LLMConfig, create_llm_provider
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.near_integration import NEARConnection

async def test_llm(provider):
    """Test LLM integration."""
    print("⏳ Testing LLM integration...")
    try:
        # Simple test prompt
        response = await provider.query(
            "Respond with 'OK' if you can understand this message.",
            temperature=0.1,  # Low temperature for deterministic response
            max_tokens=10     # Small response size
        )
        assert "OK" in response, "LLM response validation failed"
        print("✓ LLM integration verified")
        
        # Test JSON response format with structured prompt
        test_prompt = """You are a specialized AI agent in a NEAR Protocol trading swarm.
Evaluate this simple NEAR transfer based on current market conditions:

Type: transfer
Amount: 1 NEAR
Recipient: test.near
Market Context:
- Current Price: $5.00
- 24h Volume: $2.1M
- Market Trend: Stable
- Network Load: Low

Provide your evaluation in JSON format with the following structure:
{
    "decision": boolean,      // Your decision to approve or reject
    "confidence": float,      // Your confidence level (0.0 to 1.0)
    "reasoning": string       // Detailed explanation of your decision
}"""

        response = await provider.query(
            test_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        print("\nTest LLM Response:")
        print(response)
        print("\n✓ LLM JSON format verified")
        
    except Exception as e:
        print(f"❌ LLM integration failed: {str(e)}")
        raise

async def test_market_data(manager):
    """Test market data integration."""
    print("\n⏳ Testing market data integration...")
    try:
        # Fetch NEAR price
        data = await manager.get_token_price("NEAR")
        print(f"Current NEAR Price: ${data['price']:.2f}")
        print(f"Data Confidence: {data['confidence']:.2%}")
        print("✓ Market data integration verified")
    except Exception as e:
        print(f"❌ Market data integration failed: {str(e)}")
        raise

async def test_near_connection(connection):
    """Test NEAR blockchain connection."""
    print("\n⏳ Testing NEAR connection...")
    try:
        # Get account balance
        balance = await connection.get_account_balance()
        print(f"Account Balance: {balance} NEAR")
        print("✓ NEAR connection verified")
    except Exception as e:
        print(f"❌ NEAR connection failed: {str(e)}")
        raise

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

        print("\n🔧 Testing Components")
        print("━━━━━━━━━━━━━━━━━━━━━━")

        # 1. Test LLM
        config = LLMConfig(
            provider="hyperbolic",
            api_key=llm_api_key,
            model=os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-70B-Instruct"),
            api_url=os.getenv("LLM_API_URL", "https://api.hyperbolic.xyz/v1")
        )
        provider = create_llm_provider(config)
        await test_llm(provider)
        
        # 2. Test Market Data
        market = MarketDataManager()
        await test_market_data(market)
        
        # 3. Test NEAR Connection
        near = NEARConnection(
            network=network,
            account_id=account_id,
            private_key=private_key
        )
        await test_near_connection(near)
        
        print("\n✅ All systems verified!")
        
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        raise
    finally:
        # Clean up resources
        if 'provider' in locals():
            await provider.close()
        if 'market' in locals():
            await market.close()

if __name__ == "__main__":
    asyncio.run(verify_environment()) 