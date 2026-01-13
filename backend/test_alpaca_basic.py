"""Quick test of Alpaca Options Basic (indicative) endpoints.

Usage:
  Set environment variables `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY`,
  then run:

    python backend/test_alpaca_basic.py

This script calls the option chain / snapshots endpoints with `feed=indicative`
so the Basic plan will respond (indicative feed). When you have a paid OPRA
subscription, change `feed` to `opra`.
"""
import os
import requests
import sys
import time
import re

API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')
BASE = 'https://data.alpaca.markets/v1beta1'

if not API_KEY or not API_SECRET:
    print('Error: set APCA_API_KEY_ID and APCA_API_SECRET_KEY in environment')
    sys.exit(1)

HEADERS = {
    'APCA-API-KEY-ID': API_KEY,
    'APCA-API-SECRET-KEY': API_SECRET,
    'accept': 'application/json',
}

UNDERLYING = 'SPY'

# Alpaca contract symbol pattern (e.g. SPY260108C00640000)
SYMBOL_RE = re.compile(r'^[A-Z]{1,5}\d{6,7}[CP]\d{8}$')

def pretty(resp):
    print('Status:', resp.status_code)
    try:
        j = resp.json()
        import json
        print(json.dumps(j if isinstance(j, dict) else (j[:5] if isinstance(j, list) else j), indent=2))
    except Exception:
        print(resp.text[:1000])

def test_option_chain():
    print('\n1) Option chain (snapshots by underlying) - feed=indicative')
    url = f"{BASE}/options/snapshots/{UNDERLYING}?feed=indicative&limit=200"
    r = requests.get(url, headers=HEADERS, timeout=15)
    pretty(r)
    if r.status_code == 200:
        j = r.json()
        # response can be a list or a dict keyed by contract symbol
        if isinstance(j, list):
            print('Contracts returned:', len(j))
            return [c.get('symbol') or c.get('contract_symbol') for c in j][:50]
        elif isinstance(j, dict):
            # try direct symbol keys
            keys = [k for k in list(j.keys()) if SYMBOL_RE.match(k)]
            if keys:
                print('Contracts returned (dict):', len(keys))
                return keys[:50]
            # try common nested fields (e.g., 'snapshots')
            for field in ('snapshots', 'results', 'data'):
                if field in j and isinstance(j[field], dict):
                    nested = [k for k in j[field].keys() if SYMBOL_RE.match(k)]
                    if nested:
                        print(f'Contracts returned (nested:{field}):', len(nested))
                        return nested[:50]
            # try dict values that are dicts containing symbol keys
            for v in j.values():
                if isinstance(v, dict):
                    nested = [k for k in v.keys() if SYMBOL_RE.match(k)]
                    if nested:
                        print('Contracts returned (nested:value):', len(nested))
                        return nested[:50]
            print('No contract symbol keys found in response dict')
    return []

def test_snapshots_for_contracts(symbols):
    if not symbols:
        print('No contract symbols to query')
        return
    print('\n2) Snapshots for first contracts (batch) - feed=indicative')
    # filter symbols to only valid contract symbols (remove tokens like NEXT_PAGE_TOKEN)
    filtered = [s for s in symbols if s and SYMBOL_RE.match(s)]
    if not filtered:
        print('No valid contract symbols after filtering')
        return
    batch = ','.join(filtered[:20])
    url = f"{BASE}/options/snapshots?symbols={batch}&feed=indicative&limit=100"
    r = requests.get(url, headers=HEADERS, timeout=15)
    pretty(r)
    if r.status_code != 200:
        return
    data = r.json()
    # Alpaca batch snapshot response may nest results under 'snapshots'
    if isinstance(data, dict) and 'snapshots' in data and isinstance(data['snapshots'], dict):
        data = data['snapshots']

    # compute put/call metrics from snapshots
    def get_type(sym: str) -> str:
        # find 'C' or 'P' which precedes strike digits
        for i, ch in enumerate(sym):
            if ch in ('C', 'P') and i + 1 < len(sym) and sym[i+1].isdigit():
                return 'call' if ch == 'C' else 'put'
        return 'unknown'

    put_vol = 0
    call_vol = 0
    put_notional = 0.0
    call_notional = 0.0

    # response may be dict keyed by symbol
    items = data.items() if isinstance(data, dict) else ((c.get('symbol'), c) for c in data)
    for sym, obj in items:
        typ = get_type(sym)
        vol = 0
        notional = 0.0
        mb = obj.get('minuteBar') if isinstance(obj, dict) else None
        lt = obj.get('latestTrade') if isinstance(obj, dict) else None
        if mb and isinstance(mb, dict) and mb.get('v'):
            vol = int(mb.get('v', 0))
            vw = float(mb.get('vw') or 0)
            notional = vol * vw * 100
        elif lt and isinstance(lt, dict) and lt.get('s'):
            vol = int(lt.get('s', 0))
            p = float(lt.get('p') or 0)
            notional = vol * p * 100

        if typ == 'call':
            call_vol += vol
            call_notional += notional
        elif typ == 'put':
            put_vol += vol
            put_notional += notional

    print(f"\nPut/Call by contracts: put_vol={put_vol}, call_vol={call_vol}")
    print(f"Put/Call notional: put_notional=${put_notional:,.2f}, call_notional=${call_notional:,.2f}")
    if call_vol + put_vol > 0:
        print(f"Put/Call ratio (contracts) = {put_vol / max(1, call_vol):.3f}")
    if call_notional + put_notional > 0:
        print(f"Put/Call ratio (notional) = {put_notional / max(1, call_notional):.3f}")

    return list(items)[:20]

def test_option_bars():
    print('\n3) Recent option bars for underlying (if allowed) - latest 15 minutes limitation on Basic')
    # Fetch 1-minute bars for a single sample contract if available
    # This endpoint requires symbols parameter; we'll request bars for the ATM-ish contract
    sample_sym = os.getenv('ALPACA_SAMPLE_CONTRACT')
    if not sample_sym:
        print('No sample contract set (env ALPACA_SAMPLE_CONTRACT). Skipping bars test.')
        return
    now = int(time.time())
    end = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))
    start = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now - 60 * 15))
    # Alpaca expects `timeframe` param for bars (e.g., 1Min)
    url = f"{BASE}/options/bars?symbols={sample_sym}&start={start}&end={end}&timeframe=1Min&limit=200"
    r = requests.get(url, headers=HEADERS, timeout=15)
    pretty(r)

def main():
    symbols = test_option_chain()
    items = test_snapshots_for_contracts(symbols)
    # if items is a list of (symbol, obj) tuples, set first as sample contract
    if items and isinstance(items, list):
        first = items[0]
        if isinstance(first, tuple):
            sample = first[0]
            os.environ['ALPACA_SAMPLE_CONTRACT'] = sample
    test_option_bars()

if __name__ == '__main__':
    main()
