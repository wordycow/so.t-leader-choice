@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🔄 빠른 재시작 (Quick Restart)
echo ========================================
echo.

echo 🛑 1단계: 모든 서비스 종료...
call STOP_EVERYTHING.bat

echo.
echo ⏳ 3초 대기 중...
timeout /t 3 /nobreak >nul

echo.
echo 🚀 2단계: 모든 서비스 재시작...
call START_EVERYTHING.bat
