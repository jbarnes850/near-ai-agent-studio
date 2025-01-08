"""
CLI Module
Implements command-line interface for NEAR Swarm Intelligence
"""

import typer
from typing import Optional, List

from near_swarm.cli.chat import chat
from near_swarm.cli.create import create
from near_swarm.cli.test import test
from near_swarm.cli.deploy import deploy

app = typer.Typer(help="NEAR Swarm Intelligence CLI - Manage your swarm strategies.")

# Register commands
app.command()(chat)
app.command()(create)
app.command()(test)
app.command()(deploy)

if __name__ == '__main__':
    app() 