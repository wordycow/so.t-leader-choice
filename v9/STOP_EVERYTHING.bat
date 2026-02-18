@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🛑 모든 시스템 종료 (포트 기준)
echo ========================================
echo.

echo 🔍 현재 실행 중인 프로세스 확인...
echo.

REM Check and kill each port
set /a KILLED=0

echo 🧹 Port 11434 (Ollama Server) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":11434" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ Ollama Server 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo 🧹 Port 8765 (Execution Engine WebSocket) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8765" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ Execution Engine 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo 🧹 Port 5000 (Dashboard) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ Dashboard 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo 🧹 Port 5001 (IMEI System) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ IMEI System 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo.
echo 🧹 남은 Python/Ollama 프로세스 정리 중...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM ollama.exe /T >nul 2>&1

echo.
echo ========================================
echo ✅ 종료 완료!
echo ========================================
echo.
echo 📊 종료된 포트:
echo   - 11434 (Ollama Server)
echo   - 8765  (Execution Engine WebSocket)
echo   - 5000  (Dashboard)
echo   - 5001  (IMEI System)
echo.
echo 💡 3초 후 상태 확인...
timeout /t 3 /nobreak >nul

REM Run status check
call CHECK_STATUS.bat

pause
