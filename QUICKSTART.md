# 🚀 Quick Start Guide

## Fastest Way to Get Started

### Step 1: Install Dependencies

**Python (one-time setup):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Node.js (one-time setup):**
```powershell
cd Frontend
npm install
cd ..
```

### Step 2: Start Both Servers

**Option A: Using Scripts (Easiest)**

Double-click `start.bat` or run:
```powershell
.\start.ps1
```

**Option B: Manual Start**

**Terminal 1 - Start ML Backend:**
```powershell
.\venv\Scripts\Activate.ps1
python api_server.py
```

**Terminal 2 - Start Frontend:**
```powershell
cd Frontend
npm run dev
```

### Step 3: Open the App

🌐 **Frontend:** http://localhost:5000  
📖 **API Docs:** http://localhost:8000/docs

## Usage

1. Open http://localhost:5000/weather
2. Click on the map OR enter coordinates manually
3. Select a date
4. Click "Get Weather Prediction"
5. View the ML-powered rain prediction!

## Troubleshooting

**"ML Backend: Offline" badge showing?**
- Make sure you started the FastAPI server (python api_server.py)
- Check that it's running on port 8000

**Port already in use?**
```powershell
# Kill process on port 8000 (FastAPI)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 5000 (Frontend)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Module not found errors?**
```powershell
# Reinstall Python packages
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt --force-reinstall

# Reinstall Node packages
cd Frontend
npm install
```

## What Each Server Does

**FastAPI (Port 8000):** ML model that predicts rain based on season  
**Express (Port 5000):** Serves frontend and proxies requests to FastAPI

---

For detailed documentation, see [README_INTEGRATION.md](README_INTEGRATION.md)
