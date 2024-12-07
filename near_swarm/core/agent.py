"""
NEAR AI Agent Implementation
Core functionality for NEAR Protocol integration
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from near_api.account import Account
from near_api.providers import JsonProvider
import aiohttp


@dataclass
class AgentConfig:
    """Configuration for NEAR AI Agent"""
    near_network: str
    account_id: str
    private_key: str
    llm_provider: str
    llm_api_key: str


class NEARAgent:
    """Core NEAR Protocol AI Agent implementation"""
    
    def __init__(self, config: AgentConfig):
        """Initialize the NEAR agent with configuration"""
        self.config = config
        self.session = None
        self._initialize_near_connection()
        self._initialize_llm()
    
    async def initialize(self):
        """Initialize async resources"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _create_session(self):
        """Create aiohttp session"""
        return aiohttp.ClientSession()
    
    def _initialize_near_connection(self):
        """Initialize connection to NEAR Protocol"""
        # Initialize provider based on network
        if self.config.near_network == "mainnet":
            provider = JsonProvider("https://rpc.mainnet.near.org")
        else:
            provider = JsonProvider("https://rpc.testnet.near.org")
        
        self.near_account = Account(
            provider,
            self.config.account_id,
            self.config.private_key
        )
    
    def _initialize_llm(self):
        """Initialize LLM provider connection"""
        # Configure LLM based on provider
        if self.config.llm_provider == "hyperbolic":
            import openai
            openai.api_key = self.config.llm_api_key
            openai.api_base = "https://api.hyperbolic.ai/v1"
            self.llm = openai
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
    
    async def process_message(self, message: str) -> str:
        """Process a message using the LLM"""
        await self.initialize()
        response = await self.llm.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[{"role": "user", "content": message}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    async def check_balance(self, account_id: Optional[str] = None) -> float:
        """Check NEAR balance for an account"""
        await self.initialize()
        account = account_id or self.config.account_id
        balance = await self.near_account.get_account_balance()
        return float(balance['available']) / 10**24  # Convert yoctoNEAR to NEAR
    
    async def execute_transaction(
        self,
        receiver_id: str,
        amount: float,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a NEAR transaction"""
        await self.initialize()
        try:
            # Convert NEAR to yoctoNEAR
            amount_yocto = int(amount * 10**24)
            
            result = await self.near_account.send_money(
                receiver_id,
                amount_yocto
            )
            
            return {
                "status": "success",
                "transaction_hash": result['transaction']['hash'],
                "receiver_id": receiver_id,
                "amount": amount
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
            self.session = None


def create_agent(config: Dict[str, str]) -> NEARAgent:
    """Create a new NEAR agent instance"""
    agent_config = AgentConfig(
        near_network=config.get('near_network', 'testnet'),
        account_id=config['account_id'],
        private_key=config['private_key'],
        llm_provider=config.get('llm_provider', 'hyperbolic'),
        llm_api_key=config['llm_api_key']
    )
    return NEARAgent(agent_config)