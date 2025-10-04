# NASA Weather Prediction App - Startup Script
# This script helps you start both the ML backend and frontend server

Write-Host "🚀 NASA Weather Prediction App - Starting..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js 18 or higher." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Instructions" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will guide you through setting up the app." -ForegroundColor White
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
}

# Check if requirements are installed
Write-Host ""
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$response = Read-Host "Install/Update Python dependencies? (y/n)"
if ($response -eq "y") {
    Write-Host "Installing Python packages..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
}

# Check if node_modules exists
Write-Host ""
Write-Host "Checking Node.js dependencies..." -ForegroundColor Yellow
if (-Not (Test-Path "Frontend/node_modules")) {
    Write-Host "Node modules not found. Installing..." -ForegroundColor Yellow
    Set-Location Frontend
    npm install
    Set-Location ..
    Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Node.js dependencies found" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Starting Services" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You need to start TWO services in separate terminal windows:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 - FastAPI ML Backend:" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "  python api_server.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 2 - Frontend Server:" -ForegroundColor White
Write-Host "  cd Frontend" -ForegroundColor Cyan
Write-Host "  npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$startNow = Read-Host "Start ML Backend now in this terminal? (y/n)"
if ($startNow -eq "y") {
    Write-Host ""
    Write-Host "🤖 Starting ML Backend..." -ForegroundColor Cyan
    Write-Host "📍 API: http://localhost:8000" -ForegroundColor Green
    Write-Host "📖 Docs: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  Remember to start the frontend in another terminal!" -ForegroundColor Yellow
    Write-Host ""
    .\venv\Scripts\Activate.ps1
    python api_server.py
} else {
    Write-Host ""
    Write-Host "✓ Setup complete! Follow the instructions above to start the services." -ForegroundColor Green
    Write-Host ""
}
