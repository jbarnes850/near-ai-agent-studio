"""
Integration tests for NEAR Swarm Intelligence CLI commands
"""

import os
import json
import logging
import pytest
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock

from near_swarm.core.cli import run_command, init_command, create_agent_command
from near_swarm.core.near_integration import NEARConnection
from near_swarm.examples.simple_strategy import run_simple_strategy

logger = logging.getLogger(__name__)

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
    # Configure logging for better test output
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Mock JSON RPC responses
    async def json_rpc(method, params, timeout=2):
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
        return response_data
    with patch('sys.argv', ['near-swarm', 'run', '--example', 'simple_strategy']), \
         patch('near_api.signer.KeyPair') as mock_keypair_class, \
         patch('near_api.signer.Signer') as mock_signer_class, \
         patch('near_swarm.core.llm_provider.HyperbolicProvider.query', new_callable=AsyncMock) as mock_query, \
         patch('near_api.providers.JsonProvider', new_callable=AsyncMock) as mock_provider_class, \
         patch('requests.post') as mock_requests_post, \
         patch('near_api.account.Account') as mock_account_class:
        # Mock KeyPair setup with proper constructor behavior
        class MockKeyPair:
            def __init__(self, *args, **kwargs):
                self._secret_key = "mock_secret_key"
                print(f"MockKeyPair initialized with args: {args}, kwargs: {kwargs}")

            @property
            def secret_key(self):
                print("Accessing secret_key property")
                return f"ed25519:{self._secret_key}"

            def public_key(self):
                return "ed25519:mock_public_key"

        # Configure the KeyPair class mock to use our MockKeyPair class
        mock_keypair_class.side_effect = MockKeyPair
        # Create a mock instance for the signer to use
        mock_keypair_instance = MockKeyPair()
        mock_provider = MagicMock()
        mock_provider.rpc_addr = MagicMock(return_value="https://rpc.testnet.fastnear.com")
        mock_provider.json_rpc = MagicMock(side_effect=json_rpc)
        mock_provider_class.return_value = mock_provider

        # Mock requests.post responses
        def mock_post_response(*args, **kwargs):
            request_data = kwargs.get('json', {})
            response_data = {
                "jsonrpc": "2.0",
                "id": "dontcare",
                "result": {}
            }

            method = request_data.get('method', '')
            params = request_data.get('params', {})

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

        # Mock signer setup
        mock_signer = MagicMock()
        mock_signer.account_id = "test.testnet"
        mock_signer.public_key = MagicMock(return_value="ed25519:mock_key")
        mock_signer.key_pair = mock_keypair_instance
        mock_signer_class.return_value = mock_signer

        # Set up Account mock
        mock_account = AsyncMock()
        mock_account.state = {
            "amount": "100000000000000000000000000",
            "locked": "0",
            "code_hash": "11111111111111111111111111111111",
            "storage_usage": 182,
            "storage_paid_at": 0,
            "block_height": 1234567,
            "block_hash": "11111111111111111111111111111111"
        }

        # Set up provider mock with get_account method
        mock_provider = AsyncMock()
        mock_provider.get_account = MagicMock(return_value={"amount": "100000000000000000000000000"})
        mock_provider.get_access_key = MagicMock(return_value={
            "nonce": 0,
            "permission": "FullAccess",
            "block_height": 1234567,
            "block_hash": "11111111111111111111111111111111"
        })
        mock_provider.get_status = MagicMock(return_value={
            "sync_info": {
                "latest_block_hash": "mock_block_hash"
            }
        })

        # Set up the account with mocked provider
        mock_account._provider = mock_provider
        mock_account._account = {"amount": "100000000000000000000000000"}
        mock_account.send_money = AsyncMock(return_value={
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
        })
        # Configure the Account class mock to return our configured instance
        mock_account_class.return_value = mock_account

        # Create mock swarm agents
        with patch('near_swarm.core.swarm_agent.SwarmAgent') as mock_swarm_agent_class, \
             patch('near_swarm.core.near_integration.NEARConnection.__init__', return_value=None) as mock_near_init:
            # Create a single mock agent instance
            mock_agent = AsyncMock()
            mock_agent.swarm_config = MagicMock()
            mock_agent.swarm_config.role = "market_analyzer"
            mock_agent.swarm_config.min_confidence = 0.7

            # Set up evaluate_proposal to trigger LLM query
            async def mock_evaluate_proposal(proposal):
                logger.debug(f"Evaluating proposal in mock_evaluate_proposal: {proposal}")
                # Ensure proposal has required fields
                if not all(key in proposal for key in ['type', 'params', 'proposer']):
                    raise ValueError("Invalid proposal format")
                # Ensure we trigger the LLM query
                query_result = await mock_query()
                logger.debug(f"LLM query result: {query_result}")
                return json.loads(query_result)

            mock_agent.evaluate_proposal = mock_evaluate_proposal
            mock_agent.close = AsyncMock()
            mock_agent.process_message = AsyncMock(return_value="Test response")
            mock_agent.check_balance = AsyncMock(return_value="100 NEAR")
            mock_agent.__aenter__ = AsyncMock(return_value=mock_agent)
            mock_agent.__aexit__ = AsyncMock()

            # Return the same mock agent for all SwarmAgent instantiations
            mock_swarm_agent_class.side_effect = lambda *args, **kwargs: mock_agent

            # Set up LLM mock
            mock_query.return_value = '{"decision": true, "confidence": 0.85, "reasoning": "Test reasoning"}'

            # Create pre-configured NEARConnection
            with patch('requests.post') as mock_rpc_post, \
                 patch('near_swarm.core.near_integration.NEARConnection.__init__', return_value=None) as mock_near_init:
                # Mock RPC status check response
                mock_rpc_post.return_value.json.return_value = {
                    "result": {
                        "chain_id": "testnet",
                        "latest_protocol_version": 61,
                        "sync_info": {"latest_block_hash": "mock_hash"}
                    }
                }
                mock_rpc_post.return_value.raise_for_status = lambda: None

                # Create NEARConnection with proper initialization
                near_connection = NEARConnection.__new__(NEARConnection)
                # Set required attributes
                near_connection.network = "testnet"
                near_connection.account_id = "test.testnet"
                near_connection.private_key = "ed25519:mock_secret_key"
                near_connection.node_url = "https://rpc.testnet.fastnear.com"
                near_connection.provider = mock_provider
                near_connection.signer = mock_signer
                near_connection.account = mock_account

                # Mock send_tokens to use requests.post
                async def mock_send_tokens(receiver_id, amount):
                    mock_requests_post(
                        "https://rpc.testnet.fastnear.com",
                        json={
                            "jsonrpc": "2.0",
                            "id": "dontcare",
                            "method": "broadcast_tx_commit",
                            "params": {"tx_hash": "mock_tx_hash"}
                        }
                    )
                    return {
                        "transaction_outcome": {
                            "id": "mock_tx_id",
                            "block_hash": "mock_block_hash",
                            "outcome": {"status": {"SuccessValue": ""}}
                        }
                    }

                near_connection.send_tokens = mock_send_tokens

                # Run simple strategy with our pre-configured connection
                try:
                    await run_simple_strategy(near_connection=near_connection)
                except Exception as e:
                    logger.error(f"Strategy execution failed: {str(e)}")
                    raise

                # Verify LLM was queried
                assert mock_query.called, "LLM query was not called during strategy execution"
                assert mock_requests_post.called, "No NEAR RPC requests were made"
