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
    
    def _get_historical_scenario(self, date_str: str, symbol: str) -> Dict:
        """Get realistic market scenario for a specific historical date"""
        # Default scenario
        default = {'bias': 0.0, 'volatility': 1.0, 'seed': 0, 'description': 'Normal Trading'}
        
        if not date_str:
            return default
        
        # Pre-defined scenarios for specific dates (realistic market conditions)
        scenarios = {
            '2025-12-27': {  # Day after Christmas - Low volume, slight bullish
                'bias': 0.15,
                'volatility': 0.7,
                'seed': 1227,
                'description': 'Post-Holiday Low Volume Rally'
            },
            '2025-12-26': {  # Day after Christmas - Very low volume
                'bias': 0.05,
                'volatility': 0.5,
                'seed': 1226,
                'description': 'Holiday Trading - Thin Volume'
            },
            '2025-12-24': {  # Christmas Eve - Early close, low volume
                'bias': -0.1,
                'volatility': 0.6,
                'seed': 1224,
                'description': 'Christmas Eve - Light Selling'
            },
            '2025-12-23': {  # Pre-Christmas - Normal to low volume
                'bias': 0.1,
                'volatility': 0.8,
                'seed': 1223,
                'description': 'Pre-Holiday Positioning'
            },
            '2025-12-20': {  # Quad witching Friday - High volume/volatility
                'bias': -0.2,
                'volatility': 1.6,
                'seed': 1220,
                'description': 'Quad Witching - High Volatility'
            },
            '2025-12-19': {  # Fed decision day - High volatility
                'bias': 0.25,
                'volatility': 1.8,
                'seed': 1219,
                'description': 'Fed Decision Day - Volatile Rally'
            },
            '2025-12-18': {  # FOMC day - Extreme volatility
                'bias': -0.3,
                'volatility': 2.0,
                'seed': 1218,
                'description': 'FOMC Day - Heavy Volatility'
            },
        }
        
        # Get scenario for date or generate based on date hash
        if date_str in scenarios:
            return scenarios[date_str]
        
        # For dates without explicit scenarios, create consistent patterns
        # Hash the date to get reproducible characteristics
        import hashlib
        date_hash = int(hashlib.md5(date_str.encode()).hexdigest()[:8], 16)
        np.random.seed(date_hash)
        
        return {
            'bias': np.random.uniform(-0.25, 0.25),
            'volatility': np.random.uniform(0.8, 1.4),
            'seed': date_hash % 10000,
            'description': 'Generated Market Day'
        }
    
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
    
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min', replay_date: str = None, replay_time: str = None) -> Dict:
        """Generate simulated options flow data"""
        # Timeframe multipliers
        multipliers = {
            '5min': 1.0,
            '10min': 2.0,
            '30min': 6.0,
            '60min': 12.0
        }
        
        mult = multipliers.get(timeframe, 1.0)
        
        # Use replay time to generate time-based progression
        if replay_time:
            hours, minutes = map(int, replay_time.split(':'))
            time_minutes = hours * 60 + minutes
            market_open = 9 * 60 + 30  # 09:30
            time_factor = (time_minutes - market_open) / 390  # 0 to 1 through trading day
            
            # Get date-based scenario for realistic historical patterns
            scenario = self._get_historical_scenario(replay_date, symbol)
            
            # Volume increases through the day
            volume_factor = 0.5 + time_factor * 1.5
            # Add some noise based on time to make each minute unique
            np.random.seed(time_minutes + scenario['seed'])
            market_bias = scenario['bias'] + np.random.uniform(-0.2, 0.2)
            mult *= volume_factor * scenario['volatility']
        else:
            # LIVE MODE: Add timestamp-based micro-variations
            # This makes data change every 1-2 seconds
            current_timestamp = int(datetime.now().timestamp())
            np.random.seed(current_timestamp)
            
            # Base pattern on time of day if during market hours
            now = datetime.now()
            if 9 <= now.hour < 16:  # Market hours
                minutes_since_open = (now.hour - 9) * 60 + now.minute - 30
                if minutes_since_open >= 0:
                    time_factor = minutes_since_open / 390
                    mult *= (0.7 + time_factor * 0.6)  # Gradual volume increase
            
            market_bias = np.random.uniform(-0.3, 0.3)
        
        # Ensure minimum volumes to avoid division by zero
        # Add micro-variations (±5%) to make data feel live
        micro_var = np.random.uniform(0.95, 1.05)
        call_buy = max(1000, int(np.random.uniform(10000, 30000) * mult * (1 + market_bias) * micro_var))
        call_sell = max(1000, int(np.random.uniform(15000, 35000) * mult * (1 - market_bias * 0.5) * micro_var))
        put_buy = max(1000, int(np.random.uniform(15000, 40000) * mult * (1 - market_bias) * micro_var))
        put_sell = max(1000, int(np.random.uniform(10000, 30000) * mult * (1 + market_bias * 0.5) * micro_var))
        
        chain = self.get_options_chain(symbol)
        
        # Safe division with guaranteed non-zero denominators
        call_ratio = round(call_buy / max(call_sell, 1), 4)
        put_ratio = round(put_buy / max(put_sell, 1), 4)
        put_call_ratio = round((put_buy + put_sell) / max((call_buy + call_sell), 1), 4)
        
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
