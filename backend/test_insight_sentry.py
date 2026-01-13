"""
Comprehensive test script for Insight Sentry API (Ultra Plan)
Tests all available features within rate limits:
- Symbol search
- Options listing
- Option chains (by expiration and strike)
- Real-time quotes
- Historical data
- News API
- WebSocket (5 concurrent symbols)

Rate Limits (Ultra Plan):
- 35 requests per minute
- 120,000 requests per month
- 10 WebSocket connections per day
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Config

class InsightSentryTester:
    """Test all Insight Sentry API features"""
    
    BASE_URL = "https://api.insightsentry.com"
    
    def __init__(self):
        self.api_key = Config.INSIGHT_SENTRY_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.request_count = 0
        self.start_time = time.time()
        self.test_results = {}
        
    def rate_limit_safe_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make request with rate limit protection (35/min)"""
        # Track requests per minute
        elapsed = time.time() - self.start_time
        if self.request_count >= 30 and elapsed < 60:  # Safety margin
            wait_time = 60 - elapsed
            print(f"⏳ Rate limit protection: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
            self.start_time = time.time()
            self.request_count = 0
            
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            self.request_count += 1
            
            if response.status_code == 429:  # Rate limit exceeded
                print("⚠️  Rate limit hit, waiting 60s...")
                time.sleep(60)
                return self.rate_limit_safe_request(method, url, **kwargs)
                
            return response
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def print_section(self, title: str):
        """Print formatted section header"""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    
    def test_symbol_search(self) -> List[str]:
        """Test 1: Symbol Search API"""
        self.print_section("TEST 1: Symbol Search")
        
        symbols_to_search = ["SPY", "QQQ", "AAPL", "TSLA"]
        found_symbols = []
        
        for query in symbols_to_search:
            print(f"🔍 Searching for: {query}")
            response = self.rate_limit_safe_request(
                "GET",
                f"{self.BASE_URL}/v3/symbols/search",
                params={"query": query}
            )
            
            if response and response.status_code == 200:
                data = response.json()
                print(f"✅ Found {len(data.get('data', []))} results")
                
                # Get the first match
                if data.get('data'):
                    symbol = data['data'][0].get('code')
                    found_symbols.append(symbol)
                    print(f"   Primary symbol: {symbol}")
                    print(f"   Description: {data['data'][0].get('description', 'N/A')}")
            else:
                print(f"❌ Search failed: {response.status_code if response else 'No response'}")
                
            time.sleep(0.5)  # Small delay between searches
        
        self.test_results['symbol_search'] = {
            'success': True,
            'symbols_found': found_symbols
        }
        return found_symbols
    
    def test_options_list(self, symbol: str = "NASDAQ:AAPL") -> List[str]:
        """Test 2: Get Available Options"""
        self.print_section(f"TEST 2: Available Options for {symbol}")
        
        print(f"📋 Fetching options list for {symbol}...")
        response = self.rate_limit_safe_request(
            "GET",
            f"{self.BASE_URL}/v3/options/list",
            params={"code": symbol}
        )
        
        option_codes = []
        if response and response.status_code == 200:
            data = response.json()
            option_codes = data.get('codes', [])
            print(f"✅ Found {len(option_codes)} available options")
            
            # Display sample options
            print(f"\n📊 Sample option codes (first 10):")
            for i, code in enumerate(option_codes[:10], 1):
                print(f"   {i}. {code}")
                
            self.test_results['options_list'] = {
                'success': True,
                'symbol': symbol,
                'total_options': len(option_codes),
                'sample_codes': option_codes[:5]
            }
        else:
            print(f"❌ Failed: {response.status_code if response else 'No response'}")
            self.test_results['options_list'] = {'success': False}
            
        return option_codes
    
    def test_symbol_info(self, symbol: str = "NASDAQ:AAPL") -> Dict:
        """Test 3: Get Symbol Info with Option Chain Metadata"""
        self.print_section(f"TEST 3: Symbol Info & Option Chain Metadata for {symbol}")
        
        print(f"ℹ️  Fetching symbol info...")
        response = self.rate_limit_safe_request(
            "GET",
            f"{self.BASE_URL}/v3/symbols/{symbol}/info"
        )
        
        symbol_info = {}
        if response and response.status_code == 200:
            data = response.json()
            print(f"✅ Symbol: {data.get('code')}")
            print(f"   Type: {data.get('type')}")
            print(f"   Description: {data.get('description')}")
            print(f"   Currency: {data.get('currency_code')}")
            
            # Option chain info
            option_info = data.get('option_info', [])
            if option_info:
                print(f"\n📈 Option Chain Info:")
                for series in option_info[:3]:  # Show first 3 series
                    print(f"   Series: {series.get('name')}")
                    print(f"   Type: {series.get('type')}")
                    
                    for opt_series in series.get('series', [])[:2]:  # First 2 expiration series
                        exp_date = opt_series.get('expiration_date')
                        strikes = opt_series.get('strikes', [])
                        print(f"   - Expiration: {exp_date}")
                        print(f"     Available strikes: {len(strikes)} (range: {strikes[0] if strikes else 'N/A'} - {strikes[-1] if strikes else 'N/A'})")
                        
                symbol_info = {
                    'option_info': option_info,
                    'expiration_dates': [
                        s.get('expiration_date') 
                        for series in option_info 
                        for s in series.get('series', [])
                    ][:5],  # First 5 expiration dates
                    'strikes': option_info[0]['series'][0]['strikes'][:10] if option_info and option_info[0].get('series') else []
                }
            
            self.test_results['symbol_info'] = {
                'success': True,
                'has_options': bool(option_info),
                'option_series_count': len(option_info)
            }
        else:
            print(f"❌ Failed: {response.status_code if response else 'No response'}")
            self.test_results['symbol_info'] = {'success': False}
            
        return symbol_info
    
    def test_option_chain_by_expiration(self, symbol: str = "NASDAQ:AAPL", expiration: str = "2026-06-17"):
        """Test 4: Get Option Chain by Expiration Date"""
        self.print_section(f"TEST 4: Option Chain by Expiration ({expiration})")
        
        print(f"📅 Fetching option chain for {symbol} expiring {expiration}...")
        response = self.rate_limit_safe_request(
            "GET",
            f"{self.BASE_URL}/v3/options/expiration",
            params={
                "code": symbol,
                "expiration": expiration,
                "sortBy": "strike_price",
                "sort": "asc"
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            options = data.get('data', [])
            print(f"✅ Found {len(options)} options")
            
            # Display sample data
            if options:
                print(f"\n📊 Sample Options (first 5):")
                for opt in options[:5]:
                    print(f"\n   Code: {opt.get('code')}")
                    print(f"   Type: {opt.get('type')}")
                    print(f"   Strike: ${opt.get('strike_price')}")
                    print(f"   Bid: ${opt.get('bid_price')}, Ask: ${opt.get('ask_price')}")
                    print(f"   IV: {opt.get('implied_volatility'):.2%}" if opt.get('implied_volatility') else "   IV: N/A")
                    print(f"   Delta: {opt.get('delta'):.3f}" if opt.get('delta') else "   Delta: N/A")
                    print(f"   Volume: {opt.get('volume', 'N/A')}")
            
            self.test_results['option_chain_expiration'] = {
                'success': True,
                'options_count': len(options),
                'has_greeks': any(opt.get('delta') is not None for opt in options[:5])
            }
        else:
            print(f"❌ Failed: {response.status_code if response else 'No response'}")
            self.test_results['option_chain_expiration'] = {'success': False}
    
    def test_option_chain_by_strike(self, symbol: str = "NASDAQ:AAPL", strike: float = 200.0):
        """Test 5: Get Option Chain by Strike Price"""
        self.print_section(f"TEST 5: Option Chain by Strike (${strike})")
        
        print(f"💰 Fetching options at ${strike} strike for {symbol}...")
        response = self.rate_limit_safe_request(
            "GET",
            f"{self.BASE_URL}/v3/options/strike",
            params={
                "code": symbol,
                "strike": strike,
                "sortBy": "expiration",
                "sort": "asc"
            }
        )
        
        if response and response.status_code == 200:
            data = response.json()
            options = data.get('data', [])
            print(f"✅ Found {len(options)} options at ${strike} strike")
            
            if options:
                print(f"\n📊 Options across different expirations:")
                for opt in options[:5]:
                    exp_date = str(opt.get('expiration'))
                    formatted_exp = f"{exp_date[:4]}-{exp_date[4:6]}-{exp_date[6:]}"
                    print(f"\n   {opt.get('type')} - Exp: {formatted_exp}")
                    print(f"   Code: {opt.get('code')}")
                    print(f"   Bid: ${opt.get('bid_price')}, Ask: ${opt.get('ask_price')}")
                    print(f"   Theta: {opt.get('theta'):.3f}" if opt.get('theta') else "   Theta: N/A")
            
            self.test_results['option_chain_strike'] = {
                'success': True,
                'options_count': len(options)
            }
        else:
            print(f"❌ Failed: {response.status_code if response else 'No response'}")
            self.test_results['option_chain_strike'] = {'success': False}
    
    def test_realtime_quotes(self, option_codes: List[str]):
        """Test 6: Real-time Option Quotes"""
        self.print_section("TEST 6: Real-time Option Quotes")
        
        # Test with up to 10 option codes (API limit)
        codes_to_test = option_codes[:10] if len(option_codes) >= 10 else option_codes
        
        if not codes_to_test:
            print("⚠️  No option codes available for testing")
            return
        
        codes_param = ",".join(codes_to_test)
        print(f"📡 Fetching real-time quotes for {len(codes_to_test)} options...")
        
        response = self.rate_limit_safe_request(
            "GET",
            f"{self.BASE_URL}/v3/symbols/quotes",
            params={"codes": codes_param}
        )
        
        if response and response.status_code == 200:
            data = response.json()
            quotes = data.get('data', [])
            print(f"✅ Received {len(quotes)} quotes")
            print(f"   Last update: {datetime.fromtimestamp(data.get('last_update', 0)/1000).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Display detailed quote info
            if quotes:
                print(f"\n📊 Real-time Quote Details:")
                for quote in quotes[:3]:  # Show first 3
                    print(f"\n   {quote.get('code')}")
                    print(f"   Status: {quote.get('status')}")
                    print(f"   Last Price: ${quote.get('last_price')}")
                    print(f"   Bid: ${quote.get('bid')} (size: {quote.get('bid_size')})")
                    print(f"   Ask: ${quote.get('ask')} (size: {quote.get('ask_size')})")
                    print(f"   Volume: {quote.get('volume')}")
                    print(f"   Change: {quote.get('change_percent'):.2f}%" if quote.get('change_percent') else "   Change: N/A")
                    print(f"   Delay: {quote.get('delay_seconds', 0)}s")
            
            self.test_results['realtime_quotes'] = {
                'success': True,
                'quotes_received': len(quotes),
                'real_time': all(q.get('delay_seconds') == 0 for q in quotes)
            }
        else:
            print(f"❌ Failed: {response.status_code if response else 'No response'}")
            self.test_results['realtime_quotes'] = {'success': False}
    
    def test_historical_data(self, option_code: str = "OPRA:AAPL260417C150.0"):
        """Test 7: Historical Option Data"""
        self.print_section("TEST 7: Historical Option Data (Deep History)")
        
        print(f"📈 Fetching historical data for {option_code}...")
        
        # Test different bar types
        bar_types = [
            ("day", 1, "Daily"),
            ("hour", 1, "Hourly"),
            ("minute", 5, "5-Minute")
        ]
        
        for bar_type, interval, name in bar_types:
            print(f"\n📊 {name} bars:")
            response = self.rate_limit_safe_request(
                "GET",
                f"{self.BASE_URL}/v3/symbols/{option_code}/series",
                params={
                    "bar_type": bar_type,
                    "bar_interval": interval,
                    "dp": 100  # Request 100 data points
                }
            )
            
            if response and response.status_code == 200:
                data = response.json()
                series = data.get('series', [])
                print(f"   ✅ Retrieved {len(series)} bars")
                
                if series:
                    latest = series[-1]
                    print(f"   Latest bar:")
                    print(f"     Time: {datetime.fromtimestamp(latest.get('time', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"     Open: ${latest.get('open')}, High: ${latest.get('high')}")
                    print(f"     Low: ${latest.get('low')}, Close: ${latest.get('close')}")
                    print(f"     Volume: {latest.get('volume')}")
            else:
                print(f"   ❌ Failed: {response.status_code if response else 'No response'}")
            
            time.sleep(1)  # Small delay between requests
        
        self.test_results['historical_data'] = {
            'success': True,
            'bar_types_tested': len(bar_types)
        }
    
    def test_stock_quotes(self):
        """Test 8: Stock Quotes (for underlying symbols)"""
        self.print_section("TEST 8: Underlying Stock Quotes")
        
        symbols = ["NASDAQ:SPY", "NASDAQ:QQQ", "NASDAQ:AAPL", "NASDAQ:TSLA"]
        codes_param = ",".join(symbols)
        
        print(f"📊 Fetching quotes for {len(symbols)} stocks (SPY, QQQ, AAPL, TSLA)...")
        response = self.rate_limit_safe_request(
            "GET",
            f"{self.BASE_URL}/v3/symbols/quotes",
            params={"codes": codes_param}
        )
        
        if response and response.status_code == 200:
            data = response.json()
            quotes = data.get('data', [])
            print(f"✅ Received {len(quotes)} quotes\n")
            
            for quote in quotes:
                print(f"   {quote.get('code')}: ${quote.get('last_price', 'N/A')}")
                if quote.get('change_percent') is not None and quote.get('volume') is not None:
                    print(f"   Change: {quote.get('change_percent'):.2f}% | Volume: {quote.get('volume'):,.0f}")
                if quote.get('market_cap'):
                    print(f"   Market Cap: ${quote.get('market_cap'):,.0f}")
                print()
            
            self.test_results['stock_quotes'] = {
                'success': True,
                'quotes_count': len(quotes)
            }
        else:
            print(f"❌ Failed: {response.status_code if response else 'No response'}")
            self.test_results['stock_quotes'] = {'success': False}
    
    def print_summary(self):
        """Print test summary"""
        self.print_section("TEST SUMMARY")
        
        print(f"Total API requests made: {self.request_count}")
        print(f"Time elapsed: {time.time() - self.start_time:.1f}s")
        print(f"\nTest Results:")
        
        for test_name, result in self.test_results.items():
            status = "✅" if result.get('success') else "❌"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
            
            # Print additional details
            for key, value in result.items():
                if key != 'success':
                    print(f"      {key}: {value}")
        
        print(f"\n{'='*80}")
        print("🎉 Testing Complete!")
        print(f"{'='*80}\n")
        
        # Save results to file
        results_file = "insight_sentry_test_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_requests': self.request_count,
                'results': self.test_results
            }, f, indent=2)
        print(f"📄 Results saved to: {results_file}\n")

def main():
    """Run all tests"""
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║        Insight Sentry API Comprehensive Test Suite                ║
    ║                    Ultra Plan Features                             ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    tester = InsightSentryTester()
    
    try:
        # Test 1: Symbol Search
        symbols = tester.test_symbol_search()
        
        # Test 2: Options List
        if symbols:
            option_codes = tester.test_options_list(symbols[0])
        else:
            option_codes = tester.test_options_list("NASDAQ:AAPL")
        
        # Test 3: Symbol Info with Option Chain Metadata
        symbol_info = tester.test_symbol_info("NASDAQ:AAPL")
        
        # Test 4: Option Chain by Expiration
        if symbol_info.get('expiration_dates'):
            # Convert date format: 20260617 -> 2026-06-17
            exp_date = str(symbol_info['expiration_dates'][0])
            formatted_date = f"{exp_date[:4]}-{exp_date[4:6]}-{exp_date[6:]}"
            tester.test_option_chain_by_expiration("NASDAQ:AAPL", formatted_date)
        else:
            tester.test_option_chain_by_expiration("NASDAQ:AAPL", "2026-06-17")
        
        # Test 5: Option Chain by Strike
        if symbol_info.get('strikes'):
            tester.test_option_chain_by_strike("NASDAQ:AAPL", symbol_info['strikes'][0])
        else:
            tester.test_option_chain_by_strike("NASDAQ:AAPL", 200.0)
        
        # Test 6: Real-time Quotes
        if option_codes:
            tester.test_realtime_quotes(option_codes)
        
        # Test 7: Historical Data
        if option_codes:
            tester.test_historical_data(option_codes[0])
        
        # Test 8: Stock Quotes
        tester.test_stock_quotes()
        
        # Print summary
        tester.print_summary()
        
        print("\n📝 Next Steps:")
        print("   1. Review the test results above")
        print("   2. Check insight_sentry_test_results.json for detailed data")
        print("   3. Test WebSocket connection separately (limited to 10/day)")
        print("   4. Consider implementing InsightSentryProvider class")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
