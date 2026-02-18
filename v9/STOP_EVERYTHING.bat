@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🛑 모든 시스템 종료 (포트 기준)
echo ========================================
echo.

echo 🧹 Port 11434 (Ollama Server) 종료...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":11434" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo 🧹 Port 8765 (Execution Engine WebSocket) 종료...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8765" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo 🧹 Port 5000 (Dashboard) 종료...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo 🧹 Port 5001 (IMEI System) 종료...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

echo 🧹 남은 Python/Ollama 프로세스 정리...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM ollama.exe /T >nul 2>&1

echo.
echo ✅ 모든 시스템이 종료되었습니다.
echo.
echo 📊 종료된 포트:
echo   - 11434 (Ollama Server)
echo   - 8765  (Execution Engine WebSocket)
echo   - 5000  (Dashboard)
echo   - 5001  (IMEI System)
echo.
pause
