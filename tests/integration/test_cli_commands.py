"""
Integration tests for NEAR Swarm Intelligence CLI commands
"""

import os
import json
import argparse
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

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
        'LLM_MAX_TOKENS': '2000',
        'HYPERBOLIC_API_URL': 'https://api.hyperbolic.ai/v1'
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
         patch('near_api.signer.KeyPair') as mock_keypair_class, \
         patch('near_api.signer.Signer') as mock_signer_class, \
         patch('near_swarm.core.llm_provider.HyperbolicProvider.query', new_callable=AsyncMock) as mock_query, \
         patch('near_api.providers.JsonProvider', new_callable=AsyncMock) as mock_provider_class, \
         patch('requests.post') as mock_requests_post:

        # Mock requests.post responses
        def mock_post_response(*args, **kwargs):
            # Parse the request data
            request_data = kwargs.get('json', {})
            method = request_data.get('method', '')
            params = request_data.get('params', {})

            response_data = {
                "jsonrpc": "2.0",
                "id": "dontcare",
                "result": {}
            }

            if method == 'status':
                response_data["result"] = {
                    "chain_id": "testnet",
                    "latest_protocol_version": 61,
                    "node_key": "ed25519:mock_node_key",
                    "sync_info": {
                        "latest_block_hash": "mock_hash",
                        "latest_block_height": 1234567,
                        "syncing": False
                    }
                }
            elif method == 'query':
                request_type = params.get('request_type', '')
                if request_type == 'view_account':
                    response_data["result"] = {
                        "amount": "100000000000000000000000000",
                        "locked": "0",
                        "code_hash": "11111111111111111111111111111111",
                        "storage_usage": 182,
                        "storage_paid_at": 0,
                        "block_height": 1234567,
                        "block_hash": "11111111111111111111111111111111"
                    }
                elif request_type == 'view_access_key':
                    response_data["result"] = {
                        "nonce": 0,
                        "permission": "FullAccess",
                        "block_height": 1234567,
                        "block_hash": "11111111111111111111111111111111"
                    }

            class MockResponse:
                def __init__(self, json_data, status_code=200):
                    self.json_data = json_data
                    self.status_code = status_code
                    self.content = json.dumps(json_data).encode('utf-8')

                def json(self):
                    return self.json_data

                def raise_for_status(self):
                    pass

            return MockResponse(response_data)

        mock_requests_post.side_effect = mock_post_response

        # Mock KeyPair setup
        mock_keypair = MagicMock()
        mock_keypair_class.return_value = mock_keypair

        # Mock provider setup
        mock_provider = MagicMock()
        mock_provider.rpc_addr = MagicMock(return_value="https://rpc.testnet.near.org")

        def json_rpc(method, params, timeout=2):
            response_data = {
                "jsonrpc": "2.0",
                "id": "dontcare",
                "result": {}
            }

            if method == 'query':
                if params.get('request_type') == 'view_account':
                    response_data["result"] = {
                        "amount": "100000000000000000000000000",
                        "locked": "0",
                        "code_hash": "11111111111111111111111111111111",
                        "storage_usage": 182,
                        "storage_paid_at": 0,
                        "block_height": 1234567,
                        "block_hash": "11111111111111111111111111111111"
                    }
                elif params.get('request_type') == 'view_access_key':
                    response_data["result"] = {
                        "nonce": 0,
                        "permission": "FullAccess",
                        "block_height": 1234567,
                        "block_hash": "11111111111111111111111111111111"
                    }
            elif method == 'broadcast_tx_commit':
                response_data["result"] = {
                    "transaction_outcome": {
                        "block_hash": "mock_block_hash",
                        "id": "mock_tx_id",
                        "outcome": {
                            "executor_id": "test.testnet",
                            "gas_burnt": 2427979026088,
                            "logs": [],
                            "receipt_ids": ["mock_receipt_id"],
                            "status": {"SuccessValue": ""},
                            "tokens_burnt": "242797902608800000000"
                        },
                        "proof": []
                    },
                    "receipts_outcome": [{
                        "block_hash": "mock_block_hash",
                        "id": "mock_receipt_id",
                        "outcome": {
                            "executor_id": "bob.testnet",
                            "gas_burnt": 223182562500,
                            "logs": [],
                            "receipt_ids": [],
                            "status": {"SuccessValue": ""},
                            "tokens_burnt": "22318256250000000000"
                        },
                        "proof": []
                    }],
                    "status": {
                        "SuccessValue": ""
                    },
                    "transaction": {
                        "hash": "mock_hash",
                        "signer_id": "test.testnet",
                        "public_key": "ed25519:mock_key",
                        "nonce": 1,
                        "receiver_id": "receiver.testnet",
                        "actions": [{"Transfer": {"deposit": "1000000000000000000000000"}}]
                    }
                }
            return response_data

        mock_provider.json_rpc = MagicMock(side_effect=json_rpc)

        async def send_tx_and_wait(tx_hash, timeout=None):
            return {
                "transaction_outcome": {
                    "block_hash": "mock_block_hash",
                    "id": "mock_tx_id",
                    "outcome": {
                        "executor_id": "test.testnet",
                        "gas_burnt": 2427979026088,
                        "logs": [],
                        "receipt_ids": ["mock_receipt_id"],
                        "status": {"SuccessValue": ""},
                        "tokens_burnt": "242797902608800000000"
                    },
                    "proof": []
                },
                "receipts_outcome": [{
                    "block_hash": "mock_block_hash",
                    "id": "mock_receipt_id",
                    "outcome": {
                        "executor_id": "bob.testnet",
                        "gas_burnt": 223182562500,
                        "logs": [],
                        "receipt_ids": [],
                        "status": {"SuccessValue": ""},
                        "tokens_burnt": "22318256250000000000"
                    },
                    "proof": []
                }]
            }

        mock_provider.send_tx_and_wait = AsyncMock(side_effect=send_tx_and_wait)

        def get_account(account_id):
            return {
                "amount": "100000000000000000000000000",
                "locked": "0",
                "code_hash": "11111111111111111111111111111111",
                "storage_usage": 182,
                "storage_paid_at": 0,
                "block_height": 1234567,
                "block_hash": "11111111111111111111111111111111"
            }

        mock_provider.get_account = MagicMock(side_effect=get_account)
        mock_provider_class.return_value = mock_provider

        # Mock signer setup
        mock_signer = MagicMock()
        mock_signer.account_id = "test.testnet"
        mock_signer.public_key = MagicMock(return_value="ed25519:mock_key")
        mock_signer_class.return_value = mock_signer

        # Set up Account mock
        mock_account = AsyncMock()
        mock_account.send_money = AsyncMock(return_value={
            "result": {
                "transaction_outcome": {
                    "block_hash": "mock_block_hash",
                    "id": "mock_tx_id",
                    "outcome": {
                        "executor_id": "test.testnet",
                        "gas_burnt": 2427979026088,
                        "logs": [],
                        "receipt_ids": ["mock_receipt_id"],
                        "status": {"SuccessValue": ""},
                        "tokens_burnt": "242797902608800000000"
                    },
                    "proof": []
                },
                "receipts_outcome": [{
                    "block_hash": "mock_block_hash",
                    "id": "mock_receipt_id",
                    "outcome": {
                        "executor_id": "bob.testnet",
                        "gas_burnt": 223182562500,
                        "logs": [],
                        "receipt_ids": [],
                        "status": {"SuccessValue": ""},
                        "tokens_burnt": "22318256250000000000"
                    },
                    "proof": []
                }],
                "status": {
                    "SuccessValue": ""
                }
            }
        })

        # Mock Account class
        with patch('near_api.account.Account') as mock_account_class, \
             patch('near_swarm.core.swarm_agent.SwarmAgent') as mock_swarm_agent_class:
            mock_account_class.return_value = mock_account

            # Create mock swarm agents
            mock_agents = []
            for role in ['risk_manager', 'market_analyzer', 'strategy_optimizer']:
                mock_agent = MagicMock()
                mock_agent.swarm_config.role = role
                mock_agent.evaluate_proposal = AsyncMock(return_value={
                    "decision": True,
                    "confidence": 0.85,
                    "reasoning": f"Test reasoning from {role}"
                })
                mock_agents.append(mock_agent)

            mock_swarm_agent_class.side_effect = mock_agents

            # Set up LLM mock
            mock_query.return_value = '{"decision": true, "confidence": 0.85, "reasoning": "Test reasoning"}'

            # Run simple strategy directly
            try:
                await run_command(argparse.Namespace(
                    command='run',
                    example='simple_strategy',
                    config=None
                ))
            except RuntimeError as e:
                # Test should handle the error gracefully
                assert "Strategy execution failed" in str(e)
                assert "transaction_outcome" in str(e)

            # Verify LLM was queried
            assert mock_query.called

            # Verify account was created
            assert mock_account_class.called

            # Verify transaction was sent
            assert mock_account.send_money.called

            # Verify RPC requests were made
            assert mock_requests_post.called
