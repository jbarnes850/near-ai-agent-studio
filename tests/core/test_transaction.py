import asyncio
import os
import logging
from dotenv import load_dotenv, find_dotenv
from near_swarm.core.near_integration import NEARConfig, create_near_connection

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_transaction():
    try:
        # Force reload environment variables
        load_dotenv(find_dotenv(), override=True)
        
        # Debug: Print environment variables
        logger.info(f"NEAR_NETWORK: {os.getenv('NEAR_NETWORK')}")
        logger.info(f"NEAR_ACCOUNT_ID: {os.getenv('NEAR_ACCOUNT_ID')}")
        logger.info(f"NEAR_PRIVATE_KEY: {os.getenv('NEAR_PRIVATE_KEY')}")
        
        # Validate environment variables
        required_vars = ['NEAR_NETWORK', 'NEAR_ACCOUNT_ID', 'NEAR_PRIVATE_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Create NEAR config with FastNEAR RPC
        config = NEARConfig(
            network=os.getenv('NEAR_NETWORK'),
            account_id=os.getenv('NEAR_ACCOUNT_ID'),
            private_key=os.getenv('NEAR_PRIVATE_KEY'),
            node_url="https://test.rpc.fastnear.com"  # FastNEAR RPC endpoint
        )
        
        logger.info(f"Testing transaction on {config.network} for account {config.account_id}")
        logger.info(f"Using RPC endpoint: {config.node_url}")
        
        # Create connection
        near = await create_near_connection(config)
        try:
            # Check account balance before transaction
            balance = await near.get_account_balance()
            logger.info(f"Current balance: {float(balance['available'])/1e24:.6f} NEAR")
            
            # Send a small test transaction (0.0001 NEAR) - same amount as CLI test
            amount = 0.0001
            logger.info(f"Sending {amount} NEAR to {config.account_id}")
            
            result = await near.send_transaction(
                receiver_id=config.account_id,  # Send to self as in CLI test
                amount=amount
            )
            
            logger.info("Transaction successful!")
            logger.info(f"Transaction hash: {result['transaction_id']}")
            logger.info(f"Explorer URL: {result['explorer_url']}")
            
            # Check balance after transaction
            new_balance = await near.get_account_balance()
            logger.info(f"New balance: {float(new_balance['available'])/1e24:.6f} NEAR")
            
        finally:
            await near.close()
            
    except Exception as e:
        logger.error(f"Error during transaction test: {str(e)}")
        logger.error("Traceback:", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(test_transaction()) 