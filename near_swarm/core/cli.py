"""
Command Line Interface for NEAR AI Agent
Provides a simple CLI for interacting with the NEAR AI Agent.
"""

import os
import sys
import asyncio
import logging
import argparse
from typing import Optional
from dotenv import load_dotenv

from agent import create_agent, AgentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> AgentConfig:
    """Load configuration from environment variables."""
    load_dotenv()
    
    required_vars = [
        'NEAR_NETWORK',
        'NEAR_ACCOUNT_ID',
        'NEAR_PRIVATE_KEY',
        'LLM_PROVIDER',
        'LLM_API_KEY'
    ]
    
    # Check for required environment variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    return AgentConfig(
        near_network=os.getenv('NEAR_NETWORK', 'testnet'),
        account_id=os.getenv('NEAR_ACCOUNT_ID'),
        private_key=os.getenv('NEAR_PRIVATE_KEY'),
        llm_provider=os.getenv('LLM_PROVIDER'),
        llm_api_key=os.getenv('LLM_API_KEY')
    )

async def interactive_mode(agent):
    """Run the agent in interactive mode."""
    print("NEAR AI Agent Interactive Mode")
    print("Type 'exit' to quit")
    print("Type 'help' for available commands")
    
    while True:
        try:
            user_input = input("\nEnter command or message > ").strip()
            
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower().startswith('balance'):
                # Check balance command
                parts = user_input.split()
                account_id = parts[1] if len(parts) > 1 else None
                balance = await agent.check_balance(account_id)
                print(f"Balance: {balance} NEAR")
            else:
                # Process as a message to the agent
                response = await agent.process_message(user_input)
                print(f"\nAgent: {response}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {str(e)}")

def print_help():
    """Print available commands."""
    print("\nAvailable Commands:")
    print("  balance [account_id] - Check NEAR balance")
    print("  help               - Show this help message")
    print("  exit               - Exit the program")
    print("\nYou can also type any message to interact with the AI agent.")

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="NEAR AI Agent CLI")
    parser.add_argument(
        '--config',
        type=str,
        default='.env',
        help='Path to configuration file (default: .env)'
    )
    parser.add_argument(
        '--network',
        type=str,
        choices=['testnet', 'mainnet'],
        help='NEAR network to use (overrides config)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        if args.network:
            config.near_network = args.network
        
        # Create agent
        agent = create_agent(config)
        
        # Run interactive mode
        asyncio.run(interactive_mode(agent))
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 