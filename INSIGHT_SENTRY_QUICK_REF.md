# Insight Sentry API Quick Reference

## Authentication
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

## Base URL
```
https://api.insightsentry.com
```

---

## Common Endpoints

### 1. Symbol Search
```bash
GET /v3/symbols/search?query=AAPL
```
**Returns**: List of matching symbols

### 2. Get Available Options
```bash
GET /v3/options/list?code=NASDAQ:AAPL
```
**Returns**: Array of option codes (e.g., `["OPRA:AAPL260116C150.0", ...]`)

### 3. Symbol Info (Metadata)
```bash
GET /v3/symbols/NASDAQ:AAPL/info
```
**Returns**: Symbol details + option chain metadata (expirations, strikes)

### 4. Option Chain by Expiration
```bash
GET /v3/options/expiration?code=NASDAQ:AAPL&expiration=2026-01-16&sortBy=strike_price&sort=asc
```
**Returns**: All options expiring on specified date with Greeks

**Available sortBy fields**:
- `strike_price`, `implied_volatility`, `delta`, `gamma`, `theta`, `vega`, `rho`, `type`

### 5. Option Chain by Strike
```bash
GET /v3/options/strike?code=NASDAQ:AAPL&strike=200&sortBy=expiration&sort=asc
```
**Returns**: All options at specified strike across different expirations

### 6. Real-time Quotes (up to 10 symbols)
```bash
GET /v3/symbols/quotes?codes=OPRA:AAPL260116C200.0,OPRA:AAPL260116P200.0
```
**Returns**: Real-time bid/ask/last prices, volume, status

### 7. Historical Data
```bash
GET /v3/symbols/OPRA:AAPL260116C200.0/series?bar_type=day&bar_interval=1&dp=1000
```
**Parameters**:
- `bar_type`: `tick`, `second`, `minute`, `hour`, `day`, `week`, `month`
- `bar_interval`: Number of bars (e.g., 5 for 5-minute)
- `dp`: Data points to retrieve (up to 30,000 for Ultra plan)

**Returns**: OHLCV historical bars

---

## Data Formats

### Option Code Format
```
OPRA:AAPL260417C150.0
└─┬─┘ └┬─┘└─┬──┘└┬└─┬─┘
  │    │   │   │  │
  │    │   │   │  └─ Strike price
  │    │   │   └─ C=Call, P=Put
  │    │   └─ Expiration (YYMMDD: Apr 17, 2026)
  │    └─ Underlying symbol
  └─ Exchange (OPRA for equity options)
```

### Option Chain Response
```json
{
  "code": "OPRA:AAPL260116C200.0",
  "type": "CALL",
  "strike_price": 200,
  "expiration": 20260116,
  "bid_price": 60.5,
  "ask_price": 61.0,
  "theoretical_price": 60.75,
  "implied_volatility": 0.25,
  "delta": 0.65,
  "gamma": 0.02,
  "theta": -0.05,
  "vega": 0.15,
  "rho": 0.08,
  "bid_iv": 0.24,
  "ask_iv": 0.26,
  "volume": 150
}
```

### Quote Response
```json
{
  "code": "NASDAQ:AAPL",
  "status": "OPEN",
  "last_price": 260.78,
  "change": 1.35,
  "change_percent": 0.52,
  "bid": 260.75,
  "ask": 260.80,
  "bid_size": 100,
  "ask_size": 200,
  "volume": 24934196,
  "market_cap": 3848769788587,
  "delay_seconds": 0
}
```

---

## WebSocket API (⚠️ 10 connections/day limit)

### Market Data
```javascript
const ws = new WebSocket('wss://realtime.insightsentry.com/live');

// After connection
ws.send(JSON.stringify({
  api_key: "your_key_here",
  subscriptions: [
    {
      code: "NASDAQ:AAPL",
      type: "quote"  // or "series" for OHLCV
    },
    {
      code: "NASDAQ:SPY",
      type: "series",
      bar_type: "minute",
      bar_interval: 1,
      recent_bars: true,
      max_dp: 100
    }
    // Up to 5 total subscriptions
  ]
}));
```

### News Feed
```javascript
const ws = new WebSocket('wss://realtime.insightsentry.com/newsfeed');

// After connection
ws.send(JSON.stringify({
  api_key: "your_key_here"
}));

// Automatically receives 10 most recent news items
```

---

## Rate Limits

### Ultra Plan
- **REST API**: 35 requests/minute, 120,000/month
- **WebSocket**: 10 connections/day, 5 concurrent symbols
- **Bandwidth**: 10GB/month (+ $0.001 per MB overage)

### Handling Rate Limits
If you receive HTTP 429:
```python
if response.status_code == 429:
    time.sleep(60)  # Wait 1 minute
    # Retry request
```

---

## Python Examples

### Get Stock Price
```python
import requests

def get_stock_price(symbol):
    url = f"https://api.insightsentry.com/v3/symbols/quotes"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.get(url, headers=headers, 
                           params={"codes": f"NASDAQ:{symbol}"})
    data = response.json()
    return data['data'][0]['last_price']
```

### Get Options with Greeks
```python
def get_options_with_greeks(symbol, expiration):
    url = f"https://api.insightsentry.com/v3/options/expiration"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {
        "code": f"NASDAQ:{symbol}",
        "expiration": expiration,
        "sortBy": "strike_price"
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()['data']
```

### Get Historical Options Data
```python
def get_option_history(option_code, days=30):
    url = f"https://api.insightsentry.com/v3/symbols/{option_code}/series"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params = {
        "bar_type": "day",
        "bar_interval": 1,
        "dp": days
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json()['series']
```

---

## Common Symbol Formats

### Stocks
```
NASDAQ:AAPL    # Apple
NASDAQ:TSLA    # Tesla
NASDAQ:SPY     # S&P 500 ETF
NASDAQ:QQQ     # NASDAQ 100 ETF
```

### Options
```
OPRA:AAPL260116C200.0   # AAPL Jan 16, 2026 $200 Call
OPRA:TSLA260320P800.0   # TSLA Mar 20, 2026 $800 Put
```

### Futures Options
```
CME_MINI:NQZ2025        # E-mini NASDAQ futures (Dec 2025)
CME_MINI:ESH2026        # E-mini S&P 500 futures (Mar 2026)
```

---

## Error Handling

### Common Error Responses
```json
{
  "message": "Invalid Symbol Code"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `429` - Rate Limit Exceeded
- `500` - Server Error

---

## Tips & Best Practices

1. **Batch Requests**: Get up to 10 quotes in one request
2. **Cache Data**: Store symbol info, expirations, strikes locally
3. **Use Historical Data**: For backtesting, download once and cache
4. **Monitor Rate Limits**: Track your daily/monthly usage
5. **WebSocket Sparingly**: Limited to 10 connections/day
6. **Handle Errors Gracefully**: Always check response status
7. **Set Timeouts**: Use reasonable timeout values (10s recommended)
8. **Validate Symbols**: Check symbol format before making requests

---

## Resources

- **Full Documentation**: https://insightsentry.com/docs/options
- **WebSocket Docs**: https://insightsentry.com/docs/ws
- **API Playground**: https://insightsentry.com/demo/restapi
- **Support**: Check documentation or contact support

---

## Quick Start Checklist

- [ ] API key added to config
- [ ] Test connection with symbol info endpoint
- [ ] Retrieve options list for a symbol
- [ ] Get option chain with Greeks
- [ ] Fetch real-time quotes
- [ ] Get historical data
- [ ] Implement rate limiting
- [ ] Add error handling
- [ ] Cache frequently used data
- [ ] Monitor API usage

**You're ready to go!** 🚀
