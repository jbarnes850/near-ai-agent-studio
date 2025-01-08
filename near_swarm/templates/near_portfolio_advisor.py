"""
NEAR Portfolio Advisor
A voice-enabled AI agent that provides personalized portfolio insights and market analysis.
"""

import os
import signal
import sys
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from near_swarm.core.agent import Agent, AgentConfig
from near_swarm.core.market_data import MarketDataManager
from near_swarm.core.web_search import WebSearchManager
from dotenv import load_dotenv

class PortfolioManager:
    """Manages portfolio analysis and market data."""
    
    def __init__(self):
        """Initialize portfolio manager."""
        self.agent = Agent(
            AgentConfig(
                network=os.getenv("NEAR_NETWORK", "testnet"),
                account_id=os.getenv("NEAR_ACCOUNT_ID"),
                private_key=os.getenv("NEAR_PRIVATE_KEY"),
                rpc_url=os.getenv("NEAR_RPC_URL"),
                llm_provider=os.getenv("LLM_PROVIDER", "hyperbolic"),
                llm_api_key=os.getenv("LLM_API_KEY"),
                llm_model=os.getenv("LLM_MODEL", "deepseek-ai/DeepSeek-V3"),
                llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                llm_max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
                api_url=os.getenv("LLM_API_URL")
            )
        )
        self.market_data = MarketDataManager()
        self.web_search = WebSearchManager(max_results=3)
    
    async def get_portfolio_status(self) -> str:
        """Get current portfolio status."""
        try:
            await self.agent.start()
            balance = await self.agent.check_balance()
            near_data = await self.market_data.get_token_price("near")
            return f"NEAR Balance: {balance} NEAR (${float(balance) * near_data['price']:.2f})"
        except Exception as e:
            return f"Error getting portfolio status: {e}"
    
    async def search_news(self, query: str) -> str:
        """Search for news and market information."""
        try:
            results = await self.web_search.search_news(query)
            if results:
                response = "Here's what I found:\n\n"
                for result in results:
                    response += f"• {result['title']}\n"
                    response += f"  {result['snippet']}\n\n"
                return response
            return "I couldn't find any relevant information."
        except Exception as e:
            return f"Error searching news: {e}"
    
    async def close(self):
        """Clean up resources."""
        if self.web_search:
            await self.web_search.close()

def handle_user_input(transcript: str, portfolio: PortfolioManager):
    """Handle user input and trigger appropriate actions."""
    print(f"User: {transcript}")
    
    # Look for portfolio/market related queries
    query = transcript.lower()
    
    if any(term in query for term in ["balance", "portfolio", "holdings"]):
        asyncio.create_task(
            handle_portfolio_query(portfolio)
        )
    elif any(term in query for term in ["news", "latest", "updates"]):
        asyncio.create_task(
            handle_news_query(portfolio, "NEAR Protocol latest news")
        )
    elif any(term in query for term in ["price", "market", "trend"]):
        asyncio.create_task(
            handle_news_query(portfolio, "NEAR Protocol price analysis")
        )

async def handle_portfolio_query(portfolio: PortfolioManager):
    """Handle portfolio-related queries."""
    status = await portfolio.get_portfolio_status()
    print(f"Agent: Here's your current portfolio status:\n{status}")

async def handle_news_query(portfolio: PortfolioManager, query: str):
    """Handle news-related queries."""
    results = await portfolio.search_news(query)
    print(f"Agent: {results}")

async def main():
    load_dotenv()
    
    # Check required environment variables
    AGENT_ID = os.getenv("AGENT_ID")
    API_KEY = os.getenv("ELEVENLABS_API_KEY")
    
    if not AGENT_ID:
        sys.stderr.write("AGENT_ID environment variable must be set\n")
        sys.exit(1)
    
    if not API_KEY:
        sys.stderr.write("ELEVENLABS_API_KEY not set, assuming the agent is public\n")
    
    # Initialize portfolio manager
    portfolio = PortfolioManager()
    
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=API_KEY)
        
        # Initialize conversation
        conversation = Conversation(
            client,
            AGENT_ID,
            requires_auth=bool(API_KEY),
            audio_interface=DefaultAudioInterface(),
            callback_agent_response=lambda response: print(f"Agent: {response}"),
            callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
            callback_user_transcript=lambda transcript: handle_user_input(transcript, portfolio)
        )
        
        # Get initial portfolio status
        status = await portfolio.get_portfolio_status()
        print("\n=== 🎙️ NEAR Portfolio Voice Assistant ===")
        print("\n📊 Current Portfolio Status:")
        print(status)
        print("\n💬 Voice Commands You Can Try:")
        print("• 'What's my portfolio balance?'")
        print("• 'Show me the latest NEAR news'")
        print("• 'What are the current market trends?'")
        print("\n🎯 How to Use:")
        print("1. Wait for the microphone icon 🎤 to appear")
        print("2. Speak your question clearly")
        print("3. Wait for the AI to respond")
        print("4. Press Ctrl+C when you want to end the conversation")
        print("\n🚀 Ready! Waiting for your voice command...\n")
        
        # Start conversation
        conversation.start_session()
        
        # Set up clean shutdown
        signal.signal(
            signal.SIGINT,
            lambda sig, frame: conversation.end_session()
        )
        
        # Wait for conversation to end
        conversation_id = conversation.wait_for_session_end()
        print(f"Conversation ID: {conversation_id}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await portfolio.close()

if __name__ == "__main__":
    asyncio.run(main()) 