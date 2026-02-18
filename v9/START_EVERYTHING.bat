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
echo 🚀 Upbit Bot v9 - 완전 자동 시작
echo ========================================
echo.
echo 🔥 이 파일 하나로 모든 게 실행됩니다!
echo.
echo ✅ 자동 실행 항목:
echo   1. Cloudflare Tunnel (ollama.thetheunique.com)
echo   2. Ollama 서버 (localhost:11434)
echo   3. Execution Engine (WebSocket 8765)
echo   4. Signal Engine (Top20 스캔)
echo   5. Dashboard (port 5000)
echo   6. IMEI System (port 5001 + Ollama Router)
echo.
echo 💡 이 파일 하나로 6개 서비스가 모두 실행됩니다!
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았거나 PATH에 없습니다!
    pause
    exit /b 1
)

REM Check Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama가 설치되지 않았습니다!
    echo.
    echo 📥 설치 방법:
    echo    https://ollama.com/download
    echo.
    pause
    exit /b 1
)

REM Check Cloudflared
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo ❌ Cloudflared가 설치되지 않았습니다!
    echo.
    echo 📥 설치 방법:
    echo    https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
    echo.
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

echo ========================================
echo 🧹 기존 프로세스 정리...
echo ========================================

REM Kill existing processes
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM ollama.exe /T >nul 2>&1
taskkill /F /IM cloudflared.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo 🌐 1/6 Cloudflare Tunnel 시작...
echo ========================================
start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run ollama-stable"
echo ✅ Cloudflare Tunnel 실행 완료 (ollama.thetheunique.com)
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 🤖 2/6 Ollama 서버 시작...
echo ========================================
start "Ollama Server" cmd /k "ollama serve"
echo ✅ Ollama 서버 실행 완료 (localhost:11434)
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 📡 3/6 Execution Engine 시작...
echo ========================================
start "Execution Engine" cmd /k "cd /d %~dp0 && python execution_engine/main_loop.py > logs/execution_engine.log 2>&1"
echo ✅ Execution Engine 실행 완료 (WebSocket 8765 서버)
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo ⚡ 4/6 Signal Engine 시작...
echo ========================================
start "Signal Engine" cmd /k "cd /d %~dp0 && python signal_engine/main_loop.py > logs/signal_engine.log 2>&1"
echo ✅ Signal Engine 실행 완료 (Top20 스캔 + 신호 발생)
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 📊 5/6 Dashboard 시작...
echo ========================================
start "Dashboard" cmd /k "cd /d %~dp0 && python dashboard/standalone_dashboard.py > logs/dashboard.log 2>&1"
echo ✅ Dashboard 실행 완료 (http://localhost:5000)
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 🧠 6/6 IMEI System 시작...
echo ========================================
start "IMEI System" cmd /k "cd /d %~dp0 && python imei_system/main_app.py > logs/imei_app.log 2>&1"
echo ✅ IMEI System 실행 완료 (http://localhost:5001)
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo ✅ 모든 시스템 시작 완료!
echo ========================================
echo.
echo 🎉 실행 중인 창 (6개):
echo   1️⃣  Cloudflare Tunnel (ollama.thetheunique.com)
echo   2️⃣  Ollama Server (localhost:11434)
echo   3️⃣  Execution Engine (WebSocket 8765 서버)
echo   4️⃣  Signal Engine (Top20 스캔 + 신호 전송)
echo   5️⃣  Dashboard (http://localhost:5000)
echo   6️⃣  IMEI System (http://localhost:5001)
echo.
echo 🌐 접속 주소:
echo   - Dashboard: http://localhost:5000
echo   - IMEI Chat: http://localhost:5001
echo.
echo 🔥 Ollama 연결:
echo   - Local: http://localhost:11434
echo   - Tunnel: http://ollama.thetheunique.com
echo   - Model: qwen2.5:7b
echo.
echo 📊 로그 파일:
echo   - logs\signal_engine.log
echo   - logs\execution_engine.log
echo   - logs\dashboard.log
echo   - logs\imei_app.log
echo.
echo 🛑 종료 방법:
echo   - STOP_EVERYTHING.bat 실행 (관리자 권한으로)
echo   - 또는 각 창에서 Ctrl+C
echo.
echo ⏳ 5초 후 대시보드 자동 오픈...
timeout /t 5 /nobreak >nul

REM Open Dashboard
start http://localhost:5000

echo.
echo 💡 이 창은 닫지 마세요!
echo    (닫으면 모든 봇이 종료됩니다)
echo.
pause
