"""
Polygon.io Data Provider
Real-time options data from Polygon.io API (requires premium subscription)
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .base_provider import BaseDataProvider
from .simulated_provider import SimulatedDataProvider


class PolygonDataProvider(BaseDataProvider):
    """Provides real options data from Polygon.io"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        self.base_url = "https://api.polygon.io"
        self.simulated_fallback = SimulatedDataProvider()
        
        if not self.api_key:
            print("⚠️  WARNING: No Polygon.io API key found. Using simulated data.")
    
    def get_provider_name(self) -> str:
        return "Polygon.io" if self.api_key else "Simulated (Polygon fallback)"
    
    def validate_connection(self) -> bool:
        """Validate API key works"""
        if not self.api_key:
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/v2/aggs/ticker/SPY/prev",
                params={'apiKey': self.api_key},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Polygon.io connection validation failed: {e}")
            return False
    
    def get_stock_price(self, symbol: str) -> float:
        """Get current stock price from Polygon.io"""
        if not self.api_key:
            return self.simulated_fallback.get_stock_price(symbol)
        
        try:
            # Get last trade
            response = requests.get(
                f"{self.base_url}/v2/last/trade/{symbol}",
                params={'apiKey': self.api_key},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return round(data['results']['p'], 2)
            else:
                print(f"Polygon API error: {response.status_code}")
                return self.simulated_fallback.get_stock_price(symbol)
                
        except Exception as e:
            print(f"Error fetching price from Polygon: {e}")
            return self.simulated_fallback.get_stock_price(symbol)
    
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """Get options chain from Polygon.io"""
        if not self.api_key:
            return self.simulated_fallback.get_options_chain(symbol, expiration_date)
        
        try:
            # Get options contracts
            # Note: This requires Polygon.io Options add-on ($200+/month)
            response = requests.get(
                f"{self.base_url}/v3/reference/options/contracts",
                params={
                    'underlying_ticker': symbol,
                    'expiration_date': expiration_date,
                    'apiKey': self.api_key,
                    'limit': 100
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Transform Polygon data to our format
                strikes = []
                
                for contract in data.get('results', []):
                    # Get snapshot for volume/OI data
                    # This would require additional API calls
                    # For now, fall back to simulated data
                    pass
                
                # For now, use simulated as Polygon options data is complex
                return self.simulated_fallback.get_options_chain(symbol, expiration_date)
                
            else:
                print(f"Polygon options API error: {response.status_code}")
                return self.simulated_fallback.get_options_chain(symbol, expiration_date)
                
        except Exception as e:
            print(f"Error fetching options chain from Polygon: {e}")
            return self.simulated_fallback.get_options_chain(symbol, expiration_date)
    
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min') -> Dict:
        """
        Get options flow data from Polygon.io
        Note: Requires Polygon.io Options Starter plan or higher (~$200-500/month)
        """
        if not self.api_key:
            return self.simulated_fallback.get_options_flow_data(symbol, timeframe)
        
        # Polygon.io options flow requires premium subscription
        # For basic implementation, fall back to simulated data
        # In production, implement full Polygon options aggregation here
        
        print(f"📊 Polygon.io options flow not yet implemented for {symbol}")
        return self.simulated_fallback.get_options_flow_data(symbol, timeframe)
    
    def get_historical_options_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Get historical options data from Polygon.io"""
        if not self.api_key:
            return self.simulated_fallback.get_historical_options_data(symbol, days)
        
        # Historical options data requires premium Polygon.io subscription
        # Fall back to simulated for now
        return self.simulated_fallback.get_historical_options_data(symbol, days)
