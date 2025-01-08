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
    rpc_url: Optional[str] = None
    use_backup_rpc: bool = False

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
        
        # Initialize NEAR connection with configurable RPC
        self.near = NEARConnection(
            network=config.network,
            account_id=config.account_id,
            private_key=config.private_key,
            node_url=config.rpc_url,
            use_backup=config.use_backup_rpc
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
        amount: str,  # Amount in NEAR or token units
        token_id: Optional[str] = None,
        gas: Optional[int] = None,
        attached_deposit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send tokens to another account.
        
        Args:
            recipient_id: Recipient account ID
            amount: Amount to send (in NEAR or token units)
            token_id: Optional token contract ID for NEP-141 tokens
            gas: Optional gas amount for the transaction
            attached_deposit: Optional yoctoNEAR to attach
            
        Returns:
            Transaction outcome
        """
        if not self._is_running:
            raise RuntimeError("Agent must be running to send tokens")
            
        try:
            # Convert amount from string to float for NEAR conversion
            amount_float = float(amount)
            
            # If this is a token transfer, use the token contract
            if token_id:
                # Prepare FT transfer call
                tx_args = {
                    "receiver_id": recipient_id,
                    "amount": str(amount_float)
                }
                
                # Send tokens using async transaction method
                result = await self.near.send_transaction(
                    receiver_id=token_id,  # Token contract
                    amount=0,  # No NEAR transfer
                    gas=gas,
                    attached_deposit=attached_deposit,
                    method_name="ft_transfer",
                    args=tx_args
                )
            else:
                # Direct NEAR transfer
                result = await self.near.send_transaction(
                    receiver_id=recipient_id,
                    amount=amount_float,
                    gas=gas,
                    attached_deposit=attached_deposit
                )
            
            logger.info(
                f"Sent {amount} {'NEAR' if not token_id else token_id} to {recipient_id}"
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
            if token_id:
                # Get token balance using ft_balance_of
                result = await self.near.view_function(
                    token_id,
                    "ft_balance_of",
                    {"account_id": self.config.account_id}
                )
                return result
            else:
                # Get NEAR balance
                balance = await self.near.get_account_balance()
                return balance["available"]
            
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            raise

    async def close(self):
        """Clean up resources."""
        await self.stop()
        await self.near.close()
