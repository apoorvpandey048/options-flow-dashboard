"""
Historical Scenario Generator for Backtesting
Creates realistic day-by-day options flow data based on actual market characteristics
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import hashlib


class HistoricalScenarioGenerator:
    """Generate realistic historical market scenarios for backtesting"""
    
    def __init__(self):
        # Market regime definitions
        self.market_regimes = {
            'bull_run': {'trend': 0.6, 'volatility': 0.8, 'pc_ratio_avg': 0.85},
            'bear_market': {'trend': -0.6, 'volatility': 1.4, 'pc_ratio_avg': 1.45},
            'high_vol': {'trend': 0.0, 'volatility': 2.0, 'pc_ratio_avg': 1.25},
            'low_vol': {'trend': 0.1, 'volatility': 0.5, 'pc_ratio_avg': 0.95},
            'choppy': {'trend': 0.0, 'volatility': 1.2, 'pc_ratio_avg': 1.10},
        }
        
        # Real event scenarios (Dec 2025)
        self.known_events = {
            '2025-12-18': {
                'regime': 'high_vol',
                'event': 'FOMC Decision',
                'description': 'Fed announcement causes extreme volatility',
                'intraday_pattern': 'whipsaw',
                'vol_spike_frequency': 'high'
            },
            '2025-12-19': {
                'regime': 'high_vol',
                'event': 'Fed Press Conference',
                'description': 'Post-Fed rally with high volume',
                'intraday_pattern': 'rally',
                'vol_spike_frequency': 'high'
            },
            '2025-12-20': {
                'regime': 'high_vol',
                'event': 'Quad Witching',
                'description': 'Options/futures expiration - elevated activity',
                'intraday_pattern': 'volatile',
                'vol_spike_frequency': 'very_high'
            },
            '2025-12-23': {
                'regime': 'low_vol',
                'event': 'Pre-Holiday',
                'description': 'Light trading ahead of Christmas',
                'intraday_pattern': 'drift',
                'vol_spike_frequency': 'low'
            },
            '2025-12-24': {
                'regime': 'low_vol',
                'event': 'Christmas Eve',
                'description': 'Half day, minimal trading',
                'intraday_pattern': 'flat',
                'vol_spike_frequency': 'very_low'
            },
            '2025-12-26': {
                'regime': 'low_vol',
                'event': 'Post-Christmas',
                'description': 'Thin volume, holiday trading',
                'intraday_pattern': 'drift',
                'vol_spike_frequency': 'low'
            },
            '2025-12-27': {
                'regime': 'low_vol',
                'event': 'Year-End Positioning',
                'description': 'Portfolio rebalancing, low volume',
                'intraday_pattern': 'grind_higher',
                'vol_spike_frequency': 'medium'
            },
        }
    
    def get_daily_scenario(self, date_str: str) -> Dict:
        """Get or generate realistic scenario for a specific date"""
        # Check if we have a known event for this date
        if date_str in self.known_events:
            event_data = self.known_events[date_str]
            regime_data = self.market_regimes[event_data['regime']]
            
            return {
                **event_data,
                **regime_data,
                'date': date_str,
                'seed': int(hashlib.md5(date_str.encode()).hexdigest()[:8], 16)
            }
        
        # Generate consistent scenario based on date hash
        date_hash = int(hashlib.md5(date_str.encode()).hexdigest()[:8], 16)
        np.random.seed(date_hash)
        
        # Pick a random regime
        regime_name = np.random.choice(list(self.market_regimes.keys()))
        regime_data = self.market_regimes[regime_name]
        
        # Determine intraday pattern
        patterns = ['rally', 'selloff', 'choppy', 'drift', 'reversal']
        pattern = np.random.choice(patterns)
        
        # Volume spike frequency
        vol_frequencies = ['low', 'medium', 'high']
        vol_freq = np.random.choice(vol_frequencies, p=[0.3, 0.5, 0.2])
        
        return {
            'regime': regime_name,
            'event': 'Regular Trading',
            'description': f'{regime_name.replace("_", " ").title()} day',
            'intraday_pattern': pattern,
            'vol_spike_frequency': vol_freq,
            **regime_data,
            'date': date_str,
            'seed': date_hash % 100000
        }
    
    def generate_intraday_data(self, date_str: str, symbol: str = 'SPY') -> List[Dict]:
        """Generate minute-by-minute options flow for entire trading day"""
        scenario = self.get_daily_scenario(date_str)
        
        # Market hours: 9:30 AM to 4:00 PM = 390 minutes
        data_points = []
        
        for minute in range(390):
            time_factor = minute / 390  # 0 to 1 through day
            
            # Generate data point for this minute
            data = self._generate_minute_data(
                scenario, 
                time_factor, 
                minute,
                symbol
            )
            
            # Add timestamp
            market_open = datetime.strptime(f"{date_str} 09:30:00", "%Y-%m-%d %H:%M:%S")
            data['timestamp'] = (market_open + timedelta(minutes=minute)).isoformat()
            data['minute'] = minute
            
            data_points.append(data)
        
        return data_points
    
    def _generate_minute_data(self, scenario: Dict, time_factor: float, minute: int, symbol: str) -> Dict:
        """Generate realistic options flow data for a single minute"""
        # Seed based on date + minute for consistency
        np.random.seed(scenario['seed'] + minute)
        
        # Base volumes
        base_volume = 10000
        
        # Apply intraday pattern
        volume_mult = self._get_volume_multiplier(scenario['intraday_pattern'], time_factor)
        
        # Apply volatility from regime
        vol_mult = scenario['volatility']
        
        # Determine if this minute has a volume spike
        spike_prob = {
            'very_low': 0.02,
            'low': 0.05,
            'medium': 0.10,
            'high': 0.20,
            'very_high': 0.35
        }
        has_spike = np.random.random() < spike_prob.get(scenario['vol_spike_frequency'], 0.10)
        
        spike_mult = np.random.uniform(1.5, 2.5) if has_spike else 1.0
        
        # Generate volumes
        total_mult = volume_mult * vol_mult * spike_mult
        call_buy = int(np.random.uniform(8000, 15000) * total_mult)
        call_sell = int(np.random.uniform(10000, 18000) * total_mult)
        put_buy = int(np.random.uniform(12000, 22000) * total_mult * (1 + scenario['trend'] * 0.3))
        put_sell = int(np.random.uniform(8000, 16000) * total_mult * (1 - scenario['trend'] * 0.3))
        
        # Calculate ratios
        put_call_ratio = (put_buy + put_sell) / max((call_buy + call_sell), 1)
        
        # Add noise to match scenario's PC ratio average
        target_pc = scenario['pc_ratio_avg']
        put_call_ratio = put_call_ratio * 0.7 + target_pc * 0.3 + np.random.uniform(-0.15, 0.15)
        put_call_ratio = max(0.5, min(2.5, put_call_ratio))  # Clamp to realistic range
        
        # IV percentile (higher in high vol scenarios)
        iv_base = 45 if scenario['volatility'] > 1.5 else 35
        iv_percentile = max(10, min(90, iv_base + np.random.uniform(-15, 15)))
        
        return {
            'symbol': symbol,
            'put_call_ratio': round(put_call_ratio, 4),
            'call_volume': call_buy + call_sell,
            'put_volume': put_buy + put_sell,
            'total_volume': call_buy + call_sell + put_buy + put_sell,
            'volume_spike': has_spike,
            'volume_spike_mult': round(spike_mult, 2) if has_spike else 1.0,
            'iv_percentile': round(iv_percentile, 1),
            'regime': scenario['regime'],
            'event': scenario.get('event', 'Regular'),
        }
    
    def _get_volume_multiplier(self, pattern: str, time_factor: float) -> float:
        """Get volume multiplier based on intraday pattern"""
        # time_factor: 0 (open) to 1 (close)
        
        if pattern == 'rally':
            # Volume increases steadily
            return 0.7 + time_factor * 0.8
        
        elif pattern == 'selloff':
            # Volume spikes early, stays elevated
            if time_factor < 0.1:
                return 1.5  # Opening spike
            return 1.2 + time_factor * 0.3
        
        elif pattern == 'choppy':
            # Multiple volume waves
            wave = np.sin(time_factor * 4 * np.pi) * 0.3 + 1.0
            return max(0.6, wave)
        
        elif pattern == 'drift':
            # Low volume, slight increase into close
            return 0.5 + time_factor * 0.4
        
        elif pattern == 'reversal':
            # V-shaped: high early, low mid, high late
            if time_factor < 0.2 or time_factor > 0.8:
                return 1.3
            return 0.7
        
        elif pattern == 'volatile' or pattern == 'whipsaw':
            # Random spikes throughout
            return 1.0 + np.random.uniform(-0.3, 0.7)
        
        elif pattern == 'flat':
            # Very low, consistent volume
            return 0.4
        
        elif pattern == 'grind_higher':
            # Steady volume with slight uptick
            return 0.8 + time_factor * 0.3
        
        else:
            # Default: slight U-shape (higher at open/close)
            if time_factor < 0.1 or time_factor > 0.9:
                return 1.2
            return 0.9


# Global instance
historical_generator = HistoricalScenarioGenerator()


if __name__ == '__main__':
    # Test the generator
    print("Testing Historical Scenario Generator\n")
    
    # Test specific dates
    test_dates = ['2025-12-18', '2025-12-20', '2025-12-24', '2025-12-27']
    
    for date in test_dates:
        scenario = historical_generator.get_daily_scenario(date)
        print(f"\n{'='*60}")
        print(f"Date: {date}")
        print(f"Event: {scenario['event']}")
        print(f"Regime: {scenario['regime']}")
        print(f"Description: {scenario['description']}")
        print(f"Intraday Pattern: {scenario['intraday_pattern']}")
        print(f"Volume Spike Frequency: {scenario['vol_spike_frequency']}")
        print(f"Avg P/C Ratio: {scenario['pc_ratio_avg']:.2f}")
        print(f"Volatility: {scenario['volatility']:.1f}x")
        
        # Generate a few sample minutes
        print(f"\nSample Minutes:")
        intraday = historical_generator.generate_intraday_data(date)
        for i in [0, 60, 120, 180, 240, 300, 360, 389]:  # Various times through day
            minute_data = intraday[i]
            print(f"  {i:3d}min: P/C={minute_data['put_call_ratio']:.2f}, "
                  f"Vol={minute_data['total_volume']:,}, "
                  f"Spike={'YES' if minute_data['volume_spike'] else 'no '}, "
                  f"IV={minute_data['iv_percentile']:.0f}%")
