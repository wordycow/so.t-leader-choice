@echo off
REM 관리자 권한 자동 요청
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo 관리자 권한이 필요합니다. 권한 상승 중...
    goto UACPrompt
) else (
    goto gotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

REM ===== 실제 스크립트 시작 =====
chcp 65001 > nul
cls

echo ========================================
echo 🔄 Upbit Bot v9 - 재시작
echo ========================================
echo.

echo 🛑 1단계: 모든 서비스 종료...
echo.

REM Kill all processes
echo 🧹 기존 프로세스 정리 중...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM ollama.exe /T >nul 2>&1
taskkill /F /IM cloudflared.exe /T >nul 2>&1

REM Kill specific ports
for /f "tokens=5" %%a in ('netstat -aon ^| find ":11434" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8765" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo ✅ 종료 완료
echo.
echo ⏳ 5초 대기 중...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 🚀 2단계: 모든 서비스 재시작...
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았거나 PATH에 없습니다!
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

echo 🌐 1/6 Cloudflare Tunnel 시작...
start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run ollama-stable"
echo ✅ Cloudflare Tunnel 실행 완료
timeout /t 5 /nobreak >nul

echo.
echo 🤖 2/6 Ollama 서버 시작...
start "Ollama Server" cmd /k "ollama serve"
echo ✅ Ollama 서버 실행 완료
timeout /t 5 /nobreak >nul

echo.
echo 📡 3/6 Execution Engine 시작...
start "Execution Engine" cmd /k "cd /d %~dp0 && python execution_engine/main_loop.py > logs/execution_engine.log 2>&1"
echo ✅ Execution Engine 실행 완료
timeout /t 5 /nobreak >nul

echo.
echo ⚡ 4/6 Signal Engine 시작...
start "Signal Engine" cmd /k "cd /d %~dp0 && python signal_engine/main_loop.py > logs/signal_engine.log 2>&1"
echo ✅ Signal Engine 실행 완료
timeout /t 3 /nobreak >nul

echo.
echo 📊 5/6 Dashboard 시작...
start "Dashboard" cmd /k "cd /d %~dp0 && python dashboard/standalone_dashboard.py > logs/dashboard.log 2>&1"
echo ✅ Dashboard 실행 완료
timeout /t 3 /nobreak >nul

echo.
echo 🧠 6/6 IMEI System 시작...
start "IMEI System" cmd /k "cd /d %~dp0 && python imei_system/main_app.py > logs/imei_app.log 2>&1"
echo ✅ IMEI System 실행 완료
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo ✅ 재시작 완료!
echo ========================================
echo.
echo 🎉 실행 중인 창 (6개):
echo   1️⃣  Cloudflare Tunnel
echo   2️⃣  Ollama Server
echo   3️⃣  Execution Engine
echo   4️⃣  Signal Engine
echo   5️⃣  Dashboard
echo   6️⃣  IMEI System
echo.
echo 🌐 접속 주소:
echo   - Dashboard: http://localhost:5000
echo   - IMEI Chat: http://localhost:5001
echo.
echo ⏳ 5초 후 대시보드 자동 오픈...
timeout /t 5 /nobreak >nul

REM Open Dashboard
start http://localhost:5000

echo.
echo 💡 이 창은 닫지 마세요!
echo.
pause
