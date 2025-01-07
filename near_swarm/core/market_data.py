"""
Market Data Manager
Integrates with CoinGecko API for real-time market data.
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MarketDataManager:
    """Manages market data integration with CoinGecko."""
    
    # Token ID mappings for CoinGecko
    TOKEN_IDS = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "near": "near",
        "usdc": "usd-coin",
        "usdt": "tether",
        "ref": "ref-finance",
        "aurora": "aurora-near"
    }
    
    def __init__(self):
        """Initialize market data manager."""
        # API endpoints
        self.api_url = "https://api.coingecko.com/api/v3"
        
        # Session management
        self.session = None
        
        # Cache management
        self.cache = {}
        self.cache_ttl = 60  # Cache for 60 seconds
        
        # Rate limiting
        self.rate_limit_delay = 1.0  # Base delay between requests
        self.last_request_time = 0.0
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        data, timestamp = self.cache[key]
        return datetime.now() - timestamp < timedelta(seconds=self.cache_ttl)
    
    async def _rate_limit(self):
        """Ensure we don't exceed rate limits."""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    async def get_token_price(self, token: str = "near") -> Dict[str, Any]:
        """
        Get current token price and 24h volume from CoinGecko.
        
        Args:
            token: Token symbol (default: "near")
            
        Returns:
            Dict with price, volume, and market data
        """
        # Convert token to CoinGecko ID
        token_id = self.TOKEN_IDS.get(token.lower(), token.lower())
        
        cache_key = f"price_{token_id}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][0]
        
        await self._ensure_session()
        await self._rate_limit()
        
        try:
            # Get current price and market data
            async with self.session.get(
                f"{self.api_url}/coins/{token_id}"
            ) as response:
                if response.status == 429:  # Too Many Requests
                    logger.warning("Rate limit hit, increasing delay")
                    self.rate_limit_delay *= 1.5
                    await asyncio.sleep(2)
                    return await self.get_token_price(token)
                
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                
                data = await response.json()
                if not data or "market_data" not in data:
                    raise Exception(f"No data found for token: {token_id}")
                
                market_data = data["market_data"]
                
                result = {
                    "price": market_data["current_price"]["usd"],
                    "24h_volume": f"${market_data.get('total_volume', {}).get('usd', 0):,.1f}",
                    "24h_change": market_data.get("price_change_percentage_24h", 0),
                    "timestamp": int(time.time()),
                    "confidence": 0.9,  # Default high confidence
                    "market_trend": "upward" if market_data.get("price_change_percentage_24h", 0) > 0 else "downward",
                    "volatility": self._calculate_volatility_from_changes(market_data),
                }
                
                self.cache[cache_key] = (result, datetime.now())
                return result
                
        except Exception as e:
            logger.error(f"Error fetching price data: {str(e)}")
            raise
    
    def _calculate_volatility_from_changes(self, market_data: Dict[str, Any]) -> str:
        """Calculate volatility from price changes."""
        changes = [
            abs(market_data.get("price_change_percentage_24h", 0)),
            abs(market_data.get("price_change_percentage_7d", 0) / 7),
            abs(market_data.get("price_change_percentage_14d", 0) / 14),
            abs(market_data.get("price_change_percentage_30d", 0) / 30),
        ]
        
        avg_change = sum(c for c in changes if c is not None) / len([c for c in changes if c is not None])
        
        if avg_change < 2:  # Less than 2% daily change
            return "low"
        elif avg_change < 5:  # Less than 5% daily change
            return "medium"
        else:
            return "high"
    
    async def get_dex_data(self, dex: str = "ref-finance") -> Dict[str, Any]:
        """
        Get DEX-specific data from CoinGecko.
        
        Args:
            dex: DEX name (default: "ref-finance")
            
        Returns:
            Dict with DEX metrics
        """
        cache_key = f"dex_{dex}"
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key][0]
        
        await self._ensure_session()
        await self._rate_limit()
        
        try:
            # Get exchange data
            async with self.session.get(
                f"{self.api_url}/exchanges/{dex}"
            ) as response:
                if response.status != 200:
                    # If DEX not found, return estimated data
                    result = {
                        "tvl": 1_000_000,  # Default $1M TVL
                        "24h_volume": 100_000,  # Default $100K volume
                        "total_volume": 1_000_000,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    data = await response.json()
                    result = {
                        "tvl": float(data.get("trade_volume_24h_btc", 0) * 50000),  # Rough estimate
                        "24h_volume": float(data.get("trade_volume_24h_btc", 0) * 50000),
                        "total_volume": float(data.get("trade_volume_24h_btc", 0) * 50000),
                        "timestamp": datetime.now().isoformat(),
                    }
                
                self.cache[cache_key] = (result, datetime.now())
                return result
                
        except Exception as e:
            logger.error(f"Error fetching DEX data: {str(e)}")
            # Return estimated data on error
            return {
                "tvl": 1_000_000,  # Default $1M TVL
                "24h_volume": 100_000,  # Default $100K volume
                "total_volume": 1_000_000,
                "timestamp": datetime.now().isoformat(),
            }
    
    async def analyze_market_opportunity(
        self,
        token_pair: str,
        amount: float,
        max_slippage: float
    ) -> Dict[str, Any]:
        """
        Analyze market opportunity for a given token pair.
        
        Args:
            token_pair: Trading pair (e.g., "NEAR/USDC")
            amount: Trade amount
            max_slippage: Maximum acceptable slippage
            
        Returns:
            Dict with opportunity analysis
        """
        # Get market data
        [base_token, quote_token] = token_pair.split('/')
        
        try:
            # Get data for both tokens
            base_data = await self.get_token_price(base_token)
            quote_data = await self.get_token_price(quote_token)
            
            # Get DEX data
            dex_data = await self.get_dex_data("ref-finance")
            
            # Calculate metrics
            trade_value = amount * base_data["price"]
            price_impact = min(trade_value / dex_data["tvl"], 0.1)  # Cap at 10%
            
            # Analyze opportunity
            is_opportunity = (
                base_data["market_trend"] == "upward" and
                base_data["volatility"] != "high" and
                price_impact < max_slippage and
                base_data["confidence"] > 0.8
            )
            
            return {
                "analysis": {
                    "is_opportunity": is_opportunity,
                    "price_impact": price_impact,
                    "confidence": base_data["confidence"],
                    "market_data": {
                        "base_token": base_data,
                        "quote_token": quote_data,
                        "dex": dex_data
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market: {str(e)}")
            raise
