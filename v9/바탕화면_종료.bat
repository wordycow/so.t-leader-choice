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
echo 🛑 Upbit Bot v9 - 바탕화면 종료
echo ========================================
echo.

REM 프로젝트 디렉토리 설정
set PROJECT_DIR=C:\Windows\System32\webapp\v9

echo 📂 프로젝트 경로: %PROJECT_DIR%
echo.

echo 🔍 현재 실행 중인 프로세스 확인...
echo.

REM Check and kill each port
setlocal enabledelayedexpansion
set /a KILLED=0

echo 🧹 Port 11434 (Ollama Server) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":11434" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ Ollama Server 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo 🧹 Port 8765 (Execution Engine WebSocket) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8765" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ Execution Engine 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo 🧹 Port 5000 (Dashboard) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ Dashboard 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo 🧹 Port 5001 (IMEI System) 종료 중...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo    ✅ IMEI System 종료됨 (PID: %%a^)
        set /a KILLED+=1
    )
)

echo.
echo 🧹 남은 Python/Ollama/Cloudflared 프로세스 정리 중...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM ollama.exe /T >nul 2>&1
taskkill /F /IM cloudflared.exe /T >nul 2>&1

echo.
echo ========================================
echo ✅ 종료 완료!
echo ========================================
echo.
echo 📊 종료된 포트:
echo   - 11434 (Ollama Server)
echo   - 8765  (Execution Engine WebSocket)
echo   - 5000  (Dashboard)
echo   - 5001  (IMEI System)
echo   - Cloudflare Tunnel (cloudflared.exe)
echo.
echo 💡 모든 프로세스가 종료되었습니다.
echo.
pause
