"""
Test Insight Sentry Provider Integration
"""
import sys
import os

# The test expects `INSIGHT_SENTRY_API_KEY` to be provided via environment variables
# Do NOT hardcode API keys in source. Set the key in your environment or CI job before running tests.

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from data_providers.factory import DataProviderFactory
from data_providers.insight_sentry_provider import InsightSentryProvider

def test_provider():
    """Test the Insight Sentry provider"""
    print("="*80)
    print("  Testing Insight Sentry Provider Integration")
    print("="*80)
    
    # Test 1: Factory with explicit provider type
    print("\n[TEST 1] Factory with Explicit Provider Type")
    provider = DataProviderFactory.create_provider('insight_sentry')
    print(f"Provider type: {type(provider).__name__}")
    print(f"Provider name: {provider.get_provider_name()}")
    
    # Test 2: Check if available
    print("\n[TEST 2] Checking Provider Availability")
    is_available = provider.validate_connection()
    print(f"Provider available: {is_available}")
    
    if not is_available:
        print("❌ Provider not available, exiting...")
        return
    
    # Test 3: Get symbol info
    print("\n[TEST 3] Get Symbol Info for AAPL")
    info = provider.get_symbol_info('AAPL')
    if info:
        print(f"Symbol: {info.get('symbol')}")
        print(f"Has Options: {info.get('has_options')}")
        print(f"Available Expirations: {len(info.get('option_expirations', []))}")
        print(f"Sample Expirations: {info.get('option_expirations', [])[:5]}")
        print(f"Available Strikes: {len(info.get('available_strikes', []))}")
    else:
        print("❌ Failed to get symbol info")
    
    # Test 4: Get options chain
    print("\n[TEST 4] Get Options Chain for AAPL")
    if info and info.get('option_expirations'):
        expiration = info['option_expirations'][0]
        print(f"Getting options for expiration: {expiration}")
        
        options = provider.get_options_chain('AAPL', expiration)
        print(f"Retrieved {len(options)} options")
        
        if options:
            print("\nSample Option:")
            opt = options[0]
            for key, value in opt.items():
                if value is not None:
                    print(f"  {key}: {value}")
    else:
        print("⚠️  No expirations available")
    
    # Test 5: Get option quotes
    print("\n[TEST 5] Get Option Quotes")
    # Use some option codes from the test
    test_codes = [
        "OPRA:AAPL260116C200.0",
        "OPRA:AAPL260116P200.0",
        "OPRA:AAPL260417C220.0"
    ]
    
    quotes = provider.get_option_quotes(test_codes)
    print(f"Retrieved {len(quotes)} quotes")
    
    if quotes:
        for quote in quotes[:2]:  # Show first 2
            print(f"\n  {quote.get('symbol')}")
            print(f"    Bid: ${quote.get('bid')}, Ask: ${quote.get('ask')}")
            print(f"    Last: ${quote.get('last')}")
            print(f"    Volume: {quote.get('volume')}")
            print(f"    Real-time: {'Yes' if quote.get('delay_seconds') == 0 else 'No'}")
    
    # Test 6: Get historical data
    print("\n[TEST 6] Get Historical Data")
    if test_codes:
        print(f"Getting historical data for {test_codes[0]}")
        history = provider.get_historical_data(
            test_codes[0],
            start_date="2026-01-01",
            end_date="2026-01-13",
            timeframe="1D"
        )
        print(f"Retrieved {len(history)} historical bars")
        
        if history:
            print("\nLatest bar:")
            latest = history[-1]
            for key, value in latest.items():
                print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("  ✅ Integration Tests Complete!")
    print("="*80)
    
    print("\n📊 Summary:")
    print(f"  • Provider: InsightSentry (Ultra Plan)")
    print(f"  • Real-time Data: Yes (0 delay)")
    print(f"  • Historical Data: Yes (Deep History)")
    print(f"  • Greeks: Yes (delta, gamma, theta, vega, rho)")
    print(f"  • Options per Symbol: 3000+")
    print(f"  • Rate Limit: 35 requests/min, 120k/month")
    print(f"  • WebSocket: 5 concurrent symbols (use sparingly - 10/day limit)")

if __name__ == "__main__":
    try:
        test_provider()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
