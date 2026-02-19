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
echo 🚀 Upbit Bot v9 - 스마트 시작
echo ========================================
echo.
echo 🔥 이미 실행 중인 서비스는 건너뜁니다!
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
echo 🔍 서비스 상태 확인 중...
echo ========================================
echo.

REM ========================================
REM 1. Cloudflare Tunnel 체크
REM ========================================
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I /N "cloudflared.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Cloudflare Tunnel 이미 실행 중 - 건너뜀
) else (
    echo 🌐 1/6 Cloudflare Tunnel 시작 중...
    start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run ollama-stable"
    echo ✅ Cloudflare Tunnel 실행 완료
    timeout /t 5 /nobreak >nul
)

REM ========================================
REM 2. Ollama 서버 체크
REM ========================================
netstat -ano | findstr ":11434" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ Ollama 서버 이미 실행 중 (port 11434) - 건너뜀
) else (
    echo 🤖 2/6 Ollama 서버 시작 중...
    start "Ollama Server" cmd /k "ollama serve"
    echo ✅ Ollama 서버 실행 완료
    timeout /t 5 /nobreak >nul
)

REM ========================================
REM 3. Execution Engine 체크 (port 8765)
REM ========================================
netstat -ano | findstr ":8765" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ Execution Engine 이미 실행 중 (port 8765) - 건너뜀
) else (
    echo 📡 3/6 Execution Engine 시작 중...
    start "Execution Engine" cmd /k "cd /d %~dp0 && python execution_engine/main_loop.py"
    echo ✅ Execution Engine 실행 완료
    timeout /t 5 /nobreak >nul
)

REM ========================================
REM 4. Signal Engine 체크
REM ========================================
tasklist /FI "WINDOWTITLE eq Signal Engine" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Signal Engine 이미 실행 중 - 건너뜀
) else (
    echo ⚡ 4/6 Signal Engine 시작 중...
    start "Signal Engine" cmd /k "cd /d %~dp0 && python signal_engine/main_loop.py"
    echo ✅ Signal Engine 실행 완료
    timeout /t 3 /nobreak >nul
)

REM ========================================
REM 5. Dashboard 체크 (port 5000)
REM ========================================
netstat -ano | findstr ":5000" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ Dashboard 이미 실행 중 (port 5000) - 건너뜀
) else (
    echo 📊 5/6 Dashboard 시작 중...
    start "Dashboard" cmd /k "cd /d %~dp0 && python dashboard/standalone_dashboard.py"
    echo ✅ Dashboard 실행 완료
    timeout /t 3 /nobreak >nul
)

REM ========================================
REM 6. IMEI System 체크 (port 5001)
REM ========================================
netstat -ano | findstr ":5001" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ IMEI System 이미 실행 중 (port 5001) - 건너뜀
) else (
    echo 🧠 6/6 IMEI System 시작 중...
    start "IMEI System" cmd /k "cd /d %~dp0 && python imei_system/main_app.py"
    echo ✅ IMEI System 실행 완료
    timeout /t 5 /nobreak >nul
)

echo.
echo ========================================
echo ✅ 시스템 시작/확인 완료!
echo ========================================
echo.
echo 🎉 실행 중인 서비스:
echo   1️⃣  Cloudflare Tunnel (ollama.thetheunique.com)
echo   2️⃣  Ollama Server (localhost:11434)
echo   3️⃣  Execution Engine (WebSocket 8765)
echo   4️⃣  Signal Engine (Top20 스캔 + 신호 전송)
echo   5️⃣  Dashboard (http://localhost:5000)
echo   6️⃣  IMEI System (http://localhost:5001)
echo.
echo 🌐 접속 주소:
echo   - Dashboard: http://localhost:5000
echo   - IMEI Chat: 우측 패널
echo.
echo 💡 Tip:
echo   - 이미 실행 중이면 자동으로 건너뜁니다
echo   - 모든 창을 닫으면 시스템이 종료됩니다
echo   - 종료하려면: 종료.bat 실행
echo.
echo ⏰ 5초 후 브라우저가 열립니다...
timeout /t 5 /nobreak >nul

REM Open browser
start http://localhost:5000

echo.
echo ✅ Dashboard가 브라우저에서 열렸습니다!
echo.
echo ⚠️  이 창을 닫지 마세요!
echo     (닫으면 시스템이 종료될 수 있습니다)
echo.
pause
