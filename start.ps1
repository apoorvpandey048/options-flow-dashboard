#!/usr/bin/env pwsh
# Start Options Flow Dashboard
# Starts both backend (Flask) and frontend (React) servers

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    Options Flow Dashboard - Starting Application" -ForegroundColor Cyan  
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "⚠️  Frontend dependencies not installed. Installing now..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host "✅ Starting Backend Server (Flask on port 10000)..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; & '$PWD\.venv\Scripts\python.exe' app.py"

Start-Sleep -Seconds 3

Write-Host "✅ Starting Frontend Server (React on port 3000)..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm start"

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "    🚀 Application Started Successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend API:  http://localhost:10000" -ForegroundColor Yellow
Write-Host "  Frontend UI:  http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "  📊 Open your browser and go to http://localhost:3000" -ForegroundColor Cyan
Write-Host "  📅 New: Historical Replay feature with 4 sample dates" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press Ctrl+C in each terminal window to stop the servers" -ForegroundColor Gray
Write-Host ""
