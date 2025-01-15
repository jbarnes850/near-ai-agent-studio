"""
Plugin management commands
"""

import os
import shutil
import click
import yaml
import git
from typing import Optional
from pathlib import Path
from ..plugins import PluginLoader

@click.group()
def plugins():
    """Manage NEAR Swarm plugins"""
    pass

@plugins.command()
@click.argument('name')
@click.option('--template', default='plugin_template', help='Template to use')
def create(name: str, template: str):
    """Create a new plugin from template"""
    try:
        # Get template path
        template_path = os.path.join(
            os.path.dirname(__file__), 
            '../../templates', 
            template
        )
        
        # Create plugin directory
        plugin_path = os.path.join('plugins', name)
        if os.path.exists(plugin_path):
            click.echo(f"Plugin {name} already exists")
            return
        
        # Copy template
        shutil.copytree(template_path, plugin_path)
        
        # Update configuration
        config_path = os.path.join(plugin_path, 'agent.yaml')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            config['name'] = name
            config['role'] = f"{name}_role"
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f)
        
        click.echo(f"Created plugin: {name}")
        
    except Exception as e:
        click.echo(f"Error creating plugin: {str(e)}", err=True)

@plugins.command()
def list():
    """List available plugins"""
    try:
        # List core plugins
        core_path = os.path.join(
            os.path.dirname(__file__), 
            '../../plugins'
        )
        core_plugins = [
            d for d in os.listdir(core_path) 
            if os.path.isdir(os.path.join(core_path, d)) 
            and not d.startswith('__')
        ]
        
        # List custom plugins
        custom_path = 'plugins'
        custom_plugins = []
        if os.path.exists(custom_path):
            custom_plugins = [
                d for d in os.listdir(custom_path) 
                if os.path.isdir(os.path.join(custom_path, d))
            ]
        
        if core_plugins:
            click.echo("Core plugins:")
            for plugin in core_plugins:
                click.echo(f"  - {plugin}")
                
        if custom_plugins:
            click.echo("\nCustom plugins:")
            for plugin in custom_plugins:
                click.echo(f"  - {plugin}")
                
        if not core_plugins and not custom_plugins:
            click.echo("No plugins found")
            
    except Exception as e:
        click.echo(f"Error listing plugins: {str(e)}", err=True)

@plugins.command()
@click.argument('name')
def validate(name: str):
    """Validate a plugin configuration"""
    try:
        # Check core plugins
        core_path = os.path.join(
            os.path.dirname(__file__),
            '../../plugins',
            name
        )
        
        # Check custom plugins
        custom_path = os.path.join('plugins', name)
        
        config_path = None
        if os.path.exists(os.path.join(core_path, 'agent.yaml')):
            config_path = os.path.join(core_path, 'agent.yaml')
        elif os.path.exists(os.path.join(custom_path, 'agent.yaml')):
            config_path = os.path.join(custom_path, 'agent.yaml')
        
        if not config_path:
            click.echo(f"Plugin {name} not found")
            return
            
        # Validate configuration
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        required_fields = ['name', 'role', 'capabilities']
        for field in required_fields:
            if field not in config:
                click.echo(f"Missing required field: {field}")
                return
                
        click.echo(f"Plugin {name} configuration is valid")
        click.echo("\nConfiguration:")
        click.echo(yaml.dump(config, default_flow_style=False))
        
    except Exception as e:
        click.echo(f"Error validating plugin: {str(e)}", err=True)

@plugins.command()
@click.argument('source')
@click.option('--name', help='Plugin name (defaults to source name)')
def install(source: str, name: Optional[str] = None):
    """Install a plugin from a Git repository, local directory, or Python file"""
    try:
        plugins_dir = Path('plugins')
        plugins_dir.mkdir(exist_ok=True)
        
        source_path = Path(source)
        if source_path.exists():
            if source_path.is_file() and source_path.suffix == '.py':
                # Python file installation
                plugin_name = name or source_path.stem
                target_path = plugins_dir / plugin_name
                target_path.mkdir(exist_ok=True)
                
                # Copy the Python file
                shutil.copy2(source_path, target_path / 'plugin.py')
                
                # Create default agent.yaml if it doesn't exist
                config_path = target_path / 'agent.yaml'
                if not config_path.exists():
                    config = {
                        'name': plugin_name,
                        'role': f"{plugin_name}_role",
                        'capabilities': ['execute', 'evaluate']
                    }
                    with open(config_path, 'w') as f:
                        yaml.dump(config, f)
                        
                click.echo(f"Installed plugin from {source}")
                
            else:
                # Local directory installation
                plugin_name = name or source_path.name
                target_path = plugins_dir / plugin_name
                
                if target_path.exists():
                    click.echo(f"Plugin {plugin_name} is already installed")
                    return
                    
                shutil.copytree(source_path, target_path)
                click.echo(f"Installed plugin from {source}")
        else:
            # Git repository installation
            try:
                repo_name = name or source.split('/')[-1].replace('.git', '')
                target_path = plugins_dir / repo_name
                
                if target_path.exists():
                    click.echo(f"Plugin {repo_name} is already installed")
                    return
                
                git.Repo.clone_from(source, target_path)
                click.echo(f"Installed plugin from {source}")
                
            except git.exc.GitCommandError as e:
                click.echo(f"Error cloning repository: {str(e)}", err=True)
                return
        
        # Validate plugin structure
        config_path = target_path / 'agent.yaml'
        if not config_path.exists():
            click.echo("Warning: Plugin does not contain agent.yaml")
        else:
            # Validate configuration
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            required_fields = ['name', 'role', 'capabilities']
            for field in required_fields:
                if field not in config:
                    click.echo(f"Warning: Missing required field in agent.yaml: {field}")
        
        plugin_file = target_path / 'plugin.py'
        if not plugin_file.exists():
            click.echo("Warning: Plugin does not contain plugin.py")
            
    except Exception as e:
        click.echo(f"Error installing plugin: {str(e)}", err=True)

@plugins.command()
@click.argument('name')
def uninstall(name: str):
    """Uninstall a plugin"""
    try:
        plugin_path = Path('plugins') / name
        
        if not plugin_path.exists():
            click.echo(f"Plugin {name} is not installed")
            return
            
        shutil.rmtree(plugin_path)
        click.echo(f"Uninstalled plugin: {name}")
        
    except Exception as e:
        click.echo(f"Error uninstalling plugin: {str(e)}", err=True)

@plugins.command()
@click.argument('name')
def update(name: str):
    """Update an installed plugin"""
    try:
        plugin_path = Path('plugins') / name
        
        if not plugin_path.exists():
            click.echo(f"Plugin {name} is not installed")
            return
            
        # Check if it's a git repository
        try:
            repo = git.Repo(plugin_path)
            repo.remotes.origin.pull()
            click.echo(f"Updated plugin: {name}")
        except git.exc.InvalidGitRepositoryError:
            click.echo("Plugin was not installed from a git repository")
        except git.exc.GitCommandError as e:
            click.echo(f"Error updating plugin: {str(e)}", err=True)
            
    except Exception as e:
        click.echo(f"Error updating plugin: {str(e)}", err=True) 