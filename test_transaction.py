import asyncio
import os
from dotenv import load_dotenv
from near_swarm.core.near_integration import NEARConfig, create_near_connection

async def test_transaction():
    # Load environment variables
    load_dotenv()
    
    # Create NEAR config
    config = NEARConfig(
        network=os.getenv('NEAR_NETWORK', 'testnet'),
        account_id=os.getenv('NEAR_ACCOUNT_ID'),
        private_key=os.getenv('NEAR_PRIVATE_KEY')
    )
    
    # Create connection
    near = await create_near_connection(config)
    try:
        # Send a small test transaction (0.0001 NEAR)
        result = await near.send_transaction(
            receiver_id=os.getenv('NEAR_ACCOUNT_ID'),  # Send to self
            amount=0.0001
        )
        print(f"Transaction successful!")
        print(f"Transaction hash: {result['hash']}")
        print(f"Explorer URL: {result['explorer_url']}")
        
    finally:
        await near.close()

if __name__ == "__main__":
    asyncio.run(test_transaction()) 