"""
Command Line Interface for NEAR Swarm Intelligence
Provides a CLI for managing and running swarm agents.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.config import load_config
from near_swarm.examples.simple_strategy import run_simple_strategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def init_command(args):
    """Initialize a new strategy."""
    try:
        # Get current working directory from args
        cwd = Path.cwd()

        # Create strategy directory
        strategy_dir = cwd / args.name
        if strategy_dir.exists():
            logger.error(f"Directory {args.name} already exists")
            return

        strategy_dir.mkdir(parents=True)

        # Create strategy files
        config = {
            "name": args.name,
            "roles": ["market_analyzer", "risk_manager", "strategy_optimizer"],
            "min_confidence": 0.7,
            "min_votes": 2
        }

        # Write config file
        with open(strategy_dir / "config.json", "w") as f:
            json.dump(config, f, indent=2)

        # Create strategy template
        template = f"""\"\"\"
{args.name} Strategy
\"\"\"

import asyncio
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.config import load_config

async def run_strategy():
    \"\"\"Run the {args.name} strategy.\"\"\"
    try:
        # Initialize your strategy here
        config = load_config()
        agent = SwarmAgent(
            config,
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )
        # Add your strategy logic here
        pass
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(run_strategy())
"""
        with open(strategy_dir / f"{args.name}.py", "w") as f:
            f.write(template)

        logger.info(f"Initialized new strategy in {args.name}/")

    except Exception as e:
        logger.error(f"Error initializing strategy: {str(e)}")
        sys.exit(1)

async def run_command(args):
    """Run a strategy."""
    try:
        if args.example:
            if args.example == "simple_strategy":
                await run_simple_strategy()
            else:
                logger.error(f"Unknown example strategy: {args.example}")
                return
        else:
            # Load strategy config
            config_path = Path(args.config).resolve()
            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                return

            with open(config_path) as f:
                config = json.load(f)

            # Get strategy directory from config path
            strategy_dir = config_path.parent

            # Run custom strategy
            strategy_path = strategy_dir / f"{config['name']}.py"
            if not strategy_path.exists():
                logger.error(f"Strategy file not found: {strategy_path}")
                return

            # Import and run strategy
            import importlib.util
            spec = importlib.util.spec_from_file_location("strategy", strategy_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            await module.run_strategy()

    except Exception as e:
        logger.error(f"Error running strategy: {str(e)}")
        sys.exit(1)

async def create_agent_command(args):
    """Create a new agent with specified role."""
    try:
        config = load_config()
        agent = SwarmAgent(
            config,
            SwarmConfig(
                role=args.role,
                min_confidence=args.min_confidence,
                min_votes=args.min_votes
            )
        )
        logger.info(f"Created agent with role: {args.role}")
        return agent
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        sys.exit(1)

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
    parser = argparse.ArgumentParser(description="NEAR Swarm Intelligence CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new strategy")
    init_parser.add_argument("name", help="Strategy name")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a strategy")
    run_parser.add_argument("--example", help="Run example strategy (e.g., simple_strategy)")
    run_parser.add_argument("--config", help="Path to strategy config file")

    # Create agent command
    create_parser = subparsers.add_parser("create-agent", help="Create a new agent")
    create_parser.add_argument("role", choices=["market_analyzer", "risk_manager", "strategy_optimizer"])
    create_parser.add_argument("--min-confidence", type=float, default=0.7)
    create_parser.add_argument("--min-votes", type=int, default=2)

    # Interactive mode
    interactive_parser = subparsers.add_parser("interactive", help="Run in interactive mode")
    interactive_parser.add_argument(
        '--config',
        type=str,
        default='.env',
        help='Path to configuration file (default: .env)'
    )
    interactive_parser.add_argument(
        '--network',
        type=str,
        choices=['testnet', 'mainnet'],
        help='NEAR network to use (overrides config)'
    )

    args = parser.parse_args()

    try:
        if args.command == "init":
            asyncio.run(init_command(args))
        elif args.command == "run":
            asyncio.run(run_command(args))
        elif args.command == "create-agent":
            asyncio.run(create_agent_command(args))
        elif args.command == "interactive" or not args.command:
            config = load_config()
            if hasattr(args, 'network') and args.network:
                config.near_network = args.network
            agent = SwarmAgent(config, SwarmConfig(role="market_analyzer"))
            asyncio.run(interactive_mode(agent))
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 