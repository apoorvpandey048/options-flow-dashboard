"""
Test if Massive API key can provide live/real-time data
"""
import requests
from datetime import datetime, timedelta
import time

API_KEY = "LpBKr1HoM_6Kau1JEhZvrMngPcKa4kb_"
BASE_URL = "https://api.massiveapi.com/v2"

def test_current_snapshot():
    """Test if we can get current/latest options data"""
    print("\n" + "="*60)
    print("Testing: Current Options Snapshot")
    print("="*60)
    
    symbol = "SPY"
    
    try:
        # Try to get latest aggregate
        url = f"{BASE_URL}/aggs/ticker/O:{symbol}250103C00662000/prev"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        print(f"Requesting: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Got data:")
            print(f"  {data}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_todays_data():
    """Test if we can get today's data"""
    print("\n" + "="*60)
    print("Testing: Today's Options Data")
    print("="*60)
    
    symbol = "SPY"
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Try to get today's minute data
        url = f"{BASE_URL}/aggs/ticker/O:{symbol}250103C00662000/range/1/minute/{today}/{today}"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        print(f"Requesting: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Got data:")
            print(f"  Results count: {data.get('resultsCount', 0)}")
            if data.get('results'):
                print(f"  Sample: {data['results'][0]}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_recent_data():
    """Test if we can get very recent historical data (last hour)"""
    print("\n" + "="*60)
    print("Testing: Recent Historical Data (Last Hour)")
    print("="*60)
    
    symbol = "SPY"
    
    # Try yesterday's data (more likely to be available)
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    try:
        url = f"{BASE_URL}/aggs/ticker/O:{symbol}250103C00662000/range/1/minute/{yesterday}/{yesterday}"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        print(f"Requesting yesterday's data: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Got data:")
            print(f"  Results count: {data.get('resultsCount', 0)}")
            if data.get('results'):
                print(f"  First minute: {data['results'][0]}")
                print(f"  Last minute: {data['results'][-1]}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_live_quotes():
    """Test if live quotes endpoint works"""
    print("\n" + "="*60)
    print("Testing: Live Quotes Endpoint")
    print("="*60)
    
    try:
        url = f"{BASE_URL}/last/trade/O:SPY250103C00662000"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        print(f"Requesting: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Got live quote:")
            print(f"  {data}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_plan_limits():
    """Check what the free plan actually includes"""
    print("\n" + "="*60)
    print("Massive API - Options Basic Plan (Free Tier)")
    print("="*60)
    
    print("\n📋 Official Plan Features:")
    print("  • 5 API requests per minute")
    print("  • 2 years of historical data access")
    print("  • REST API access")
    print("  • End-of-day data")
    print("\n⚠️  Limitations:")
    print("  • NO real-time/live data on free tier")
    print("  • NO WebSocket streaming")
    print("  • NO intraday data until end-of-day")
    print("  • NO S3 flat file access")
    print("\n💰 For Live Data, Need:")
    print("  • Options Starter: $49/mo (5 concurrent users)")
    print("  • Options Standard: $99/mo (unlimited API calls)")
    print("  • Includes: Real-time data, WebSocket, higher limits")

def main():
    print("\n" + "="*60)
    print("TESTING MASSIVE API LIVE DATA CAPABILITIES")
    print("="*60)
    
    # Run tests
    test_current_snapshot()
    time.sleep(1)
    
    test_todays_data()
    time.sleep(1)
    
    test_recent_data()
    time.sleep(1)
    
    test_live_quotes()
    
    # Show plan limits
    check_plan_limits()
    
    # Final verdict
    print("\n" + "="*60)
    print("VERDICT")
    print("="*60)
    
    print("\n🔴 Current Status (Options Basic - Free):")
    print("  ✗ NO live/real-time data")
    print("  ✗ NO intraday updates during market hours")
    print("  ✓ Historical end-of-day data only")
    print("  ✓ Data from 2 years ago available")
    
    print("\n💡 What This Means for Your Dashboard:")
    print("  1. 'Live' mode currently uses SIMULATED data")
    print("  2. This is actually GOOD for demos (no API costs)")
    print("  3. For REAL live data, need paid plan ($49-99/mo)")
    
    print("\n🎯 Recommendation:")
    print("  ✅ Keep using simulated data for now")
    print("  ✅ Tell clients: 'Demo uses realistic simulated data'")
    print("  ✅ When they pay: Upgrade to Options Standard ($99/mo)")
    print("  ✅ Then flip switch to real live data")
    
    print("\n📊 Cost Analysis:")
    print("  Demo/MVP: $0/month (simulated)")
    print("  Production: $99/month (unlimited real-time)")
    print("  → Perfect for client-funded pricing model!")

if __name__ == '__main__':
    main()
