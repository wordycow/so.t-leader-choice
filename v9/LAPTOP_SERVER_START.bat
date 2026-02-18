@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🚀 Upbit Bot v9 + IMEI v3.0 + Ollama
echo ========================================
echo.
echo 🔥 올인원 시작 스크립트 (노트북 로컬 서버용)
echo.
echo ✅ 필수 요구사항:
echo   - Python 3.8+ ✅
echo   - Internet Connection ✅
echo   - 🔥 Ollama 터널 활성화 (http://ollama.thetheunique.com)
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았거나 PATH에 없습니다!
    echo.
    pause
    exit /b 1
)

REM Create logs directory
if not exist "logs" mkdir logs

echo ========================================
echo 🧹 기존 프로세스 종료...
echo ========================================
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo 🤖 4개 엔진 시작 중...
echo ========================================
echo.

REM 1. Signal Engine (WebSocket Emitter)
echo 1️⃣  시그널 엔진 시작...
start "Signal Engine" cmd /k "cd /d %~dp0 && python signal_engine/websocket_emitter.py > logs/signal_engine.log 2>&1"
timeout /t 3 /nobreak >nul

REM 2. Execution Engine (WebSocket Receiver)
echo 2️⃣  실행 엔진 시작...
start "Execution Engine" cmd /k "cd /d %~dp0 && python execution_engine/websocket_receiver.py > logs/execution_engine.log 2>&1"
timeout /t 3 /nobreak >nul

REM 3. Dashboard (Standalone Flask)
echo 3️⃣  대시보드 시작 (http://localhost:5000)...
start "Dashboard" cmd /k "cd /d %~dp0 && python dashboard/standalone_dashboard.py > logs/dashboard.log 2>&1"
timeout /t 3 /nobreak >nul

REM 4. IMEI System (Main Flask App with Ollama Router)
echo 4️⃣  IMEI 시스템 시작 (http://localhost:5001 + Ollama Router)...
start "IMEI System" cmd /k "cd /d %~dp0 && python imei_system/main_app.py > logs/imei_app.log 2>&1"
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo ✅ 모든 엔진 시작 완료!
echo ========================================
echo.
echo 🌐 접속 주소:
echo   - Dashboard: http://localhost:5000
echo   - IMEI Chat: http://localhost:5001
echo.
echo 🔥 Ollama 연결:
echo   - URL: http://ollama.thetheunique.com
echo   - Model: qwen2.5:7b
echo.
echo 📊 로그 파일:
echo   - logs\signal_engine.log
echo   - logs\execution_engine.log
echo   - logs\dashboard.log
echo   - logs\imei_app.log
echo.
echo 🛑 종료 방법:
echo   - STOP_ALL_BOTS.bat 실행
echo   - 또는 각 창에서 Ctrl+C
echo.
echo ⏳ 5초 후 대시보드 자동 오픈...
timeout /t 5 /nobreak >nul

REM Open Dashboard in browser
start http://localhost:5000

echo.
echo 🎉 봇이 실행 중입니다. 이 창은 닫지 마세요!
echo.
pause
