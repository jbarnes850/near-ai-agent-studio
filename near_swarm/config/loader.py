"""
Configuration loader for NEAR Swarm Intelligence
Handles loading and merging configurations from multiple sources
"""

import os
import re
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from .schema import AgentConfig, LLMSettings, PluginSettings

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Unified configuration management"""
    
    DEFAULT_CONFIG_PATHS = [
        "near_swarm.yaml",
        "~/.near_swarm/config.yaml",
        "/etc/near_swarm/config.yaml"
    ]
    
    ENV_PREFIX = "NEAR_SWARM_"
    VAR_PATTERN = re.compile(r'\${([^}]+)}')
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._loaded = False
        self._env_vars = {}
    
    def load_defaults(self) -> None:
        """Load default configuration"""
        self._config.update({
            "environment": "development",
            "log_level": "INFO",
            "llm": {
                "temperature": 0.7,
                "max_tokens": 1000
            }
        })
    
    def load_config_file(self, path: Optional[str] = None) -> None:
        """Load configuration from file"""
        # Try all default paths if none specified
        paths = [path] if path else self.DEFAULT_CONFIG_PATHS
        
        for config_path in paths:
            try:
                path = os.path.expanduser(config_path)
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        config = yaml.safe_load(f)
                        if config:
                            # Substitute variables before updating config
                            config = self._substitute_variables(config)
                            self._config.update(config)
                            logger.info(f"Loaded configuration from {path}")
                            break
            except Exception as e:
                logger.warning(f"Error loading config from {path}: {str(e)}")
    
    def load_env(self) -> None:
        """Load configuration from environment variables"""
        # Store environment variables for substitution
        self._env_vars = {
            key[len(self.ENV_PREFIX):].lower(): value
            for key, value in os.environ.items()
            if key.startswith(self.ENV_PREFIX)
        }
        
        env_config = {}
        for key, value in self._env_vars.items():
            # Convert NEAR_SWARM_LLM_TEMPERATURE to llm.temperature
            parts = key.split('_')
            
            # Build nested dictionary
            current = env_config
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        
        # Update config with environment variables
        self._deep_update(self._config, env_config)
    
    def load_cli_args(self, args: Dict[str, Any]) -> None:
        """Load configuration from CLI arguments"""
        if args:
            # Substitute variables in CLI args
            args = self._substitute_variables(args)
            self._deep_update(self._config, args)
    
    def get_config(self) -> AgentConfig:
        """Get final configuration"""
        if not self._loaded:
            self.load_defaults()
            self.load_config_file()
            self.load_env()
            self._loaded = True
        
        # Convert to Pydantic model for validation
        return AgentConfig(**self._config)
    
    def _substitute_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively substitute variables in configuration"""
        if isinstance(config, dict):
            return {
                key: self._substitute_variables(value)
                for key, value in config.items()
            }
        elif isinstance(config, list):
            return [
                self._substitute_variables(item)
                for item in config
            ]
        elif isinstance(config, str):
            return self._substitute_value(config)
        return config
    
    def _substitute_value(self, value: str) -> str:
        """Substitute variables in a string value"""
        def replace(match):
            var_name = match.group(1).lower()
            # Check environment variables first
            if var_name in self._env_vars:
                return self._env_vars[var_name]
            # Then check config values
            try:
                parts = var_name.split('.')
                current = self._config
                for part in parts:
                    current = current[part]
                return str(current)
            except (KeyError, TypeError):
                logger.warning(f"Variable ${{{var_name}}} not found")
                return match.group(0)
        
        return self.VAR_PATTERN.sub(replace, value)
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively update nested dictionaries"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value 