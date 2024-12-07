"""
NEAR Protocol integration.
"""

from typing import Dict, Optional
import asyncio
import json
import logging
import requests
from near_api.account import Account
from near_api.providers import JsonProvider
from near_api.signer import Signer

logger = logging.getLogger(__name__)

class NEARConnectionError(Exception):
    """Custom exception for NEAR connection issues."""
    pass

class NEARConnection:
    """NEAR Protocol connection manager."""
    
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
                self.node_url = "https://rpc.testnet.near.org"
            
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
                logger.info("RPC connection test successful")
            except Exception as e:
                logger.error(f"RPC connection test failed: {str(e)}")
                raise
            
            # Initialize provider
            provider = JsonProvider(self.node_url)
            
            # Initialize signer
            signer = Signer(account_id, private_key)
            
            # Initialize account with proper parameters
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
                logger.info(f"Account data retrieved: {json.dumps(account_data, indent=2)}")
            except Exception as e:
                logger.error(f"Failed to retrieve account data: {str(e)}")
                raise
            
            self.account = Account(
                provider,
                account_id,
                signer
            )
            logger.info(f"Successfully initialized NEAR connection for {account_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize NEAR connection: {str(e)}")
            raise NEARConnectionError(f"NEAR connection failed: {str(e)}")
    
    async def swap_tokens(
        self,
        token_in: str,
        token_out: str,
        amount: float
    ) -> Dict:
        """Execute token swap on Ref Finance."""
        try:
            result = await self.account.function_call(
                "ref-finance.testnet",
                "swap",
                {
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount": str(int(amount * 10**24))  # Convert to yoctoNEAR
                }
            )
            
            return {
                "status": "success",
                "transaction_hash": result['transaction']['hash']
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def estimate_swap_gas(
        self,
        token_in: str,
        token_out: str,
        amount: float
    ) -> float:
        """Estimate gas for token swap."""
        try:
            result = await self.account.view_function(
                "ref-finance.testnet",
                "get_swap_gas_estimate",
                {
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount": str(int(amount * 10**24))
                }
            )
            
            return float(result['gas']) / 10**12  # Convert to NEAR
        except Exception as e:
            raise Exception(f"Error estimating gas: {str(e)}")
    
    async def get_pool_data(
        self,
        token_a: str,
        token_b: str
    ) -> Dict:
        """Get pool data from Ref Finance."""
        try:
            result = await self.account.view_function(
                "ref-finance.testnet",
                "get_pool",
                {
                    "token_a": token_a,
                    "token_b": token_b
                }
            )
            
            return {
                "price": float(result['price']) / 10**24,
                "liquidity": float(result['liquidity']) / 10**24
            }
        except Exception as e:
            raise Exception(f"Error getting pool data: {str(e)}")
    
    async def execute_strategy(self, strategy: Dict) -> Dict:
        """Execute trading strategy."""
        try:
            if strategy["action"] == "swap":
                return await self.swap_tokens(
                    strategy["params"]["from_token"],
                    strategy["params"]["to_token"],
                    strategy["params"]["amount"]
                )
            else:
                raise ValueError(f"Unsupported action: {strategy['action']}")
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def check_transaction(self, tx_hash: str) -> Dict:
        """Check transaction status."""
        try:
            result = await self.account.get_transaction_result(tx_hash)
            return {
                "success": "SuccessValue" in result["status"],
                "status": result["status"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_network_conditions(self) -> Dict:
        """Check network conditions."""
        try:
            result = await self.account.view_function(
                "system",
                "get_network_info",
                {}
            )
            
            return {
                "block_height": int(result["block_height"]),
                "gas_price": int(result["gas_price"])
            }
        except Exception as e:
            raise Exception(f"Error checking network: {str(e)}")
    
    async def close(self):
        """Clean up resources."""
        pass  # No async resources to clean up