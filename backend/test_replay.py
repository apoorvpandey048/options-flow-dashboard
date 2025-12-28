"""
Test S3 connection and download historical replay data
"""
import os
from dotenv import load_dotenv
from historical_replay import get_replay_loader

# Load environment variables
load_dotenv()

def test_s3_connection():
    """Test S3 connection to Massive Flat Files"""
    print("=" * 80)
    print("TESTING MASSIVE S3 FLAT FILES CONNECTION")
    print("=" * 80)
    
    replay_loader = get_replay_loader()
    
    # Test with recent date (Dec 27, 2025)
    test_date = '2025-12-27'
    test_symbol = 'SPY'
    
    print(f"\n📅 Testing replay snapshots for {test_date} ({test_symbol})")
    print("-" * 80)
    
    try:
        snapshots = replay_loader.create_snapshots(test_date, test_symbol, num_snapshots=4)
        
        if snapshots:
            print(f"\n✅ Successfully created {len(snapshots)} snapshots!")
            print("\n" + "=" * 80)
            
            for i, snapshot in enumerate(snapshots, 1):
                print(f"\nSnapshot #{i}: {snapshot.get('snapshot_label', 'Unknown')} at {snapshot.get('snapshot_time', 'N/A')}")
                print("-" * 40)
                
                calls = snapshot.get('calls', {})
                puts = snapshot.get('puts', {})
                
                print(f"  📞 Calls Total:  {calls.get('total', 0):,}")
                print(f"  📉 Puts Total:   {puts.get('total', 0):,}")
                print(f"  📊 P/C Ratio:    {snapshot.get('put_call_ratio', 0):.2f}")
                print(f"  💰 Price:        ${snapshot.get('price', 0):.2f}")
                print(f"  📈 Sentiment:    {snapshot.get('sentiment', 'N/A').upper()}")
                print(f"  🎯 Strikes:      {len(snapshot.get('strikes', []))} strikes")
                
                # Show top 3 strikes by volume
                strikes = snapshot.get('strikes', [])
                if strikes:
                    print("\n  Top 3 Strikes by Volume:")
                    sorted_strikes = sorted(strikes, 
                                          key=lambda s: s.get('call_volume', 0) + s.get('put_volume', 0), 
                                          reverse=True)[:3]
                    for strike in sorted_strikes:
                        total_vol = strike.get('call_volume', 0) + strike.get('put_volume', 0)
                        print(f"    ${strike.get('strike', 0):.1f}: Calls {strike.get('call_volume', 0):,} | "
                              f"Puts {strike.get('put_volume', 0):,} | Total {total_vol:,}")
            
            print("\n" + "=" * 80)
            print("✅ TEST PASSED - Historical Replay is working!")
            print("=" * 80)
            
            # Analyze differences between snapshots
            print("\n📊 ANALYSIS: Data Changes Throughout The Day")
            print("=" * 80)
            
            if len(snapshots) >= 2:
                first = snapshots[0]
                last = snapshots[-1]
                
                call_change = last['calls']['total'] - first['calls']['total']
                put_change = last['puts']['total'] - first['puts']['total']
                price_change = last['price'] - first['price']
                
                print(f"\nFrom {first['snapshot_label']} to {last['snapshot_label']}:")
                print(f"  Calls: {first['calls']['total']:,} → {last['calls']['total']:,} ({call_change:+,})")
                print(f"  Puts:  {first['puts']['total']:,} → {last['puts']['total']:,} ({put_change:+,})")
                print(f"  Price: ${first['price']:.2f} → ${last['price']:.2f} (${price_change:+.2f})")
                
                print("\n💡 INSIGHT:")
                if abs(call_change) > 10000 or abs(put_change) > 10000:
                    print("  ✅ Data changes SIGNIFICANTLY throughout the day")
                    print("  ✅ Real-time monitoring (2s refresh) makes sense")
                else:
                    print("  ⚠️  Data changes moderately throughout the day")
                    print("  ⚠️  Consider 5-10s refresh instead of 2s")
            
        else:
            print("\n⚠️  No snapshots created - using fallback data")
            print("This is normal if:")
            print("  1. S3 credentials are not set")
            print("  2. Date is too recent (data available next day at 11 AM ET)")
            print("  3. Date is a weekend/holiday")
            
    except Exception as e:
        print(f"\n❌ Error creating snapshots: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    test_s3_connection()
