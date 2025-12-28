"""
Test script to analyze options flow data update frequency and patterns.
This will help understand if data changes every 2s or takes longer.
"""
import time
import json
from datetime import datetime
from data_fetcher import DataFetcher

def compare_data(data1, data2):
    """Compare two data snapshots and return what changed."""
    changes = {
        'calls_total': data1['calls']['total'] != data2['calls']['total'],
        'puts_total': data1['puts']['total'] != data2['puts']['total'],
        'calls_ratio': data1['calls']['ratio'] != data2['calls']['ratio'],
        'puts_ratio': data1['puts']['ratio'] != data2['puts']['ratio'],
        'price': data1['price'] != data2['price'],
        'strikes_changed': []
    }
    
    # Check which strikes changed
    for i, (strike1, strike2) in enumerate(zip(data1['strikes'], data2['strikes'])):
        if (strike1['call_volume'] != strike2['call_volume'] or 
            strike1['put_volume'] != strike2['put_volume']):
            changes['strikes_changed'].append({
                'strike': strike1['strike'],
                'call_volume_delta': strike2['call_volume'] - strike1['call_volume'],
                'put_volume_delta': strike2['put_volume'] - strike1['put_volume']
            })
    
    return changes

def has_any_changes(changes):
    """Check if there are any actual changes."""
    return (changes['calls_total'] or changes['puts_total'] or 
            changes['calls_ratio'] or changes['puts_ratio'] or 
            changes['price'] or len(changes['strikes_changed']) > 0)

def main():
    print("=" * 80)
    print("OPTIONS FLOW DATA UPDATE FREQUENCY TEST (Quick Run)")
    print("=" * 80)
    print("\nThis test will:")
    print("1. Fetch data every 2 seconds for 20 seconds (10 samples)")
    print("2. Track what actually changes between each fetch")
    print("3. Measure time between real changes")
    print("4. Show patterns in update frequency")
    print("\n" + "=" * 80)
    
    fetcher = DataFetcher()
    symbol = 'SPY'
    timeframe = '5min'
    
    print(f"\nMonitoring: {symbol} | Timeframe: {timeframe}")
    print(f"Start time: {datetime.now().strftime('%H:%M:%S')}")
    print("\n" + "-" * 80)
    
    samples = []
    previous_data = None
    change_count = 0
    no_change_count = 0
    last_change_time = time.time()
    time_between_changes = []
    
    # Collect 10 samples over 20 seconds
    for i in range(10):
        current_time = datetime.now()
        
        try:
            data = fetcher.get_options_flow_data(symbol, timeframe)
            
            # Compare with previous data
            if previous_data is not None:
                changes = compare_data(previous_data, data)
                has_changes = has_any_changes(changes)
                
                if has_changes:
                    change_count += 1
                    time_since_last_change = time.time() - last_change_time
                    time_between_changes.append(time_since_last_change)
                    
                    print(f"\n[{current_time.strftime('%H:%M:%S')}] Sample #{i+1} - 🔄 DATA CHANGED")
                    print(f"  Time since last change: {time_since_last_change:.1f}s")
                    
                    if changes['calls_total']:
                        print(f"  📊 Calls Total: {previous_data['calls']['total']:,} → {data['calls']['total']:,}")
                    if changes['puts_total']:
                        print(f"  📊 Puts Total: {previous_data['puts']['total']:,} → {data['puts']['total']:,}")
                    if changes['price']:
                        print(f"  💵 Price: ${previous_data['price']:.2f} → ${data['price']:.2f}")
                    
                    if len(changes['strikes_changed']) > 0:
                        print(f"  📈 {len(changes['strikes_changed'])} strikes changed")
                        # Show first 3 changes
                        for change in changes['strikes_changed'][:3]:
                            print(f"     Strike ${change['strike']:.1f}: "
                                  f"Calls {change['call_volume_delta']:+,} | "
                                  f"Puts {change['put_volume_delta']:+,}")
                    
                    last_change_time = time.time()
                else:
                    no_change_count += 1
                    print(f"[{current_time.strftime('%H:%M:%S')}] Sample #{i+1} - ⏸️  No change "
                          f"(same for {time.time() - last_change_time:.1f}s)")
            else:
                print(f"[{current_time.strftime('%H:%M:%S')}] Sample #1 - 🎯 Initial snapshot")
                print(f"  Calls: {data['calls']['total']:,} | Puts: {data['puts']['total']:,}")
                print(f"  Price: ${data['price']:.2f}")
            
            samples.append({
                'time': current_time,
                'data': data,
                'has_changes': has_any_changes(changes) if previous_data else True
            })
            
            previous_data = data
            
        except Exception as e:
            print(f"[{current_time.strftime('%H:%M:%S')}] Sample #{i+1} - ❌ Error: {e}")
        
        # Wait 2 seconds before next sample (except on last iteration)
        if i < 9:
            time.sleep(2)
    
    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    
    total_samples = len(samples)
    update_percentage = (change_count / (total_samples - 1) * 100) if total_samples > 1 else 0
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total samples collected: {total_samples}")
    print(f"  Samples with changes: {change_count}")
    print(f"  Samples with no changes: {no_change_count}")
    print(f"  Update rate: {update_percentage:.1f}%")
    
    if time_between_changes:
        avg_time = sum(time_between_changes) / len(time_between_changes)
        min_time = min(time_between_changes)
        max_time = max(time_between_changes)
        
        print(f"\n⏱️  Time Between Changes:")
        print(f"  Average: {avg_time:.1f} seconds")
        print(f"  Minimum: {min_time:.1f} seconds")
        print(f"  Maximum: {max_time:.1f} seconds")
    
    print("\n" + "-" * 80)
    print("\n💡 INSIGHTS:")
    
    if update_percentage > 80:
        print("  ✅ Data changes VERY FREQUENTLY (>80% of samples)")
        print("     → 2-second refresh makes sense")
        print("     → Charts are highly dynamic")
    elif update_percentage > 50:
        print("  ⚡ Data changes FREQUENTLY (50-80% of samples)")
        print("     → 2-second refresh is reasonable")
        print("     → Charts update regularly")
    elif update_percentage > 20:
        print("  🔄 Data changes MODERATELY (20-50% of samples)")
        print("     → 2-second refresh may be too fast")
        print("     → Consider 5-10 second refresh")
    else:
        print("  ⏸️  Data changes SLOWLY (<20% of samples)")
        print("     → 2-second refresh is excessive")
        print("     → Consider 30-60 second refresh")
    
    print("\n" + "=" * 80)
    
    # Save detailed results
    output_file = 'update_frequency_test_results.json'
    results = {
        'test_time': datetime.now().isoformat(),
        'symbol': symbol,
        'timeframe': timeframe,
        'total_samples': total_samples,
        'changes': change_count,
        'no_changes': no_change_count,
        'update_percentage': update_percentage,
        'avg_time_between_changes': sum(time_between_changes) / len(time_between_changes) if time_between_changes else 0
    }
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    main()
