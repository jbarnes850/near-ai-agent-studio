"""
Configuration management for NEAR Swarm Intelligence
"""

import os
import sys
import logging
from dotenv import load_dotenv
from near_swarm.core.agent import AgentConfig

logger = logging.getLogger(__name__)

def load_config() -> AgentConfig:
    """Load configuration from environment variables."""
    load_dotenv()

    required_vars = [
        'NEAR_NETWORK',
        'NEAR_ACCOUNT_ID',
        'NEAR_PRIVATE_KEY',
        'LLM_PROVIDER',
        'LLM_API_KEY'
    ]

    # Check for required environment variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)

    return AgentConfig(
        network=os.getenv('NEAR_NETWORK', 'testnet'),
        account_id=os.getenv('NEAR_ACCOUNT_ID'),
        private_key=os.getenv('NEAR_PRIVATE_KEY'),
        llm_provider=os.getenv('LLM_PROVIDER'),
        llm_api_key=os.getenv('LLM_API_KEY'),
        llm_model=os.getenv('LLM_MODEL', 'meta-llama/Llama-3.3-70B-Instruct'),
        llm_temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
        llm_max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2000'))
    )
