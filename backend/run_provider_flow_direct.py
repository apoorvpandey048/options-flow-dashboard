from data_providers.factory import DataProviderFactory
import json

prov = DataProviderFactory.create_provider('insight_sentry')
print('Provider:', prov.get_provider_name())
flow = prov.get_options_flow_data('SPY')
print('Flow keys:', list(flow.keys()))
print('Strikes count:', len(flow.get('strikes', [])))
print(json.dumps(flow, indent=2))
