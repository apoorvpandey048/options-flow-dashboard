from data_fetcher import data_fetcher

prov = data_fetcher.provider
print('Provider:', prov.get_provider_name())
print('Insight key present:', getattr(prov, 'api_key', None) is not None)

info = prov.get_symbol_info('SPY')
print('Symbol info:', info)

expirations = info.get('option_expirations') if info else None
print('Expirations:', expirations)

if expirations:
    chain = prov.get_options_chain('SPY', expiration_date=expirations[0])
    print('Chain length for first expiration:', len(chain))
    print('First 5 chain items:', chain[:5])

# fallback
chain2 = prov.get_options_chain('SPY')
print('Fallback chain length:', len(chain2))
print('Fallback first 5 items:', chain2[:5])

quotes = prov.get_option_quotes(chain2[:10] if chain2 else [])
print('Quotes fetched:', len(quotes))
print('Quotes sample:', quotes[:5])
