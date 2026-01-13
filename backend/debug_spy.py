"""
Debug SPY - Find correct symbol and test all methods
"""
import requests
import time

API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiYXdlc29tZWJsb2dzMjAxMEBnbWFpbC5jb20iLCJwbGFuIjoidWx0cmEiLCJuZXdzZmVlZF9lbmFibGVkIjp0cnVlLCJ3ZWJzb2NrZXRfc3ltYm9scyI6NSwid2Vic29ja2V0X2Nvbm5lY3Rpb25zIjoxfQ.zfYCHDg7v1O3Bkb6_JLlus90FtBUfcRH_Px6_sut-Ks'

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("="*80)
print("  SPY Symbol Debug - Finding the Issue")
print("="*80)

# Test 1: Try all exchange formats for quotes
print("\n[1] Testing SPY Quote Endpoints")
exchanges = ["ARCA", "NYSE", "NASDAQ", "AMEX", "BATS", "IEX", "CBOE"]

for exchange in exchanges:
    symbol = f"{exchange}:SPY"
    try:
        response = requests.get(
            "https://api.insightsentry.com/v3/symbols/quotes",
            headers=headers,
            params={"codes": symbol},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                quote = data['data'][0]
                price = quote.get('last_price')
                if price:
                    print(f"  ✅ {symbol} - Price: ${price}")
                else:
                    print(f"  ⚠️  {symbol} - No price data")
            else:
                print(f"  ❌ {symbol} - Empty response")
        else:
            print(f"  ❌ {symbol} - Error {response.status_code}")
    except Exception as e:
        print(f"  ❌ {symbol} - {str(e)[:50]}")
    
    time.sleep(0.5)

# Test 2: Search for SPY
print("\n[2] Searching for 'SPY' in API")
try:
    response = requests.get(
        "https://api.insightsentry.com/v3/symbols/search",
        headers=headers,
        params={"query": "SPY"},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('data', [])
        print(f"  Found {len(results)} results")
        for item in results[:10]:
            print(f"    • {item.get('code')} - {item.get('description', 'N/A')[:60]}")
    else:
        print(f"  ❌ Search failed: {response.status_code}")
        print(f"     Response: {response.text[:200]}")
except Exception as e:
    print(f"  ❌ Search error: {e}")

# Test 3: Try S&P 500 alternatives
print("\n[3] Testing S&P 500 ETF Alternatives")
alternatives = [
    ("NASDAQ:IVV", "iShares Core S&P 500 ETF"),
    ("NASDAQ:VOO", "Vanguard S&P 500 ETF"),
    ("ARCA:SPY", "SPDR S&P 500 ETF"),
]

for symbol, name in alternatives:
    try:
        response = requests.get(
            "https://api.insightsentry.com/v3/symbols/quotes",
            headers=headers,
            params={"codes": symbol},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                quote = data['data'][0]
                price = quote.get('last_price')
                if price and price > 0:
                    print(f"  ✅ {symbol} ({name})")
                    print(f"     Price: ${price}, Volume: {quote.get('volume', 'N/A')}")
                else:
                    print(f"  ⚠️  {symbol} - No valid price")
            else:
                print(f"  ❌ {symbol} - Empty response")
        else:
            print(f"  ❌ {symbol} - Error {response.status_code}")
    except Exception as e:
        print(f"  ❌ {symbol} - {str(e)[:50]}")
    
    time.sleep(0.5)

# Test 4: Check if SPY has options available
print("\n[4] Checking Options Availability")
for symbol in ["ARCA:SPY", "NASDAQ:IVV", "NASDAQ:VOO"]:
    try:
        response = requests.get(
            "https://api.insightsentry.com/v3/options/list",
            headers=headers,
            params={"code": symbol},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            codes = data.get('codes', [])
            print(f"  ✅ {symbol} - {len(codes)} options available")
        else:
            print(f"  ❌ {symbol} - No options (Error {response.status_code})")
    except Exception as e:
        print(f"  ❌ {symbol} - {str(e)[:50]}")
    
    time.sleep(0.5)

print("\n" + "="*80)
print("  Recommendation:")
print("="*80)
print("\nBased on results above, we should:")
print("1. Use the symbol with valid price data")
print("2. If SPY doesn't work, replace with IVV or VOO")
print("3. Both track S&P 500 and have liquid options markets")
