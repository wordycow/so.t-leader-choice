@echo off
chcp 65001 > nul
title Upbit Trading Bot - STOP
color 0C
cls

echo ================================================
echo   UPBIT TRADING BOT v8.0 - STOP
echo ================================================
echo.

REM Stop Python processes
echo [1/1] Stopping Trading Bot...
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find "python.exe" > nul
if %errorlevel% equ 0 (
    taskkill /F /IM python.exe > nul 2>&1
    timeout /t 2 /nobreak > nul
    echo [OK] Trading Bot stopped
) else (
    echo [INFO] Trading Bot was not running
)
echo.

echo ================================================
echo   SUCCESS! Bot stopped
echo ================================================
echo.
echo All services have been terminated.
echo You can now close this window.
echo.
pause
