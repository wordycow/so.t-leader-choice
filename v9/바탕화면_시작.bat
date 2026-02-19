@echo off
REM ========================================
REM 바탕화면 실행용 스마트 시작 스크립트
REM 프로젝트 경로 자동 감지
REM ========================================

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

chcp 65001 > nul
cls

echo ========================================
echo 🚀 Upbit Bot v9 - 바탕화면 시작
echo ========================================
echo.

REM 프로젝트 경로 설정 (필요 시 수정)
set PROJECT_DIR=C:\Windows\System32\webapp\v9

REM 프로젝트 경로 확인
if not exist "%PROJECT_DIR%" (
    echo ❌ 프로젝트 폴더를 찾을 수 없습니다!
    echo    경로: %PROJECT_DIR%
    echo.
    echo 💡 해결 방법:
    echo    1. 이 파일을 메모장으로 열기
    echo    2. 9번째 줄의 PROJECT_DIR 경로 수정
    echo    3. 저장 후 다시 실행
    echo.
    pause
    exit /b 1
)

echo ✅ 프로젝트 경로 확인: %PROJECT_DIR%
echo.

REM 프로젝트 폴더로 이동
cd /d "%PROJECT_DIR%"

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다!
    echo    다운로드: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Ollama 확인
where ollama >nul 2>&1
if errorlevel 1 (
    echo ❌ Ollama가 설치되지 않았습니다!
    echo    다운로드: https://ollama.com/download
    pause
    exit /b 1
)

REM Cloudflared 확인
where cloudflared >nul 2>&1
if errorlevel 1 (
    echo ❌ Cloudflared가 설치되지 않았습니다!
    echo    다운로드: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
    pause
    exit /b 1
)

REM logs 폴더 생성
if not exist "logs" mkdir logs

echo ========================================
echo 🔍 서비스 상태 확인 중...
echo ========================================
echo.

REM ========================================
REM 1. Cloudflare Tunnel
REM ========================================
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I /N "cloudflared.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Cloudflare Tunnel 이미 실행 중
) else (
    echo 🌐 Cloudflare Tunnel 시작 중...
    start "Cloudflare Tunnel" cmd /k "cloudflared tunnel run ollama-stable"
    timeout /t 5 /nobreak >nul
    echo ✅ Cloudflare Tunnel 시작 완료
)

REM ========================================
REM 2. Ollama 서버
REM ========================================
netstat -ano | findstr ":11434" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ Ollama 서버 이미 실행 중 (port 11434)
) else (
    echo 🤖 Ollama 서버 시작 중...
    start "Ollama Server" cmd /k "ollama serve"
    timeout /t 5 /nobreak >nul
    echo ✅ Ollama 서버 시작 완료
)

REM ========================================
REM 3. Execution Engine
REM ========================================
netstat -ano | findstr ":8765" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ Execution Engine 이미 실행 중 (port 8765)
) else (
    echo 📡 Execution Engine 시작 중...
    start "Execution Engine" cmd /k "cd /d %PROJECT_DIR% && python execution_engine/main_loop.py"
    timeout /t 5 /nobreak >nul
    echo ✅ Execution Engine 시작 완료
)

REM ========================================
REM 4. Signal Engine
REM ========================================
tasklist /FI "WINDOWTITLE eq Signal Engine" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✅ Signal Engine 이미 실행 중
) else (
    echo ⚡ Signal Engine 시작 중...
    start "Signal Engine" cmd /k "cd /d %PROJECT_DIR% && python signal_engine/main_loop.py"
    timeout /t 3 /nobreak >nul
    echo ✅ Signal Engine 시작 완료
)

REM ========================================
REM 5. Dashboard
REM ========================================
netstat -ano | findstr ":5000" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ Dashboard 이미 실행 중 (port 5000)
) else (
    echo 📊 Dashboard 시작 중...
    start "Dashboard" cmd /k "cd /d %PROJECT_DIR% && python dashboard/standalone_dashboard.py"
    timeout /t 3 /nobreak >nul
    echo ✅ Dashboard 시작 완료
)

REM ========================================
REM 6. IMEI System
REM ========================================
netstat -ano | findstr ":5001" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo ✅ IMEI System 이미 실행 중 (port 5001)
) else (
    echo 🧠 IMEI System 시작 중...
    start "IMEI System" cmd /k "cd /d %PROJECT_DIR% && python imei_system/main_app.py"
    timeout /t 5 /nobreak >nul
    echo ✅ IMEI System 시작 완료
)

echo.
echo ========================================
echo ✅ 모든 시스템 시작/확인 완료!
echo ========================================
echo.
echo 🎉 실행 중인 서비스:
echo   1️⃣  Cloudflare Tunnel
echo   2️⃣  Ollama Server (localhost:11434)
echo   3️⃣  Execution Engine (WebSocket 8765)
echo   4️⃣  Signal Engine (Top20 스캔)
echo   5️⃣  Dashboard (http://localhost:5000)
echo   6️⃣  IMEI System (http://localhost:5001)
echo.
echo 🌐 접속:
echo   Dashboard: http://localhost:5000
echo.
echo ⏰ 5초 후 브라우저가 열립니다...
timeout /t 5 /nobreak >nul

start http://localhost:5000

echo.
echo ✅ Dashboard가 열렸습니다!
echo.
echo 💡 Tip:
echo   - 이미 실행 중인 서비스는 자동으로 건너뜁니다
echo   - 종료하려면: 종료.bat 실행
echo.
pause
