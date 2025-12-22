# 🚀 QUICK START GUIDE

## Current Status
✅ Backend is RUNNING on port 5000
⏳ Frontend needs: npm install && npm start

## Start Application (2 Terminals)

### Terminal 1 - Backend (Already Running!)
```powershell
cd "c:\Users\Apoor\Real-time putcall ratio tracker for S&P and QQQ\backend"
& "C:/Users/Apoor/Real-time putcall ratio tracker for S&P and QQQ/.venv/Scripts/python.exe" app.py
```
**Status: ✅ RUNNING**

### Terminal 2 - Frontend (Need to Start)
```powershell
cd "c:\Users\Apoor\Real-time putcall ratio tracker for S&P and QQQ\frontend"
npm install  # First time only (5-10 minutes)
npm start    # Opens browser automatically
```

## URLs
- Frontend: http://localhost:3000
- Backend: http://localhost:5000
- Health Check: http://localhost:5000/api/health

## Tech Stack
- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Python Flask + WebSocket
- **Real-Time**: Socket.IO

## Features
1. **Options Flow Monitor** - Real-time data, 4 timeframes, 9 symbols
2. **Strategy Backtester** - Multi-signal analysis, 1000+ trades

## Troubleshooting

### Backend Issues
```powershell
# Check if running
curl http://localhost:5000/api/health

# Restart
# Stop with Ctrl+C, then run app.py again
```

### Frontend Issues
```powershell
# Clear and reinstall
cd frontend
Remove-Item -Recurse -Force node_modules
npm install
npm start
```

### Port Conflicts
```powershell
# Backend port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Frontend port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

## File Structure
```
backend/  - Python Flask API + WebSocket
frontend/ - React TypeScript App
```

## Next Steps
1. ✅ Backend running
2. ⏳ cd frontend && npm install
3. ⏳ npm start
4. ⏳ Open http://localhost:3000
5. ⏳ Test features

---
For detailed docs: README.md, SETUP_GUIDE.md, PROJECT_SUMMARY.md
