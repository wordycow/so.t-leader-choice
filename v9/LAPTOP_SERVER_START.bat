@echo off
REM =============================================================================
REM  노트북 서버 완전 시작 스크립트 (All-in-One)
REM =============================================================================
REM  노트북을 켤 때 이것 하나만 실행하면 됩니다!
REM =============================================================================

echo.
echo ========================================================================
echo  UPBIT BOT v9 - Laptop Server Complete Startup
echo ========================================================================
echo.

cd /d "%~dp0"
echo Current Directory: %CD%
echo.

REM =============================================================================
REM  환경 체크
REM =============================================================================

echo [CHECK] Checking environment...
echo.

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)
echo [OK] Python: 
python --version
echo.

REM .env 파일 확인 (선택사항)
if not exist ".env" (
    echo [INFO] .env file not found (optional for PRACTICE mode)
)
echo.

REM =============================================================================
REM  기존 프로세스 정리 (혹시 몰라서)
REM =============================================================================

echo [CLEANUP] Stopping any existing processes...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo [OK] Cleanup complete.
echo.

REM =============================================================================
REM  로그 디렉토리 준비
REM =============================================================================

if not exist "logs" mkdir logs
if not exist "logs\backup" mkdir logs\backup
echo [OK] Log directories ready.
echo.

REM =============================================================================
REM  봇 시작 (4개)
REM =============================================================================

echo ========================================================================
echo  Starting All Services...
echo ========================================================================
echo.

REM 1. Signal Engine
echo [1/4] Starting Signal Engine...
start "📊 Signal Engine" cmd /k "cd /d %CD% && python signal_engine\websocket_emitter.py"
timeout /t 3 /nobreak >nul
echo      ✅ Started

REM 2. Execution Engine
echo [2/4] Starting Execution Engine...
start "⚙️ Execution Engine" cmd /k "cd /d %CD% && python execution_engine\websocket_receiver.py"
timeout /t 3 /nobreak >nul
echo      ✅ Started

REM 3. Dashboard
echo [3/4] Starting Dashboard (port 5000)...
start "🎨 Dashboard" cmd /k "cd /d %CD% && python dashboard\standalone_dashboard.py"
timeout /t 3 /nobreak >nul
echo      ✅ Started - http://localhost:5000

REM 4. IMEI System
echo [4/4] Starting IMEI System (port 5001)...
start "🤖 IMEI System" cmd /k "cd /d %CD% && python imei_system\main_app.py"
timeout /t 5 /nobreak >nul
echo      ✅ Started - http://localhost:5001

echo.
echo ========================================================================
echo  ✅ All Services Started!
echo ========================================================================
echo.
echo  4개의 창이 열렸습니다:
echo.
echo   📊 Signal Engine       - 신호 생성 엔진
echo   ⚙️ Execution Engine    - 주문 실행 엔진
echo   🎨 Dashboard           - http://localhost:5000
echo   🤖 IMEI System         - http://localhost:5001
echo.
echo ========================================================================
echo  브라우저 자동 실행...
echo ========================================================================
echo.

REM 5초 후 브라우저 자동 오픈
timeout /t 5 /nobreak >nul
start http://localhost:5000

echo.
echo  Dashboard가 브라우저에서 열렸습니다!
echo.
echo  문제가 있으면:
echo   - QUICK_CHECK.bat로 상태 확인
echo   - RESTART_SERVER.bat로 재시작
echo.
echo  종료하려면:
echo   - STOP_ALL_BOTS.bat 실행
echo   - 또는 각 창에서 Ctrl+C
echo.
echo ========================================================================
echo.
echo  이 창을 닫아도 봇들은 계속 실행됩니다.
echo.
pause
