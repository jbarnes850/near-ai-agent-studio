"""
NEAR Protocol Integration Module
Handles core NEAR blockchain interactions using FASTNEAR RPC
"""

import logging
import json
import base58
from typing import Optional, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)


class NEARConnectionError(Exception):
    """Custom exception for NEAR connection errors."""
    pass


class NEARConnection:
    """Manages NEAR Protocol connection and transactions."""

    YOCTO_NEAR = 10**24  # 1 NEAR = 10^24 yoctoNEAR
    DEFAULT_TESTNET_URL = "https://test.rpc.fastnear.com"  # FASTNEAR testnet endpoint
    DEFAULT_MAINNET_URL = "https://free.rpc.fastnear.com"  # FASTNEAR mainnet endpoint

    def __init__(
        self,
        network: str,
        account_id: str,
        private_key: str,
        node_url: Optional[str] = None
    ):
        """Initialize NEAR connection.
        
        Args:
            network: Either 'testnet' or 'mainnet'
            account_id: NEAR account ID
            private_key: Account's private key
            node_url: Optional custom RPC endpoint
        """
        self.network = network.lower()
        self.account_id = account_id
        self.private_key = private_key
        
        # Use FASTNEAR endpoints by default
        if node_url:
            self.node_url = node_url
        else:
            self.node_url = (
                self.DEFAULT_TESTNET_URL if self.network == "testnet"
                else self.DEFAULT_MAINNET_URL
            )
        
        logger.info(f"Initialized NEAR connection using {self.node_url}")

    async def _rpc_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make RPC call to NEAR node."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.node_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": "dontcare",
                        "method": method,
                        "params": params
                    },
                    timeout=30  # 30 second timeout
                ) as response:
                    if response.status != 200:
                        raise NEARConnectionError(
                            f"RPC request failed with status {response.status}"
                        )
                    
                    result = await response.json()
                    if "error" in result:
                        raise NEARConnectionError(result["error"])
                    return result["result"]
        except aiohttp.ClientError as e:
            raise NEARConnectionError(f"RPC connection failed: {str(e)}")
        except Exception as e:
            raise NEARConnectionError(f"Unexpected error in RPC call: {str(e)}")

    async def send_transaction(
        self,
        receiver_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """Send a NEAR transaction."""
        try:
            # Convert NEAR to yoctoNEAR
            amount_yocto = int(amount * self.YOCTO_NEAR)
            
            # Create and sign transaction
            tx = {
                "signerId": self.account_id,
                "receiverId": receiver_id,
                "actions": [{
                    "type": "Transfer",
                    "amount": str(amount_yocto)
                }]
            }
            
            # Send transaction
            result = await self._rpc_call(
                "broadcast_tx_commit",
                {"signed_transaction": json.dumps(tx)}
            )
            return result
            
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise

    async def check_account(self, account_id: str) -> bool:
        """Check if account exists."""
        try:
            await self._rpc_call(
                "query",
                {
                    "request_type": "view_account",
                    "finality": "final",
                    "account_id": account_id
                }
            )
            return True
        except NEARConnectionError:
            return False

    async def get_account_balance(self) -> Dict[str, str]:
        """Get account balance."""
        try:
            result = await self._rpc_call(
                "query",
                {
                    "request_type": "view_account",
                    "finality": "final",
                    "account_id": self.account_id
                }
            )
            return {
                "total": result["amount"],
                "available": str(int(result["amount"]) - int(result.get("locked", "0")))
            }
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise
