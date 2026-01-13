"""
MarketStack Data Provider
Provides EOD (End-of-Day) stock data from MarketStack API
Note: Free plan limited to 100 requests/month, EOD data only
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
from .base_provider import BaseDataProvider


class MarketStackProvider(BaseDataProvider):
    """Data provider for MarketStack API"""
    
    BASE_URL = "https://api.marketstack.com/v2"
    
    def __init__(self, api_key: str):
        """
        Initialize MarketStack provider
        
        Args:
            api_key: MarketStack API access key
        """
        super().__init__()
        self.api_key = api_key
        self.session = requests.Session()
        
        # Rate limiting (free plan: 5 requests/second, 100/month)
        self.requests_count = 0
        self.max_requests_per_month = 100
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 5 requests/second = 0.2s between requests
        
        print(f"✅ MarketStack provider initialized")
        print(f"⚠️  FREE PLAN LIMITS: 100 requests/month, EOD data only")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        Make API request with rate limiting
        
        Args:
            endpoint: API endpoint (e.g., 'eod', 'tickers')
            params: Query parameters
            
        Returns:
            Response data or None if error
        """
        # Check monthly limit
        if self.requests_count >= self.max_requests_per_month:
            print(f"❌ Monthly request limit reached ({self.max_requests_per_month})")
            return None
        
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        
        # Add API key to params
        params['access_key'] = self.api_key
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            self.last_request_time = time.time()
            self.requests_count += 1
            
            if response.status_code == 200:
                data = response.json()
                remaining = response.headers.get('x-ratelimit-remaining-month', 'N/A')
                print(f"✅ Request #{self.requests_count} - Remaining this month: {remaining}")
                return data
            elif response.status_code == 429:
                print(f"❌ Rate limit exceeded")
                return None
            else:
                print(f"❌ API error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None
    
    def get_eod_data(self, symbols: List[str], limit: int = 1) -> Dict[str, Any]:
        """
        Get End-of-Day stock data
        
        Args:
            symbols: List of stock symbols
            limit: Number of days to retrieve (default: 1)
            
        Returns:
            Dictionary with symbol as key and latest EOD data
        """
        result = {}
        
        # MarketStack allows multiple symbols in one request (comma-separated)
        symbols_str = ','.join(symbols)
        
        # Use /eod/latest for most recent data or /eod for historical
        endpoint = 'eod/latest' if limit == 1 else 'eod'
        
        params = {
            'symbols': symbols_str
        }
        
        if limit > 1:
            params['limit'] = limit
        
        data = self._make_request(endpoint, params)
        
        if data and 'data' in data:
            for item in data['data']:
                symbol = item['symbol']
                result[symbol] = {
                    'symbol': symbol,
                    'name': item.get('name', symbol),
                    'date': item.get('date'),
                    'open': item.get('open'),
                    'high': item.get('high'),
                    'low': item.get('low'),
                    'close': item.get('close'),
                    'volume': item.get('volume'),
                    'exchange': item.get('exchange'),
                    'currency': item.get('price_currency', 'USD')
                }
        
        return result
    
    def get_ticker_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed ticker information
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Ticker information or None
        """
        params = {'symbols': symbol}
        
        data = self._make_request('tickers', params)
        
        if data and 'data' in data and len(data['data']) > 0:
            ticker = data['data'][0]
            return {
                'symbol': ticker.get('symbol'),
                'name': ticker.get('name'),
                'exchange': ticker.get('stock_exchange', {}).get('name'),
                'exchange_code': ticker.get('stock_exchange', {}).get('acronym'),
                'currency': ticker.get('currency', 'USD'),
                'country': ticker.get('country')
            }
        
        return None
    
    def get_exchanges(self) -> List[Dict[str, Any]]:
        """
        Get list of available exchanges
        
        Returns:
            List of exchange information
        """
        params = {'limit': 50}  # Limit to reduce API calls
        
        data = self._make_request('exchanges', params)
        
        if data and 'data' in data:
            return [
                {
                    'name': exchange.get('name'),
                    'acronym': exchange.get('acronym'),
                    'mic': exchange.get('mic'),
                    'country': exchange.get('country'),
                    'currency': exchange.get('currency'),
                    'timezone': exchange.get('timezone', {}).get('timezone')
                }
                for exchange in data['data']
            ]
        
        return []
    
    def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get historical EOD data
        
        Args:
            symbol: Stock symbol
            days: Number of days of history (default: 30)
            
        Returns:
            List of historical data points
        """
        params = {
            'symbols': symbol,
            'limit': days
        }
        
        data = self._make_request('eod', params)
        
        if data and 'data' in data:
            return [
                {
                    'date': item.get('date'),
                    'open': item.get('open'),
                    'high': item.get('high'),
                    'low': item.get('low'),
                    'close': item.get('close'),
                    'volume': item.get('volume')
                }
                for item in data['data']
            ]
        
        return []
    
    def get_options_data(self, symbol: str) -> List[Dict[str, Any]]:
        """
        MarketStack does NOT provide options data
        This method is not supported
        
        Returns:
            Empty list with warning
        """
        print(f"⚠️  MarketStack does not provide options data")
        print(f"⚠️  Only stock EOD data is available on this provider")
        return []
    
    def get_realtime_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        MarketStack free plan does NOT provide real-time data
        Returns latest EOD data instead
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest EOD data
        """
        print(f"⚠️  Real-time data not available on free plan")
        print(f"ℹ️  Returning latest EOD data instead")
        
        eod_data = self.get_eod_data([symbol], limit=1)
        return eod_data.get(symbol)
    
    def validate_connection(self) -> bool:
        """
        Validate API connection and key
        
        Returns:
            True if connection is valid
        """
        print("🔍 Validating MarketStack API connection...")
        
        params = {
            'access_key': self.api_key,
            'symbols': 'AAPL'
        }
        
        try:
            response = self.session.get(f"{self.BASE_URL}/eod/latest", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    print("✅ MarketStack API connection valid")
                    
                    # Show rate limit info
                    limit_month = response.headers.get('x-ratelimit-limit-month', 'N/A')
                    remaining_month = response.headers.get('x-ratelimit-remaining-month', 'N/A')
                    print(f"📊 Monthly limit: {remaining_month}/{limit_month} requests remaining")
                    
                    return True
            elif response.status_code == 401:
                print("❌ Invalid API key")
            elif response.status_code == 429:
                print("❌ Rate limit exceeded")
            else:
                print(f"❌ API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
        
        return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics
        
        Returns:
            Usage statistics
        """
        return {
            'provider': 'MarketStack',
            'plan': 'FREE',
            'requests_made': self.requests_count,
            'monthly_limit': self.max_requests_per_month,
            'remaining': self.max_requests_per_month - self.requests_count,
            'features': [
                'EOD Stock Data',
                'Historical Data (1 year)',
                'Stock Tickers Info',
                '2700+ Exchanges Info',
                'Splits & Dividends'
            ],
            'limitations': [
                'NO real-time data',
                'NO intraday data',
                'NO options data',
                '100 requests/month only'
            ]
        }
    
    # Implementation of abstract methods from BaseDataProvider
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "MarketStack"
    
    def get_stock_price(self, symbol: str) -> float:
        """
        Get current (EOD) stock price
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Latest closing price
        """
        data = self.get_eod_data([symbol], limit=1)
        if data and symbol in data:
            return data[symbol].get('close', 0.0)
        return 0.0
    
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """
        MarketStack does NOT provide options chain data
        
        Returns:
            Empty dictionary with warning
        """
        print(f"⚠️  MarketStack does not provide options chain data")
        return {
            'symbol': symbol,
            'strikes': [],
            'current_price': self.get_stock_price(symbol),
            'expiration': None,
            'error': 'Options data not available on MarketStack'
        }
    
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min') -> Dict:
        """
        MarketStack does NOT provide options flow data
        
        Returns:
            Empty dictionary with warning
        """
        print(f"⚠️  MarketStack does not provide options flow data")
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'call_volume': 0,
            'put_volume': 0,
            'put_call_ratio': 0,
            'total_premium': 0,
            'error': 'Options flow data not available on MarketStack'
        }
    
    def get_historical_options_data(self, symbol: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        MarketStack does NOT provide historical options data
        Returns historical stock prices instead
        
        Args:
            symbol: Stock symbol
            days: Number of days
            
        Returns:
            List of historical stock prices
        """
        print(f"⚠️  MarketStack does not provide options data")
        print(f"ℹ️  Returning historical stock prices instead")
        return self.get_historical_data(symbol, days)
