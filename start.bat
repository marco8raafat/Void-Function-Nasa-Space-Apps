@echo off
echo ========================================
echo  NASA Weather Prediction App
echo  Quick Start Guide
echo ========================================
echo.
echo This app requires TWO terminal windows:
echo.
echo Terminal 1 - ML Backend (FastAPI):
echo   venv\Scripts\activate
echo   python api_server.py
echo.
echo Terminal 2 - Frontend (React):
echo   cd Frontend
echo   npm run dev
echo.
echo ========================================
echo.
echo After starting both servers:
echo   Frontend: http://localhost:5000
echo   API: http://localhost:8000/docs
echo.
echo ========================================
echo.
choice /C YN /M "Start ML Backend in this window"
if errorlevel 2 goto end
if errorlevel 1 goto start

:start
echo.
echo Starting ML Backend...
echo.
call venv\Scripts\activate
python api_server.py
goto end

:end
pause
