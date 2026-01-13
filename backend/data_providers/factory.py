"""
Data Provider Factory
Creates the appropriate data provider based on configuration
"""
import os
from typing import Optional

from .base_provider import BaseDataProvider
from .simulated_provider import SimulatedDataProvider
from .polygon_provider import PolygonDataProvider
from .massive_provider import MassiveDataProvider
from .marketstack_provider import MarketStackProvider
from .insight_sentry_provider import InsightSentryProvider


class DataProviderFactory:
    """Factory for creating data provider instances"""
    
    @staticmethod
    def create_provider(provider_type: Optional[str] = None) -> BaseDataProvider:
        """
        Create a data provider instance
        
        Args:
            provider_type: Type of provider ('simulated', 'massive', 'polygon', 'td_ameritrade')
                          If None, auto-detects based on environment variables
        
        Returns:
            BaseDataProvider instance
        """
        if provider_type is None:
            provider_type = os.getenv('DATA_PROVIDER', 'auto')
        
        # Auto-detect based on API keys
        if provider_type == 'auto':
            insight_key = os.getenv('INSIGHT_SENTRY_API_KEY')
            massive_key = os.getenv('MASSIVE_API_KEY')
            polygon_key = os.getenv('POLYGON_API_KEY')
            td_key = os.getenv('TD_AMERITRADE_API_KEY')
            marketstack_key = os.getenv('MARKETSTACK_API_KEY')
            
            if insight_key:
                print("✅ Detected Insight Sentry API key - using InsightSentry provider")
                return InsightSentryProvider(insight_key)
            elif massive_key:
                print("✅ Detected Massive API key - using Massive provider")
                return MassiveDataProvider(massive_key)
            elif polygon_key:
                print("✅ Detected Polygon.io API key - using Polygon provider")
                return PolygonDataProvider(polygon_key)
            elif marketstack_key:
                print("✅ Detected MarketStack API key - using MarketStack provider")
                return MarketStackProvider(marketstack_key)
            elif td_key:
                print("✅ Detected TD Ameritrade API key - using TD provider")
                # return TDAmeritadeProvider(td_key)  # TODO: Implement
                print("⚠️  TD Ameritrade provider not yet implemented, using simulated")
                return SimulatedDataProvider()
            else:
                print("ℹ️  No API keys found - using simulated data provider")
                return SimulatedDataProvider()
        
        # Explicit provider selection
        elif provider_type == 'simulated':
            print("ℹ️  Using simulated data provider")
            return SimulatedDataProvider()
        
        elif provider_type == 'insight_sentry':
            api_key = os.getenv('INSIGHT_SENTRY_API_KEY')
            if not api_key:
                print("⚠️  No Insight Sentry API key found, falling back to simulated")
                return SimulatedDataProvider()
            print("✅ Using Insight Sentry data provider")
            return InsightSentryProvider(api_key)
        
        elif provider_type == 'massive':
            api_key = os.getenv('MASSIVE_API_KEY')
            if not api_key:
                print("⚠️  No Massive API key found, falling back to simulated")
                return SimulatedDataProvider()
            print("✅ Using Massive API data provider")
            return MassiveDataProvider(api_key)
        
        elif provider_type == 'polygon':
            api_key = os.getenv('POLYGON_API_KEY')
            if not api_key:
                print("⚠️  No Polygon.io API key found, falling back to simulated")
                return SimulatedDataProvider()
            print("✅ Using Polygon.io data provider")
            return PolygonDataProvider(api_key)
        
        elif provider_type == 'td_ameritrade':
            print("⚠️  TD Ameritrade provider not yet implemented, using simulated")
            return SimulatedDataProvider()
        
        else:
            print(f"⚠️  Unknown provider type '{provider_type}', using simulated")
            return SimulatedDataProvider()
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available provider types"""
        return ['simulated', 'insight_sentry', 'massive', 'polygon', 'marketstack', 'td_ameritrade']
