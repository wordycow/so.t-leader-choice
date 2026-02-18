@echo off
REM =============================================================================
REM  UPBIT BOT v9 - 서버 상태 빠른 체크 (Windows)
REM =============================================================================
REM  서버가 살아있는지 빠르게 확인
REM =============================================================================

echo.
echo ========================================================================
echo  UPBIT BOT v9 - Quick Status Check
echo ========================================================================
echo.

cd /d "%~dp0"

REM Python 프로세스 확인
echo [CHECK 1] Python processes:
tasklist | findstr python.exe
if errorlevel 1 (
    echo   [WARNING] No Python processes found!
) else (
    echo   [OK] Python is running.
)
echo.

REM 포트 확인
echo [CHECK 2] Network ports:

netstat -an | findstr ":5000" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   [X] Port 5000 (Dashboard) - NOT listening
) else (
    echo   [OK] Port 5000 (Dashboard) - Listening
)

netstat -an | findstr ":5001" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   [X] Port 5001 (IMEI) - NOT listening
) else (
    echo   [OK] Port 5001 (IMEI) - Listening
)

netstat -an | findstr ":8765" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo   [X] Port 8765 (WebSocket) - NOT listening
) else (
    echo   [OK] Port 8765 (WebSocket) - Listening
)
echo.

REM 로그 파일 확인
echo [CHECK 3] Recent log activity:
if exist logs\dashboard.log (
    echo   Dashboard log: 
    for %%F in (logs\dashboard.log) do echo     Size: %%~zF bytes, Modified: %%~tF
) else (
    echo   [X] Dashboard log not found
)

if exist logs\imei_app.log (
    echo   IMEI log:
    for %%F in (logs\imei_app.log) do echo     Size: %%~zF bytes, Modified: %%~tF
) else (
    echo   [X] IMEI log not found
)
echo.

echo ========================================================================
echo  Status check complete.
echo ========================================================================
echo.
echo  If services are NOT running, execute RESTART_SERVER.bat
echo.
pause
