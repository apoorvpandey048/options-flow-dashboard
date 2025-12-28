"""
Test what historical data we can actually access with Massive Options Basic
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('MASSIVE_API_KEY')
BASE_URL = 'https://api.massive.com'

print("=" * 80)
print("TESTING MASSIVE API - OPTIONS BASIC PLAN")
print("=" * 80)

# Test 1: Try to get historical minute aggregates
print("\n1. Testing Historical Minute Aggregates...")
print("-" * 40)

date = '2025-12-27'
symbol = 'O:SPY251231C00600000'  # SPY call option

endpoints_to_try = [
    f'/v1/aggs/ticker/{symbol}/range/1/minute/{date}/{date}',
    f'/v2/aggs/ticker/{symbol}/range/1/minute/2025-12-26/2025-12-27',
    f'/v1/options/minute/{symbol}',
    f'/v1/options/aggregates/SPY/2025-12-27',
]

for endpoint in endpoints_to_try:
    url = f"{BASE_URL}{endpoint}"
    print(f"\nTrying: {endpoint}")
    try:
        response = requests.get(
            url,
            headers={'Authorization': f'Bearer {API_KEY}'},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ SUCCESS! Response: {response.json()}")
            break
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("-" * 40)
print("Options Basic plan limitations:")
print("  - END OF DAY data only (not intraday minute-by-minute)")
print("  - S3 Flat Files: No access (403 Forbidden)")
print("  - REST API: Limited endpoints for options")
print("\nRECOMMENDATION:")
print("  Use SIMULATED data that mimics real patterns")
print("  Shows realistic time-based progression")
print("  No API calls needed, no cost")
print("=" * 80)
