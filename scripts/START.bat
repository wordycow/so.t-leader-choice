@echo off
chcp 65001 > nul
title Lee May Training Center - START
color 0A

echo ========================================
echo 🤖 Lee May Training Center
echo ========================================
echo.

REM Python 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

echo [1/2] Installing dependencies...
pip install -q flask flask-cors psutil
echo [OK] Dependencies installed
echo.

echo [2/2] Starting API Server...
start /B python api/main_api.py
timeout /t 3 /nobreak > nul
echo [OK] API Server started
echo.

echo ========================================
echo ✅ SUCCESS! Server is running
echo ========================================
echo.
echo [ACCESS URL]
echo   Local:  http://localhost:5000
echo   Domain: https://leemay.더유니크.com
echo.
echo [STOP]
echo   Run: STOP.bat
echo.
pause
