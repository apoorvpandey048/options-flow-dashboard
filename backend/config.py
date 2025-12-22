"""
Configuration settings for the Options Flow Monitor application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Keys
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    
    # Options data settings
    SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'META', 'GOOGL', 'AMZN']
    TIMEFRAMES = ['5min', '10min', '30min', '60min']
    
    # Refresh rate in seconds
    REFRESH_RATE = 5
    
    # Backtester defaults
    DEFAULT_PUT_CALL_THRESHOLD = 1.1
    DEFAULT_NUM_TRADES = 1000
    DEFAULT_INITIAL_CAPITAL = 10000
    DEFAULT_POSITION_SIZE = 100
    DEFAULT_PROFIT_TARGET = 0.20
    DEFAULT_STOP_LOSS = -0.50
    DEFAULT_VOLUME_SPIKE_THRESHOLD = 1.5
    DEFAULT_IV_THRESHOLD = 30
