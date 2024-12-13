"""
NEAR Protocol Integration Module
Handles core NEAR blockchain interactions
"""

import json
import logging
from typing import Optional, Dict, Any
import base58
import requests
from near_api.providers import JsonProvider
from near_api.signer import Signer, KeyPair
from near_api.account import Account, TransactionError

logger = logging.getLogger(__name__)


class NEARConnectionError(Exception):
    """Custom exception for NEAR connection errors."""
    pass


class NEARConnection:
    """Manages NEAR Protocol connection and transactions."""

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
        self.private_key = private_key
        
        # Always use FastNEAR for testnet
        self.node_url = "https://rpc.testnet.fastnear.com"
        
        # Initialize provider
        self.provider = JsonProvider(self.node_url)
        
        # Initialize key pair and signer
        try:
            # Create KeyPair from private key
            key_pair = KeyPair(private_key)  # Direct initialization
            self.signer = Signer(account_id, key_pair)
            
            # Initialize account
            self.account = Account(
                self.provider,
                self.signer,
                account_id
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize NEAR connection: {str(e)}")
            raise NEARConnectionError(f"NEAR connection failed: {str(e)}")

    async def send_transaction(
        self,
        receiver_id: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Send a NEAR transaction.
        
        Args:
            receiver_id: Recipient account ID
            amount: Amount in NEAR (will be converted to yoctoNEAR)
            
        Returns:
            Transaction outcome
        """
        try:
            # Convert NEAR to yoctoNEAR (1 NEAR = 10^24 yoctoNEAR)
            amount_yocto = int(amount * 10**24)
            
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
        """Check if the account exists and initialize it if needed."""
        try:
            # Get account details using provider directly
            account_request = {
                "jsonrpc": "2.0",
                "id": "dontcare",
                "method": "query",
                "params": {
                    "request_type": "view_account",
                    "finality": "final",
                    "account_id": account_id
                }
            }

            response = requests.post(self.node_url, json=account_request)
            response.raise_for_status()
            account_data = response.json()

            if 'error' in account_data:
                if 'does not exist' in account_data['error']['cause']['name']:
                    return False
                raise NEARConnectionError(f"Failed to check account: {account_data['error']}")

            if not isinstance(account_data, dict) or 'result' not in account_data:
                raise NEARConnectionError("Invalid account data format from RPC endpoint")

            logger.debug(f"Account info: {account_data['result']}")
            return True

        except Exception as e:
            logger.error(f"Failed to check account: {str(e)}")
            raise NEARConnectionError(f"Failed to check account: {str(e)}")

    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance."""
        try:
            balance_request = {
                "jsonrpc": "2.0",
                "id": "dontcare",
                "method": "query",
                "params": {
                    "request_type": "view_account",
                    "finality": "final",
                    "account_id": self.account_id
                }
            }
            response = requests.post(self.node_url, json=balance_request)
            response.raise_for_status()
            account_data = response.json()
            return {
                "total": account_data["result"]["amount"],
                "available": str(int(account_data["result"]["amount"]) - int(account_data["result"].get("locked", "0")))
            }
        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            raise NEARConnectionError(f"Failed to get account balance: {str(e)}")
