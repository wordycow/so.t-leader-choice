@echo off
chcp 65001 > nul
title Upbit Trading Bot - START
color 0A
cls

echo ================================================
echo   UPBIT TRADING BOT v8.0 - START
echo ================================================
echo.

REM Check Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if already running
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" > nul
if %errorlevel% equ 0 (
    echo [WARNING] Python process already running!
    echo If bot is already running, use STOP.bat first
    echo.
)

REM Install dependencies
echo [1/2] Installing Python packages...
pip install -q flask pyupbit pandas ta numpy requests pyjwt python-dotenv
echo [OK] Dependencies installed
echo.

REM Start bot
echo [2/2] Starting Trading Bot...
start /B python upbit-smart-bot-v8.0-ULTIMATE.py
timeout /t 3 /nobreak > nul
echo [OK] Bot started successfully!
echo.

echo ================================================
echo   SUCCESS! Bot is now running
echo ================================================
echo.
echo [ACCESS URL]
echo   http://localhost:5000
echo.
echo [LOGIN]
echo   Username: wordycow
echo   Password: 1234
echo.
echo [WARNING] Do NOT close this window!
echo           Bot will stop if you close it.
echo           Use STOP.bat to safely stop the bot.
echo.
pause
