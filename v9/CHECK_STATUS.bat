@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🔍 시스템 상태 체크
echo ========================================
echo.

REM Check each port
set /a RUNNING=0
set /a TOTAL=4

echo 📊 포트 상태 확인 중...
echo.

REM Port 11434 - Ollama
netstat -aon | find ":11434" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Port 11434 - Ollama Server          [실행중]
    set /a RUNNING+=1
) else (
    echo ❌ Port 11434 - Ollama Server          [중지됨]
)

REM Port 8765 - Execution Engine
netstat -aon | find ":8765" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Port 8765  - Execution Engine       [실행중]
    set /a RUNNING+=1
) else (
    echo ❌ Port 8765  - Execution Engine       [중지됨]
)

REM Port 5000 - Dashboard
netstat -aon | find ":5000" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Port 5000  - Dashboard              [실행중]
    set /a RUNNING+=1
) else (
    echo ❌ Port 5000  - Dashboard              [중지됨]
)

REM Port 5001 - IMEI System
netstat -aon | find ":5001" | find "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Port 5001  - IMEI System            [실행중]
    set /a RUNNING+=1
) else (
    echo ❌ Port 5001  - IMEI System            [중지됨]
)

echo.
echo ========================================
echo 📈 요약: %RUNNING% / %TOTAL% 서비스 실행 중
echo ========================================
echo.

if %RUNNING% equ 0 (
    echo 🛑 모든 서비스가 중지되었습니다.
) else if %RUNNING% equ %TOTAL% (
    echo ✅ 모든 서비스가 정상 실행 중입니다!
    echo.
    echo 🌐 접속 주소:
    echo    - Dashboard: http://localhost:5000
    echo    - IMEI Chat: http://localhost:5001
) else (
    echo ⚠️  일부 서비스만 실행 중입니다. 전체 재시작을 권장합니다.
    echo.
    echo 💡 전체 재시작 방법:
    echo    1. STOP_EVERYTHING.bat 실행
    echo    2. START_EVERYTHING.bat 실행
)

echo.
echo 🔄 API 상태 확인 (Dashboard 실행 중일 때):
echo.

if %RUNNING% gtr 0 (
    echo 📊 /health 체크 중...
    curl -s http://localhost:5000/health 2>nul | python -c "import sys, json; d=json.load(sys.stdin); print('   Signal Engine:', d['signal_engine']['status']); print('   Execution Engine:', d['execution_engine']['status'])" 2>nul
    if %errorlevel% neq 0 (
        echo    ⚠️  Dashboard가 응답하지 않습니다.
    )
)

echo.
pause
