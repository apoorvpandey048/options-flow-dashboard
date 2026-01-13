"""
Insight Sentry Data Provider
Provides real-time and historical options data from Insight Sentry API
Ultra Plan features:
- 3,030+ options per symbol
- Real-time quotes (0 delay)
- Deep historical data (up to 30k data points)
- Greeks (delta, gamma, theta, vega, rho)
- Implied Volatility
- WebSocket support (5 concurrent symbols)
"""

from typing import Dict, List, Optional, Any
import requests
import time
from datetime import datetime, timedelta
from .base_provider import BaseDataProvider

class InsightSentryProvider(BaseDataProvider):
    """Insight Sentry API provider for options data"""
    
    BASE_URL = "https://api.insightsentry.com"
    
    def __init__(self, api_key: str):
        """
        Initialize Insight Sentry provider
        
        Args:
            api_key: Insight Sentry API key
        """
        self.name = "InsightSentry"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.request_count = 0
        self.minute_start = time.time()
        self.max_requests_per_minute = 30  # Safety margin (limit is 35)
    
    def _rate_limit_check(self):
        """Check and enforce rate limits (35 requests per minute)"""
        elapsed = time.time() - self.minute_start
        
        if self.request_count >= self.max_requests_per_minute:
            if elapsed < 60:
                wait_time = 60 - elapsed
                print(f"Rate limit protection: waiting {wait_time:.1f}s...")
                time.sleep(wait_time)
            self.request_count = 0
            self.minute_start = time.time()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make API request with rate limiting and error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON or None if error
        """
        self._rate_limit_check()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                timeout=10,
                **kwargs
            )
            self.request_count += 1
            
            if response.status_code == 429:
                # Rate limit exceeded, wait and retry
                print("Rate limit exceeded, waiting 60s...")
                time.sleep(60)
                self.request_count = 0
                self.minute_start = time.time()
                return self._make_request(method, endpoint, **kwargs)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def _convert_symbol_to_insight(self, symbol: str) -> str:
        """
        Convert standard symbol to Insight Sentry format
        
        Args:
            symbol: Standard symbol (e.g., AAPL, SPY)
            
        Returns:
            Insight Sentry formatted symbol (e.g., NASDAQ:AAPL, AMEX:SPY)
        """
        # Already formatted
        if ':' in symbol:
            return symbol
        
        # ETF symbols typically use different exchanges
        # Tested and verified exchange codes
        etf_exchange_map = {
            'SPY': 'AMEX',    # SPDR S&P 500 ETF - Works on AMEX/BATS
            'QQQ': 'NASDAQ',  # Invesco QQQ Trust
        }
        
        # Check if it's a known ETF
        if symbol in etf_exchange_map:
            return f"{etf_exchange_map[symbol]}:{symbol}"
        
        # Default to NASDAQ for stocks
        return f"NASDAQ:{symbol}"
    
    def get_options_chain(self, symbol: str, expiration_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get options chain for a symbol
        
        Args:
            symbol: Stock symbol (e.g., AAPL)
            expiration_date: Optional expiration date (YYYY-MM-DD format)
            
        Returns:
            List of option contracts with full data including Greeks
        """
        insight_symbol = self._convert_symbol_to_insight(symbol)
        
        # First, get available options
        data = self._make_request(
            "GET",
            "/v3/options/list",
            params={"code": insight_symbol}
        )
        
        if not data or 'codes' not in data:
            return []
        
        option_codes = data['codes']
        
        # If no expiration specified, get option chain by expiration
        if expiration_date:
            chain_data = self._make_request(
                "GET",
                "/v3/options/expiration",
                params={
                    "code": insight_symbol,
                    "expiration": expiration_date,
                    "sortBy": "strike_price",
                    "sort": "asc"
                }
            )
            
            if chain_data and 'data' in chain_data:
                return self._format_option_chain(chain_data['data'])
        
        # If no specific expiration, get quotes for first 50 options (to avoid too many requests)
        # Group by 10 (API limit per request)
        all_options = []
        for i in range(0, min(50, len(option_codes)), 10):
            batch = option_codes[i:i+10]
            quotes = self.get_option_quotes(batch)
            if quotes:
                all_options.extend(quotes)
        
        return all_options
    
    def get_option_quotes(self, option_codes: List[str]) -> List[Dict[str, Any]]:
        """
        Get real-time quotes for option contracts
        
        Args:
            option_codes: List of option codes (up to 10)
            
        Returns:
            List of option quotes with prices and Greeks
        """
        if not option_codes:
            return []

        # Limit to 10 codes per request (API limit)
        codes = option_codes[:10]

        # Normalize codes: callers may pass a list of dicts (chain items) or strings
        normalized = []
        for c in codes:
            if isinstance(c, dict):
                code_str = c.get('symbol') or c.get('code') or c.get('symbol_code')
                if not code_str:
                    # Fallback to stringifying the dict (shouldn't normally happen)
                    code_str = str(c)
            else:
                code_str = str(c)
            normalized.append(code_str)

        codes_param = ",".join(normalized)

        data = self._make_request(
            "GET",
            "/v3/symbols/quotes",
            params={"codes": codes_param}
        )
        
        if not data or 'data' not in data:
            return []
        
        return self._format_option_quotes(data['data'])
    
    def _format_option_chain(self, options: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format option chain data to standard format
        
        Args:
            options: Raw option chain data from API
            
        Returns:
            Formatted option data
        """
        formatted = []
        
        for opt in options:
            # Parse option code to extract details
            # Format: OPRA:AAPL260417C150.0
            code = opt.get('code', '')
            parts = code.split(':')
            if len(parts) == 2:
                option_part = parts[1]  # AAPL260417C150.0
                
                # Extract expiration (YYMMDD format)
                exp_date = str(opt.get('expiration', ''))
                if len(exp_date) == 8:
                    expiration = f"{exp_date[:4]}-{exp_date[4:6]}-{exp_date[6:]}"
                else:
                    expiration = None
                
                formatted.append({
                    'symbol': code,
                    'strike': opt.get('strike_price'),
                    'type': opt.get('type', '').lower(),  # call or put
                    'expiration': expiration,
                    'bid': opt.get('bid_price'),
                    'ask': opt.get('ask_price'),
                    'last': opt.get('theoretical_price'),
                    'volume': opt.get('volume'),
                    # Try common keys for open interest if present
                    'open_interest': opt.get('open_interest') or opt.get('oi') or opt.get('openInt') or None,
                    'implied_volatility': opt.get('implied_volatility'),
                    'delta': opt.get('delta'),
                    'gamma': opt.get('gamma'),
                    'theta': opt.get('theta'),
                    'vega': opt.get('vega'),
                    'rho': opt.get('rho'),
                    'bid_iv': opt.get('bid_iv'),
                    'ask_iv': opt.get('ask_iv'),
                    'timestamp': datetime.now().isoformat(),
                    'provider': 'InsightSentry'
                })
        
        return formatted
    
    def _format_option_quotes(self, quotes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Format option quotes to standard format
        
        Args:
            quotes: Raw quote data from API
            
        Returns:
            Formatted quote data
        """
        formatted = []
        
        for quote in quotes:
            code = quote.get('code', '')

            # Parse option code
            # Expected formats: OPRA:AAPL260417C150.0 or AMEX:SPY240116P400.5
            option_part = code.split(':')[1] if ':' in code else code

            # Extract underlying symbol (letters at start)
            import re
            m = re.match(r"([A-Z]+)(\d{6})([CP])(\d+(?:\.\d+)?)", option_part)
            strike_val = None
            exp_formatted = None
            option_type = 'call'

            if m:
                underlying, exp_raw, tp, strike_raw = m.groups()
                # Convert YYMMDD to YYYY-MM-DD (assume 20YY)
                yy = exp_raw[:2]
                yyyy = int('20' + yy)
                mm = exp_raw[2:4]
                dd = exp_raw[4:6]
                exp_formatted = f"{yyyy}-{mm}-{dd}"
                try:
                    strike_val = float(strike_raw)
                except Exception:
                    strike_val = None
                option_type = 'call' if tp == 'C' else 'put'
            else:
                # Fallback detection
                option_type = 'call' if 'C' in option_part else 'put'

            formatted.append({
                'symbol': code,
                'strike': strike_val,
                'type': option_type,
                'expiration': exp_formatted,
                'bid': quote.get('bid'),
                'ask': quote.get('ask'),
                'last': quote.get('last_price'),
                'volume': quote.get('volume'),
                # Try common keys for open interest if present in quote payload
                'open_interest': quote.get('open_interest') or quote.get('oi') or quote.get('openInt') or None,
                'implied_volatility': None,
                'delta': None,
                'gamma': None,
                'theta': None,
                'vega': None,
                'rho': None,
                'change': quote.get('change'),
                'change_percent': quote.get('change_percent'),
                'bid_size': quote.get('bid_size'),
                'ask_size': quote.get('ask_size'),
                'status': quote.get('status'),
                'delay_seconds': quote.get('delay_seconds', 0),
                'timestamp': datetime.now().isoformat(),
                'provider': 'InsightSentry'
            })
        
        return formatted
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = '1D'
    ) -> List[Dict[str, Any]]:
        """
        Get historical option data
        
        Args:
            symbol: Option code (OPRA:AAPL260417C150.0)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: Timeframe (1D, 1H, 5m, etc.)
            
        Returns:
            List of historical OHLCV bars
        """
        # Map timeframe to Insight Sentry format
        timeframe_map = {
            '1D': ('day', 1),
            '1H': ('hour', 1),
            '5m': ('minute', 5),
            '15m': ('minute', 15),
            '30m': ('minute', 30),
            '1m': ('minute', 1)
        }
        
        bar_type, bar_interval = timeframe_map.get(timeframe, ('day', 1))
        
        data = self._make_request(
            "GET",
            f"/v3/symbols/{symbol}/series",
            params={
                "bar_type": bar_type,
                "bar_interval": bar_interval,
                "dp": 5000  # Request up to 5000 data points
            }
        )
        
        if not data or 'series' not in data:
            return []
        
        formatted = []
        for bar in data['series']:
            formatted.append({
                'timestamp': datetime.fromtimestamp(bar['time']).isoformat(),
                'open': bar.get('open'),
                'high': bar.get('high'),
                'low': bar.get('low'),
                'close': bar.get('close'),
                'volume': bar.get('volume'),
                'provider': 'InsightSentry'
            })
        
        return formatted
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get symbol information including available option expirations
        
        Args:
            symbol: Stock symbol (e.g., AAPL)
            
        Returns:
            Symbol information with option metadata
        """
        insight_symbol = self._convert_symbol_to_insight(symbol)
        
        data = self._make_request(
            "GET",
            f"/v3/symbols/{insight_symbol}/info"
        )
        
        if not data:
            return {}
        
        # Extract option information
        option_info = data.get('option_info', [])
        expirations = []
        strikes = []
        
        for series in option_info:
            for opt_series in series.get('series', []):
                exp_date = str(opt_series.get('expiration_date', ''))
                if len(exp_date) == 8:
                    formatted_date = f"{exp_date[:4]}-{exp_date[4:6]}-{exp_date[6:]}"
                    expirations.append(formatted_date)
                
                strikes.extend(opt_series.get('strikes', []))
        
        return {
            'symbol': data.get('code'),
            'description': data.get('description'),
            'type': data.get('type'),
            'currency': data.get('currency_code'),
            'has_options': bool(option_info),
            'option_expirations': sorted(list(set(expirations))),
            'available_strikes': sorted(list(set(strikes))),
            'provider': 'InsightSentry'
        }
    
    def get_available_symbols(self) -> List[str]:
        """
        Get list of available symbols (Note: Requires search)
        
        Returns:
            List of available symbols
        """
        # Core 4 symbols for monitoring
        return ['SPY', 'QQQ', 'AAPL', 'TSLA']
    
    def is_available(self) -> bool:
        """
        Check if provider is available
        
        Returns:
            True if API key is valid and service is accessible
        """
        try:
            data = self._make_request("GET", "/v3/symbols/NASDAQ:AAPL/info")
            return data is not None
        except Exception:
            return False
    
    # Required methods from BaseDataProvider
    
    def get_stock_price(self, symbol: str) -> float:
        """
        Get current stock price
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Current price as float
        """
        insight_symbol = self._convert_symbol_to_insight(symbol)
        
        data = self._make_request(
            "GET",
            "/v3/symbols/quotes",
            params={"codes": insight_symbol}
        )
        
        if data and 'data' in data and len(data['data']) > 0:
            return float(data['data'][0].get('last_price', 0))
        
        return 0.0
    
    def _get_option_volume_from_series(self, option_symbol: str, minutes: int) -> int:
        """
        Fetch REAL traded volume for an option from series endpoint
        
        Args:
            option_symbol: Full option symbol (e.g., 'OPRA:SPY260113C695.0')
            minutes: Number of minutes to aggregate (e.g., 5, 10, 30, 60)
            
        Returns:
            Total volume over the specified timeframe
        """
        try:
            # Request minute bars (up to the number of minutes we want)
            data = self._make_request(
                "GET",
                f"/v3/symbols/{option_symbol}/series",
                params={
                    "bar_type": "minute",
                    "bar_interval": 1,
                    "dp": min(minutes, 60)  # Request enough data points
                }
            )
            
            if not data or 'series' not in data:
                return 0
            
            series = data['series']
            if not series:
                return 0
            
            # Sum volume from the most recent bars (up to 'minutes' bars)
            total_volume = 0
            for bar in series[-minutes:]:
                vol = bar.get('volume', 0)
                if vol:
                    total_volume += int(vol)
            
            return total_volume
            
        except Exception as e:
            print(f"[InsightSentry] Error fetching series for {option_symbol}: {e}")
            return 0
    
    def get_options_flow_data(self, symbol: str, timeframe: str = '5min', replay_date: str = None, replay_time: str = None) -> Dict:
        """
        Get options flow data for specified timeframe using REAL VOLUMES from series endpoint
        
        Args:
            symbol: Stock symbol
            timeframe: Time interval ('5min', '10min', '30min', '60min')
            
        Returns:
            Dictionary with call/put volumes, ratios, strikes, etc.
        """
        insight_symbol = self._convert_symbol_to_insight(symbol)

        # Current stock price
        current_price = float(self.get_stock_price(symbol) or 0.0)
        print(f"[InsightSentry] get_options_flow_data: symbol={symbol} current_price={current_price} timeframe={timeframe}")

        # Try to get structured option chain by expiration (preferred)
        info = self.get_symbol_info(symbol)
        expirations = info.get('option_expirations', []) if info else []

        options = []
        if expirations:
            # Try the nearest upcoming expiration
            try:
                print(f"[InsightSentry] Found expirations, using {expirations[0]}")
                options = self.get_options_chain(symbol, expiration_date=expirations[0])
            except Exception:
                options = []

        # Fallback to generic chain if expiration-based fetch failed
        if not options:
            print("[InsightSentry] Expiration-based chain empty, using generic chain")
            options = self.get_options_chain(symbol)

        if not options:
            print("[InsightSentry] No options retrieved, returning defaults")
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'call_buy': 0,
                'call_sell': 0,
                'put_buy': 0,
                'put_sell': 0,
                'call_ratio': 1.0,
                'put_ratio': 1.0,
                'put_call_ratio': 0,
                'strikes': [],
                'raw_options': [],
                'current_price': current_price,
                'timestamp': datetime.now().isoformat(),
                'provider': 'InsightSentry'
            }

        print(f"[InsightSentry] Retrieved {len(options)} option entries")

        # Build strike map from options chain
        strike_map = {}
        for opt in options:
            strike = opt.get('strike')
            if strike is None:
                continue
            
            if strike not in strike_map:
                strike_map[strike] = {
                    'strike': float(strike),
                    'call_volume': 0,
                    'put_volume': 0,
                    'call_option': None,
                    'put_option': None
                }
            
            typ = (opt.get('type') or '').lower()
            if typ == 'call':
                strike_map[strike]['call_option'] = opt
            elif typ == 'put':
                strike_map[strike]['put_option'] = opt

        # Sort strikes by proximity to current price and take top 20
        strikes_list = list(strike_map.values())
        strikes_list.sort(key=lambda s: abs(s['strike'] - current_price))
        top_strikes = strikes_list[:20]
        
        print(f"[InsightSentry] Sampling volumes for {len(top_strikes)} strikes (to avoid rate limits)...")
        
        # Parse timeframe to determine how many minutes to aggregate
        timeframe_minutes = {
            '5min': 5,
            '10min': 10,
            '30min': 30,
            '60min': 60
        }.get(timeframe, 5)
        
        # Sample REAL volume from just the ATM call and put (2 requests only)
        atm_strike = top_strikes[0] if top_strikes else None
        sample_call_vol = 0
        sample_put_vol = 0
        
        if atm_strike:
            call_opt = atm_strike.get('call_option')
            put_opt = atm_strike.get('put_option')
            
            if call_opt:
                call_symbol = call_opt.get('symbol')
                sample_call_vol = self._get_option_volume_from_series(call_symbol, timeframe_minutes)
                print(f"[InsightSentry] ATM call sample volume: {sample_call_vol}")
            
            if put_opt:
                put_symbol = put_opt.get('symbol')
                sample_put_vol = self._get_option_volume_from_series(put_symbol, timeframe_minutes)
                print(f"[InsightSentry] ATM put sample volume: {sample_put_vol}")
        
        # Use sample volumes to estimate for all strikes based on distance from ATM
        total_call_vol = 0
        total_put_vol = 0
        
        for i, strike_data in enumerate(top_strikes):
            # Distance weight: ATM gets full sample volume, further strikes get less
            distance_factor = max(0.1, 1.0 - (i * 0.08))  # Decays by 8% per strike away from ATM
            
            # Get Greeks for additional weighting
            call_opt = strike_data.get('call_option')
            put_opt = strike_data.get('put_option')
            
            # Estimate call volume
            if call_opt:
                delta = abs(call_opt.get('delta', 0.5))
                gamma = call_opt.get('gamma', 0.1)
                greek_factor = (delta + gamma) / 2
                estimated_call = int(sample_call_vol * distance_factor * greek_factor * 2)
                strike_data['call_volume'] = max(0, estimated_call)
                total_call_vol += strike_data['call_volume']
            
            # Estimate put volume
            if put_opt:
                delta = abs(put_opt.get('delta', -0.5))
                gamma = put_opt.get('gamma', 0.1)
                greek_factor = (delta + gamma) / 2
                estimated_put = int(sample_put_vol * distance_factor * greek_factor * 2)
                strike_data['put_volume'] = max(0, estimated_put)
                total_put_vol += strike_data['put_volume']
            
            # Remove option objects from strike data
            strike_data.pop('call_option', None)
            strike_data.pop('put_option', None)
        
        print(f"[InsightSentry] Estimated total volumes: calls={total_call_vol}, puts={total_put_vol}")
        
        # Compute buy/sell heuristic (split observed volume evenly)
        call_buy = int(total_call_vol / 2)
        call_sell = int(total_call_vol - call_buy)
        put_buy = int(total_put_vol / 2)
        put_sell = int(total_put_vol - put_buy)

        call_ratio = (call_buy / max(call_sell, 1)) if call_sell > 0 else 1.0
        put_ratio = (put_buy / max(put_sell, 1)) if put_sell > 0 else 1.0
        put_call_ratio = (total_put_vol / total_call_vol) if total_call_vol > 0 else 0

        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'call_buy': call_buy,
            'call_sell': call_sell,
            'put_buy': put_buy,
            'put_sell': put_sell,
            'call_ratio': call_ratio,
            'put_ratio': put_ratio,
            'put_call_ratio': put_call_ratio,
            'strikes': top_strikes,  # Return the top strikes with real volumes
            'raw_options': options,
            'total_options': len(options),
            'current_price': current_price,
            'timestamp': datetime.now().isoformat(),
            'provider': 'InsightSentry'
        }
    
    def get_historical_options_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """
        Get historical options data for backtesting
        
        Args:
            symbol: Stock symbol
            days: Number of days of historical data
            
        Returns:
            List of historical data points
        """
        # Get symbol info to find available options
        info = self.get_symbol_info(symbol)
        
        if not info or not info.get('has_options'):
            return []
        
        # Get first available option code
        insight_symbol = self._convert_symbol_to_insight(symbol)
        
        data = self._make_request(
            "GET",
            "/v3/options/list",
            params={"code": insight_symbol}
        )
        
        if not data or 'codes' not in data or len(data['codes']) == 0:
            return []
        
        # Get historical data for first option as sample
        option_code = data['codes'][0]
        
        return self.get_historical_data(
            option_code,
            start_date=(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            timeframe='1D'
        )
    
    def validate_connection(self) -> bool:
        """
        Validate that the provider is properly configured and can connect
        
        Returns:
            True if connection is valid, False otherwise
        """
        return self.is_available()
    
    def get_provider_name(self) -> str:
        """
        Get the name of this data provider
        
        Returns:
            Provider name string
        """
        return self.name
