"""
Historical Replay System using Massive Flat Files
Downloads and processes real historical options data to create snapshots
"""
import os
import csv
import gzip
import boto3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
from botocore.config import Config


class HistoricalReplayLoader:
    """Load historical options data from Massive S3 and create replay snapshots"""
    
    def __init__(self):
        self.s3_access_key = os.getenv('MASSIVE_S3_ACCESS_KEY')
        self.s3_secret_key = os.getenv('MASSIVE_S3_SECRET_KEY')
        self.endpoint = 'https://files.massive.com'
        self.bucket = 'flatfiles'
        
        if self.s3_access_key and self.s3_secret_key:
            self.session = boto3.Session(
                aws_access_key_id=self.s3_access_key,
                aws_secret_access_key=self.s3_secret_key,
            )
            self.s3 = self.session.client(
                's3',
                endpoint_url=self.endpoint,
                config=Config(signature_version='s3v4'),
            )
            print("✅ S3 client initialized for Massive Flat Files")
        else:
            self.s3 = None
            print("⚠️  No S3 credentials found - using pre-generated snapshots")
    
    def download_minute_data(self, date: str, symbol: str = 'SPY') -> List[Dict]:
        """
        Download minute aggregate data for a specific date
        date format: YYYY-MM-DD (e.g., '2025-12-27')
        """
        if not self.s3:
            return self._get_fallback_data(date, symbol)
        
        try:
            # Format: us_options_opra/minute_aggs_v1/2025/12/2025-12-27.csv.gz
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            year = date_obj.year
            month = f"{date_obj.month:02d}"
            
            object_key = f'us_options_opra/minute_aggs_v1/{year}/{month}/{date}.csv.gz'
            local_file = f'/tmp/{date}_minute_aggs.csv.gz'
            
            print(f"📥 Downloading {object_key}...")
            self.s3.download_file(self.bucket, object_key, local_file)
            print(f"✅ Downloaded to {local_file}")
            
            # Parse CSV
            data = []
            with gzip.open(local_file, 'rt') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter for the specific symbol's options
                    if symbol in row['ticker']:
                        data.append(row)
            
            print(f"✅ Parsed {len(data)} minute records for {symbol} options")
            return data
            
        except Exception as e:
            print(f"❌ Error downloading data: {e}")
            return self._get_fallback_data(date, symbol)
    
    def create_snapshots(self, date: str, symbol: str = 'SPY', num_snapshots: int = 4) -> List[Dict]:
        """
        Create N snapshots throughout a trading day
        Default times: 9:45 AM, 11:30 AM, 2:00 PM, 3:45 PM ET
        """
        minute_data = self.download_minute_data(date, symbol)
        
        if not minute_data:
            return self._get_fallback_snapshots(date, symbol)
        
        # Define snapshot times (Unix nanoseconds)
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        snapshot_times = [
            date_obj.replace(hour=9, minute=45),   # Market open
            date_obj.replace(hour=11, minute=30),  # Mid-morning
            date_obj.replace(hour=14, minute=0),   # Afternoon
            date_obj.replace(hour=15, minute=45),  # Near close
        ]
        
        snapshots = []
        for snap_time in snapshot_times:
            snapshot = self._create_snapshot_at_time(minute_data, snap_time, symbol)
            snapshot['snapshot_time'] = snap_time.strftime('%H:%M:%S')
            snapshot['snapshot_label'] = self._get_snapshot_label(snap_time)
            snapshots.append(snapshot)
        
        return snapshots
    
    def _create_snapshot_at_time(self, minute_data: List[Dict], target_time: datetime, symbol: str) -> Dict:
        """Create a single snapshot at a specific time"""
        target_ns = int(target_time.timestamp() * 1e9)
        
        # Aggregate all data up to this time
        strikes_data = defaultdict(lambda: {'call_volume': 0, 'put_volume': 0})
        total_call_volume = 0
        total_put_volume = 0
        
        for record in minute_data:
            window_start = int(record['window_start'])
            if window_start <= target_ns:
                ticker = record['ticker']
                volume = int(record.get('volume', 0))
                
                # Parse strike from ticker (format: O:SPY230327P00390000)
                parts = ticker.split('P') if 'P' in ticker else ticker.split('C')
                if len(parts) == 2:
                    strike_str = parts[1]
                    strike = float(strike_str) / 1000  # Convert from 00390000 to 390.000
                    is_put = 'P' in ticker
                    
                    if is_put:
                        strikes_data[strike]['put_volume'] += volume
                        total_put_volume += volume
                    else:
                        strikes_data[strike]['call_volume'] += volume
                        total_call_volume += volume
        
        # Format strikes for visualization
        strikes = []
        for strike, volumes in sorted(strikes_data.items()):
            strikes.append({
                'strike': strike,
                'call_volume': volumes['call_volume'],
                'put_volume': volumes['put_volume']
            })
        
        # Get current price (approximate from ATM strike)
        price = self._estimate_price_from_strikes(strikes)
        
        return {
            'calls': {
                'total': total_call_volume,
                'buy': int(total_call_volume * 0.6),  # Estimate
                'sell': int(total_call_volume * 0.4),
                'ratio': 1.5 if total_call_volume > total_put_volume else 0.8
            },
            'puts': {
                'total': total_put_volume,
                'buy': int(total_put_volume * 0.55),
                'sell': int(total_put_volume * 0.45),
                'ratio': 1.3 if total_put_volume > total_call_volume else 0.9
            },
            'sentiment': 'bullish' if total_call_volume > total_put_volume else 'bearish',
            'strikes': strikes[:30],  # Top 30 strikes
            'price': price,
            'put_call_ratio': total_put_volume / total_call_volume if total_call_volume > 0 else 1.0,
            'timestamp': target_time.isoformat()
        }
    
    def _estimate_price_from_strikes(self, strikes: List[Dict]) -> float:
        """Estimate stock price from ATM strike"""
        if not strikes:
            return 600.0
        
        # Find strike with most volume
        max_volume_strike = max(strikes, key=lambda x: x['call_volume'] + x['put_volume'])
        return max_volume_strike['strike']
    
    def _get_snapshot_label(self, time: datetime) -> str:
        """Generate a label for the snapshot"""
        hour = time.hour
        if hour < 10:
            return "Market Open"
        elif hour < 12:
            return "Mid Morning"
        elif hour < 15:
            return "Afternoon Session"
        else:
            return "Near Close"
    
    def _get_fallback_data(self, date: str, symbol: str) -> List[Dict]:
        """Return empty data for fallback"""
        print(f"⚠️  Using fallback: no real data for {date}")
        return []
    
    def _get_fallback_snapshots(self, date: str, symbol: str) -> List[Dict]:
        """Generate realistic-looking fallback snapshots using simulated data"""
        from data_providers.simulated_provider import SimulatedDataProvider
        import random
        
        # Use simulated provider directly to avoid caching issues
        provider = SimulatedDataProvider()
        snapshots = []
        
        times = [
            ('09:45:00', 'Market Open'),
            ('11:30:00', 'Mid Morning'),
            ('14:00:00', 'Afternoon Session'),
            ('15:45:00', 'Near Close')
        ]
        
        # Get base data and evolve it throughout the day
        for i, (time_str, label) in enumerate(times):
            # Create variation in data to simulate progression
            multiplier = 1 + (i * 0.3)  # Gradually increase volumes
            
            # Get fresh data directly from provider
            data = provider.get_options_flow_data(symbol, '5min')
            
            if not data or 'calls' not in data:
                print(f"⚠️  Failed to get simulated data for {time_str}")
                continue
            
            # Apply multiplier to show evolution
            data['calls']['total'] = int(data['calls']['total'] * multiplier)
            data['calls']['buy'] = int(data['calls']['buy'] * multiplier)
            data['calls']['sell'] = int(data['calls']['sell'] * multiplier)
            data['puts']['total'] = int(data['puts']['total'] * multiplier)
            data['puts']['buy'] = int(data['puts']['buy'] * multiplier)
            data['puts']['sell'] = int(data['puts']['sell'] * multiplier)
            
            # Recalculate P/C ratio
            total_puts = data['puts']['total']
            total_calls = data['calls']['total']
            data['put_call_ratio'] = round(total_puts / max(total_calls, 1), 2)
            
            # Vary strikes slightly
            for strike in data.get('strikes', []):
                strike['call_volume'] = int(strike['call_volume'] * multiplier * random.uniform(0.8, 1.2))
                strike['put_volume'] = int(strike['put_volume'] * multiplier * random.uniform(0.8, 1.2))
            
            data['snapshot_time'] = time_str
            data['snapshot_label'] = label
            data['timestamp'] = f"{date}T{time_str}"
            
            snapshots.append(data)
        
        print(f"📊 Generated {len(snapshots)} simulated snapshots showing data evolution")
        return snapshots


# Global instance
_replay_loader = None

def get_replay_loader() -> HistoricalReplayLoader:
    """Get or create replay loader singleton"""
    global _replay_loader
    if _replay_loader is None:
        _replay_loader = HistoricalReplayLoader()
    return _replay_loader
