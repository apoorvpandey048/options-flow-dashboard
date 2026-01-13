"""Test Data Bento OPRA options data"""
import databento as db

API_KEY = "db-9r4bnaxpLhTeVjLwkxrAC6TR3Prjx"

print("=" * 60)
print("DATA BENTO OPRA OPTIONS TEST")
print("=" * 60)

client = db.Historical(API_KEY)

# Test 1: Find SPY option symbols
print("\n1. Finding SPY option symbols for Dec 1, 2025...")
try:
    result = client.symbology.resolve(
        dataset='OPRA.PILLAR',
        symbols=['SPY.OPT'],
        stype_in='parent',
        stype_out='instrument_id',
        start_date='2025-12-01',
        end_date='2025-12-02'
    )
    
    spy_options = result.get('SPY.OPT', [])
    print(f"✅ Found {len(spy_options)} SPY option contracts")
    print(f"Sample IDs: {spy_options[:3]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    spy_options = []

# Test 2: Get actual trades data
if spy_options:
    print("\n2. Fetching options trades for first 3 SPY options...")
    try:
        sample_symbols = spy_options[:3]
        
        data = client.timeseries.get_range(
            dataset='OPRA.PILLAR',
            symbols=sample_symbols,
            schema='trades',
            start='2025-12-01T14:30',
            end='2025-12-01T14:35',
            limit=100
        )
        
        trades = list(data)
        print(f"✅ Retrieved {len(trades)} option trades")
        
        if trades:
            print("\nFirst 5 trades:")
            for i, trade in enumerate(trades[:5], 1):
                print(f"  {i}. {trade}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

# Test 3: Get OHLCV bars (1-minute) - using ALL_SYMBOLS
print("\n3. Testing 1-minute OHLCV bars for ALL OPRA options...")
try:
    data = client.timeseries.get_range(
        dataset='OPRA.PILLAR',
        symbols='ALL_SYMBOLS',
        schema='ohlcv-1m',
        start='2025-12-01T14:30',
        end='2025-12-01T14:32',
        limit=50
    )
    
    bars = list(data)
    print(f"✅ Retrieved {len(bars)} OHLCV bars")
    
    if bars:
        print("\nFirst 3 bars:")
        for i, bar in enumerate(bars[:3], 1):
            print(f"  {i}. {bar}")
            
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Get trades - ALL_SYMBOLS to see if we get any data
print("\n4. Testing trades for ALL OPRA options...")
try:
    data = client.timeseries.get_range(
        dataset='OPRA.PILLAR',
        symbols='ALL_SYMBOLS',
        schema='trades',
        start='2025-12-01T14:30',
        end='2025-12-01T14:31',
        limit=50
    )
    
    trades_all = list(data)
    print(f"✅ Retrieved {len(trades_all)} option trades")
    
    if trades_all:
        print("\nFirst 5 trades:")
        for i, trade in enumerate(trades_all[:5], 1):
            print(f"  {i}. {trade}")
            
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
