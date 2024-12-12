#!/bin/bash

# Exit on error
set -e

# Function to print section header
print_header() {
    echo ""
    echo "🔍 $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to check command
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ Required command not found: $1"
        exit 1
    fi
}

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "⚠️  No .env file found. Using default configuration."
fi

print_header "Verifying System Requirements"

# Check basic requirements
echo "Checking required commands..."
check_command python3
check_command pip
check_command near
check_command jq

# Check Python version
echo "Checking Python version..."
python3 -c "import sys; assert sys.version_info >= (3, 8), 'Python 3.8+ required'"
echo "✅ Python version OK"

print_header "Verifying Dependencies"

# Check core dependencies
echo "Checking core packages..."
pip list | grep -E "aiohttp|near-api-py|numpy"

print_header "Verifying NEAR Setup"

# Check NEAR connection
echo "Testing NEAR RPC connection..."
python3 -c "
import os
import asyncio
import logging
import requests
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.memory_manager import MemoryManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_setup():
    try:
        # Test RPC connection
        logger.info('Testing NEAR RPC connection...')
        response = requests.post(
            'https://rpc.testnet.fastnear.com',
            json={
                'jsonrpc': '2.0',
                'id': 'dontcare',
                'method': 'status',
                'params': []
            }
        )
        response.raise_for_status()
        status = response.json()
        logger.info(f'✅ NEAR RPC connection successful - Chain ID: {status.get(\"result\", {}).get(\"chain_id\")}')

        # Test market data
        logger.info('Testing market data integration...')
        market = MarketDataManager()
        logger.info('✅ Market data initialized')

        # Test memory system
        logger.info('Testing memory system...')
        memory = MemoryManager()
        logger.info('✅ Memory system initialized')

        # Check NEAR credentials
        if not os.getenv('NEAR_ACCOUNT_ID') or not os.getenv('NEAR_PRIVATE_KEY'):
            logger.warning('⚠️  NEAR credentials not found - please set NEAR_ACCOUNT_ID and NEAR_PRIVATE_KEY in .env')
        else:
            logger.info(f'✅ NEAR credentials found for account: {os.getenv(\"NEAR_ACCOUNT_ID\")}')

    except Exception as e:
        logger.error(f'Error during setup: {str(e)}')
        raise

asyncio.run(test_setup())
"

print_header "Verifying LLM Integration"

# Check LLM configuration
if [ -n "$LLM_PROVIDER" ] && [ -n "$LLM_API_KEY" ]; then
    echo "Testing LLM configuration..."
    python3 -c "
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

provider = os.getenv('LLM_PROVIDER', '').lower()
api_key = os.getenv('LLM_API_KEY')

if provider == 'hyperbolic':
    import openai
    openai.api_key = api_key
    openai.api_base = os.getenv('HYPERBOLIC_API_URL', 'https://api.hyperbolic.ai/v1')
    logger.info('✅ Hyperbolic configuration found')
elif provider == 'openai':
    import openai
    openai.api_key = api_key
    logger.info('✅ OpenAI configuration found')
elif provider == 'anthropic':
    import anthropic
    client = anthropic.Client(api_key=api_key)
    logger.info('✅ Anthropic configuration found')
elif provider == 'local':
    if not os.system('which ollama >/dev/null 2>&1'):
        logger.info('✅ Local LLM (Ollama) found')
    else:
        logger.warning('⚠️  Ollama not found for local LLM')
else:
    logger.warning('⚠️  No valid LLM provider configured')
"
else
    echo "⚠️  LLM configuration not found - skipping LLM verification"
fi

print_header "Verification Summary"

echo "Core Components:"
echo "✅ Python environment"
echo "✅ Dependencies"
echo "✅ NEAR integration"
echo "✅ Market data"
echo "✅ Memory system"
echo ""
echo "Optional Components:"
[ -n "$LLM_PROVIDER" ] && echo "✅ LLM integration" || echo "⚠️  LLM not configured"
[ -n "$NEAR_ACCOUNT_ID" ] && echo "✅ NEAR wallet" || echo "⚠️  NEAR wallet not configured"
echo ""
echo "Next Steps:"
echo "1. If any warnings appeared, check the relevant configuration"
echo "2. Run './scripts/near-swarm init' to create your first strategy"
echo "3. Review the documentation in docs/ for more information" 