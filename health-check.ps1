# Health Check Script for NASA Weather Prediction App

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NASA Weather App - Health Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check Python
Write-Host "[1/7] Checking Python..." -ForegroundColor Yellow -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.[8-9]|Python 3\.1[0-9]") {
        Write-Host " ✓" -ForegroundColor Green
        Write-Host "      $pythonVersion" -ForegroundColor Gray
    } else {
        Write-Host " ⚠" -ForegroundColor Yellow
        Write-Host "      Found: $pythonVersion (Need Python 3.8+)" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "      Python not found!" -ForegroundColor Red
    $allGood = $false
}

# Check Node.js
Write-Host "[2/7] Checking Node.js..." -ForegroundColor Yellow -NoNewline
try {
    $nodeVersion = node --version 2>&1
    Write-Host " ✓" -ForegroundColor Green
    Write-Host "      $nodeVersion" -ForegroundColor Gray
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "      Node.js not found!" -ForegroundColor Red
    $allGood = $false
}

# Check virtual environment
Write-Host "[3/7] Checking virtual environment..." -ForegroundColor Yellow -NoNewline
if (Test-Path "venv") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "      Run: python -m venv venv" -ForegroundColor Red
    $allGood = $false
}

# Check data file
Write-Host "[4/7] Checking weather data..." -ForegroundColor Yellow -NoNewline
if (Test-Path "data/weather_cleaned.csv") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "      Missing: data/weather_cleaned.csv" -ForegroundColor Red
    $allGood = $false
}

# Check Node modules
Write-Host "[5/7] Checking Node modules..." -ForegroundColor Yellow -NoNewline
if (Test-Path "Frontend/node_modules") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "      Run: cd Frontend; npm install" -ForegroundColor Red
    $allGood = $false
}

# Check if FastAPI is running
Write-Host "[6/7] Checking FastAPI server..." -ForegroundColor Yellow -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host " ✓" -ForegroundColor Green
    Write-Host "      Server is running on port 8000" -ForegroundColor Gray
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "      Server not running on port 8000" -ForegroundColor Red
    Write-Host "      Start with: python api_server.py" -ForegroundColor Yellow
}

# Check if Frontend is running
Write-Host "[7/7] Checking Frontend server..." -ForegroundColor Yellow -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host " ✓" -ForegroundColor Green
    Write-Host "      Server is running on port 5000" -ForegroundColor Gray
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "      Server not running on port 5000" -ForegroundColor Red
    Write-Host "      Start with: cd Frontend; npm run dev" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "  Status: Ready to start! ✓" -ForegroundColor Green
} else {
    Write-Host "  Status: Setup needed ⚠" -ForegroundColor Yellow
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Quick actions
Write-Host "Quick Actions:" -ForegroundColor White
Write-Host "  [1] Install Python dependencies" -ForegroundColor Cyan
Write-Host "  [2] Install Node.js dependencies" -ForegroundColor Cyan
Write-Host "  [3] Start FastAPI server" -ForegroundColor Cyan
Write-Host "  [4] Start Frontend server" -ForegroundColor Cyan
Write-Host "  [5] View API documentation" -ForegroundColor Cyan
Write-Host "  [Q] Quit" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Select option"

switch ($choice) {
    "1" {
        Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
        .\venv\Scripts\Activate.ps1
        pip install -r requirements.txt
    }
    "2" {
        Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
        Set-Location Frontend
        npm install
        Set-Location ..
    }
    "3" {
        Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
        .\venv\Scripts\Activate.ps1
        python api_server.py
    }
    "4" {
        Write-Host "Starting Frontend server..." -ForegroundColor Yellow
        Set-Location Frontend
        npm run dev
    }
    "5" {
        Start-Process "http://localhost:8000/docs"
    }
    "Q" {
        exit
    }
    default {
        Write-Host "Invalid option" -ForegroundColor Red
    }
}
