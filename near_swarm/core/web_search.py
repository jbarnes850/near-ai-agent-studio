"""
Web Search Manager
Simple web search integration using DuckDuckGo.
"""

import asyncio
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

class WebSearchManager:
    """
    Manages web searches using DuckDuckGo.
    Provides simple, privacy-focused web search capabilities.
    """

    def __init__(self, max_results: int = 5):
        """Initialize web search manager.
        
        Args:
            max_results: Maximum number of results to return
        """
        self.max_results = max_results
        self._session = None
        
        # DuckDuckGo search URL
        self.search_url = "https://html.duckduckgo.com/html/"
        
        # Headers to mimic browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session
    
    async def search(
        self,
        query: str,
        time_filter: str = None  # Options: d (day), w (week), m (month)
    ) -> List[Dict[str, str]]:
        """
        Perform web search using DuckDuckGo.
        
        Args:
            query: Search query
            time_filter: Optional time filter (d/w/m)
            
        Returns:
            List of search results with title, snippet, and URL
        """
        try:
            session = await self._get_session()
            
            # Add time filter if specified
            params = {
                "q": query,
                "kl": "us-en"  # Language/region
            }
            if time_filter:
                params["df"] = time_filter
            
            # Make search request
            async with session.post(
                self.search_url,
                data=params
            ) as response:
                if response.status != 200:
                    return []
                
                # Parse results
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                results = []
                for result in soup.select(".result"):
                    # Extract title and URL
                    title_elem = result.select_one(".result__title a")
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get("href", "")
                    
                    # Extract snippet
                    snippet_elem = result.select_one(".result__snippet")
                    snippet = (
                        snippet_elem.get_text(strip=True)
                        if snippet_elem else ""
                    )
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })
                    
                    if len(results) >= self.max_results:
                        break
                
                return results
                
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    async def search_news(
        self,
        query: str,
        max_age_days: int = 7
    ) -> List[Dict[str, str]]:
        """
        Search for recent news articles.
        
        Args:
            query: Search query
            max_age_days: Maximum age of articles in days
            
        Returns:
            List of news articles
        """
        # Add news-specific terms
        news_query = f"{query} news article"
        
        # Use appropriate time filter
        time_filter = (
            "d" if max_age_days == 1
            else "w" if max_age_days <= 7
            else "m"
        )
        
        return await self.search(news_query, time_filter)
    
    async def get_market_news(
        self,
        symbol: str = "NEAR",
        max_age_days: int = 1
    ) -> List[Dict[str, str]]:
        """
        Get recent market news for a specific token.
        
        Args:
            symbol: Token symbol
            max_age_days: Maximum age of news in days
            
        Returns:
            List of relevant news articles
        """
        query = f"{symbol} Protocol crypto price news analysis"
        return await self.search_news(query, max_age_days)
    
    async def close(self):
        """Clean up resources."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None 