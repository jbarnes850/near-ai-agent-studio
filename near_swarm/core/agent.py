"""
Base Agent Implementation
Provides core functionality for NEAR Protocol agents.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from near_swarm.core.near_integration import NEARConnection

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for NEAR agents."""
    network: str = "testnet"
    account_id: str = ""
    private_key: str = ""
    llm_provider: str = "hyperbolic"
    llm_api_key: str = ""
    llm_model: str = "deepseek-ai/DeepSeek-V3"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    api_url: Optional[str] = None
    system_prompt: Optional[str] = None

    def validate(self) -> None:
        """Validate configuration."""
        if not self.network in ["mainnet", "testnet"]:
            raise ValueError("Network must be mainnet or testnet")
        if not self.account_id:
            raise ValueError("Account ID is required")
        if not self.private_key:
            raise ValueError("Private key is required")
        if not self.llm_api_key:
            raise ValueError("LLM API key is required")

class Agent:
    """Base NEAR Protocol agent."""

    def __init__(self, config: AgentConfig):
        """Initialize agent with configuration."""
        self.config = config
        self.config.validate()
        
        # Initialize NEAR connection (always using FastNEAR for testnet)
        self.near = NEARConnection(
            network="testnet",  # Force testnet
            account_id=config.account_id,
            private_key=config.private_key
        )
        
        self._is_running = False
        logger.info(f"Initialized agent: {config.account_id}")

    async def start(self):
        """Start the agent."""
        if not self._is_running:
            # Verify account exists
            if not await self.near.check_account(self.config.account_id):
                raise RuntimeError(f"Account {self.config.account_id} not found")
                
            self._is_running = True
            logger.info(f"Started agent: {self.config.account_id}")

    async def stop(self):
        """Stop the agent."""
        if self._is_running:
            self._is_running = False
            logger.info(f"Stopped agent: {self.config.account_id}")

    def is_running(self) -> bool:
        """Check if agent is running."""
        return self._is_running

    async def send_tokens(
        self,
        recipient_id: str,
        amount: str,  # Amount in NEAR
        token_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send tokens to another account.
        
        Args:
            recipient_id: Recipient account ID
            amount: Amount to send in NEAR (will be converted to yoctoNEAR)
            token_id: Optional token contract ID for NEP-141 tokens
            
        Returns:
            Transaction outcome
        """
        if not self._is_running:
            raise RuntimeError("Agent must be running to send tokens")
            
        try:
            # Convert amount from string to float for NEAR conversion
            amount_near = float(amount)
            
            # Send tokens using async transaction method
            result = await self.near.send_transaction(
                receiver_id=recipient_id,
                amount=amount_near
            )
            
            logger.info(
                f"Sent {amount} NEAR to {recipient_id}"
                f"{' via ' + token_id if token_id else ''}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending tokens: {str(e)}")
            raise

    async def check_balance(self, token_id: Optional[str] = None) -> str:
        """Check account balance."""
        if not self._is_running:
            raise RuntimeError("Agent must be running to check balance")
            
        try:
            balance = await self.near.get_account_balance()
            return balance["available"]
            
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            raise

    async def close(self):
        """Clean up resources."""
        await self.stop()
