@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🛑 모든 시스템 종료
echo ========================================
echo.

echo 🧹 Ollama 서버 종료...
taskkill /F /IM ollama.exe /T >nul 2>&1

echo 🧹 Python 봇 종료...
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ✅ 모든 시스템이 종료되었습니다.
echo.
pause
