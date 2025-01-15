"""
NEAR Protocol Integration Module
Handles core NEAR blockchain interactions using Lava andFASTNEAR RPC
"""

import logging
import json
import base58
from typing import Optional, Dict, Any, Union
import aiohttp
import asyncio
from aiohttp.client_exceptions import ClientError
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
DEFAULT_GAS = 100_000_000_000_000  # 100 TGas

class NEARConfig(BaseModel):
    """NEAR connection configuration."""
    network: str = Field(..., description="Network to connect to (testnet/mainnet)")
    account_id: str = Field(..., description="NEAR account ID")
    private_key: str = Field(..., description="Account private key")
    node_url: Optional[str] = Field(None, description="Custom RPC endpoint")
    use_backup: bool = Field(False, description="Use backup RPC endpoints")

class NEARConnectionError(Exception):
    """Custom exception for NEAR connection errors."""
    pass

class NEARConnection:
    """Manages NEAR Protocol connection and transactions."""

    YOCTO_NEAR = 10**24  # 1 NEAR = 10^24 yoctoNEAR
    DEFAULT_TESTNET_URL = "https://neart.lava.build"  # Lava testnet endpoint
    DEFAULT_MAINNET_URL = "https://near.lava.build"   # Lava mainnet endpoint
    BACKUP_TESTNET_URL = "https://test.rpc.fastnear.com"  # FASTNEAR testnet endpoint
    BACKUP_MAINNET_URL = "https://free.rpc.fastnear.com"  # FASTNEAR mainnet endpoint

    def __init__(
        self,
        network: str,
        account_id: str,
        private_key: str,
        node_url: Optional[str] = None,
        use_backup: bool = False
    ):
        """Initialize NEAR connection.
        
        Args:
            network: Either 'testnet' or 'mainnet'
            account_id: NEAR account ID
            private_key: Account's private key
            node_url: Optional custom RPC endpoint
            use_backup: Use backup RPC endpoints if True
        """
        self.network = network.lower()
        self.account_id = account_id
        self.private_key = private_key
        
        # Use provided URL or select appropriate default
        if node_url:
            self.node_url = node_url
        else:
            if use_backup:
                self.node_url = (
                    self.BACKUP_TESTNET_URL if self.network == "testnet"
                    else self.BACKUP_MAINNET_URL
                )
            else:
                self.node_url = (
                    self.DEFAULT_TESTNET_URL if self.network == "testnet"
                    else self.DEFAULT_MAINNET_URL
                )
        
        # Initialize session
        self._session = None
        
        logger.info(f"Initialized NEAR connection using {self.node_url}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _rpc_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make RPC call to NEAR node with retries."""
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                session = await self._get_session()
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
                    
            except asyncio.CancelledError:
                # Don't retry on cancellation
                raise
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY * (attempt + 1)
                    logger.warning(
                        f"RPC call failed (attempt {attempt + 1}/{MAX_RETRIES}), "
                        f"retrying in {delay}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                    continue
                break
        
        # If we get here, all retries failed
        raise NEARConnectionError(f"RPC call failed after {MAX_RETRIES} attempts: {str(last_error)}")

    async def send_transaction(
        self,
        receiver_id: str,
        amount: float,
        gas: Optional[int] = None,
        attached_deposit: Optional[int] = None,
        method_name: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a NEAR transaction.
        
        Args:
            receiver_id: Recipient account ID
            amount: Amount in NEAR
            gas: Optional gas amount (default: 100 TGas)
            attached_deposit: Optional yoctoNEAR to attach
            method_name: Optional contract method to call
            args: Optional arguments for contract call
        """
        try:
            # Convert NEAR to yoctoNEAR
            amount_yocto = int(amount * self.YOCTO_NEAR)
            
            # Prepare actions
            actions = []
            
            # Add transfer action if amount > 0
            if amount_yocto > 0:
                actions.append({
                    "type": "Transfer",
                    "amount": str(amount_yocto)
                })
            
            # Add function call action if method specified
            if method_name:
                actions.append({
                    "type": "FunctionCall",
                    "method_name": method_name,
                    "args": json.dumps(args or {}),
                    "gas": str(gas or DEFAULT_GAS),
                    "deposit": str(attached_deposit or 0)
                })
            
            # Create transaction
            tx = {
                "signerId": self.account_id,
                "receiverId": receiver_id,
                "actions": actions
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
    
    async def get_gas_price(self) -> int:
        """Get current gas price."""
        try:
            result = await self._rpc_call(
                "gas_price",
                [None]  # Get latest gas price
            )
            return int(result["gas_price"])
        except Exception as e:
            logger.error(f"Failed to get gas price: {str(e)}")
            raise
    
    async def view_function(
        self,
        contract_id: str,
        method_name: str,
        args: Dict[str, Any]
    ) -> Any:
        """Call a view function on a contract."""
        try:
            result = await self._rpc_call(
                "query",
                {
                    "request_type": "call_function",
                    "finality": "final",
                    "account_id": contract_id,
                    "method_name": method_name,
                    "args_base64": base58.b58encode(
                        json.dumps(args).encode()
                    ).decode()
                }
            )
            return json.loads(
                base58.b58decode(result["result"]).decode()
            )
        except Exception as e:
            logger.error(f"View function call failed: {str(e)}")
            raise
    
    async def close(self):
        """Close the connection and cleanup."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._get_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return None

async def create_near_connection(config: NEARConfig) -> NEARConnection:
    """Create a new NEAR connection from configuration.
    
    Args:
        config: NEARConfig instance with connection settings
        
    Returns:
        Initialized NEARConnection instance
    """
    try:
        connection = NEARConnection(
            network=config.network,
            account_id=config.account_id,
            private_key=config.private_key,
            node_url=config.node_url,
            use_backup=config.use_backup
        )
        
        # Test connection by checking account
        await connection.check_account(config.account_id)
        
        return connection
        
    except Exception as e:
        logger.error(f"Failed to create NEAR connection: {str(e)}")
        raise NEARConnectionError(f"Connection failed: {str(e)}")
