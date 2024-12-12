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
    """Handles NEAR Protocol connection and interactions."""

    def __init__(
        self,
        network: str,
        account_id: str,
        private_key: str,
        node_url: Optional[str] = None
    ):
        """Initialize NEAR connection."""
        try:
            self.network = network
            self.account_id = account_id

            # Initialize provider based on network or custom node URL
            if node_url:
                logger.info(f"Using custom RPC endpoint: {node_url}")
                self.node_url = node_url
            elif network == "mainnet":
                self.node_url = "https://rpc.mainnet.near.org"
            else:
                self.node_url = "https://rpc.testnet.fastnear.com"

            # Initialize provider
            self.provider = JsonProvider(self.node_url)

            # Test connection with a status check
            try:
                status_request = {
                    "jsonrpc": "2.0",
                    "id": "dontcare",
                    "method": "status",
                    "params": []
                }
                response = requests.post(self.node_url, json=status_request)
                response.raise_for_status()
                status_data = response.json()
                if not isinstance(status_data, dict) or 'result' not in status_data:
                    raise ValueError("Invalid response format from RPC endpoint")
                logger.info("RPC connection test successful")
            except Exception as e:
                logger.error(f"RPC connection test failed: {str(e)}")
                raise

            # Initialize key pair and signer
            try:
                # Handle private key initialization
                key_str = private_key.strip()
                try:
                    # Initialize Account first
                    key_pair = KeyPair(key_str)
                    self.signer = Signer(account_id, key_pair)
                    self.account = Account(
                        self.provider,
                        self.signer,
                        self.account_id
                    )
                    logger.info("Successfully initialized key pair and signer")
                except Exception as e:
                    logger.error(f"Failed to initialize key pair: {str(e)}")
                    raise NEARConnectionError(f"Failed to initialize key pair: {str(e)}")

            except Exception as e:
                logger.error(f"Failed to initialize key pair: {str(e)}")
                raise NEARConnectionError(f"Failed to initialize key pair: {str(e)}")

            # Now check account data after Account is initialized
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

            try:
                response = requests.post(self.node_url, json=account_request)
                response.raise_for_status()
                account_data = response.json()
                if not isinstance(account_data, dict) or 'result' not in account_data:
                    raise ValueError("Invalid account data format from RPC endpoint")
                logger.info("Account data retrieved successfully")
            except Exception as e:
                logger.error(f"Failed to retrieve account data: {str(e)}")
                raise

            logger.info(f"Successfully initialized NEAR connection for {account_id}")

        except Exception as e:
            logger.error(f"Failed to initialize NEAR connection: {str(e)}")
            raise NEARConnectionError(f"NEAR connection failed: {str(e)}")

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
            account_data = self.provider.get_account(self.account_id)
            return {
                "total": account_data["amount"],
                "staked": account_data["locked"],
                "available": str(int(account_data["amount"]) - int(account_data["locked"]))
            }
        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            raise

    def send_transaction(self, receiver_id: str, amount: float) -> Dict[str, Any]:
        """Send a NEAR transaction."""
        try:
            # Convert amount to yoctoNEAR (1 NEAR = 10^24 yoctoNEAR)
            amount_yocto = int(amount * 10**24)

            # Use the account's send_money method which handles all transaction details
            try:
                result = self.account.send_money(receiver_id, amount_yocto)
                logger.info(f"Transaction sent successfully: {result}")
                return result
            except TransactionError as tx_error:
                logger.error(f"Failed to send transaction: {str(tx_error)}")
                raise NEARConnectionError(f"Failed to send transaction: {str(tx_error)}")
            except Exception as e:
                logger.error(f"Unexpected error in send_transaction: {str(e)}")
                raise NEARConnectionError(f"Unexpected error in send_transaction: {str(e)}")

        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise NEARConnectionError(f"Failed to send transaction: {str(e)}")
