"""
CLI Module
Implements command-line interface for NEAR Swarm Intelligence
"""

import click
from typing import Optional

from near_swarm.cli.chat import chat

@click.group()
def cli():
    """NEAR Swarm Intelligence CLI"""
    pass

@cli.command()
@click.option(
    '--agent',
    type=click.Choice(['market_analyzer', 'risk_manager', 'strategy_optimizer']),
    default='market_analyzer',
    help='Type of agent to chat with'
)
def chat_cmd(agent: str):
    """Start interactive chat session with an agent."""
    chat(agent)

if __name__ == '__main__':
    cli() 