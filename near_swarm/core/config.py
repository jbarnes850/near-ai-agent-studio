"""
Configuration management for NEAR Swarm Intelligence
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
from near_swarm.core.agent import AgentConfig

logger = logging.getLogger(__name__)

def load_config() -> AgentConfig:
    """Load configuration from environment variables."""
    load_dotenv()

    # Get required variables with validation
    account_id = os.getenv('NEAR_ACCOUNT_ID')
    if not account_id:
        logger.error("NEAR_ACCOUNT_ID environment variable is required")
        sys.exit(1)

    private_key = os.getenv('NEAR_PRIVATE_KEY')
    if not private_key:
        logger.error("NEAR_PRIVATE_KEY environment variable is required")
        sys.exit(1)

    llm_provider = os.getenv('LLM_PROVIDER')
    if not llm_provider:
        logger.error("LLM_PROVIDER environment variable is required")
        sys.exit(1)

    llm_api_key = os.getenv('LLM_API_KEY')
    if not llm_api_key:
        logger.error("LLM_API_KEY environment variable is required")
        sys.exit(1)

    # Create config with validated values
    return AgentConfig(
        network=os.getenv('NEAR_NETWORK', 'testnet'),
        account_id=account_id,  # Now we know this is not None
        private_key=private_key,  # Now we know this is not None
        llm_provider=llm_provider,  # Now we know this is not None
        llm_api_key=llm_api_key,  # Now we know this is not None
        llm_model=os.getenv('LLM_MODEL', 'meta-llama/Llama-3.3-70B-Instruct'),
        llm_temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
        llm_max_tokens=int(os.getenv('LLM_MAX_TOKENS', '2000')),
        api_url=os.getenv('LLM_API_URL')
    )
