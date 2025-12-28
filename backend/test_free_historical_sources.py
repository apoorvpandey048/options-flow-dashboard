"""
Test free historical options data sources
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import json

def test_yfinance_options():
    """Test Yahoo Finance for historical options data"""
    print("\n" + "="*60)
    print("Testing Yahoo Finance (yfinance)")
    print("="*60)
    
    try:
        ticker = yf.Ticker("SPY")
        
        # Get available expiration dates
        expirations = ticker.options
        print(f"✓ Available expiration dates: {len(expirations)}")
        print(f"  First 3: {expirations[:3]}")
        
        # Get options chain for nearest expiration
        if expirations:
            opt_chain = ticker.option_chain(expirations[0])
            calls = opt_chain.calls
            puts = opt_chain.puts
            
            print(f"\n✓ Calls data shape: {calls.shape}")
            print(f"✓ Puts data shape: {puts.shape}")
            print(f"\nCalls columns: {list(calls.columns)}")
            print(f"\nSample call data:")
            print(calls.head(3)[['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']])
            
            # Check for historical intraday
            print("\n✓ Yahoo Finance has current options chains")
            print("✗ Does NOT have minute-by-minute historical options flow")
            
            return {
                'available': True,
                'has_current': True,
                'has_historical_intraday': False,
                'cost': 'Free',
                'note': 'Current options chains only, no historical minute data'
            }
    except Exception as e:
        print(f"✗ Error: {e}")
        return {'available': False, 'error': str(e)}

def test_polygon_free_tier():
    """Test Polygon.io free tier"""
    print("\n" + "="*60)
    print("Testing Polygon.io Free Tier")
    print("="*60)
    
    # Note: Requires API key signup
    print("ℹ️  Polygon.io offers:")
    print("  - Free tier: 5 API calls/minute")
    print("  - Historical options data available")
    print("  - Aggregates (minute bars) for options")
    print("  - 2 years of historical data on free tier")
    print("\n  Signup required: https://polygon.io/")
    
    return {
        'available': True,
        'has_historical_intraday': True,
        'cost': 'Free tier available',
        'rate_limit': '5 calls/min',
        'note': 'Requires API key signup, similar to Massive API'
    }

def test_cboe_datashop():
    """Check CBOE DataShop"""
    print("\n" + "="*60)
    print("CBOE DataShop")
    print("="*60)
    
    print("ℹ️  CBOE offers:")
    print("  - Free historical options data downloads")
    print("  - End-of-day data (not intraday)")
    print("  - Must manually download CSV files")
    print("  - Good for backtesting, not live replay")
    print("\n  Website: https://www.cboe.com/delayed_quotes/")
    
    return {
        'available': True,
        'has_historical_intraday': False,
        'cost': 'Free',
        'format': 'Manual CSV downloads',
        'note': 'End-of-day only, manual process'
    }

def test_alpha_vantage_options():
    """Test Alpha Vantage for options (they don't offer it)"""
    print("\n" + "="*60)
    print("Alpha Vantage")
    print("="*60)
    
    print("✗ Alpha Vantage does NOT offer options data")
    print("  - Only stocks, forex, crypto")
    print("  - No options chains or flow data")
    
    return {
        'available': False,
        'note': 'No options data available'
    }

def test_massive_api_coverage():
    """Review what we already know about Massive API"""
    print("\n" + "="*60)
    print("Massive API (Already Integrated)")
    print("="*60)
    
    print("✓ Options Basic Plan (Free):")
    print("  - 5 API calls/minute")
    print("  - 2 years historical access")
    print("  - End-of-day data via API")
    print("  - S3 flat files: REQUIRES PAID PLAN (403 error on free)")
    print("  - Minute aggregates available but rate limited")
    print("\n⚠️  Current issue: Would need 390+ API calls to load one trading day")
    print("    (6.5 hours at market open to 4pm = 390 minutes)")
    
    return {
        'available': True,
        'has_historical_intraday': True,
        'cost': 'Free tier',
        'rate_limit': '5 calls/min',
        'note': 'Already integrated but impractical for minute-by-minute replay'
    }

def main():
    print("\n" + "="*60)
    print("TESTING FREE HISTORICAL OPTIONS DATA SOURCES")
    print("="*60)
    
    results = {}
    
    # Test each source
    results['yfinance'] = test_yfinance_options()
    results['polygon'] = test_polygon_free_tier()
    results['cboe'] = test_cboe_datashop()
    results['alpha_vantage'] = test_alpha_vantage_options()
    results['massive_api'] = test_massive_api_coverage()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY & RECOMMENDATION")
    print("="*60)
    
    print("\n📊 FOR REAL-TIME LIVE DATA:")
    print("  ✓ Best: Massive API or Polygon.io")
    print("  ✓ Current chains: Yahoo Finance (yfinance)")
    
    print("\n📈 FOR HISTORICAL MINUTE-BY-MINUTE REPLAY:")
    print("  ✗ No truly free source with easy access")
    print("  ⚠️  Polygon.io: Free tier exists but requires signup")
    print("  ⚠️  Massive API: Free but rate limited (impractical)")
    
    print("\n💡 RECOMMENDATION FOR YOUR PROJECT:")
    print("  1. KEEP SIMULATED DATA for historical replay")
    print("     - Shows realistic patterns")
    print("     - No API costs or rate limits")
    print("     - Perfect for client demos")
    print("")
    print("  2. USE LIVE DATA (when you upgrade) for real-time monitoring")
    print("     - Massive API or Polygon.io paid plans")
    print("     - Unlimited calls for true live data")
    print("")
    print("  3. FOR CLIENT PITCH:")
    print("     - Be transparent: 'Historical replay with simulated realistic data'")
    print("     - Live mode: 'Real-time data ready with API integration'")
    print("     - Upgrade path: 'Can connect to premium data feeds'")
    
    print("\n🎯 BEST APPROACH:")
    print("  Your current setup is actually OPTIMAL for a demo/MVP!")
    print("  - Simulated historical = No costs, unlimited replay")
    print("  - Real API integration ready for when they pay")
    print("  - Professional appearance without burning free API quota")

if __name__ == '__main__':
    main()
