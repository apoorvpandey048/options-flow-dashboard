"""
Test WebSocket integration for Insight Sentry
"""
import os
import asyncio
from data_providers.insight_sentry_websocket import InsightSentryWebSocket

# Test callback
async def test_callback(symbol: str, data: dict):
    print(f"Received update: {symbol}")
    print(f"  Price: ${data.get('last_price')}")
    print(f"  Volume: {data.get('volume')}")
    print(f"  Bid: ${data.get('bid')} / Ask: ${data.get('ask')}")
    print()

async def main():
    # Get API key from environment
    api_key = os.environ.get('INSIGHT_SENTRY_API_KEY')
    if not api_key:
        print("ERROR: INSIGHT_SENTRY_API_KEY environment variable not set")
        return
    
    print("Testing Insight Sentry WebSocket Integration")
    print("=" * 50)
    print()
    
    # Create WebSocket client
    ws_client = InsightSentryWebSocket(
        rest_api_key=api_key,
        callback=test_callback
    )
    
    # Subscribe to test symbols
    symbols = ["NASDAQ:AAPL", "AMEX:SPY", "NASDAQ:QQQ", "NASDAQ:TSLA"]
    ws_client.subscribe_symbols(symbols)
    
    print(f"Subscribed to: {', '.join(symbols)}")
    print("Waiting for real-time updates... (Press Ctrl+C to stop)")
    print()
    
    # Run for 60 seconds to capture market data
    try:
        task = asyncio.create_task(ws_client.connect())
        await asyncio.sleep(60)
        await ws_client.stop()
        print("\nTest completed successfully!")
    except KeyboardInterrupt:
        print("\nStopping...")
        await ws_client.stop()

if __name__ == "__main__":
    asyncio.run(main())
