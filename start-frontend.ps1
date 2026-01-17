# Start Frontend Server Script
# This script starts the React development server

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Set-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "✗ node_modules not found. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "Starting React development server..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Make sure backend is running on port 5000" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Ensure the frontend dev server points to the correct backend URL
$env:REACT_APP_API_URL = 'http://localhost:10000'
$env:REACT_APP_WS_URL = 'http://localhost:10000'

npm start
