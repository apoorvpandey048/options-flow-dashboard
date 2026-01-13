"""
MarketStack API Test Script
Tests all available endpoints and features
"""
import os
import sys
from pprint import pprint
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_providers.marketstack_provider import MarketStackProvider

load_dotenv()

def print_section(title: str):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_connection():
    """Test API connection and validation"""
    print_section("1. Testing API Connection")
    
    api_key = os.getenv('MARKETSTACK_API_KEY')
    if not api_key:
        print("❌ MARKETSTACK_API_KEY not found in environment")
        return None
    
    provider = MarketStackProvider(api_key)
    
    if provider.validate_connection():
        print("✅ Connection test passed")
        return provider
    else:
        print("❌ Connection test failed")
        return None

def test_eod_data(provider: MarketStackProvider):
    """Test End-of-Day data retrieval"""
    print_section("2. Testing EOD Data")
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    print(f"\n📊 Fetching EOD data for: {', '.join(symbols)}")
    
    data = provider.get_eod_data(symbols, limit=1)
    
    if data:
        print(f"✅ Received data for {len(data)} symbols")
        for symbol, info in data.items():
            print(f"\n{symbol}:")
            print(f"  Name: {info.get('name')}")
            print(f"  Date: {info.get('date')}")
            print(f"  Close: ${info.get('close'):.2f}")
            print(f"  Volume: {info.get('volume'):,.0f}")
            print(f"  Exchange: {info.get('exchange')}")
    else:
        print("❌ No data received")

def test_ticker_info(provider: MarketStackProvider):
    """Test ticker information retrieval"""
    print_section("3. Testing Ticker Information")
    
    symbol = 'TSLA'
    print(f"\n🔍 Fetching ticker info for: {symbol}")
    
    info = provider.get_ticker_info(symbol)
    
    if info:
        print("✅ Ticker information:")
        pprint(info, indent=2)
    else:
        print("❌ No ticker info received")

def test_historical_data(provider: MarketStackProvider):
    """Test historical data retrieval"""
    print_section("4. Testing Historical Data")
    
    symbol = 'SPY'
    days = 5
    print(f"\n📈 Fetching {days} days of historical data for: {symbol}")
    
    data = provider.get_historical_data(symbol, days=days)
    
    if data:
        print(f"✅ Received {len(data)} historical data points")
        for i, point in enumerate(data[:3], 1):  # Show first 3
            print(f"\n  Day {i}:")
            print(f"    Date: {point.get('date')}")
            print(f"    Close: ${point.get('close'):.2f}")
            print(f"    Volume: {point.get('volume'):,.0f}")
    else:
        print("❌ No historical data received")

def test_exchanges(provider: MarketStackProvider):
    """Test exchange information retrieval"""
    print_section("5. Testing Exchange Information")
    
    print("\n🌍 Fetching exchange information...")
    
    exchanges = provider.get_exchanges()
    
    if exchanges:
        print(f"✅ Received {len(exchanges)} exchanges")
        print("\nFirst 5 exchanges:")
        for i, exchange in enumerate(exchanges[:5], 1):
            print(f"\n  {i}. {exchange.get('name')} ({exchange.get('acronym')})")
            print(f"     Country: {exchange.get('country')}")
            print(f"     Currency: {exchange.get('currency')}")
    else:
        print("❌ No exchange data received")

def test_realtime_quote(provider: MarketStackProvider):
    """Test real-time quote (will return EOD on free plan)"""
    print_section("6. Testing Real-Time Quote (Returns EOD on Free Plan)")
    
    symbol = 'NVDA'
    print(f"\n💹 Fetching quote for: {symbol}")
    
    quote = provider.get_realtime_quote(symbol)
    
    if quote:
        print("✅ Quote data:")
        pprint(quote, indent=2)
    else:
        print("❌ No quote data received")

def test_options_data(provider: MarketStackProvider):
    """Test options data (not supported)"""
    print_section("7. Testing Options Data (NOT SUPPORTED)")
    
    symbol = 'SPY'
    print(f"\n❓ Attempting to fetch options data for: {symbol}")
    
    data = provider.get_options_data(symbol)
    
    if not data:
        print("✅ Correctly returns empty - options data not available")

def test_usage_stats(provider: MarketStackProvider):
    """Display usage statistics"""
    print_section("8. API Usage Statistics")
    
    stats = provider.get_usage_stats()
    
    print(f"\n📊 Provider: {stats['provider']}")
    print(f"📦 Plan: {stats['plan']}")
    print(f"🔢 Requests Made: {stats['requests_made']}")
    print(f"📈 Monthly Limit: {stats['monthly_limit']}")
    print(f"✅ Remaining: {stats['remaining']}")
    
    print("\n✅ Features Available:")
    for feature in stats['features']:
        print(f"  • {feature}")
    
    print("\n❌ Limitations:")
    for limitation in stats['limitations']:
        print(f"  • {limitation}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("  MARKETSTACK API COMPREHENSIVE TEST")
    print("="*80)
    print("\n⚠️  WARNING: This will use ~8-10 API requests from your 100/month limit")
    
    response = input("\nContinue with tests? (y/n): ")
    if response.lower() != 'y':
        print("Tests cancelled")
        return
    
    # Test connection
    provider = test_connection()
    if not provider:
        print("\n❌ Cannot proceed without valid connection")
        return
    
    # Run all tests
    try:
        test_eod_data(provider)
        test_ticker_info(provider)
        test_historical_data(provider)
        test_exchanges(provider)
        test_realtime_quote(provider)
        test_options_data(provider)
        test_usage_stats(provider)
        
        # Final summary
        print_section("TEST SUMMARY")
        print(f"\n✅ All tests completed")
        print(f"📊 Total API requests made: {provider.requests_count}")
        print(f"💰 Remaining requests: {provider.max_requests_per_month - provider.requests_count}/100")
        
        print("\n" + "="*80)
        print("  CONCLUSION")
        print("="*80)
        print("\n✅ MarketStack API works for:")
        print("  • Getting stock prices (EOD)")
        print("  • Historical price data for backtesting")
        print("  • Company/ticker reference information")
        
        print("\n❌ MarketStack API CANNOT be used for:")
        print("  • Real-time options flow monitoring")
        print("  • Intraday/minute-level data")
        print("  • Options chain data")
        print("  • Put/call ratios")
        
        print("\n💡 RECOMMENDATION:")
        print("  Use MarketStack for:")
        print("  1. Strategy backtester (historical stock prices)")
        print("  2. End-of-day position valuations")
        print("  3. Reference data enrichment")
        print("\n  For options flow, you still need:")
        print("  - Polygon.io ($199+/month)")
        print("  - Tradier (with brokerage account)")
        print("  - CBOE DataFeed (enterprise)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during tests: {str(e)}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
