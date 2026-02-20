@echo off
chcp 65001 > nul
title Lee May Training Center - STOP
color 0C

echo ========================================
echo 🛑 Lee May Training Center - STOP
echo ========================================
echo.

echo [1/1] Stopping all services...
taskkill /F /IM python.exe > nul 2>&1
echo [OK] All services stopped
echo.

echo ========================================
echo ✅ SUCCESS! All stopped
echo ========================================
echo.
pause
