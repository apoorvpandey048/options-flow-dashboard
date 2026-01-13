"""
Insight Sentry WebSocket Client
Handles real-time options data streaming via WebSocket
"""

import asyncio
import json
import time
import websockets
from typing import Dict, Callable, Optional, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightSentryWebSocket:
    """WebSocket client for Insight Sentry real-time options data"""
    
    WS_URL = "wss://realtime.insightsentry.com/live"
    
    def __init__(self, rest_api_key: str, callback: Callable):
        """
        Initialize WebSocket client
        
        Args:
            rest_api_key: Your REST API key (will be used to get WebSocket key)
            callback: Function to call with new data updates
        """
        self.rest_api_key = rest_api_key
        self.callback = callback
        self.ws_api_key = None
        self.websocket = None
        self.subscribed_symbols = []
        self.is_running = False
        self.reconnect_delay = 1  # Start with 1 second
        self.max_reconnect_delay = 30
        
        # Store latest data for each option symbol
        self.option_data_cache = {}
        
    def _get_ws_api_key(self) -> Optional[str]:
        """
        Get WebSocket API key from REST API
        For native API users, REST key can be used directly
        
        Returns:
            WebSocket API key or None if error
        """
        # For InsightSentry native API, we can use the REST API key directly
        # If using RapidAPI, you'd need to call /v2/websocket-key endpoint
        return self.rest_api_key
    
    async def connect(self):
        """Establish WebSocket connection with auto-reconnect"""
        self.is_running = True
        
        while self.is_running:
            try:
                logger.info("Connecting to Insight Sentry WebSocket...")
                
                if not self.ws_api_key:
                    self.ws_api_key = self._get_ws_api_key()
                    if not self.ws_api_key:
                        logger.error("Failed to get WebSocket API key")
                        await asyncio.sleep(5)
                        continue
                
                async with websockets.connect(
                    self.WS_URL,
                    ping_interval=None,  # We'll handle pings manually
                    close_timeout=10
                ) as websocket:
                    self.websocket = websocket
                    logger.info("WebSocket connected successfully")
                    
                    # Reset reconnect delay on successful connection
                    self.reconnect_delay = 1
                    
                    # Subscribe to symbols
                    await self._subscribe()
                    
                    # Start ping task
                    ping_task = asyncio.create_task(self._send_ping())
                    
                    try:
                        # Handle incoming messages
                        await self._handle_messages()
                    finally:
                        ping_task.cancel()
                        try:
                            await ping_task
                        except asyncio.CancelledError:
                            pass
                        
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed: {e}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}", exc_info=True)
            
            if self.is_running:
                logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)
                
                # Exponential backoff
                self.reconnect_delay = min(
                    self.reconnect_delay * 2,
                    self.max_reconnect_delay
                )
    
    async def _subscribe(self):
        """Send subscription message for all symbols"""
        if not self.subscribed_symbols or not self.websocket:
            return
        
        # Build subscription message
        # For options, we subscribe to quote type for real-time updates
        subscriptions = []
        
        for symbol in self.subscribed_symbols:
            # Subscribe to the underlying symbol for quote data
            subscriptions.append({
                "code": symbol,
                "type": "quote"
            })
        
        subscription_msg = {
            "api_key": self.ws_api_key,  # Standard field name for API key
            "subscriptions": subscriptions
        }
        
        logger.info(f"Subscribing to {len(subscriptions)} symbols: {self.subscribed_symbols}")
        await self.websocket.send(json.dumps(subscription_msg))
    
    async def _send_ping(self):
        """Send periodic ping messages to keep connection alive"""
        while self.is_running and self.websocket:
            try:
                await asyncio.sleep(20)  # Every 20 seconds
                if self.websocket:
                    await self.websocket.send('ping')
                    logger.debug("Sent ping")
            except Exception as e:
                logger.error(f"Ping failed: {e}")
                break
    
    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        async for message in self.websocket:
            try:
                # Skip pong responses
                if message == 'pong':
                    logger.debug("Received pong")
                    continue
                
                # Parse JSON message
                data = json.loads(message)
                
                # Check for server heartbeat
                if 'server_time' in data:
                    logger.debug(f"Server heartbeat: {data['server_time']}")
                    continue
                
                # Check for error messages
                if 'message' in data and 'code' not in data:
                    logger.warning(f"Server message: {data['message']}")
                    continue
                
                # Check for quote data
                if 'data' in data and isinstance(data['data'], list):
                    for quote in data['data']:
                        if 'code' in quote:
                            await self._process_quote(quote)
                
                # Check for series data
                elif 'code' in data and 'series' in data:
                    await self._process_series(data)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}, message: {message}")
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
    
    async def _process_quote(self, quote: Dict):
        """
        Process quote data update
        
        Args:
            quote: Quote data from WebSocket
        """
        code = quote.get('code')
        
        # Update cache
        self.option_data_cache[code] = {
            'last_price': quote.get('last_price'),
            'volume': quote.get('volume', 0),
            'bid': quote.get('bid'),
            'ask': quote.get('ask'),
            'bid_size': quote.get('bid_size'),
            'ask_size': quote.get('ask_size'),
            'change_percent': quote.get('change_percent'),
            'timestamp': quote.get('lp_time') or time.time(),
            'last_update': quote.get('last_update', int(time.time() * 1000))
        }
        
        # Call the callback with updated data
        if self.callback:
            try:
                await self.callback(code, self.option_data_cache[code])
            except Exception as e:
                logger.error(f"Callback error: {e}", exc_info=True)
    
    async def _process_series(self, data: Dict):
        """
        Process series (OHLCV) data update
        
        Args:
            data: Series data from WebSocket
        """
        code = data.get('code')
        series = data.get('series', [])
        
        if not series:
            return
        
        # Get latest bar
        latest_bar = series[-1]
        
        # Update cache
        self.option_data_cache[code] = {
            'last_price': latest_bar.get('close'),
            'volume': latest_bar.get('volume', 0),
            'open': latest_bar.get('open'),
            'high': latest_bar.get('high'),
            'low': latest_bar.get('low'),
            'timestamp': latest_bar.get('time'),
            'last_update': data.get('last_update', int(time.time() * 1000))
        }
        
        # Call the callback
        if self.callback:
            try:
                await self.callback(code, self.option_data_cache[code])
            except Exception as e:
                logger.error(f"Callback error: {e}", exc_info=True)
    
    def subscribe_symbols(self, symbols: List[str]):
        """
        Subscribe to symbols for real-time updates
        
        Args:
            symbols: List of symbol codes (e.g., ["NASDAQ:AAPL", "AMEX:SPY"])
        """
        self.subscribed_symbols = symbols
        logger.info(f"Subscription list updated: {symbols}")
    
    async def change_subscriptions(self, symbols: List[str]):
        """
        Change subscriptions dynamically
        
        Args:
            symbols: New list of symbols to subscribe to
        """
        self.subscribed_symbols = symbols
        if self.websocket:
            await self._subscribe()
    
    def get_cached_data(self, symbol: str) -> Optional[Dict]:
        """
        Get cached data for a symbol
        
        Args:
            symbol: Symbol code
            
        Returns:
            Cached data or None
        """
        return self.option_data_cache.get(symbol)
    
    def get_all_cached_data(self) -> Dict[str, Dict]:
        """
        Get all cached data
        
        Returns:
            Dictionary of symbol -> data
        """
        return self.option_data_cache.copy()
    
    async def stop(self):
        """Stop the WebSocket connection"""
        logger.info("Stopping WebSocket client...")
        self.is_running = False
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
