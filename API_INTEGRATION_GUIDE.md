# API Integration Guide

## Overview
The application uses a **Provider Pattern** for data sources, making it easy to switch between simulated data and real market APIs.

## Current Providers

### 1. Simulated Data Provider (Default)
- ✅ **Status:** Fully implemented
- 💰 **Cost:** Free
- 🎯 **Use Case:** Development, testing, demos
- 📊 **Data Quality:** Realistic patterns, proper distributions

**Features:**
- Generates realistic options flow data
- Volume spikes and IV patterns
- Strike-level granularity
- No API limits or costs

### 2. Polygon.io Provider
- ⚠️ **Status:** Framework ready, needs subscription
- 💰 **Cost:** $200-500/month (Options Starter plan)
- 🎯 **Use Case:** Production real-time data
- 📊 **Data Quality:** Exchange-direct data

**Setup:**
```bash
# 1. Get API key from polygon.io
# 2. Add to backend/.env
POLYGON_API_KEY=your_api_key_here
DATA_PROVIDER=polygon

# 3. Restart backend - auto-detects Polygon
```

**What Works:**
- Stock prices ✅
- Basic validation ✅
- Connection testing ✅

**What Needs Implementation:**
- Options chain data (requires additional API calls)
- Options flow aggregation (requires premium subscription)
- Historical options data

### 3. TD Ameritrade Provider
- ❌ **Status:** Not implemented
- 💰 **Cost:** Free with TD Ameritrade account
- 🎯 **Use Case:** Delayed data, retail traders

**Future Implementation:**
Framework exists in `data_providers/`, needs:
1. TD Ameritrade authentication (OAuth)
2. Options chain API calls
3. Real-time quote streaming

## Architecture

```
┌─────────────────┐
│   Flask App     │
└────────┬────────┘
         │
    ┌────▼─────┐
    │DataFetcher│
    └────┬──────┘
         │
┌────────▼──────────────┐
│DataProviderFactory    │
└───┬───────────────────┘
    │ (auto-detects)
    │
    ├───► SimulatedDataProvider
    ├───► PolygonDataProvider
    └───► TDAmeritrade Provider (future)
```

## How to Add a New Provider

### Step 1: Create Provider Class
```python
# backend/data_providers/my_provider.py

from .base_provider import BaseDataProvider

class MyDataProvider(BaseDataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_provider_name(self) -> str:
        return "My Data Provider"
    
    def validate_connection(self) -> bool:
        # Test API key
        return True
    
    def get_stock_price(self, symbol: str) -> float:
        # Implement your API call
        pass
    
    def get_options_chain(self, symbol: str, expiration: str = None):
        # Implement your API call
        pass
    
    def get_options_flow_data(self, symbol: str, timeframe: str):
        # Implement your API call
        pass
    
    def get_historical_options_data(self, symbol: str, days: int):
        # Implement your API call
        pass
```

### Step 2: Add to Factory
```python
# backend/data_providers/factory.py

from .my_provider import MyDataProvider

class DataProviderFactory:
    @staticmethod
    def create_provider(provider_type: str = None):
        if provider_type == 'myprovider':
            api_key = os.getenv('MY_PROVIDER_API_KEY')
            return MyDataProvider(api_key)
        # ... existing code
```

### Step 3: Use It
```bash
# .env file
MY_PROVIDER_API_KEY=your_key
DATA_PROVIDER=myprovider
```

## API Requirements

### Must Implement (Required)
All providers MUST implement these methods:

1. **get_stock_price(symbol)** - Current underlying price
2. **get_options_chain(symbol, expiration)** - Strikes, volumes, OI, IV
3. **get_options_flow_data(symbol, timeframe)** - Call/put buying pressure
4. **get_historical_options_data(symbol, days)** - For backtesting
5. **validate_connection()** - Test API connectivity
6. **get_provider_name()** - Display name

### Data Format Requirements

#### Options Flow Data
```python
{
    'symbol': 'SPY',
    'timeframe': '5min',
    'timestamp': '2025-12-22T10:30:00',
    'call_buy': 45000,      # Buy volume
    'call_sell': 32000,     # Sell volume
    'put_buy': 38000,
    'put_sell': 25000,
    'call_ratio': 1.406,    # Buy/Sell ratio
    'put_ratio': 1.520,
    'put_call_ratio': 0.844, # Put/Call ratio
    'strikes': [
        {
            'strike': 660.0,
            'call_volume': 12500,
            'put_volume': 8300,
            'call_oi': 45000,
            'put_oi': 38000,
            'call_iv': 0.1823,
            'put_iv': 0.1967
        },
        # ... more strikes
    ],
    'current_price': 662.17
}
```

#### Options Chain
```python
{
    'strikes': [strike_data_array],
    'current_price': 662.17,
    'expiration': '2025-12-29'
}
```

## Provider Comparison

| Provider | Cost | Latency | Options Flow | Historical | Ease |
|----------|------|---------|-------------|-----------|------|
| Simulated | Free | Instant | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| Polygon.io | $200-500/mo | <100ms | ✅ (premium) | ✅ | ⭐⭐⭐⭐ |
| TD Ameritrade | Free | 500-1000ms | ❌ | Limited | ⭐⭐⭐ |
| Interactive Brokers | $10-120/mo | <50ms | ✅ | ✅ | ⭐⭐ |
| Tradier | $10-250/mo | 100-300ms | ✅ | ✅ | ⭐⭐⭐⭐ |

## Switching Providers at Runtime

```python
# In app.py or any module
from data_fetcher import data_fetcher
from data_providers import PolygonDataProvider, SimulatedDataProvider

# Check current provider
print(data_fetcher.provider.get_provider_name())

# Switch to Polygon
if data_fetcher.validate_provider():
    print("Current provider is working")
else:
    # Fallback to simulated
    data_fetcher.switch_provider(SimulatedDataProvider())
```

## Environment Variables

```bash
# Data Provider Selection
DATA_PROVIDER=auto  # Options: auto, simulated, polygon, td_ameritrade

# API Keys
POLYGON_API_KEY=your_polygon_key
TD_AMERITRADE_API_KEY=your_td_key

# Optional: Force simulated even with keys
USE_SIMULATED_DATA=true
```

## Testing Your Provider

```python
# backend/test_provider.py
from data_providers import DataProviderFactory

provider = DataProviderFactory.create_provider('polygon')

# Test connection
assert provider.validate_connection(), "Connection failed"

# Test stock price
price = provider.get_stock_price('SPY')
assert 400 < price < 700, f"Price {price} out of range"

# Test options data
flow = provider.get_options_flow_data('SPY', '5min')
assert flow['symbol'] == 'SPY'
assert flow['put_call_ratio'] > 0

print("✅ All tests passed!")
```

## Recommended: Polygon.io Setup

### 1. Create Account
Visit [polygon.io/dashboard](https://polygon.io/dashboard)

### 2. Choose Plan
- **Starter:** $29/mo - Stocks only (no options)
- **Developer:** $99/mo - Delayed options
- **Advanced:** $249/mo - Real-time options ✅ **RECOMMENDED**
- **Enterprise:** Custom - Full market depth

### 3. Get API Key
Dashboard → API Keys → Create

### 4. Test Connection
```bash
curl "https://api.polygon.io/v2/aggs/ticker/SPY/prev?apiKey=YOUR_KEY"
```

### 5. Configure Application
```bash
# backend/.env
POLYGON_API_KEY=pk_live_xxxxxxxxx
DATA_PROVIDER=polygon
```

### 6. Verify
```bash
cd backend
python -c "from data_fetcher import data_fetcher; print(data_fetcher.provider.get_provider_name())"
# Should output: "Polygon.io"
```

## Troubleshooting

### "No API keys found - using simulated"
- Check `.env` file exists in `backend/` folder
- Verify key name is exact: `POLYGON_API_KEY` (not `POLYGON_KEY`)
- Restart Flask server after changing `.env`

### "Polygon API error: 401"
- API key invalid or expired
- Check dashboard for active subscriptions

### "Polygon options not implemented"
- Options flow requires additional code (marked as TODO)
- Currently falls back to simulated data
- Stock prices work correctly

### Provider Not Switching
```python
# Force reload
import importlib
import data_fetcher
importlib.reload(data_fetcher)
```

## Future Enhancements

1. **Interactive Brokers Provider** - Lowest latency, institutional quality
2. **Tradier Provider** - Good balance of cost and quality
3. **CBOE LiveVol** - Premium implied volatility data
4. **Data Aggregation** - Combine multiple providers for redundancy
5. **Caching Layer** - Redis cache for frequently accessed data
6. **WebSocket Streaming** - Real-time push instead of polling

## Support

For provider implementation help:
1. Check `backend/data_providers/base_provider.py` for interface
2. Reference `simulated_provider.py` for full example
3. See `polygon_provider.py` for real API integration patterns
