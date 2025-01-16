"""
CLI commands for creating new components
"""

import os
import shutil
import click
import yaml
from typing import Optional

@click.group()
def create():
    """Create new components"""
    pass

@create.command()
@click.argument('name')
@click.option('--role', default=None, help='Agent role (market_analyzer/strategy_optimizer)')
@click.option('--template', default='plugin_template', help='Template to use')
@click.option('--path', default='near_swarm/agents', help='Where to create the agent')
def agent(name: str, role: Optional[str], template: str, path: str):
    """Create a new agent"""
    try:
        # Get template path
        template_path = os.path.join(
            os.path.dirname(__file__), 
            '../templates', 
            template
        )
        
        # Create agent directory
        agent_path = os.path.join(path, name)
        if os.path.exists(agent_path):
            click.echo(f"Agent {name} already exists")
            return
            
        # Create directories
        os.makedirs(agent_path, exist_ok=True)
        
        # Copy template files individually
        for item in os.listdir(template_path):
            source = os.path.join(template_path, item)
            dest = os.path.join(agent_path, item)
            
            if os.path.isfile(source):
                shutil.copy2(source, dest)
            elif os.path.isdir(source):
                shutil.copytree(source, dest)
        
        # Update configuration
        config_path = os.path.join(agent_path, 'agent.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            config['name'] = name
            
            # Set role-specific configuration
            if role:
                config['role'] = role
                if role == 'market_analyzer':
                    config['capabilities'] = [
                        'market_analysis',
                        'price_monitoring',
                        'risk_assessment'
                    ]
                    config['system_prompt'] = """You are a market analysis agent monitoring NEAR token prices.
Your role is to analyze market conditions, identify trends, and assess risks.
Consider price movements, trading volume, market sentiment, and external factors.
Always provide clear reasoning and confidence levels for your analysis."""
                    
                elif role == 'strategy_optimizer':
                    config['capabilities'] = [
                        'strategy_optimization',
                        'decision_making',
                        'risk_management'
                    ]
                    config['system_prompt'] = """You are a decision-making agent evaluating market opportunities.
Your role is to analyze market conditions and recommend optimal trading strategies.
Consider risk factors, potential returns, and market analysis from other agents.
Always provide clear reasoning and confidence levels for your decisions."""
            
            # Update plugin.py
            plugin_path = os.path.join(agent_path, 'plugin.py')
            if os.path.exists(plugin_path):
                with open(plugin_path, 'r') as f:
                    plugin_code = f.read()
                
                # Update class name
                plugin_code = plugin_code.replace('CustomAgentPlugin', f"{name.replace('-', '_').title()}Plugin")
                
                # Update registration
                plugin_code = plugin_code.replace('register_plugin("custom_agent"', f'register_plugin("{name}"')
                
                with open(plugin_path, 'w') as f:
                    f.write(plugin_code)
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
        
        click.echo(f"✅ Created agent: {name}")
        
    except Exception as e:
        click.echo(f"❌ Error creating agent: {str(e)}", err=True)

@create.command()
@click.argument('name')
@click.option('--template', default='strategy_template', help='Template to use')
@click.option('--path', default='strategies', help='Where to create the strategy')
def strategy(name: str, template: str, path: str):
    """Create a new strategy"""
    try:
        # Get template path
        template_path = os.path.join(
            os.path.dirname(__file__), 
            '../templates', 
            template
        )
        
        # Create strategy directory
        strategy_path = os.path.join(path, name)
        if os.path.exists(strategy_path):
            click.echo(f"Strategy {name} already exists")
            return
            
        # Create directories
        os.makedirs(strategy_path, exist_ok=True)
        
        # Copy template
        shutil.copytree(template_path, strategy_path, dirs_exist_ok=True)
        
        # Update configuration
        config_path = os.path.join(strategy_path, 'strategy.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            config['name'] = name
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
        
        click.echo(f"Created strategy: {name}")
        
    except Exception as e:
        click.echo(f"Error creating strategy: {str(e)}", err=True)

@create.command()
@click.argument('name')
@click.option('--template', default='project_template', help='Template to use')
def project(name: str, template: str):
    """Create a new project"""
    try:
        # Get template path
        template_path = os.path.join(
            os.path.dirname(__file__), 
            '../templates', 
            template
        )
        
        # Create project directory
        if os.path.exists(name):
            click.echo(f"Directory {name} already exists")
            return
            
        # Copy template
        shutil.copytree(template_path, name)
        
        # Update configuration
        config_path = os.path.join(name, 'near_swarm.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            config['name'] = name
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
        
        # Create required directories
        os.makedirs(os.path.join(name, 'agents', 'custom'), exist_ok=True)
        os.makedirs(os.path.join(name, 'strategies'), exist_ok=True)
        os.makedirs(os.path.join(name, 'plugins'), exist_ok=True)
        
        click.echo(f"Created project: {name}")
        click.echo("\nNext steps:")
        click.echo("1. cd " + name)
        click.echo("2. python -m venv venv")
        click.echo("3. source venv/bin/activate  # or .\\venv\\Scripts\\activate on Windows")
        click.echo("4. pip install -r requirements.txt")
        click.echo("5. near-swarm init")
        
    except Exception as e:
        click.echo(f"Error creating project: {str(e)}", err=True) 