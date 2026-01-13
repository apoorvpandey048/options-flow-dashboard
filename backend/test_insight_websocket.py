"""
WebSocket test for Insight Sentry API
⚠️  WARNING: Ultra plan allows only 10 WebSocket connections per day!
Use this test sparingly.

Features available:
- 5 concurrent symbol subscriptions
- Real-time quotes
- Real-time series data (OHLCV)
- News feed (separate endpoint)
"""

import asyncio
import websockets
import json
import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config

class InsightWebSocketTester:
    """Test Insight Sentry WebSocket API"""
    
    MARKET_DATA_URL = "wss://realtime.insightsentry.com/live"
    NEWS_FEED_URL = "wss://realtime.insightsentry.com/newsfeed"
    
    def __init__(self):
        self.api_key = Config.INSIGHT_SENTRY_API_KEY
        self.message_count = 0
        self.start_time = time.time()
        
    async def test_market_data(self, duration_seconds: int = 30):
        """Test real-time market data WebSocket"""
        print(f"\n{'='*80}")
        print("  TESTING: Real-time Market Data WebSocket")
        print(f"{'='*80}\n")
        
        print(f"⏱️  Will run for {duration_seconds} seconds")
        print(f"📡 Connecting to {self.MARKET_DATA_URL}...")
        
        try:
            async with websockets.connect(self.MARKET_DATA_URL) as websocket:
                print("✅ Connected!")
                
                # Subscribe to 5 symbols (Ultra plan limit)
                # Mix of quotes and series data
                subscription_msg = {
                    "api_key": self.api_key,
                    "subscriptions": [
                        {
                            "code": "NASDAQ:AAPL",
                            "type": "quote"  # Real-time quote
                        },
                        {
                            "code": "NASDAQ:TSLA",
                            "type": "quote"
                        },
                        {
                            "code": "NASDAQ:SPY",
                            "type": "series",
                            "bar_type": "minute",
                            "bar_interval": 1,
                            "recent_bars": True,  # Get recent historical bars
                            "max_dp": 100  # Last 100 bars
                        },
                        {
                            "code": "NASDAQ:QQQ",
                            "type": "series",
                            "bar_type": "minute",
                            "bar_interval": 5
                        },
                        {
                            "code": "OPRA:AAPL260417C150.0",  # Option contract
                            "type": "quote"
                        }
                    ]
                }
                
                print(f"\n📤 Sending subscription for 5 symbols...")
                await websocket.send(json.dumps(subscription_msg))
                print("✅ Subscription sent!")
                
                # Start ping task
                ping_task = asyncio.create_task(self.send_ping(websocket))
                
                try:
                    # Collect messages for specified duration
                    end_time = time.time() + duration_seconds
                    
                    print(f"\n📥 Receiving data...\n")
                    
                    while time.time() < end_time:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=max(1, end_time - time.time())
                            )
                            
                            if message == "pong":
                                print("💓 Pong received")
                                continue
                            
                            # Parse JSON message
                            data = json.loads(message)
                            self.message_count += 1
                            
                            # Handle different message types
                            if 'server_time' in data:
                                server_time = datetime.fromtimestamp(data['server_time'] / 1000)
                                latency = time.time() * 1000 - data['server_time']
                                print(f"⏰ Server heartbeat: {server_time.strftime('%H:%M:%S')} (latency: {latency:.0f}ms)")
                            
                            elif 'message' in data:
                                print(f"📨 Server message: {data['message']}")
                            
                            elif 'code' in data:
                                # Market data update
                                if 'series' in data:
                                    # Series data (OHLCV)
                                    series = data['series']
                                    if series:
                                        bar = series[-1]  # Latest bar
                                        print(f"📊 {data['code']} [{data['bar_type']}]:")
                                        print(f"   Time: {datetime.fromtimestamp(bar['time']).strftime('%H:%M:%S')}")
                                        print(f"   OHLC: ${bar['open']:.2f} / ${bar['high']:.2f} / ${bar['low']:.2f} / ${bar['close']:.2f}")
                                        print(f"   Volume: {bar['volume']:,.0f}")
                                    
                                    if len(series) > 1:
                                        print(f"   (Received {len(series)} historical bars)")
                                
                                elif 'data' in data:
                                    # Quote data
                                    for quote in data['data']:
                                        print(f"💹 {quote['code']}:")
                                        print(f"   Last: ${quote.get('last_price', 'N/A')}")
                                        print(f"   Bid: ${quote.get('bid', 'N/A')} x {quote.get('bid_size', 0)}")
                                        print(f"   Ask: ${quote.get('ask', 'N/A')} x {quote.get('ask_size', 0)}")
                                        print(f"   Volume: {quote.get('volume', 0):,.0f}")
                                        print(f"   Change: {quote.get('change_percent', 0):.2f}%")
                                        print(f"   Status: {quote.get('status', 'N/A')}")
                            
                            print()  # Blank line between messages
                            
                        except asyncio.TimeoutError:
                            break
                    
                finally:
                    ping_task.cancel()
                    try:
                        await ping_task
                    except asyncio.CancelledError:
                        pass
                
                print(f"\n✅ Test completed!")
                print(f"   Messages received: {self.message_count}")
                print(f"   Duration: {time.time() - self.start_time:.1f}s")
                
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            import traceback
            traceback.print_exc()
    
    async def test_news_feed(self, duration_seconds: int = 30):
        """Test real-time news feed WebSocket"""
        print(f"\n{'='*80}")
        print("  TESTING: Real-time News Feed WebSocket")
        print(f"{'='*80}\n")
        
        print(f"⏱️  Will run for {duration_seconds} seconds")
        print(f"📰 Connecting to {self.NEWS_FEED_URL}...")
        
        try:
            async with websockets.connect(self.NEWS_FEED_URL) as websocket:
                print("✅ Connected!")
                
                # Send authentication
                auth_msg = {
                    "api_key": self.api_key
                }
                
                print(f"\n📤 Sending authentication...")
                await websocket.send(json.dumps(auth_msg))
                print("✅ Authentication sent!")
                print("📥 Receiving news feed (you'll get 10 most recent items immediately)...\n")
                
                # Start ping task
                ping_task = asyncio.create_task(self.send_ping(websocket))
                
                try:
                    end_time = time.time() + duration_seconds
                    news_count = 0
                    
                    while time.time() < end_time:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=max(1, end_time - time.time())
                            )
                            
                            if message == "pong":
                                print("💓 Pong received")
                                continue
                            
                            data = json.loads(message)
                            
                            if 'server_time' in data:
                                server_time = datetime.fromtimestamp(data['server_time'] / 1000)
                                print(f"⏰ Server heartbeat: {server_time.strftime('%H:%M:%S')}")
                            
                            elif isinstance(data, dict) and 'headline' in data:
                                # News item
                                news_count += 1
                                print(f"\n📰 NEWS #{news_count}:")
                                print(f"   Headline: {data.get('headline')}")
                                print(f"   Source: {data.get('source', 'N/A')}")
                                print(f"   Time: {datetime.fromtimestamp(data.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
                                print(f"   Symbols: {', '.join(data.get('symbols', []))}")
                                if data.get('url'):
                                    print(f"   URL: {data['url']}")
                            
                            elif isinstance(data, list):
                                # Multiple news items (initial batch)
                                print(f"📰 Received {len(data)} news items:")
                                for i, item in enumerate(data, 1):
                                    print(f"\n   [{i}] {item.get('headline')}")
                                    print(f"       Source: {item.get('source', 'N/A')}")
                                    print(f"       Symbols: {', '.join(item.get('symbols', []))}")
                                news_count += len(data)
                            
                        except asyncio.TimeoutError:
                            break
                    
                finally:
                    ping_task.cancel()
                    try:
                        await ping_task
                    except asyncio.CancelledError:
                        pass
                
                print(f"\n✅ News feed test completed!")
                print(f"   News items received: {news_count}")
                print(f"   Duration: {time.time() - self.start_time:.1f}s")
                
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            import traceback
            traceback.print_exc()
    
    async def send_ping(self, websocket):
        """Send periodic ping to keep connection alive"""
        while True:
            try:
                await asyncio.sleep(20)  # Every 20 seconds
                await websocket.send('ping')
                print("🏓 Ping sent")
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  Ping error: {e}")
                break

async def main():
    """Run WebSocket tests"""
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║        Insight Sentry WebSocket Test Suite                        ║
    ║        ⚠️  WARNING: Limited to 10 connections per day!             ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    print("Choose test mode:")
    print("  1. Market Data (5 concurrent symbols)")
    print("  2. News Feed")
    print("  3. Both (uses 2 connections)")
    print("  4. Cancel")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "4":
            print("Test cancelled.")
            return
        
        duration = int(input("Enter test duration in seconds (default: 30): ") or "30")
        
        tester = InsightWebSocketTester()
        
        if choice == "1":
            await tester.test_market_data(duration)
        elif choice == "2":
            await tester.test_news_feed(duration)
        elif choice == "3":
            await tester.test_market_data(duration)
            print("\n" + "="*80)
            print("  Switching to News Feed...")
            print("="*80)
            await asyncio.sleep(2)
            await tester.test_news_feed(duration)
        else:
            print("Invalid choice!")
            return
        
        print("\n✅ All tests completed!")
        print(f"\n⚠️  Remember: You have used WebSocket connection(s) from your daily limit of 10")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
