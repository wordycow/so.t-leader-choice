@echo off
chcp 65001 >nul
REM =========================================
REM Cloudflare Tunnel 안정화 시작 스크립트
REM 자동 재연결 + 에러 복구
REM =========================================

echo 🚀 Cloudflare Tunnel 시작 중...
echo.

REM 기존 cloudflared 프로세스 종료
taskkill /F /IM cloudflared.exe >nul 2>&1

REM 5초 대기
timeout /t 5 /nobreak >nul

:START
echo [%date% %time%] Tunnel 시작 시도...

REM Cloudflare Tunnel 실행 (자동 재시작 모드)
cloudflared tunnel --protocol http2 run ollama-stable

REM 프로세스가 종료되면 10초 대기 후 재시작
echo [%date% %time%] Tunnel 종료됨. 10초 후 재시작...
timeout /t 10 /nobreak >nul

goto START
