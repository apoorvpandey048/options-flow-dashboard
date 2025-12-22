# Installation and Setup Guide

## Complete Setup Instructions

### Step 1: Backend Setup

1. Open a terminal/PowerShell and navigate to the backend directory:
```powershell
cd "c:\Users\Apoor\Real-time putcall ratio tracker for S&P and QQQ\backend"
```

2. The Python environment is already configured. Install dependencies (already done):
```powershell
# Dependencies are installed
```

3. Start the backend server:
```powershell
& "C:/Users/Apoor/Real-time putcall ratio tracker for S&P and QQQ/.venv/Scripts/python.exe" app.py
```

Backend is now running on http://localhost:5000

### Step 2: Frontend Setup

1. Open a NEW terminal/PowerShell and navigate to the frontend directory:
```powershell
cd "c:\Users\Apoor\Real-time putcall ratio tracker for S&P and QQQ\frontend"
```

2. Install Node.js dependencies:
```powershell
npm install
```

3. Start the frontend development server:
```powershell
npm start
```

Frontend will open automatically at http://localhost:3000

### Step 3: Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:5000/api/health
- **WebSocket**: ws://localhost:5000

## Current Status

✅ Backend is running successfully
✅ All Python dependencies installed
✅ WebSocket server active
✅ Background data streaming enabled

⏳ Next: Install frontend dependencies and start React app

## Quick Commands

### Start Backend (Terminal 1)
```powershell
cd "c:\Users\Apoor\Real-time putcall ratio tracker for S&P and QQQ\backend"
& "C:/Users/Apoor/Real-time putcall ratio tracker for S&P and QQQ/.venv/Scripts/python.exe" app.py
```

### Start Frontend (Terminal 2)
```powershell
cd "c:\Users\Apoor\Real-time putcall ratio tracker for S&P and QQQ\frontend"
npm start
```

## Troubleshooting

### Backend Issues
- **Port 5000 already in use**: Stop any other Flask/Python servers
- **Module not found**: Reinstall packages with pip install -r requirements.txt

### Frontend Issues
- **npm not found**: Install Node.js from https://nodejs.org/
- **Port 3000 already in use**: The app will prompt to use another port

## Features Available

### Real-Time Options Flow Monitor
- Live data streaming via WebSocket
- Multiple timeframes (5min, 10min, 30min, 60min)
- 9 symbols (SPY, QQQ, AAPL, MSFT, NVDA, TSLA, META, GOOGL, AMZN)
- Visual options chain
- Put/Call ratios and sentiment indicators

### Strategy Backtester
- Multi-signal analysis
- Volume spike, IV, and multi-timeframe filters
- Strategy comparison (Puts vs Calls)
- Comprehensive performance metrics
- Detailed trade logs

## Next Steps

1. Install frontend dependencies: `npm install` in frontend directory
2. Start frontend server: `npm start`
3. Open http://localhost:3000 in your browser
4. Explore the application features
5. Test with simulated data
6. Configure API keys for real data (optional)

## Notes

- Currently using simulated data for demonstration
- Backend automatically refreshes data every 5 seconds
- WebSocket provides real-time updates
- All data is generated realistically for testing purposes
