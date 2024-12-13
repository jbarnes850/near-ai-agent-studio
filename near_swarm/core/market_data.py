"""
Market data integration using DeFi Llama API.
Provides real-time price, volume, and liquidity data for NEAR ecosystem.
"""

import asyncio
from typing import Dict, List, Optional, Any
import aiohttp
import time
import logging

logger = logging.getLogger(__name__)

class MarketDataManager:
    """Manages market data integration using DeFi Llama API."""

    # Token ID mappings with correct prefixes
    TOKEN_IDS = {
        "btc": "coingecko:bitcoin",
        "eth": "coingecko:ethereum",
        "near": "coingecko:near",
        "usdc": "coingecko:usd-coin",
        "usdt": "coingecko:tether",
        "ref": "coingecko:ref-finance",
        "aurora": "coingecko:aurora-near",
    }

    def __init__(self):
        """Initialize market data manager."""
        # Session management
        self.session: Optional[aiohttp.ClientSession] = None
        
        # API endpoints
        self.coins_url = "https://coins.llama.fi"  # For price data
        self.api_url = "https://api.llama.fi"      # For protocol data
        
        # Cache management
        self.cache = {}
        self.price_cache = {}
        self.cache_expiry = 60  
        
        # Rate limiting
        self.rate_limit_delay = 1.0  
        self.last_request_time = 0.0
        
    async def initialize(self):
        """Initialize connections and cache."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure session exists and return it."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()

    async def get_token_price(
        self,
        token_id: str,
    ) -> Dict:
        """
        Get token price and market data from DeFi Llama.
        
        Args:
            token_id: Token contract address or symbol
            
        Returns:
            Dict containing price and market data
        """
        # Convert common token names to DeFi Llama IDs with coingecko prefix
        token_id = self.TOKEN_IDS.get(token_id.lower(), f"coingecko:{token_id.lower()}")
        
        # Check cache first
        if token_id in self.price_cache:
            timestamp, data = self.price_cache[token_id]
            if time.time() - timestamp < self.cache_expiry:
                return data

        # Rate limit and make request
        await self._rate_limit()
        session = await self._ensure_session()

        try:
            # Current prices endpoint
            url = f"{self.coins_url}/prices/current/{token_id}"
            
            async with session.get(url) as response:
                if response.status == 429:  # Too Many Requests
                    logger.warning("Rate limit hit, increasing delay")
                    self.rate_limit_delay *= 1.5
                    await asyncio.sleep(2)
                    return await self.get_token_price(token_id)
                    
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                
                data = await response.json()
                if not data or "coins" not in data or token_id not in data["coins"]:
                    raise Exception(f"No data found for token: {token_id}")
                
                coin_data = data["coins"][token_id]
                token_data = {
                    "price": coin_data["price"],
                    "timestamp": coin_data["timestamp"],
                    "confidence": coin_data.get("confidence", 0.9)
                }
                
                # Update cache
                self.price_cache[token_id] = (time.time(), token_data)
                return token_data

        except Exception as e:
            logger.error(f"Error fetching price: {str(e)}")
            raise

    async def get_dex_data(self, protocol: str) -> Dict:
        """Get basic DEX data focusing on TVL."""
        await self._rate_limit()
        session = await self._ensure_session()
        
        try:
            # Use TVL endpoint which is more reliable
            url = f"{self.api_url}/tvl/{protocol}"
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                
                tvl_data = await response.json()
                
                # Get protocol info for basic metadata
                protocol_url = f"{self.api_url}/protocol/{protocol}"
                async with session.get(protocol_url) as protocol_response:
                    protocol_data = await protocol_response.json() if protocol_response.status == 200 else {}
                
                return {
                    "name": protocol_data.get("name", protocol),
                    "tvl": float(tvl_data),  # TVL endpoint returns just the number
                    "chain": protocol_data.get("chain", "Unknown"),
                    "timestamp": time.time()
                }

        except Exception as e:
            logger.error(f"Error fetching DEX data: {str(e)}")
            raise

    async def analyze_market_opportunity(
        self,
        token_pair: str,
        amount: float,
        max_slippage: float = 0.01,
        protocol: str = "ref-finance"
    ) -> Dict:
        """
        Analyze market opportunities for a token pair.
        
        Args:
            token_pair: Trading pair (e.g., "NEAR/USDC")
            amount: Trade amount in base token
            max_slippage: Maximum acceptable slippage
            protocol: DEX protocol to analyze (default: ref-finance)
            
        Returns:
            Dict containing opportunity analysis
        """
        [base_token, quote_token] = token_pair.split('/')
        
        try:
            # Get market data for both tokens
            base_data = await self.get_token_price(base_token)
            quote_data = await self.get_token_price(quote_token)
            
            # Get DEX data with specified protocol
            dex_data = await self.get_dex_data(protocol)
            
            # Calculate metrics
            price_impact = self._calculate_price_impact(
                amount,
                base_data["price"],
                dex_data["tvl"]
            )
            
            is_opportunity = price_impact < max_slippage
            
            return {
                "timestamp": time.time(),
                "pair": token_pair,
                "protocol": protocol,
                "market_data": {
                    "base_token": base_data,
                    "quote_token": quote_data,
                    "dex": dex_data
                },
                "analysis": {
                    "price_impact": price_impact,
                    "is_opportunity": is_opportunity,
                    "estimated_output": amount * base_data["price"] * (1 - price_impact),
                    "slippage_warning": price_impact > max_slippage
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing market: {str(e)}")
            raise

    def _calculate_price_impact(
        self,
        amount: float,
        price: float,
        tvl: float
    ) -> float:
        """Calculate estimated price impact of a trade."""
        trade_value = amount * price
        return min(trade_value / tvl, 0.1)  # Cap at 10% impact

    async def get_historical_prices(
        self,
        token_id: str,
        chain: str = "near",
        days: int = 7
    ) -> List[Dict]:
        """
        Get historical price data.
        
        Args:
            token_id: Token contract address or symbol
            chain: Blockchain (default: near)
            days: Number of days of history
            
        Returns:
            List of historical price points
        """
        session = await self._ensure_session()  # Ensure session exists
        
        try:
            url = f"{self.coins_url}/v2/tokens/{chain}/{token_id}/history"
            params = {"days": days}
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                
                data = await response.json()
                return data["prices"]
                
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise
