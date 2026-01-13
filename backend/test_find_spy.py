"""Quick test to find correct SPY symbol format"""
import requests

API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiYXdlc29tZWJsb2dzMjAxMEBnbWFpbC5jb20iLCJwbGFuIjoidWx0cmEiLCJuZXdzZmVlZF9lbmFibGVkIjp0cnVlLCJ3ZWJzb2NrZXRfc3ltYm9scyI6NSwid2Vic29ja2V0X2Nvbm5lY3Rpb25zIjoxfQ.zfYCHDg7v1O3Bkb6_JLlus90FtBUfcRH_Px6_sut-Ks'

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Try different formats
formats_to_try = [
    "ARCA:SPY",
    "NYSE:SPY", 
    "NASDAQ:SPY",
    "AMEX:SPY",
    "BATS:SPY"
]

print("Testing different SPY formats...\n")

for symbol_format in formats_to_try:
    print(f"Trying {symbol_format}...")
    response = requests.get(
        f"https://api.insightsentry.com/v3/symbols/quotes",
        headers=headers,
        params={"codes": symbol_format},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('data') and len(data['data']) > 0:
            quote = data['data'][0]
            print(f"  ✅ FOUND! Price: ${quote.get('last_price')}")
            print(f"     Full code: {quote.get('code')}")
            break
    else:
        print(f"  ❌ {response.status_code}")

print("\nDone!")
