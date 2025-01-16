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
from ..core.market_data import MarketDataManager
import os
import yaml
import time

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

@cli.command()
@click.option('--tutorial', type=str, help='Start a guided tutorial (e.g., create-first-agent)')
def chat(tutorial: str = None):
    """Start interactive chat assistant"""
    from .chat import start_chat
    start_chat(tutorial_mode=tutorial)

@cli.command()
@click.argument('agents', nargs=-1, required=True)
@click.option('--timeout', default=60, help='Timeout in seconds')
def run(agents, timeout):
    """Run multiple agents together"""
    try:
        if not agents:
            click.echo("Please specify at least one agent to run")
            return
            
        click.echo(f"Starting agents: {', '.join(agents)}")
        
        async def run_agents():
            loader = PluginLoader()
            market_data = MarketDataManager()
            loaded_agents = []
            
            # Load and validate each agent
            for agent in agents:
                config_file = f"near_swarm/agents/{agent}/agent.yaml"
                if not os.path.exists(config_file):
                    # Try alternate locations
                    alternate_paths = [
                        f"agents/{agent}/agent.yaml",
                        f"near_swarm/examples/{agent}.yaml",
                        f"plugins/{agent}/agent.yaml"
                    ]
                    found = False
                    for path in alternate_paths:
                        if os.path.exists(path):
                            config_file = path
                            found = True
                            break
                    
                    if not found:
                        click.echo(f"❌ Agent not found: {agent}")
                        click.echo("Looked in:")
                        click.echo(f"- near_swarm/agents/{agent}/agent.yaml")
                        for path in alternate_paths:
                            click.echo(f"- {path}")
                        return
                    
                # Load config to verify it exists
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if not config:
                        click.echo(f"❌ Invalid configuration for agent: {agent}")
                        return
                
                # Load agent plugin
                plugin = await loader.load_plugin(agent)
                if not plugin:
                    click.echo(f"❌ Failed to load agent: {agent}")
                    return
                    
                loaded_agents.append(plugin)
                click.echo(f"✅ Loaded agent: {agent} ({config.get('role', 'unknown role')})")
            
            click.echo("\n🤖 Agents are now running and collaborating:")
            
            try:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    # Get current market data
                    near_data = await market_data.get_token_price('near')
                    near_price = near_data['price']
                    click.echo(f"\n📊 Current NEAR Price: ${near_price:.2f}")
                    
                    # Price monitor agent analyzes market data
                    if loaded_agents[0].role == "market_analyzer":
                        click.echo("\n🔍 Price Monitor thinking...")
                        click.echo("Sending request to agent for market analysis...")
                        
                        analysis = await loaded_agents[0].evaluate({
                            "price": near_price,
                            "timestamp": time.time(),
                            "request": """Analyze the current NEAR price and market conditions:
                            1. Evaluate recent price movements and volatility
                            2. Identify any significant trends or patterns
                            3. Consider market sentiment and external factors
                            4. Provide a clear recommendation based on your analysis
                            
                            Format your response with clear observations, reasoning, and conclusions."""
                        })
                        
                        # Show the agent's reasoning process
                        click.echo(f"\n📝 Analysis from agent:")
                        click.echo(f"  • Observation: {analysis.get('observation', 'Analyzing price data...')}")
                        click.echo(f"  • Reasoning: {analysis.get('reasoning', 'Evaluating market conditions...')}")
                        click.echo(f"  • Conclusion: {analysis.get('conclusion', 'Forming market opinion...')}")
                        click.echo(f"  • Confidence: {analysis.get('confidence', 0):.0%}")
                        
                        # Decision maker agent evaluates the analysis
                        if len(loaded_agents) > 1 and loaded_agents[1].role == "strategy_optimizer":
                            click.echo("\n🤔 Decision Maker consulting agent...")
                            click.echo("Sending market analysis to agent for strategic evaluation...")
                            
                            decision = await loaded_agents[1].evaluate({
                                "market_analysis": analysis,
                                "current_price": near_price,
                                "request": """Based on the price monitor's analysis, evaluate potential trading strategies:
                                1. Review the market analysis and current price
                                2. Consider risk levels and market conditions
                                3. Evaluate potential trading opportunities
                                4. Recommend specific actions with confidence levels
                                
                                Format your response with clear context, strategy, rationale, and specific actions."""
                            })
                            
                            # Show the decision-making process
                            click.echo(f"\n📋 Strategic Decision from agent analysis:")
                            click.echo(f"  • Context: {decision.get('context', 'Reviewing market analysis...')}")
                            click.echo(f"  • Strategy: {decision.get('strategy', 'Formulating approach...')}")
                            click.echo(f"  • Rationale: {decision.get('rationale', 'Evaluating options...')}")
                            click.echo(f"  • Action: {decision.get('action', 'Determining next steps...')}")
                            click.echo(f"  • Confidence: {decision.get('confidence', 0):.0%}")
                            
                            if decision.get("confidence", 0) > 0.8:
                                click.echo(f"\n✨ High Confidence Decision:")
                                click.echo(f"  {decision.get('action', 'No action needed')}")
                                
                                # Execute the decision if confidence is high
                                execution_result = await loaded_agents[1].execute({
                                    'type': 'evaluate_market',
                                    'data': {
                                        'market_analysis': analysis,
                                        'current_price': near_price
                                    }
                                })
                                
                                # Show transaction details if available
                                if 'transaction' in execution_result:
                                    tx = execution_result['transaction']
                                    click.echo(f"\n🔄 Executing Trade:")
                                    click.echo(f"  • Amount: {tx['amount']} NEAR")
                                    click.echo(f"  • Status: {tx['status']}")
                                    click.echo(f"  • View Transaction: {tx['explorer_url']}")
                    
                    click.echo("\n⏳ Waiting 60 seconds before next analysis...")
                    await asyncio.sleep(60)
                    
            except KeyboardInterrupt:
                click.echo("\n👋 Stopping agents gracefully...")
            finally:
                # Cleanup
                for agent in loaded_agents:
                    await agent.cleanup()
                await loader.cleanup()
                await market_data.close()
                
        asyncio.run(run_agents())
        
    except Exception as e:
        click.echo(f"❌ Error running agents: {str(e)}")

# Register commands
cli.add_command(plugins)
cli.add_command(create)
cli.add_command(config)
cli.add_command(run)

if __name__ == '__main__':
    cli() 