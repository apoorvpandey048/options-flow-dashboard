"""
Data fetcher module for retrieving real-time and historical options data
Supports multiple data providers via abstraction layer
"""
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Optional

from data_providers import DataProviderFactory, BaseDataProvider
from config import Config


class DataFetcher:
    """Handles data fetching from various APIs using provider abstraction"""
    
    def __init__(self, provider: Optional[BaseDataProvider] = None):
        # Use provided provider or create one via factory
        self.provider = provider or DataProviderFactory.create_provider()
        self.cache = {}
        self.cache_timeout = 60  # seconds
        self.max_cache_size = 100  # Maximum cache entries
        self._cache_lock = threading.Lock()  # Thread-safe cache access
        
        print(f"📊 Data Fetcher initialized with: {self.provider.get_provider_name()}")
        
    def get_stock_price(self, symbol: str) -> float:
        """Get current stock price"""
        try:
            return self.provider.get_stock_price(symbol)
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return 100.0
    
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> dict:
        """Get options chain data"""
        try:
            return self.provider.get_options_chain(symbol, expiration_date)
        except Exception as e:
            print(f"Error fetching options chain for {symbol}: {e}")
            return {'strikes': [], 'current_price': 100.0, 'expiration': None}
    
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min', replay_date: str = None, replay_time: str = None) -> dict:
        """
        Get options flow data for specified timeframe
        Returns put/call ratios and volume data
        Thread-safe with proper cache management
        """
        # Don't cache historical replay data - need fresh data each time
        if replay_date or replay_time:
            try:
                return self.provider.get_options_flow_data(symbol, timeframe, replay_date, replay_time)
            except Exception as e:
                print(f"Error fetching flow data for {symbol}: {e}")
                return self._get_default_data(symbol, timeframe)
        
        cache_key = f"{symbol}_{timeframe}"
        
        # Thread-safe cache check
        with self._cache_lock:
            if cache_key in self.cache:
                timestamp, data = self.cache[cache_key]
                if time.time() - timestamp < self.cache_timeout:
                    return data
            
            # Clear old cache entries to prevent memory leak
            self._clear_old_cache_entries()
            
            # Enforce max cache size
            if len(self.cache) >= self.max_cache_size:
                self._clear_old_cache_entries(force=True)
        
        try:
            data = self.provider.get_options_flow_data(symbol, timeframe, replay_date, replay_time)
            
            # Thread-safe cache update
            with self._cache_lock:
                self.cache[cache_key] = (time.time(), data)
            
            return data
            
        except Exception as e:
            print(f"Error fetching flow data for {symbol}: {e}")
            return self._get_default_data(symbol, timeframe)
    
    def _get_default_data(self, symbol: str, timeframe: str) -> dict:
        """Return safe default data"""
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'call_buy': 1000,
            'call_sell': 1000,
            'put_buy': 1000,
            'put_sell': 1000,
            'call_ratio': 1.0,
            'put_ratio': 1.0,
            'put_call_ratio': 1.0,
            'strikes': [],
            'current_price': 100.0
        }
    
    def _clear_old_cache_entries(self, force=False):
        """Clear cache entries older than timeout to prevent memory leak"""
        current_time = time.time()
        if force:
            # Aggressive cleanup - remove oldest 50% of entries
            sorted_cache = sorted(self.cache.items(), key=lambda x: x[1][0])
            to_remove = len(sorted_cache) // 2
            for key, _ in sorted_cache[:to_remove]:
                del self.cache[key]
        else:
            # Normal cleanup - remove expired entries
            keys_to_delete = [
                key for key, (timestamp, _) in self.cache.items()
                if current_time - timestamp > self.cache_timeout * 2
            ]
            for key in keys_to_delete:
                del self.cache[key]
    
    
    def get_multi_timeframe_data(self, symbol: str) -> dict:
        """Get data for all timeframes"""
        data = {}
        for tf in Config.TIMEFRAMES:
            data[tf] = self.get_options_flow_data(symbol, tf)
        return data
    
    def get_historical_options_data(self, symbol: str, days: int = 30):
        """Get historical options data for backtesting"""
        try:
            return self.provider.get_historical_options_data(symbol, days)
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return []
    
    def switch_provider(self, provider: BaseDataProvider):
        """Switch to a different data provider at runtime"""
        old_provider = self.provider.get_provider_name()
        self.provider = provider
        print(f"🔄 Switched data provider from {old_provider} to {provider.get_provider_name()}")
        
        # Clear cache when switching providers
        with self._cache_lock:
            self.cache.clear()
    
    def validate_provider(self) -> bool:
        """Check if current provider is working correctly"""
        return self.provider.validate_connection()


# Singleton instance - auto-detects provider from environment
data_fetcher = DataFetcher()
