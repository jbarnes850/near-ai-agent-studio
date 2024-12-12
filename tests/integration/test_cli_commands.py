"""
Integration tests for NEAR Swarm Intelligence CLI commands
"""

import os
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
import argparse

from near_swarm.core.cli import main, init_command, run_command, create_agent_command
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig

@pytest.fixture
def env_setup():
    """Set up test environment variables."""
    os.environ.update({
        'NEAR_NETWORK': 'testnet',
        'NEAR_ACCOUNT_ID': 'test.testnet',
        'NEAR_PRIVATE_KEY': 'ed25519:3D4YudUQRE39Lc4JHghuB5WM8kbgDDa34mnrEP5DdTApVH81af3e7MvFrog1CMNn67PCQmNkxQLPoacMuZydf2hL',
        'LLM_PROVIDER': 'hyperbolic',
        'LLM_API_KEY': 'test_key',
        'LLM_MODEL': 'meta-llama/Llama-3.3-70B-Instruct',
        'LLM_TEMPERATURE': '0.7',
        'LLM_MAX_TOKENS': '2000'
    })
    yield
    for key in os.environ:
        if key.startswith(('NEAR_', 'LLM_')):
            del os.environ[key]

@pytest.mark.asyncio
async def test_init_command(env_setup, tmp_path):
    """Test strategy initialization."""
    with patch('sys.argv', ['near-swarm', 'init', 'test_strategy']), \
         patch('near_swarm.core.cli.Path.cwd', return_value=tmp_path):

        # Run init command directly without asyncio.run
        await init_command(argparse.Namespace(command='init', name='test_strategy'))

        # Verify files were created
        strategy_dir = tmp_path / 'test_strategy'
        assert strategy_dir.exists()
        assert (strategy_dir / 'config.json').exists()
        assert (strategy_dir / 'test_strategy.py').exists()

        # Verify config content
        with open(strategy_dir / 'config.json') as f:
            config = json.load(f)
            assert config['name'] == 'test_strategy'
            assert 'market_analyzer' in config['roles']
            assert config['min_confidence'] == 0.7

@pytest.mark.asyncio
async def test_create_agent_command(env_setup):
    """Test agent creation."""
    with patch('sys.argv', ['near-swarm', 'create-agent', 'market_analyzer']), \
         patch('near_swarm.core.near_integration.NEARConnection') as mock_connection:

        mock_connection.return_value.check_account = AsyncMock(return_value=True)

        # Run create-agent command directly
        await create_agent_command(argparse.Namespace(
            command='create-agent',
            role='market_analyzer',
            min_confidence=0.7,
            min_votes=2
        ))

@pytest.mark.asyncio
async def test_run_simple_strategy(env_setup):
    """Test running simple strategy example."""
    with patch('sys.argv', ['near-swarm', 'run', '--example', 'simple_strategy']), \
         patch('near_swarm.core.near_integration.NEARConnection') as mock_connection, \
         patch('near_swarm.core.llm_provider.HyperbolicProvider.query', new_callable=AsyncMock) as mock_query:

        mock_connection.return_value.check_account = AsyncMock(return_value=True)
        mock_query.return_value = '{"decision": true, "confidence": 0.85, "reasoning": "Test reasoning"}'

        # Run simple strategy directly
        await run_command(argparse.Namespace(
            command='run',
            example='simple_strategy',
            config=None
        ))

        # Verify LLM was queried
        assert mock_query.called

        # Verify connection was checked
        assert mock_connection.return_value.check_account.called

@pytest.mark.asyncio
async def test_run_custom_strategy(env_setup, tmp_path):
    """Test running a custom strategy."""
    # First create a test strategy
    strategy_dir = tmp_path / 'test_strategy'
    strategy_dir.mkdir()

    config = {
        "name": "test_strategy",
        "roles": ["market_analyzer", "risk_manager"],
        "min_confidence": 0.7,
        "min_votes": 2
    }

    with open(strategy_dir / 'config.json', 'w') as f:
        json.dump(config, f)

    strategy_code = """
import asyncio
from near_swarm.core.agent import AgentConfig
from near_swarm.core.swarm_agent import SwarmAgent, SwarmConfig
from near_swarm.core.config import load_config
from near_swarm.core.near_integration import NEARConnection

async def run_strategy():
    agent = None
    try:
        # Initialize configuration and NEAR connection
        config = load_config()
        near = NEARConnection(
            network=config.network,
            account_id=config.account_id,
            private_key=config.private_key
        )
        await near.check_account(config.account_id)

        # Initialize agent
        agent = SwarmAgent(
            config,
            SwarmConfig(role="market_analyzer", min_confidence=0.7)
        )

        # Add strategy logic here
        pass

    finally:
        if agent:
            await agent.close()

if __name__ == "__main__":
    asyncio.run(run_strategy())
"""

    with open(strategy_dir / 'test_strategy.py', 'w') as f:
        f.write(strategy_code)

    with patch('sys.argv', ['near-swarm', 'run', '--config', str(strategy_dir / 'config.json')]), \
         patch('near_swarm.core.near_integration.NEARConnection') as mock_connection:

        mock_connection.return_value.check_account = AsyncMock(return_value=True)

        # Run custom strategy directly
        await run_command(argparse.Namespace(
            command='run',
            example=None,
            config=str(strategy_dir / 'config.json')
        ))

        # Verify connection was checked
        assert mock_connection.return_value.check_account.called
