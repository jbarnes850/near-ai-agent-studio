"""
NEAR Swarm Intelligence Demo
Demonstrates plugin-based agents with voice interaction and market analysis.

This example shows:
1. How to load and use multiple plugins
2. Voice-enabled portfolio management
3. Market analysis and decision making
4. Proper error handling and cleanup
5. Best practices for logging

Usage:
1. Install required plugins:
   ```bash
   near-swarm plugins install ./portfolio-advisor
   near-swarm plugins install ./market-analyzer
   ```

2. Run demo:
   ```bash
   # Run specific demo
   near-swarm demo voice     # Voice portfolio assistant
   near-swarm demo market    # Market analysis
   near-swarm demo all       # Run all demos
   ```

Integration Patterns:
- Plugin loading and initialization
- Voice interface integration
- Market data processing
- Error handling and logging

Testing:
1. Unit tests: Test core functionality
2. Integration tests: Test plugin interactions
3. End-to-end tests: Test full demo flow
"""

import os
import sys
import asyncio
import logging
from typing import Optional, Dict, Any
from near_swarm.plugins import PluginLoader
from near_swarm.core.exceptions import AgentError

# Configure logging
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))
logger = logging.getLogger(__name__)
logger.handlers = []  # Clear existing handlers
logger.addHandler(handler)
logger.setLevel(logging.INFO)

async def run_voice_demo() -> None:
    """Run the voice-enabled portfolio assistant demo."""
    loader = PluginLoader()
    plugin = None
    
    try:
        print("\n=== 🎙️ Voice Portfolio Assistant ===")
        print("This demo shows how AI can provide natural voice interactions")
        print("for managing your NEAR portfolio and getting market insights.")
        input("\nPress Enter to start the voice assistant...")
        
        # Load portfolio advisor plugin
        plugin = await loader.load_plugin("portfolio-advisor")
        
        # Start voice interaction
        await plugin.evaluate({
            "operation": "start_voice",
            "mode": "interactive"
        })
        
    except AgentError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if plugin:
            await loader.unload_plugin("portfolio-advisor")

async def run_market_demo() -> None:
    """Run the market analysis demo."""
    loader = PluginLoader()
    plugin = None
    
    try:
        print("\n=== 🧠 Market Analysis Demo ===")
        print("This demo shows how AI analyzes:")
        print("1. Market conditions")
        print("2. Trading opportunities")
        print("3. Risk factors")
        input("\nPress Enter to start the analysis...")
        
        # Load market analyzer plugin
        plugin = await loader.load_plugin("market-analyzer")
        
        # Run market analysis
        result = await plugin.evaluate({
            "operation": "analyze",
            "pair": "NEAR/USDC",
            "amount": "100"
        })
        
        # Display results
        print("\n=== Analysis Results ===")
        if result["recommendation"]["action"] == "buy":
            print("\n✅ Buy Recommendation")
            print(f"Target Price: ${result['recommendation']['target_price']}")
            print(f"Stop Loss: ${result['recommendation']['stop_loss']}")
        else:
            print("\n⚠️ Hold Recommendation")
            print("Waiting for better conditions")
        
        print("\nMarket Analysis:")
        for factor in result["analysis"]:
            print(f"• {factor}")
        
        print("\nRisk Assessment:")
        print(f"• Level: {result['risk']['level']}")
        for factor in result['risk']['factors']:
            print(f"• {factor}")
        
    except AgentError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        if plugin:
            await loader.unload_plugin("market-analyzer")

async def run_demo(demo_type: Optional[str] = None) -> None:
    """Run the NEAR Swarm Intelligence demo."""
    print("\n=== 🤖 NEAR Swarm Intelligence Demo ===")
    
    if not demo_type:
        print("\nAvailable Demos:")
        print("1. Voice Portfolio Assistant (voice)")
        print("2. Market Analysis Demo (market)")
        print("3. Run Both Demos (all)")
        choice = input("\nEnter your choice (1-3 or demo name): ").lower()
        
        if choice in ['1', 'voice']:
            demo_type = 'voice'
        elif choice in ['2', 'market']:
            demo_type = 'market'
        elif choice in ['3', 'all']:
            demo_type = 'all'
        else:
            print("Invalid choice. Please try again.")
            return
    
    try:
        if demo_type in ['voice', 'all']:
            await run_voice_demo()
            
        if demo_type in ['market', 'all']:
            await run_market_demo()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
        raise

if __name__ == "__main__":
    try:
        demo_type = sys.argv[1] if len(sys.argv) > 1 else None
        asyncio.run(run_demo(demo_type))
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise 