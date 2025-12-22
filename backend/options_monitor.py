"""
Options Flow Monitor Module
Real-time monitoring of options flow with multiple timeframes
"""
from datetime import datetime
from data_fetcher import data_fetcher
from config import Config

class OptionsFlowMonitor:
    """Monitor real-time options flow across multiple timeframes"""
    
    def __init__(self):
        self.data_fetcher = data_fetcher
        self.symbols = Config.SYMBOLS
        self.timeframes = Config.TIMEFRAMES
    
    def get_monitor_data(self, symbol, timeframe='5min'):
        """
        Get complete monitor data for a symbol and timeframe
        """
        flow_data = self.data_fetcher.get_options_flow_data(symbol, timeframe)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'price': flow_data['current_price'],
            'calls': {
                'buy': flow_data['call_buy'],
                'sell': flow_data['call_sell'],
                'total': flow_data['call_buy'] + flow_data['call_sell'],
                'ratio': flow_data['call_ratio']
            },
            'puts': {
                'buy': flow_data['put_buy'],
                'sell': flow_data['put_sell'],
                'total': flow_data['put_buy'] + flow_data['put_sell'],
                'ratio': flow_data['put_ratio']
            },
            'put_call_ratio': flow_data['put_call_ratio'],
            'sentiment': self._calculate_sentiment(flow_data),
            'strikes': flow_data['strikes']
        }
    
    def get_all_timeframes(self, symbol):
        """Get data for all timeframes for a symbol"""
        result = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'timeframes': {}
        }
        
        for tf in self.timeframes:
            result['timeframes'][tf] = self.get_monitor_data(symbol, tf)
        
        return result
    
    def get_all_symbols_summary(self, timeframe='5min'):
        """Get summary data for all symbols in specified timeframe"""
        summaries = []
        
        for symbol in self.symbols:
            data = self.get_monitor_data(symbol, timeframe)
            summaries.append({
                'symbol': symbol,
                'price': data['price'],
                'put_call_ratio': data['put_call_ratio'],
                'sentiment': data['sentiment'],
                'call_ratio': data['calls']['ratio'],
                'put_ratio': data['puts']['ratio']
            })
        
        return {
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'symbols': summaries
        }
    
    def _calculate_sentiment(self, flow_data):
        """Calculate market sentiment from flow data"""
        put_ratio = flow_data['put_ratio']
        call_ratio = flow_data['call_ratio']
        pc_ratio = flow_data['put_call_ratio']
        
        # More put buying than call buying suggests bearish sentiment
        if pc_ratio > 1.2:
            return {
                'direction': 'Bearish',
                'strength': 'Strong' if pc_ratio > 1.5 else 'Moderate',
                'score': min(100, int((pc_ratio - 1) * 100))
            }
        elif pc_ratio < 0.8:
            return {
                'direction': 'Bullish',
                'strength': 'Strong' if pc_ratio < 0.6 else 'Moderate',
                'score': min(100, int((1 - pc_ratio) * 100))
            }
        else:
            return {
                'direction': 'Neutral',
                'strength': 'Weak',
                'score': 0
            }
    
    def get_strike_analysis(self, symbol):
        """Get detailed strike-level analysis"""
        flow_data = self.data_fetcher.get_options_flow_data(symbol, '5min')
        strikes = flow_data['strikes']
        current_price = flow_data['current_price']
        
        # Find ATM strike
        atm_strike = min(strikes, key=lambda x: abs(x['strike'] - current_price))
        
        # Calculate volume concentration
        total_call_vol = sum(s['call_volume'] for s in strikes)
        total_put_vol = sum(s['put_volume'] for s in strikes)
        
        # Find strikes with highest volume
        max_call_strike = max(strikes, key=lambda x: x['call_volume'])
        max_put_strike = max(strikes, key=lambda x: x['put_volume'])
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'atm_strike': atm_strike['strike'],
            'max_call_volume_strike': {
                'strike': max_call_strike['strike'],
                'volume': max_call_strike['call_volume'],
                'percentage': round(max_call_strike['call_volume'] / max(total_call_vol, 1) * 100, 2)
            },
            'max_put_volume_strike': {
                'strike': max_put_strike['strike'],
                'volume': max_put_strike['put_volume'],
                'percentage': round(max_put_strike['put_volume'] / max(total_put_vol, 1) * 100, 2)
            },
            'total_call_volume': total_call_vol,
            'total_put_volume': total_put_vol,
            'strikes': strikes
        }


# Singleton instance
options_monitor = OptionsFlowMonitor()
