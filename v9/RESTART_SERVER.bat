@echo off
REM =============================================================================
REM  UPBIT BOT v9 - 서버 재시작 스크립트 (Windows)
REM =============================================================================
REM  노트북이 절전모드에서 깨어났거나 네트워크가 끊겼을 때 사용
REM  모든 봇을 종료하고 깨끗하게 다시 시작합니다.
REM =============================================================================

echo.
echo ========================================================================
echo  UPBIT BOT v9 - Server Restart
echo ========================================================================
echo.

cd /d "%~dp0"
echo Current Directory: %CD%
echo.

REM =============================================================================
REM  STEP 1: 기존 프로세스 종료
REM =============================================================================

echo [STEP 1/3] Stopping all existing processes...
echo.

REM Python 프로세스 종료
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1

REM 포트 점유 프로세스 강제 종료
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8765" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1

timeout /t 2 /nobreak >nul
echo [OK] All processes stopped.
echo.

REM =============================================================================
REM  STEP 2: 임시 파일 정리 (선택)
REM =============================================================================

echo [STEP 2/3] Cleaning temporary files...
echo.

REM 로그 파일 백업 (선택사항)
if exist logs\*.log (
    echo Backing up old logs...
    if not exist logs\backup mkdir logs\backup
    for %%f in (logs\*.log) do (
        copy "%%f" "logs\backup\%%~nxf.%date:~0,4%%date:~5,2%%date:~8,2%.bak" >nul 2>&1
    )
    del /Q logs\*.log >nul 2>&1
)

REM SQLite WAL/SHM 파일 정리
del /Q upbit_bot.db-shm >nul 2>&1
del /Q upbit_bot.db-wal >nul 2>&1
del /Q imei_memory.db-shm >nul 2>&1
del /Q imei_memory.db-wal >nul 2>&1

echo [OK] Cleanup complete.
echo.

REM =============================================================================
REM  STEP 3: 모든 봇 재시작
REM =============================================================================

echo [STEP 3/3] Restarting all services...
echo.

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs

REM 1. Signal Engine
echo [1/4] Starting Signal Engine...
start "Signal Engine" cmd /k "cd /d %CD% && python signal_engine\websocket_emitter.py"
timeout /t 3 /nobreak >nul
echo      Started.

REM 2. Execution Engine
echo [2/4] Starting Execution Engine...
start "Execution Engine" cmd /k "cd /d %CD% && python execution_engine\websocket_receiver.py"
timeout /t 3 /nobreak >nul
echo      Started.

REM 3. Dashboard
echo [3/4] Starting Dashboard (port 5000)...
start "Dashboard" cmd /k "cd /d %CD% && python dashboard\standalone_dashboard.py"
timeout /t 3 /nobreak >nul
echo      Started. URL: http://localhost:5000

REM 4. IMEI System
echo [4/4] Starting IMEI System (port 5001)...
start "IMEI System" cmd /k "cd /d %CD% && python imei_system\main_app.py"
timeout /t 3 /nobreak >nul
echo      Started. URL: http://localhost:5001

echo.
echo ========================================================================
echo  Server Restart Complete!
echo ========================================================================
echo.
echo  4개의 창이 열렸습니다:
echo   1. Signal Engine
echo   2. Execution Engine
echo   3. Dashboard - http://localhost:5000
echo   4. IMEI System - http://localhost:5001
echo.
echo  브라우저에서 대시보드 확인:
echo   http://localhost:5000
echo.
echo  문제가 계속되면:
echo   1. 인터넷 연결 확인
echo   2. Python 버전 확인 (python --version)
echo   3. 방화벽 설정 확인 (포트 5000, 5001, 8765)
echo.
echo ========================================================================
echo.
pause
