# Options Flow Monitor & Strategy Backtester

A professional full-stack application for monitoring real-time options flow and backtesting put/call ratio trading strategies. Built with React + TypeScript frontend and Python Flask backend.

![Options Flow Monitor](https://img.shields.io/badge/Stack-React%20%2B%20Python-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

### Real-Time Options Flow Monitor
- **Multiple Timeframes**: 5min, 10min, 30min, 60min views
- **9 Major Symbols**: SPY, QQQ, AAPL, MSFT, NVDA, TSLA, META, GOOGL, AMZN
- **Put/Call Ratios**: Real-time buy/sell ratios for both puts and calls
- **Options Chain Visualization**: Volume distribution by strike price
- **Market Sentiment Indicator**: Bullish/Bearish based on P/C ratios
- **Auto-Refresh**: Configurable automatic data updates

### Advanced Strategy Backtester
- **Multi-Signal Analysis**: Volume spikes, IV filters, multi-timeframe confirmation
- **Strategy Comparison**: Compare puts vs calls vs basic strategies
- **Performance Metrics**: Win rate, profit factor, Sharpe ratio, max drawdown
- **Trade Log**: Detailed view of individual trades with all signals
- **Filter Optimization**: Toggle filters on/off to see impact

## Setup Instructions

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
1. Copy `.env.example` to `.env`
2. Get a free API key from [Polygon.io](https://polygon.io/)
3. Add your API key to `.env`:
   ```
   POLYGON_API_KEY=your_actual_key_here
   ```

### 3. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Key Options

### Polygon.io (Recommended)
- **Free Tier**: 5 API calls/minute
- **Starter Plan**: $29/month - Good for testing
- **Developer Plan**: $99/month - Full options data
- **Sign up**: https://polygon.io/

### Alternative: Yahoo Finance (Free, Limited)
- Uses yfinance library (already included)
- No API key required
- Limited to delayed data and basic options chains
- Good for testing/development

## Usage

### Options Flow Monitor
1. Navigate to `http://localhost:5000/monitor`
2. Select a symbol (SPY, QQQ, etc.)
3. Choose a timeframe (5min, 10min, 30min, 60min)
4. View real-time put/call ratios and volume distribution
5. Toggle auto-refresh as needed

### Strategy Backtester
1. Navigate to `http://localhost:5000/backtest`
2. Adjust strategy parameters:
   - Put/Call Threshold
   - Number of trades
   - Position size
   - Profit target / Stop loss
   - Volume spike threshold
   - IV percentile range
3. Enable/disable filters:
   - Volume Spike Filter
   - IV Filter
   - Multi-Timeframe Confirmation
4. Click "Run Comprehensive Backtest"
5. View results and strategy comparison

## Project Structure

```
.
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment variables
├── options_monitor.py              # Options flow monitoring logic
├── strategy_backtester.py          # Backtesting engine
├── data_fetcher.py                 # API integration for market data
├── templates/
│   ├── index.html                  # Home page
│   ├── monitor.html                # Options flow monitor UI
│   └── backtest.html               # Backtester UI
└── static/
    ├── css/
    │   └── style.css               # Custom styles
    └── js/
        ├── monitor.js              # Monitor frontend logic
        └── backtest.js             # Backtester frontend logic
```

## Key Metrics Explained

### Put/Call Ratio
- **> 1.1**: More put buying than call buying (bearish sentiment)
- **< 0.9**: More call buying than put buying (bullish sentiment)
- **~1.0**: Neutral sentiment

### Volume Spike
- Ratio of current volume to average volume
- **> 1.5x**: Significant institutional interest
- Helps filter out low-conviction signals

### IV Percentile
- **30-70%**: Sweet spot for options entry
- **< 30%**: Too little premium
- **> 70%**: Extreme panic, may continue

### Profit Factor
- Ratio of gross profits to gross losses
- **> 1.5**: Good strategy
- **> 2.0**: Excellent strategy

### Sharpe Ratio
- Risk-adjusted returns
- **> 1.0**: Good
- **> 2.0**: Very good

## Troubleshooting

### "No API key configured"
- Make sure you've created a `.env` file (not `.env.example`)
- Add your Polygon.io API key to the `.env` file
- Restart the application

### "Rate limit exceeded"
- Free tier has 5 calls/minute limit
- Upgrade to paid plan for higher limits
- Or use simulated data for testing (toggle in settings)

### Port already in use
- Change the port in `app.py`:
  ```python
  app.run(debug=True, port=5001)  # Use different port
  ```

## Development Notes

### Using Simulated Data
For testing without API calls, the app can use simulated realistic data. Toggle in the UI or set in config:
```python
USE_SIMULATED_DATA = True
```

### Adding More Symbols
Edit `config.py`:
```python
SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'TSLA', 'META', 'GOOGL', 'AMZN', 'NFLX', 'AMD']
```

## Disclaimer

This tool is for educational and research purposes only. Past performance does not guarantee future results. Options trading involves substantial risk and is not suitable for all investors. The backtesting results use simulated data and may not reflect actual market conditions.

**Real-world factors not fully modeled:**
- Bid/ask spreads (2-5% on options is common)
- Slippage
- Commission costs
- Liquidity constraints
- Market impact
- Execution delays

Always paper trade strategies before using real capital.

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at polygon.io
3. Create an issue in the repository

## Credits

Inspired by options flow analysis from [@MarkMoses777](https://x.com/MarkMoses777) on Twitter.
