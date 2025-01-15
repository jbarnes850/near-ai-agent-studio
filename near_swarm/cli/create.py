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
@click.option('--template', default='plugin_template', help='Template to use')
@click.option('--path', default='agents/custom', help='Where to create the agent')
def agent(name: str, template: str, path: str):
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
        
        # Copy template
        shutil.copytree(template_path, agent_path, dirs_exist_ok=True)
        
        # Update configuration
        config_path = os.path.join(agent_path, 'agent.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            config['name'] = name
            config['role'] = f"{name}_agent"
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
        
        click.echo(f"Created agent: {name}")
        
    except Exception as e:
        click.echo(f"Error creating agent: {str(e)}", err=True)

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