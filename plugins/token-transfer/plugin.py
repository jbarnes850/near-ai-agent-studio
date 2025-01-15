"""
Token Transfer Strategy Example
Demonstrates how to create a plugin-based agent for NEAR token transfers.

This example shows:
1. How to create and configure a token transfer plugin
2. YAML-based configuration management
3. Proper error handling and resource cleanup
4. Integration with LLM for transfer validation
5. Best practices for logging and monitoring

Usage:
1. Create plugin configuration:
   ```yaml
   # agent.yaml
   name: token-transfer
   description: "Token transfer agent with LLM validation"
   version: "0.1.0"
   capabilities:
     - token_transfer
     - balance_check
   
   llm:
     provider: ${LLM_PROVIDER}
     model: ${LLM_MODEL}
     temperature: 0.7
   
   near:
     network: ${NEAR_NETWORK:-testnet}
     account_id: ${NEAR_ACCOUNT_ID}
     private_key: ${NEAR_PRIVATE_KEY}
   ```

2. Install plugin:
   ```bash
   near-swarm plugins install ./token-transfer
   ```

3. Run example:
   ```bash
   near-swarm execute token-transfer --operation transfer --recipient bob.testnet --amount 1.5
   ```

Integration Patterns:
- Use environment variables for sensitive configuration
- Implement proper lifecycle methods (initialize/cleanup)
- Add comprehensive error handling
- Include logging for monitoring

Testing:
1. Unit tests: Test validation logic
2. Integration tests: Test NEAR interactions
3. End-to-end tests: Test full transfer flow
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from near_swarm.plugins.base import AgentPlugin
from near_swarm.core.exceptions import AgentError, NEARError, LLMError
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.near_integration import NEARConnection

# Configure logging
logger = logging.getLogger(__name__)

class TokenTransferPlugin(AgentPlugin):
    """Plugin for secure NEAR token transfers with LLM validation."""
    
    async def initialize(self) -> None:
        """Initialize plugin."""
        try:
            # Initialize NEAR connection
            self.near = await NEARConnection.create(
                account_id=os.getenv('NEAR_ACCOUNT_ID'),
                private_key=os.getenv('NEAR_PRIVATE_KEY'),
                network="testnet"
            )
            logger.info("TokenTransferPlugin initialized successfully")
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}")
            raise
            
    async def cleanup(self) -> None:
        """Cleanup plugin resources."""
        if hasattr(self, 'near'):
            try:
                await self.near.close()
            except Exception as e:
                logger.warning(f"Error closing NEAR connection: {str(e)}")
    
    async def _create_llm_provider(self):
        """Create LLM provider from configuration."""
        from near_swarm.core.llm_provider import create_llm_provider, LLMConfig
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        config = LLMConfig(
            provider=os.getenv('LLM_PROVIDER', 'hyperbolic'),
            api_key=os.getenv('LLM_API_KEY'),
            model=os.getenv('LLM_MODEL', 'gpt-4'),
            temperature=0.7
        )
        
        return create_llm_provider(config)
    
    async def execute(self, operation: Optional[str] = None, **kwargs) -> Any:
        """Execute plugin operations."""
        if not operation:
            raise AgentError("Operation not specified")
            
        context = {"operation": operation, **kwargs}
        return await self.evaluate(context)
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process transfer requests with validation."""
        try:
            operation = context.get("operation")
            
            if operation == "transfer":
                return await self._handle_transfer(context)
            elif operation == "balance":
                return await self._handle_balance()
            else:
                raise AgentError(f"Unknown operation: {operation}")
                
        except AgentError as e:
            logger.error(f"Operation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise AgentError(f"Operation failed: {e}")
    
    async def _handle_transfer(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle token transfer operation."""
        try:
            # Extract parameters
            recipient = context.get("recipient")
            amount = context.get("amount")
            
            if not recipient or not amount:
                raise AgentError("Missing required parameters: recipient and amount")
            
            # Get current NEAR price for validation
            near_price = await self.market_data.get_token_price("near")
            
            # Validate transfer with LLM
            validation = await self._validate_transfer(
                recipient,
                amount,
                near_price["price"]
            )
            if not validation["is_valid"]:
                raise AgentError(f"Transfer validation failed: {validation['reason']}")
            
            # Check balance
            balance = await self.near.get_account_balance()
            if float(balance["available"]) < float(amount):
                raise AgentError(f"Insufficient balance: {balance['available']} NEAR")
            
            # Execute transfer
            result = await self.near.send_transaction(
                receiver_id=recipient,
                amount=float(amount)
            )
            
            logger.info(f"Transfer successful: {amount} NEAR to {recipient}")
            return {
                "status": "success",
                "transaction_hash": result.get("transaction_hash", "unknown"),
                "amount": amount,
                "recipient": recipient,
                "near_price_usd": near_price["price"]
            }
            
        except NEARError as e:
            logger.error(f"NEAR operation failed: {e}")
            raise AgentError(f"Transfer failed: {e}")
        except LLMError as e:
            logger.error(f"LLM validation failed: {e}")
            raise AgentError(f"Transfer validation failed: {e}")
    
    async def _handle_balance(self) -> Dict[str, Any]:
        """Handle balance check operation."""
        try:
            balance = await self.near.get_account_balance()
            near_price = await self.market_data.get_token_price("near")
            
            return {
                "balance": balance,
                "near_price_usd": near_price["price"],
                "balance_usd": float(balance["available"]) * near_price["price"]
            }
        except NEARError as e:
            logger.error(f"Balance check failed: {e}")
            raise AgentError(f"Failed to get balance: {e}")
    
    async def _validate_transfer(
        self,
        recipient: str,
        amount: str,
        near_price: float
    ) -> Dict[str, Any]:
        """Validate transfer parameters using LLM."""
        try:
            prompt = f"""
            Validate this NEAR token transfer:
            - Recipient: {recipient}
            - Amount: {amount} NEAR (${float(amount) * near_price:.2f} USD)
            - Current NEAR Price: ${near_price:.2f}
            
            Check for:
            1. Valid NEAR account format (must end in .near or .testnet)
            2. Reasonable amount (not suspiciously large)
            3. Any suspicious patterns
            
            Return JSON with:
            - is_valid: boolean
            - reason: string explaining decision
            """
            
            result = await self.llm_provider.query(prompt)
            return result
            
        except LLMError as e:
            logger.error(f"LLM validation failed: {e}")
            raise
    
async def main():
    """Run the token transfer example."""
    from near_swarm.plugins import PluginLoader
    
    try:
        # Load plugin
        loader = PluginLoader()
        plugin = await loader.load_plugin("token-transfer")
        
        # Example transfer
        result = await plugin.evaluate({
            "operation": "transfer",
            "recipient": "bob.testnet",
            "amount": "0.1"
        })
        
        print("\n=== Transfer Result ===")
        print(f"Status: {result['status']}")
        print(f"Transaction Hash: {result['transaction_hash']}")
        print(f"Amount: {result['amount']} NEAR")
        print(f"Recipient: {result['recipient']}")
        
    except AgentError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if 'plugin' in locals():
            await loader.unload_plugin("token-transfer")

if __name__ == "__main__":
    asyncio.run(main())
