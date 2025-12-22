"""
Base Data Provider Interface
All data providers must implement this interface
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime


class BaseDataProvider(ABC):
    """Abstract base class for all data providers"""
    
    @abstractmethod
    def get_stock_price(self, symbol: str) -> float:
        """
        Get current stock price
        
        Args:
            symbol: Stock symbol (e.g., 'SPY', 'AAPL')
            
        Returns:
            Current price as float
        """
        pass
    
    @abstractmethod
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> Dict:
        """
        Get options chain data
        
        Args:
            symbol: Stock symbol
            expiration_date: Optional specific expiration date
            
        Returns:
            Dictionary with 'strikes', 'current_price', 'expiration'
        """
        pass
    
    @abstractmethod
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min') -> Dict:
        """
        Get options flow data for specified timeframe
        
        Args:
            symbol: Stock symbol
            timeframe: Time interval ('5min', '10min', '30min', '60min')
            
        Returns:
            Dictionary with call/put volumes, ratios, strikes, etc.
        """
        pass
    
    @abstractmethod
    def get_historical_options_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Get historical options data for backtesting
        
        Args:
            symbol: Stock symbol
            days: Number of days of historical data
            
        Returns:
            List of historical data points
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the provider is properly configured and can connect
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this data provider
        
        Returns:
            Provider name string
        """
        pass
