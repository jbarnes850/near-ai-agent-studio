from typing import List
import typer
from rich.console import Console

console = Console()

def create(
    project_name: str,
    template: str = typer.Option("basic", help="Template type: basic, defi, nft, dao"),
    chain: str = typer.Option("testnet", help="Chain: testnet, mainnet"),
    agents: List[str] = typer.Option(["market", "risk"], help="Agents to include"),
    rpc_url: str = typer.Option("https://neart.lava.build", help="NEAR RPC endpoint"),
    use_backup_rpc: bool = typer.Option(False, help="Use backup RPC endpoints")
):
    """Interactive project creation wizard"""
    console.print(f"🚀 Creating new NEAR Swarm project: {project_name}")
    
    # 1. Template selection with preview
    templates = {
        "basic": "Simple trading bot",
        "defi": "DeFi automation",
        "nft": "NFT trading bot",
        "dao": "DAO governance"
    }
    
    # 2. Agent configuration
    for agent in agents:
        console.print(f"Configuring {agent} agent...")
        
    # 3. RPC configuration
    console.print(f"Using RPC endpoint: {rpc_url}")
    if use_backup_rpc:
        console.print("Backup RPC endpoints enabled") 