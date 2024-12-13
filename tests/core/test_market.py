"""Quick market data test script."""

import asyncio
import logging
from near_swarm.core.market_data import MarketDataManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_tvl(tvl: float) -> str:
    """Format TVL value."""
    if tvl >= 1_000_000_000:
        return f"${tvl/1_000_000_000:.2f}B"
    if tvl >= 1_000_000:
        return f"${tvl/1_000_000:.2f}M"
    return f"${tvl:,.2f}"

async def main():
    """Test market data integration."""
    manager = MarketDataManager()
    try:
        # Test token prices
        tokens_to_test = [
            'btc',    # Bitcoin
            'eth',    # Ethereum
            'near',   # NEAR Protocol
            'usdc'    # Stablecoin
        ]
        
        print("\n=== Token Prices ===")
        for token in tokens_to_test:
            try:
                data = await manager.get_token_price(token)
                print(f'{token.upper()}: ${data["price"]:,.2f}')
            except Exception as e:
                logger.error(f"Error fetching {token}: {e}")

        # Test major DEXes
        dexes_to_test = [
            'uniswap',     # Global liquidity benchmark
            'ref-finance'  # NEAR ecosystem DEX
        ]

        print("\n=== DEX TVL Data ===")
        for dex in dexes_to_test:
            try:
                data = await manager.get_dex_data(dex)
                print(f"{data['name']}: {format_tvl(data['tvl'])} TVL")
            except Exception as e:
                logger.error(f"Error fetching {dex} data: {e}")

    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main()) 