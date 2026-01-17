from data_providers.factory import DataProviderFactory
import json

prov = DataProviderFactory.create_provider('insight_sentry')
flow = prov.get_options_flow_data('SPY')
print('Provider:', prov.get_provider_name())
print('call_buy:', flow.get('call_buy'), 'call_sell:', flow.get('call_sell'))
print('put_buy:', flow.get('put_buy'), 'put_sell:', flow.get('put_sell'))
print('call_ratio:', flow.get('call_ratio'), 'put_ratio:', flow.get('put_ratio'), 'put_call_ratio:', flow.get('put_call_ratio'))
print('estimation_coverage:', flow.get('estimation_coverage'))
print('strikes_count:', len(flow.get('strikes', [])))
print('\nSample strikes (up to 5):')
for s in flow.get('strikes', [])[:5]:
    print('strike:', s.get('strike'), 'call_vol:', s.get('call_volume'), 'put_vol:', s.get('put_volume'), 'call_buy:', s.get('call_buy'), 'call_sell:', s.get('call_sell'), 'put_buy:', s.get('put_buy'), 'put_sell:', s.get('put_sell'))
print('\nCurrent price and timestamp:')
print(json.dumps({'current_price': flow.get('current_price'), 'timestamp': flow.get('timestamp')}, indent=2))
