"""
NEAR Swarm CLI
Main entry point for the command line interface
"""

import click
import asyncio
from .plugins import plugins
from .create import create
from .config import config
from ..plugins import PluginLoader

@click.group()
def cli():
    """NEAR Swarm Intelligence CLI"""
    pass

@cli.command()
@click.argument('plugin_name')
@click.option('--operation', '-o', help='Operation to execute')
@click.option('--config', '-c', help='Path to plugin configuration file')
def execute(plugin_name: str, operation: str = None, config: str = None):
    """Execute a plugin or strategy"""
    try:
        async def run_plugin():
            # Initialize plugin loader
            loader = PluginLoader()
            
            # Load and validate plugin
            plugin = await loader.load_plugin(plugin_name)
            if not plugin:
                click.echo(f"Plugin {plugin_name} not found")
                return
                
            # Load configuration if provided
            if config:
                plugin.load_config(config)
                
            # Execute plugin
            click.echo(f"Executing plugin: {plugin_name}")
            if operation:
                click.echo(f"Operation: {operation}")
                await plugin.execute(operation=operation)
            else:
                await plugin.execute()
            click.echo("Execution completed")
            
            # Cleanup
            await loader.cleanup()
            
        asyncio.run(run_plugin())
        
    except Exception as e:
        click.echo(f"Error executing plugin: {str(e)}", err=True)

# Register commands
cli.add_command(plugins)
cli.add_command(create)
cli.add_command(config)

if __name__ == '__main__':
    cli() 