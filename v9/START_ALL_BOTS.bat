@echo off
REM =============================================================================
REM  UPBIT BOT v9 + IMEI v3.0 - 전체 시스템 시작 스크립트 (Windows)
REM =============================================================================
REM  이 스크립트는 모든 봇을 한번에 시작합니다:
REM  1. Signal Engine (WebSocket Emitter) - 신호 생성 엔진
REM  2. Execution Engine (WebSocket Receiver) - 실행 엔진
REM  3. Dashboard (Flask App) - 대시보드 (port 5000)
REM  4. IMEI Main App (Flask App) - IMEI 앱 (port 5001)
REM =============================================================================

echo.
echo ========================================================================
echo  UPBIT BOT v9 + IMEI v3.0 - Starting All Services
echo ========================================================================
echo.

REM 현재 디렉토리 확인
cd /d "%~dp0"
echo Current Directory: %CD%
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python이 설치되어 있지 않거나 PATH에 없습니다.
    echo Python 3.8 이상을 설치하고 PATH에 추가하세요.
    pause
    exit /b 1
)

echo [OK] Python 설치 확인됨
python --version
echo.

REM .env 파일 존재 확인
if not exist ".env" (
    echo [WARNING] .env 파일이 없습니다.
    echo .env.example을 복사하여 .env를 만들고 API 키를 설정하세요.
    echo.
    echo 계속하려면 아무 키나 누르세요...
    pause >nul
)

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs
echo [OK] 로그 디렉토리 준비됨: logs\
echo.

echo ========================================================================
echo  Starting Services...
echo ========================================================================
echo.

REM 1. Signal Engine (WebSocket Emitter) - 새 창에서 실행
echo [1/4] Starting Signal Engine (WebSocket Emitter)...
start "Signal Engine - WebSocket Emitter" cmd /k "cd /d %CD% && python signal_engine\websocket_emitter.py > logs\signal_engine.log 2>&1"
timeout /t 3 /nobreak >nul
echo      신호 생성 엔진이 시작되었습니다. (새 창)
echo.

REM 2. Execution Engine (WebSocket Receiver) - 새 창에서 실행
echo [2/4] Starting Execution Engine (WebSocket Receiver)...
start "Execution Engine - WebSocket Receiver" cmd /k "cd /d %CD% && python execution_engine\websocket_receiver.py > logs\execution_engine.log 2>&1"
timeout /t 3 /nobreak >nul
echo      실행 엔진이 시작되었습니다. (새 창)
echo.

REM 3. Dashboard (Flask App) - port 5000 - 새 창에서 실행
echo [3/4] Starting Dashboard (Flask App - port 5000)...
start "Dashboard - http://localhost:5000" cmd /k "cd /d %CD% && python dashboard\dashboard_app.py > logs\dashboard.log 2>&1"
timeout /t 3 /nobreak >nul
echo      대시보드가 시작되었습니다. (새 창)
echo      URL: http://localhost:5000
echo.

REM 4. IMEI Main App (Flask App) - port 5001 - 새 창에서 실행
echo [4/4] Starting IMEI Main App (Flask App - port 5001)...
start "IMEI Main App - http://localhost:5001" cmd /k "cd /d %CD% && python imei_system\main_app.py > logs\imei_app.log 2>&1"
timeout /t 3 /nobreak >nul
echo      IMEI 앱이 시작되었습니다. (새 창)
echo      URL: http://localhost:5001
echo.

echo ========================================================================
echo  All Services Started Successfully!
echo ========================================================================
echo.
echo  4개의 새 창이 열렸습니다:
echo   1. Signal Engine        - 신호 생성 (WebSocket Emitter)
echo   2. Execution Engine     - 주문 실행 (WebSocket Receiver)
echo   3. Dashboard            - http://localhost:5000
echo   4. IMEI Main App        - http://localhost:5001
echo.
echo  로그 파일:
echo   - logs\signal_engine.log
echo   - logs\execution_engine.log
echo   - logs\dashboard.log
echo   - logs\imei_app.log
echo.
echo  종료하려면:
echo   - 각 창에서 Ctrl+C를 누르거나 창을 닫으세요.
echo   - 또는 STOP_ALL_BOTS.bat를 실행하세요.
echo.
echo  브라우저에서 대시보드에 접속하세요:
echo   http://localhost:5000
echo.
echo ========================================================================
echo.
echo 이 창을 닫아도 됩니다. 봇들은 각자의 창에서 계속 실행됩니다.
echo.
pause
