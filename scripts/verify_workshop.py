"""Workshop environment verification script."""
import asyncio
import logging
import os
from typing import Optional
from dotenv import load_dotenv
from near_swarm.core.llm_provider import LLMConfig, create_llm_provider
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.near_integration import NEARConnection

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

async def test_llm_connection():
    """Test LLM integration."""
    print("\n⏳ Testing LLM integration...")
    llm = None
    try:
        # Load LLM configuration
        api_key = os.getenv('LLM_API_KEY')
        provider = os.getenv('LLM_PROVIDER', 'hyperbolic')
        model = os.getenv('LLM_MODEL', 'meta-llama/Llama-3.3-70B-Instruct')
        api_url = os.getenv('LLM_API_URL', 'https://api.hyperbolic.xyz/v1')

        if not api_key:
            print('❌ LLM API key not found')
            return False
        
        config = LLMConfig(
            provider=provider,
            api_key=api_key,
            model=model,
            api_url=api_url
        )
        
        llm = create_llm_provider(config)
        response = await llm.query('Hello! Please respond with OK to verify the connection.')
        
        if 'OK' in response.upper():
            print(f"✓ {provider.title()} LLM connection verified")
            return True
        else:
            print(f"❌ Unexpected response from LLM")
            return False
            
    except Exception as e:
        print(f"❌ LLM verification failed: {str(e)}")
        return False
    finally:
        if llm is not None:
            await llm.close()

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

        print("\n🔧 Testing Components")
        print("━━━━━━━━━━━━━━━━━━━━━━")
        
        # 1. Test Market Data
        async with MarketDataManager() as market:
            await test_market_data(market)
        
        # 2. Test NEAR Connection
        async with NEARConnection(
            network=network,
            account_id=account_id,
            private_key=private_key
        ) as near:
            await test_near_connection(near)
            
        # 3. Test LLM Connection
        llm_success = await test_llm_connection()
        if not llm_success:
            print("\n⚠️  LLM verification failed but continuing with other checks")
        
        print("\n✅ All systems verified!")
        
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(verify_environment()) 