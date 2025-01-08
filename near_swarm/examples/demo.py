"""
NEAR Swarm Intelligence Demo
Demonstrates voice-enabled portfolio management and multi-agent decision making
"""

import os
import sys
import asyncio
import logging
from typing import Optional
from near_swarm.examples.simple_strategy import run_simple_strategy
from near_swarm.templates.near_portfolio_advisor import main as run_portfolio_advisor

# Configure logging
import colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s:%(name)s:%(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))
logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

async def run_demo(demo_type: Optional[str] = None):
    """Run the NEAR Swarm Intelligence demo."""
    
    print("\n=== 🤖 NEAR Swarm Intelligence Demo ===")
    
    if not demo_type:
        print("\nAvailable Demos:")
        print("1. Voice Portfolio Assistant (voice)")
        print("2. Multi-Agent Strategy Demo (strategy)")
        print("3. Run Both Demos (all)")
        choice = input("\nEnter your choice (1-3 or demo name): ").lower()
        
        if choice in ['1', 'voice']:
            demo_type = 'voice'
        elif choice in ['2', 'strategy']:
            demo_type = 'strategy'
        elif choice in ['3', 'all']:
            demo_type = 'all'
        else:
            print("Invalid choice. Please try again.")
            return
    
    if demo_type in ['voice', 'all']:
        print("\n=== 🎙️ Starting Voice Portfolio Assistant ===")
        print("This demo shows how AI can provide natural voice interactions")
        print("for managing your NEAR portfolio and getting market insights.")
        input("\nPress Enter to start the voice assistant...")
        
        try:
            await run_portfolio_advisor()
        except KeyboardInterrupt:
            print("\n\n✅ Voice assistant demo completed!")
    
    if demo_type in ['strategy', 'all']:
        print("\n=== 🧠 Starting Multi-Agent Strategy Demo ===")
        print("This demo shows how multiple AI agents work together to:")
        print("1. Analyze market conditions")
        print("2. Assess transaction risks")
        print("3. Optimize strategy parameters")
        print("4. Reach consensus on actions")
        input("\nPress Enter to start the strategy demo...")
        
        try:
            result = await run_simple_strategy()
            
            # Provide context about the demo results
            print("\n=== 🎯 Demo Analysis ===")
            print("\nWhat we just saw:")
            print("1. Multiple AI agents analyzed the proposed transaction")
            print("2. Each agent provided independent reasoning")
            print("3. The swarm reached a collective decision")
            
            if result['consensus']:
                print("\n✅ The swarm approved the transaction because:")
            else:
                print("\n❌ The swarm rejected the transaction because:")
            
            for i, reason in enumerate(result['reasons'], 1):
                print(f"\nAgent {i}: {reason}")
            
            print(f"\nFinal Approval Rate: {result['approval_rate']:.2%}")
            
        except Exception as e:
            logger.error(f"Strategy demo error: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            demo_type = sys.argv[1]
        else:
            demo_type = None
        
        asyncio.run(run_demo(demo_type))
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise 