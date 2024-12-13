"""
NEAR Protocol Integration Module
Handles core NEAR blockchain interactions
"""

import logging
from typing import Optional, Dict, Any
from near_api.account import Account
from near_api.signer import Signer, KeyPair
from near_api.providers import JsonProvider

logger = logging.getLogger(__name__)


class NEARConnectionError(Exception):
    """Custom exception for NEAR connection errors."""
    pass


class NEARConnection:
    """Manages NEAR Protocol connection and transactions."""

    YOCTO_NEAR = 10**24  # 1 NEAR = 10^24 yoctoNEAR

    def __init__(
        self,
        network: str,
        account_id: str,
        private_key: str,
        node_url: Optional[str] = None
    ):
        """Initialize NEAR connection."""
        self.network = network
        self.account_id = account_id
        
        # Always use FastNEAR for testnet
        self.node_url = "https://rpc.testnet.fastnear.com"
        
        # Initialize provider and signer
        self.provider = JsonProvider(self.node_url)
        key_pair = KeyPair(private_key)
        self.signer = Signer(account_id, key_pair)
        
        # Initialize account
        self.account = Account(
            self.provider,
            self.signer,
            account_id
        )

    async def send_transaction(
        self,
        receiver_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Send a NEAR transaction."""
        try:
            # Convert NEAR to yoctoNEAR
            amount_yocto = int(amount * self.YOCTO_NEAR)
            
            # Send transaction
            result = await self.account.send_money(
                receiver_id,
                amount_yocto
            )
            return result
            
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise

    async def check_account(self, account_id: str) -> bool:
        """Check if account exists."""
        try:
            await self.account.state()
            return True
        except Exception:
            return False

    async def get_account_balance(self) -> Dict[str, str]:
        """Get account balance."""
        try:
            state = await self.account.state()
            return {
                "total": state["amount"],
                "available": str(int(state["amount"]) - int(state.get("locked", "0")))
            }
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise
