@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🚀 Upbit Bot v9 - 완전 자동 시작
echo ========================================
echo.
echo 🔥 이 파일 하나로 모든 게 실행됩니다!
echo.
echo ✅ 자동 실행 항목:
echo   1. Ollama 서버 (localhost:11434)
echo   2. Signal Engine (WebSocket)
echo   3. Execution Engine (주문 실행)
echo   4. Dashboard (port 5000)
echo   5. IMEI System (port 5001 + Ollama Router)
echo.
echo 💡 Cloudflare Tunnel은 영구 고정 (ollama.thetheunique.com)
echo    → 별도 실행 불필요!
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

REM Create logs directory
if not exist "logs" mkdir logs

echo ========================================
echo 🧹 기존 프로세스 정리...
echo ========================================

REM Kill existing processes
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM ollama.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo 🤖 1/5 Ollama 서버 시작...
echo ========================================
start "Ollama Server" cmd /k "ollama serve"
echo ✅ Ollama 서버 실행 완료 (localhost:11434)
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo 📡 2/5 Signal Engine 시작...
echo ========================================
start "Signal Engine" cmd /k "cd /d %~dp0 && python signal_engine/websocket_emitter.py > logs/signal_engine.log 2>&1"
echo ✅ Signal Engine 실행 완료
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo ⚡ 3/5 Execution Engine 시작...
echo ========================================
start "Execution Engine" cmd /k "cd /d %~dp0 && python execution_engine/websocket_receiver.py > logs/execution_engine.log 2>&1"
echo ✅ Execution Engine 실행 완료
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 📊 4/5 Dashboard 시작...
echo ========================================
start "Dashboard" cmd /k "cd /d %~dp0 && python dashboard/standalone_dashboard.py > logs/dashboard.log 2>&1"
echo ✅ Dashboard 실행 완료 (http://localhost:5000)
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo 🧠 5/5 IMEI System 시작...
echo ========================================
start "IMEI System" cmd /k "cd /d %~dp0 && python imei_system/main_app.py > logs/imei_app.log 2>&1"
echo ✅ IMEI System 실행 완료 (http://localhost:5001)
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo ✅ 모든 시스템 시작 완료!
echo ========================================
echo.
echo 🎉 실행 중인 창:
echo   1️⃣  Ollama Server (localhost:11434)
echo   2️⃣  Signal Engine (WebSocket 신호 생성)
echo   3️⃣  Execution Engine (주문 실행)
echo   4️⃣  Dashboard (http://localhost:5000)
echo   5️⃣  IMEI System (http://localhost:5001)
echo.
echo 🌐 접속 주소:
echo   - Dashboard: http://localhost:5000
echo   - IMEI Chat: http://localhost:5001
echo.
echo 🔥 Ollama 연결:
echo   - Local: http://localhost:11434
echo   - Tunnel: http://ollama.thetheunique.com (Named Tunnel - 영구)
echo   - Model: qwen2.5:7b
echo.
echo 📊 로그 파일:
echo   - logs\signal_engine.log
echo   - logs\execution_engine.log
echo   - logs\dashboard.log
echo   - logs\imei_app.log
echo.
echo 🛑 종료 방법:
echo   - STOP_EVERYTHING.bat 실행
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
