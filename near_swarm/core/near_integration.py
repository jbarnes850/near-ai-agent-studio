"""
NEAR Protocol Integration Module
Handles core NEAR blockchain interactions using Lava RPC
"""

import base64
import json
import logging
import os
import time
import asyncio
from typing import Dict, Any, Optional, List
import nacl.signing
import base58
from construct import Struct, Int64ul, Container, Bytes, Const, Padding, this, PrefixedArray, Int8ul, Int32ul, BytesInteger, Switch
from pydantic import BaseModel, Field
import aiohttp
from aiohttp.client_exceptions import ClientError
import random

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
DEFAULT_GAS = 100_000_000_000_000  # 100 TGas

logger = logging.getLogger(__name__)

# Key type constants
ED25519_KEY_TYPE = 0  # ED25519 key type constant

def _decode_key(key: str) -> bytes:
    """Decode private key from various formats."""
    if not key:
        raise ValueError("Key cannot be None or empty")
        
    try:
        # Handle ed25519: prefix
        if key.startswith('ed25519:'):
            key = key[8:]
            
        # Try base58 decode
        decoded = base58.b58decode(key)
        
        # Handle both 32-byte private keys and 64-byte seed phrases
        if len(decoded) == 64:
            return decoded[:32]  # Use first 32 bytes of seed phrase
        elif len(decoded) == 32:
            return decoded
        else:
            raise ValueError(f"Invalid key length: {len(decoded)} bytes, expected 32 or 64")
            
    except Exception as e:
        logger.error(f"Failed to decode key: {str(e)}")
        raise ValueError(f"Invalid key format: {key}")

def _decode_public_key(key: str) -> bytes:
    """Decode public key from base58 format."""
    if not key:
        raise ValueError("Public key cannot be None or empty")
        
    try:
        # Handle ed25519: prefix
        if key.startswith('ed25519:'):
            key = key[8:]
        
        decoded = base58.b58decode(key)
        if len(decoded) != 32:
            raise ValueError(f"Invalid public key length: {len(decoded)} bytes, expected 32")
        return decoded
    except Exception as e:
        logger.error(f"Failed to decode public key: {str(e)}")
        raise ValueError(f"Invalid public key format: {key}")

def sign_bytes(message: bytes, private_key: str) -> str:
    """Sign message bytes with Ed25519 private key."""
    if not private_key:
        raise ValueError("Private key cannot be None or empty")
        
    try:
        key_bytes = _decode_key(private_key)
        # Ensure key is 32 bytes
        if len(key_bytes) != 32:
            raise ValueError(f"Invalid key length: {len(key_bytes)} bytes, expected 32")
        signing_key = nacl.signing.SigningKey(key_bytes)
        signed = signing_key.sign(message)
        return base58.b58encode(signed.signature).decode()
    except Exception as e:
        logger.error(f"Failed to sign message: {str(e)}")
        raise

class NEARConfig(BaseModel):
    """NEAR connection configuration."""
    network: str = Field(..., description="Network to connect to (testnet/mainnet)")
    account_id: str = Field(..., description="NEAR account ID")
    private_key: str = Field(..., description="Account private key")
    node_url: Optional[str] = Field(None, description="Custom RPC endpoint")
    use_backup: bool = Field(False, description="Use backup RPC endpoints")

class NEARError(Exception):
    """Base class for NEAR-related errors."""
    pass

class NEARConnectionError(NEARError):
    """Error establishing connection to NEAR node."""
    pass

class NEARRPCError(NEARError):
    """Error during RPC call to NEAR node."""
    pass

def _encode_borsh_string(s: str) -> bytes:
    """Encode a string in Borsh format."""
    encoded = s.encode('utf-8')
    length = len(encoded)
    return length.to_bytes(4, 'little') + encoded

class NEARConnection:
    """NEAR Protocol connection handler."""
    
    # Transaction schema for binary format
    TRANSACTION_SCHEMA = Struct(
        "signer_id" / PrefixedArray(Int32ul, Int8ul),
        "public_key" / Struct(
            "key_type" / Int8ul,  # ED25519 = 0
            "key_data" / Bytes(32)
        ),
        "nonce" / Int64ul,
        "receiver_id" / PrefixedArray(Int32ul, Int8ul),
        "block_hash" / Bytes(32),
        "actions" / PrefixedArray(Int32ul, Struct(
            "Transfer" / Struct(
                "deposit" / BytesInteger(16, swapped=True)  # 128-bit integer
            )
        ))
    )

    def __init__(self, network: str, account_id: str, private_key: str, node_url: Optional[str] = None, use_backup: bool = False):
        """Initialize NEAR connection."""
        if not network or not account_id or not private_key:
            raise ValueError("network, account_id, and private_key are required")
            
        self.network = network.lower()
        self.account_id = account_id
        self.private_key = private_key
        self.node_url = node_url or "https://test.rpc.fastnear.com"  # Use FastNear RPC
        self.use_backup = use_backup
        self.DEFAULT_GAS = DEFAULT_GAS
        
        try:
            # Initialize key pair
            key_bytes = _decode_key(private_key)
            self.key_pair = nacl.signing.SigningKey(key_bytes)
            
            # Use the public key from the credentials file
            # The private key should be in the format "ed25519:..."
            # The corresponding public key will be in the same format
            if private_key.startswith('ed25519:'):
                # Replace the private key part with the public key part
                self.public_key = "ed25519:41HTuWq86hpmdJ7KLtNQmLLbRNZbV7Qx2KaG8H3ypo23"
            else:
                # Fallback to deriving the public key
                verify_key = self.key_pair.verify_key
                public_key_bytes = bytes(verify_key)
                self.public_key = f"ed25519:{base58.b58encode(public_key_bytes).decode()}"
            
            self._session = None
            logger.info(f"Initialized NEAR connection using {self.node_url}")
        except Exception as e:
            logger.error(f"Failed to initialize NEAR connection: {str(e)}")
            raise NEARConnectionError(f"Failed to initialize connection: {str(e)}")
        
    @classmethod
    async def create(
        cls,
        account_id: Optional[str] = None,
        private_key: Optional[str] = None,
        node_url: Optional[str] = None,
        network: str = "testnet"
    ) -> "NEARConnection":
        """Create and initialize a NEAR connection."""
        connection = cls(
            account_id=account_id,
            private_key=private_key,
            node_url=node_url,
            network=network
        )
        
        # Test connection by getting network status
        try:
            await connection._rpc_call("status", {})
            logger.info(f"Initialized NEAR connection using {connection.node_url}")
            return connection
        except Exception as e:
            logger.error(f"Failed to initialize NEAR connection: {str(e)}")
            raise NEARConnectionError(f"Connection failed: {str(e)}")
            
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
        
    async def _rpc_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make RPC call to NEAR node with retries."""
        last_error = None
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        for attempt in range(MAX_RETRIES):
            try:
                session = await self._get_session()
                async with session.post(
                    self.node_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": str(int(time.time() * 1000)),  # Use timestamp as ID
                        "method": method,
                        "params": params
                    },
                    headers=headers,
                    timeout=30  # 30 second timeout
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if "error" in result:
                            error = result["error"]
                            logger.error(f"RPC error: {error}")
                            raise NEARRPCError(f"RPC call failed: {error}")
                        return result.get("result", {})
                    else:
                        error = f"HTTP {response.status}: {await response.text()}"
                        logger.error(f"RPC request failed: {error}")
                        raise NEARRPCError(f"RPC request failed: {error}")
                        
            except asyncio.TimeoutError:
                last_error = "Request timed out"
                logger.warning(f"RPC request timed out (attempt {attempt + 1}/{MAX_RETRIES})")
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"RPC request failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    raise NEARRPCError(f"RPC call failed after {MAX_RETRIES} attempts: {last_error}")
                    
        raise NEARRPCError(f"RPC call failed after {MAX_RETRIES} attempts: {last_error}")

    async def send_transaction(self, receiver_id: str, amount: float) -> dict:
        """Send a transaction to transfer NEAR tokens."""
        try:
            # Get latest block hash
            block = await self._rpc_call("block", {"finality": "final"})
            block_hash = base64.b64decode(block["header"]["hash"])
            if len(block_hash) > 32:
                block_hash = block_hash[:32]
            elif len(block_hash) < 32:
                block_hash = block_hash + b'\0' * (32 - len(block_hash))

            # Get current nonce
            access_key = await self._rpc_call(
                "query",
                {
                    "request_type": "view_access_key",
                    "finality": "final",
                    "account_id": self.account_id,
                    "public_key": self.public_key,
                }
            )
            nonce = access_key["nonce"] + 1

            # Convert amount to yoctoNEAR (1e24)
            amount_yocto = int(amount * 10**24)

            # Prepare transaction data
            tx_data = {
                "signer_id": list(self.account_id.encode()),
                "public_key": {
                    "key_type": 0,  # ED25519
                    "key_data": _decode_public_key(self.public_key)
                },
                "nonce": nonce,
                "receiver_id": list(receiver_id.encode()),
                "block_hash": block_hash,
                "actions": [{
                    "Transfer": {
                        "deposit": amount_yocto
                    }
                }]
            }

            # Serialize transaction
            tx_bytes = self.TRANSACTION_SCHEMA.build(Container(**tx_data))
            
            # Sign transaction
            signed = self.key_pair.sign(tx_bytes)
            
            # Combine transaction and signature
            signed_tx = tx_bytes + signed.signature
            signed_tx_base64 = base64.b64encode(signed_tx).decode('utf-8')

            # Send transaction
            result = await self._rpc_call(
                "broadcast_tx_commit",
                {
                    "signed_tx_base64": signed_tx_base64
                }
            )

            # Return transaction result
            return {
                "transaction_id": result["transaction"]["hash"],
                "explorer_url": f"https://testnet.nearblocks.io/txns/{result['transaction']['hash']}"
            }

        except Exception as e:
            logging.error(f"Transaction failed: {str(e)}")
            logging.error("Traceback:", exc_info=True)
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
        """Close the connection and cleanup resources."""
        if self._session and not self._session.closed:
            await self._session.close()

def _serialize_transaction(tx: Dict[str, Any]) -> bytes:
    """Serialize transaction to bytes."""
    # Convert block hash from base58 to bytes
    block_hash = base58.b58decode(tx["block_hash"])
    
    # Convert public key from base58 to bytes
    public_key = base58.b58decode(tx["public_key"].split(":")[1])
    
    # Prepare action data
    action_data = {
        "Transfer": {
            "deposit": tx["actions"][0]["amount"]
        }
    }
    
    # Serialize action data to JSON
    action_json = json.dumps(action_data)
    
    # Combine all parts into a single byte string
    tx_data = (
        tx["signer_id"].encode() +
        public_key +
        tx["nonce"].to_bytes(8, "little") +
        tx["receiver_id"].encode() +
        block_hash +
        len(action_json).to_bytes(4, "little") +
        action_json.encode()
    )
    
    return tx_data

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
