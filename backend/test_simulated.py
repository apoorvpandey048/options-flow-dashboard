"""Quick test of simulated data provider"""
from data_providers.simulated_provider import SimulatedDataProvider

provider = SimulatedDataProvider()
print(f"Provider: {provider.get_provider_name()}")

data = provider.get_options_flow_data('SPY', '5min')
print(f"\nData keys: {data.keys() if data else 'None'}")

if data:
    print(f"Calls: {data.get('calls')}")
    print(f"Puts: {data.get('puts')}")
    print(f"Strikes: {len(data.get('strikes', []))}")
else:
    print("❌ No data returned!")
