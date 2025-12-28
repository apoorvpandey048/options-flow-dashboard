"""
Massive API Data Provider
Real-time and historical options data from Massive API
Free tier: 5 calls per minute, 2 years historical data, all US options tickers
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .base_provider import BaseDataProvider
from .simulated_provider import SimulatedDataProvider


class MassiveDataProvider(BaseDataProvider):
    """Provides real options data from Massive API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('MASSIVE_API_KEY')
        self.base_url = os.getenv('MASSIVE_BASE_URL', 'https://api.massive.com')
        self.simulated_fallback = SimulatedDataProvider()
        
        if not self.api_key:
            print("⚠️  WARNING: No Massive API key found. Using simulated data.")
        else:
            print(f"✅ Massive API configured with key: {self.api_key[:10]}...")
    
    def get_provider_name(self) -> str:
        return "Massive API" if self.api_key else "Simulated (Massive fallback)"
    
    def validate_connection(self) -> bool:
        """Validate API key works"""
        if not self.api_key:
            return False
        
        try:
            # Test with a simple stock price request
            response = requests.get(
                f"{self.base_url}/v1/stock/quote/SPY",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Massive API connection validation failed: {e}")
            return False
    
    def get_stock_price(self, symbol: str) -> float:
        """Get current stock price from Massive API"""
        if not self.api_key:
            return self.simulated_fallback.get_stock_price(symbol)
        
        try:
            response = requests.get(
                f"{self.base_url}/v1/stock/quote/{symbol}",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                # Adapt to Massive API response format
                return round(float(data.get('price', data.get('last', 100.0))), 2)
            else:
                print(f"Massive API error ({response.status_code}): {response.text}")
                return self.simulated_fallback.get_stock_price(symbol)
                
        except Exception as e:
            print(f"Error fetching price from Massive: {e}")
            return self.simulated_fallback.get_stock_price(symbol)
    
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """Get options chain from Massive API"""
        if not self.api_key:
            return self.simulated_fallback.get_options_chain(symbol, expiration_date)
        
        try:
            # Build request URL
            url = f"{self.base_url}/v1/options/chain/{symbol}"
            params = {}
            if expiration_date:
                params['expiration'] = expiration_date
            
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {self.api_key}'},
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Transform Massive data to our format
                current_price = self.get_stock_price(symbol)
                strikes = []
                
                # Process options chain data
                for option in data.get('options', []):
                    strikes.append({
                        'strike': float(option.get('strike', 0)),
                        'call_volume': int(option.get('call_volume', 0)),
                        'put_volume': int(option.get('put_volume', 0)),
                        'call_open_interest': int(option.get('call_oi', 0)),
                        'put_open_interest': int(option.get('put_oi', 0))
                    })
                
                return {
                    'strikes': strikes if strikes else self.simulated_fallback.get_options_chain(symbol, expiration_date)['strikes'],
                    'current_price': current_price,
                    'expiration': expiration_date or data.get('expiration')
                }
                
            else:
                print(f"Massive options API error ({response.status_code}): {response.text}")
                return self.simulated_fallback.get_options_chain(symbol, expiration_date)
                
        except Exception as e:
            print(f"Error fetching options chain from Massive: {e}")
            return self.simulated_fallback.get_options_chain(symbol, expiration_date)
    
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min') -> Dict:
        """
        Get options flow data from Massive API
        """
        if not self.api_key:
            return self.simulated_fallback.get_options_flow_data(symbol, timeframe)
        
        try:
            url = f"{self.base_url}/v1/options/flow/{symbol}"
            print(f"🔍 Attempting Massive API call: {url}")
            
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {self.api_key}'},
                params={'timeframe': timeframe},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Massive API success! Keys: {list(data.keys())}")
                
                # Transform Massive data to our format
                return {
                    'calls': {
                        'total': int(data.get('call_volume', 0)),
                        'buy': int(data.get('call_buy_volume', 0)),
                        'sell': int(data.get('call_sell_volume', 0)),
                        'ratio': float(data.get('call_ratio', 1.0))
                    },
                    'puts': {
                        'total': int(data.get('put_volume', 0)),
                        'buy': int(data.get('put_buy_volume', 0)),
                        'sell': int(data.get('put_sell_volume', 0)),
                        'ratio': float(data.get('put_ratio', 1.0))
                    },
                    'sentiment': data.get('sentiment', 'neutral'),
                    'strikes': self._format_strikes(data.get('strikes', [])),
                    'price': self.get_stock_price(symbol),
                    'put_call_ratio': float(data.get('put_call_ratio', 1.0)),
                    'timestamp': data.get('timestamp', datetime.now().isoformat())
                }
            else:
                print(f"⚠️  Massive flow API error ({response.status_code}): {response.text}")
                print(f"⚠️  Falling back to simulated data")
                return self.simulated_fallback.get_options_flow_data(symbol, timeframe)
                
        except Exception as e:
            print(f"Error fetching options flow from Massive: {e}")
            return self.simulated_fallback.get_options_flow_data(symbol, timeframe)
    
    def _format_strikes(self, strikes_data: List) -> List[Dict]:
        """Format strike data to our internal format"""
        formatted = []
        for strike in strikes_data:
            formatted.append({
                'strike': float(strike.get('strike', 0)),
                'call_volume': int(strike.get('call_volume', 0)),
                'put_volume': int(strike.get('put_volume', 0)),
                'call_oi': int(strike.get('call_oi', 0)),
                'put_oi': int(strike.get('put_oi', 0))
            })
        return formatted
    
    def get_historical_options_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get historical options data from Massive API (2 years available on free tier)"""
        if not self.api_key:
            return self.simulated_fallback.get_historical_options_data(symbol, days)
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            response = requests.get(
                f"{self.base_url}/v1/options/historical/{symbol}",
                headers={'Authorization': f'Bearer {self.api_key}'},
                params={
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d')
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('historical_data', [])
            else:
                print(f"Massive historical API error ({response.status_code}): {response.text}")
                return self.simulated_fallback.get_historical_options_data(symbol, days)
                
        except Exception as e:
            print(f"Error fetching historical data from Massive: {e}")
            return self.simulated_fallback.get_historical_options_data(symbol, days)
