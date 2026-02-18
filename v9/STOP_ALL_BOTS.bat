@echo off
REM =============================================================================
REM  UPBIT BOT v9 + IMEI v3.0 - 전체 시스템 종료 스크립트 (Windows)
REM =============================================================================

echo.
echo ========================================================================
echo  UPBIT BOT v9 + IMEI v3.0 - Stopping All Services
echo ========================================================================
echo.

echo [1/4] Stopping Signal Engine (WebSocket Emitter)...
taskkill /FI "WINDOWTITLE eq Signal Engine*" /F /T >nul 2>&1
if errorlevel 1 (
    echo      Signal Engine이 실행 중이 아닙니다.
) else (
    echo      Signal Engine이 종료되었습니다.
)
echo.

echo [2/4] Stopping Execution Engine (WebSocket Receiver)...
taskkill /FI "WINDOWTITLE eq Execution Engine*" /F /T >nul 2>&1
if errorlevel 1 (
    echo      Execution Engine이 실행 중이 아닙니다.
) else (
    echo      Execution Engine이 종료되었습니다.
)
echo.

echo [3/4] Stopping Dashboard (port 5000)...
taskkill /FI "WINDOWTITLE eq Dashboard*" /F /T >nul 2>&1
if errorlevel 1 (
    echo      Dashboard가 실행 중이 아닙니다.
) else (
    echo      Dashboard가 종료되었습니다.
)
echo.

echo [4/4] Stopping IMEI Main App (port 5001)...
taskkill /FI "WINDOWTITLE eq IMEI Main App*" /F /T >nul 2>&1
if errorlevel 1 (
    echo      IMEI Main App이 실행 중이 아닙니다.
) else (
    echo      IMEI Main App이 종료되었습니다.
)
echo.

REM Python 프로세스도 정리 (포트 기반)
echo Cleaning up Python processes on ports 5000 and 5001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
echo.

echo ========================================================================
echo  All Services Stopped
echo ========================================================================
echo.
pause
