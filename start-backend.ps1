# Start Backend Server Script
# This script starts the Flask backend server

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Starting Backend Server" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Resolve script directory and activate virtual environment from project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvActivate = Join-Path $scriptDir ".venv\Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvActivate
} else {
    Write-Host "✗ Virtual environment not found at $venvActivate. Run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Change to backend folder (relative to repo root)
Set-Location (Join-Path $scriptDir "backend")

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
}

Write-Host ""
Write-Host "Starting Flask server..." -ForegroundColor Green
Write-Host "Backend will be available at: http://localhost:10000" -ForegroundColor Cyan
Write-Host "API Health Check: http://localhost:10000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

$env:INSIGHT_SENTRY_API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJ1dWlkIjoiYXdlc29tZWJsb2dzMjAxMEBnbWFpbC5jb20iLCJwbGFuIjoidWx0cmEiLCJuZXdzZmVlZF9lbmFibGVkIjp0cnVlLCJ3ZWJzb2NrZXRfc3ltYm9scyI6NSwid2Vic29ja2V0X2Nvbm5lY3Rpb25zIjoxfQ.zfYCHDg7v1O3Bkb6_JLlus90FtBUfcRH_Px6_sut-Ks'
$env:DATA_PROVIDER = 'insight_sentry'
# Ensure Flask uses port 10000 to match frontend proxy
$env:PORT = '10000'
# Allow both localhost and 127.0.0.1 origins for development (React may use either)
$env:ALLOWED_ORIGINS = 'http://localhost:3000,http://127.0.0.1:3000'

python app.py
