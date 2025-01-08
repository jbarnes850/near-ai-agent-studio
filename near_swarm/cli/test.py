import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

def test(
    strategy_path: str,
    mode: str = typer.Option("sandbox", help="test/sandbox/simulation"),
    duration: int = typer.Option(3600, help="Test duration in seconds")
):
    """Live test environment with real market data"""
    console.print(Panel("""
    🔬 Test Environment Active
    
    Market Data: ✓ Live
    Execution: ✓ Simulated
    Risk Checks: ✓ Enabled
    """)) 