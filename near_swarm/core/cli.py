"""
NEAR Swarm Intelligence CLI
Command-line tool for managing NEAR swarm strategies.
"""

import os
import sys
import json
import click
import asyncio
import logging
import argparse
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from importlib.util import spec_from_file_location, module_from_spec

# Import core components
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    """Monitor running strategies."""
    try:
        click.echo("Starting strategy monitor...")
        
        # Get current working directory
        cwd = Path.cwd()
        
        # Find all strategy directories
        strategies = [d for d in cwd.iterdir() if d.is_dir() and (d / 'config.json').exists()]
        
        if not strategies:
            click.echo("No strategies found.")
            return
            
        # Monitor each strategy
        for strategy_dir in strategies:
            with open(strategy_dir / 'config.json') as f:
                config = json.load(f)
                
            click.echo(f"\nStrategy: {config['name']}")
            click.echo(f"Roles: {', '.join(config['roles'])}")
            click.echo(f"Min Confidence: {config['min_confidence']}")
            
    except Exception as e:
        logger.error(f"Error monitoring strategies: {str(e)}")
        sys.exit(1)

# Add other commands...

if __name__ == "__main__":
    cli() 