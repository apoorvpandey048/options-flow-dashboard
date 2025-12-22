"""
Simulated Data Provider
Generates realistic fake data for testing and development
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .base_provider import BaseDataProvider
from config import Config


class SimulatedDataProvider(BaseDataProvider):
    """Provides simulated options data for testing"""
    
    def __init__(self):
        self.base_prices = {
            'SPY': 662.17,
            'QQQ': 485.32,
            'AAPL': 245.18,
            'MSFT': 425.67,
            'NVDA': 138.42,
            'TSLA': 387.91,
            'META': 612.83,
            'GOOGL': 178.24,
            'AMZN': 218.56
        }
    
    def get_provider_name(self) -> str:
        return "Simulated Data Provider"
    
    def validate_connection(self) -> bool:
        return True
    
    def get_stock_price(self, symbol: str) -> float:
        """Get simulated stock price with small random variation"""
        base_price = self.base_prices.get(symbol, 100.0)
        variation = np.random.uniform(-2, 2)
        return round(base_price + variation, 2)
    
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """Generate simulated options chain"""
        price = self.get_stock_price(symbol)
        
        # Generate strikes around current price
        base_strike = int(price / 5) * 5
        strikes = []
        
        for i in range(-10, 11):
            strike = base_strike + (i * 5)
            distance = abs(price - strike)
            atm_factor = max(0, 1 - (distance / 50))
            
            strikes.append({
                'strike': strike,
                'call_volume': max(100, int(np.random.uniform(1000, 50000) * (atm_factor + 0.2))),
                'put_volume': max(100, int(np.random.uniform(1000, 50000) * (atm_factor + 0.2))),
                'call_oi': max(50, int(np.random.uniform(500, 30000) * (atm_factor + 0.3))),
                'put_oi': max(50, int(np.random.uniform(500, 30000) * (atm_factor + 0.3))),
                'call_iv': round(np.random.uniform(0.15, 0.45), 4),
                'put_iv': round(np.random.uniform(0.15, 0.45), 4)
            })
        
        return {
            'strikes': strikes,
            'current_price': price,
            'expiration': expiration_date or (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        }
    
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min') -> Dict:
        """Generate simulated options flow data"""
        # Timeframe multipliers
        multipliers = {
            '5min': 1.0,
            '10min': 2.0,
            '30min': 6.0,
            '60min': 12.0
        }
        
        mult = multipliers.get(timeframe, 1.0)
        market_bias = np.random.uniform(-0.3, 0.3)
        
        # Ensure minimum volumes to avoid division by zero
        call_buy = max(1000, int(np.random.uniform(10000, 30000) * mult * (1 + market_bias)))
        call_sell = max(1000, int(np.random.uniform(15000, 35000) * mult * (1 - market_bias * 0.5)))
        put_buy = max(1000, int(np.random.uniform(15000, 40000) * mult * (1 - market_bias)))
        put_sell = max(1000, int(np.random.uniform(10000, 30000) * mult * (1 + market_bias * 0.5)))
        
        chain = self.get_options_chain(symbol)
        
        # Safe division with guaranteed non-zero denominators
        call_ratio = round(call_buy / max(call_sell, 1), 4)
        put_ratio = round(put_buy / max(put_sell, 1), 4)
        put_call_ratio = round(put_buy / max(call_buy, 1), 4)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'call_buy': call_buy,
            'call_sell': call_sell,
            'put_buy': put_buy,
            'put_sell': put_sell,
            'call_ratio': call_ratio,
            'put_ratio': put_ratio,
            'put_call_ratio': put_call_ratio,
            'strikes': chain['strikes'],
            'current_price': chain['current_price']
        }
    
    def get_historical_options_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Generate simulated historical data"""
        historical_data = []
        
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            
            for hour in range(0, 24):
                put_call_ratio = np.random.lognormal(0, 0.3) + 0.8
                volume = int(np.random.uniform(50000, 200000))
                
                historical_data.append({
                    'date': date,
                    'hour': hour,
                    'symbol': symbol,
                    'put_call_ratio': put_call_ratio,
                    'volume': volume,
                    'avg_volume': 100000,
                    'iv_percentile': np.random.uniform(20, 80),
                    'price': self.get_stock_price(symbol)
                })
        
        return historical_data
