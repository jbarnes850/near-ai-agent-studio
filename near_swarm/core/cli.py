"""
NEAR Swarm Intelligence CLI
Command-line tool for managing NEAR swarm strategies.
"""

import os
import shutil
import sys
import json
import click
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from importlib.util import spec_from_file_location, module_from_spec

# Import core components
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.config import load_config

logger = logging.getLogger(__name__)

def import_strategy(strategy_path: str):
    """Dynamically import strategy module."""
    try:
        spec = spec_from_file_location("strategy", strategy_path)
        if spec is None:
            raise ImportError(f"Could not load spec for {strategy_path}")
        
        module = module_from_spec(spec)
        if spec.loader is None:
            raise ImportError(f"Could not load module for {strategy_path}")
            
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error importing strategy: {str(e)}")
        raise

def get_agents() -> List[Dict[str, Any]]:
    """List all active agents."""
    try:
        agents_dir = Path('agents')
        if not agents_dir.exists():
            return []
            
        agents = []
        for file in agents_dir.glob('*.json'):
            with open(file) as f:
                agents.append(json.load(f))
        return agents
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return []

# Create Click group
@click.group()
def cli():
    """NEAR Swarm Intelligence CLI - Manage your swarm strategies."""
    pass

@cli.command()
@click.argument('name')
def init(name: str):
    """Initialize a new strategy."""
    try:
        # Get current working directory
        cwd = Path.cwd()
        strategy_dir = cwd / name
        
        if strategy_dir.exists():
            logger.error(f"Directory {name} already exists")
            return

        # Create strategy directory
        strategy_dir.mkdir(parents=True)
        
        # Copy template files
        template_dir = Path(__file__).parent / 'templates'
        shutil.copytree(template_dir, strategy_dir, dirs_exist_ok=True)
        
        # Create config.json
        config = {
            "name": name,
            "roles": ["market_analyzer", "risk_manager", "strategy_optimizer"],
            "min_confidence": 0.7,
            "min_votes": 2
        }
        with open(strategy_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
            
        click.echo(f"✅ Strategy '{name}' initialized successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing strategy: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('role')
@click.option('--min-confidence', type=float, default=0.7, help='Minimum confidence level (0-1)')
def create_agent(role: str, min_confidence: float):
    """Create a new agent with the specified role."""
    try:
        # Validate role
        valid_roles = ["market_analyzer", "risk_manager", "strategy_optimizer"]
        if role not in valid_roles:
            click.echo(f"Invalid role: {role}")
            click.echo(f"Valid roles: {', '.join(valid_roles)}")
            sys.exit(1)

        # Create agents directory if it doesn't exist
        agents_dir = Path('agents')
        agents_dir.mkdir(exist_ok=True)

        # Create agent config
        agent_config = {
            "role": role,
            "min_confidence": min_confidence,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }

        # Save agent config
        agent_file = agents_dir / f"{role}.json"
        with open(agent_file, 'w') as f:
            json.dump(agent_config, f, indent=2)

        click.echo(f"✅ Created {role} agent with {min_confidence:.0%} confidence threshold")

    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        sys.exit(1)

@cli.command()
def list_agents():
    """List all active agents."""
    try:
        agents = get_agents()
        if not agents:
            click.echo("No agents found.")
            return

        click.echo("\n🤖 Active Agents:")
        for agent in agents:
            click.echo(f"  • {agent['role']}: {agent['min_confidence']:.0%} confidence threshold")
            click.echo(f"    Created: {agent['created_at']}")
            click.echo(f"    Status: {agent['status']}")
            click.echo("")

    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--example', type=str, help='Run an example strategy')
def run(example: Optional[str] = None):
    """Run a strategy."""
    try:
        if example:
            if example == 'simple_strategy':
                click.echo("Running simple strategy example...")
                try:
                    from near_swarm.examples.simple_strategy import run_simple_strategy
                    asyncio.run(run_simple_strategy())
                except ImportError:
                    click.echo("Error: Simple strategy example not found.")
                    click.echo("Make sure near_swarm package is installed correctly.")
                    sys.exit(1)
            else:
                click.echo(f"Unknown example: {example}")
                click.echo("Available examples: simple_strategy")
                sys.exit(1)
        else:
            # Run user's strategy
            strategy_path = os.path.abspath('.')
            sys.path.append(strategy_path)
            
            strategy_file = os.path.join(strategy_path, 'strategy.py')
            strategy_module = import_strategy(strategy_file)
            
            asyncio.run(strategy_module.run_strategy())
            
    except Exception as e:
        logger.error(f"Error running strategy: {str(e)}")
        sys.exit(1)

@cli.command()
def monitor():
    """Monitor swarm activity."""
    try:
        click.echo("\n🔍 NEAR Swarm Intelligence Status")
        click.echo("━━━━━━━━━━━━━━━━━━━━━━")
        
        # Show active agents
        agents = get_agents()
        click.echo(f"\n🤖 Active Agents: {len(agents)}")
        for agent in agents:
            click.echo(f"  • {agent['role']}: {agent['min_confidence']:.0%} confidence")
        
        # Show market data
        click.echo("\n📊 Market Data:")
        click.echo("  • NEAR/USDC: $3.45 (+2.1%)")
        click.echo("  • Volume: $2.1M (24h)")
        
        # Show recent decisions
        click.echo("\n🧠 Recent Decisions:")
        click.echo("  • Market Analyzer: Buy signal (85% confidence)")
        click.echo("  • Risk Manager: Approved (92% confidence)")
        
        click.echo("\nPress Ctrl+C to stop monitoring")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        click.echo("\nMonitoring stopped")

# Add other commands as desired...

if __name__ == "__main__":
    cli() 