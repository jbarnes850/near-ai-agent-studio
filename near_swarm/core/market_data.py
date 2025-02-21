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
        
        # Cache management - Increase cache duration to reduce API calls
        self.cache = {}
        self.cache_ttl = 900  # Cache for 15 minutes for free API
        
        # Rate limiting with exponential backoff
        self.rate_limit_delay = 30.0  # Increase base delay for free API
        self.last_request_time = 0.0
        self.max_retries = 5  # Increase max retries
        self.max_delay = 120.0  # Maximum delay between retries
        self.request_count = 0
        self.reset_window = 60.0  # Reset counter every minute
        self.last_reset = time.time()
        self.max_requests_per_minute = 10  # Free API limit
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        return None
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self.cache:
            return False
        data, timestamp = self.cache[key]
        return datetime.now() - timestamp < timedelta(seconds=self.cache_ttl)
    
    async def _rate_limit(self):
        """Enhanced rate limiting with exponential backoff."""
        now = time.time()
        
        # Reset counter if window has passed
        if now - self.last_reset >= self.reset_window:
            self.request_count = 0
            self.last_reset = now
        
        # Check if we've exceeded rate limit
        if self.request_count >= self.max_requests_per_minute:
            delay = self.rate_limit_delay * (2 ** (self.request_count - self.max_requests_per_minute))
            delay = min(delay, self.max_delay)
            logger.info(f"Rate limit reached. Waiting {delay:.1f} seconds...")
            await asyncio.sleep(delay)
            self.request_count = 0
            self.last_reset = time.time()
        
        # Add delay between requests
        time_since_last = now - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    async def get_token_price(self, token: str = "near", retry_count: int = 0) -> Dict[str, Any]:
        """
        Get current token price and 24h volume from CoinGecko.
        Falls back to cached data if rate limited.
        
        Args:
            token: Token symbol (default: "near")
            retry_count: Number of retries attempted (internal use)
            
        Returns:
            Dict with price, volume, and market data
        """
        try:
            # Convert token to CoinGecko ID
            token_id = self.TOKEN_IDS.get(token.lower(), token.lower())
            
            cache_key = f"price_{token_id}"
            if self._is_cache_valid(cache_key):
                logger.info("Using cached price data")
                return self.cache[cache_key][0]
            
            await self._ensure_session()
            await self._rate_limit()
            
            # Get current price and market data
            async with self.session.get(
                f"{self.api_url}/coins/{token_id}"
            ) as response:
                if response.status == 429:  # Too Many Requests
                    logger.warning(f"Rate limit hit, using cached data")
                    if cache_key in self.cache:
                        return self.cache[cache_key][0]
                    
                    # If no cache, return estimated data
                    return {
                        "price": 3.30,  # Estimated NEAR price
                        "volume_24h": 1000000,
                        "market_cap": 3000000000,
                        "price_change_24h": 0.0,
                        "last_updated": datetime.now().isoformat(),
                        "confidence": 50.0  # Lower confidence for estimated data
                    }
                
                if response.status != 200:
                    raise Exception(f"API error: {response.status}")
                
                data = await response.json()
                if not data or "market_data" not in data:
                    raise Exception(f"No data found for token: {token_id}")
                
                market_data = data["market_data"]
                
                result = {
                    "price": market_data["current_price"].get("usd", 0),
                    "volume_24h": market_data["total_volume"].get("usd", 0),
                    "market_cap": market_data["market_cap"].get("usd", 0),
                    "price_change_24h": market_data["price_change_percentage_24h"],
                    "last_updated": market_data["last_updated"],
                    "confidence": 90.0  # Base confidence score
                }
                
                # Cache the result
                self.cache[cache_key] = (result, datetime.now())
                return result
                
        except Exception as e:
            logger.error(f"Error fetching price data: {str(e)}")
            
            # Fallback to cached data if available
            if cache_key in self.cache:
                logger.warning("Using cached data due to error")
                return self.cache[cache_key][0]
            
            # Return estimated data if no cache available
            return {
                "price": 3.30,  # Estimated NEAR price
                "volume_24h": 1000000,
                "market_cap": 3000000000,
                "price_change_24h": 0.0,
                "last_updated": datetime.now().isoformat(),
                "confidence": 50.0  # Lower confidence for estimated data
            }
    
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
        try:
            cache_key = f"dex_{dex}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key][0]
            
            await self._ensure_session()
            await self._rate_limit()
            
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
        finally:
            # Don't close the session here as it may be reused
            pass
    
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
        try:
            # Get market data
            [base_token, quote_token] = token_pair.split('/')
            
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
        finally:
            # Don't close the session here as it may be reused
            pass
    
    async def get_market_context(self) -> Dict[str, Any]:
        """Get comprehensive market context."""
        try:
            # Get NEAR price and market data
            near_data = await self.get_token_price("near")
            
            # Get DEX data
            dex_data = await self.get_dex_data("ref-finance")
            
            # Calculate market metrics
            volatility = self._calculate_volatility_from_changes(near_data)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "near": {
                    "price": near_data["price"],
                    "market_trend": near_data.get("market_trend", "stable"),
                    "confidence": near_data.get("confidence", 0.8),
                    "volatility": volatility
                },
                "market": {
                    "dex_tvl": dex_data["tvl"],
                    "24h_volume": dex_data["24h_volume"],
                    "network_load": "moderate"  # TODO: Implement network load calculation
                },
                "indicators": {
                    "trend_strength": "medium",  # TODO: Implement trend strength calculation
                    "market_sentiment": "neutral",  # TODO: Implement sentiment analysis
                    "risk_level": "medium"  # TODO: Implement risk level calculation
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting market context: {str(e)}")
            # Return default context on error
            return {
                "timestamp": datetime.now().isoformat(),
                "near": {
                    "price": 0.0,
                    "market_trend": "unknown",
                    "confidence": 0.5,
                    "volatility": "unknown"
                },
                "market": {
                    "dex_tvl": 0.0,
                    "24h_volume": 0.0,
                    "network_load": "unknown"
                },
                "indicators": {
                    "trend_strength": "unknown",
                    "market_sentiment": "unknown",
                    "risk_level": "unknown"
                }
            }
        finally:
            # Don't close the session here as it may be reused
            pass