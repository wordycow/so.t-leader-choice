@echo off
chcp 65001 > nul
title 🚀 Upbit Smart Bot v8.0 ULTIMATE

echo ═══════════════════════════════════════════════════
echo 🏆 Upbit Smart Bot v8.0 ULTIMATE
echo ═══════════════════════════════════════════════════
echo.

:: Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 오류: Python이 설치되어 있지 않습니다.
    echo.
    echo Python 3.8 이상을 다운로드하세요:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python 확인 완료
echo.

:: 의존성 확인 및 설치
echo 📦 필수 라이브러리 확인 중...
pip list | findstr /C:"pyupbit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📥 필수 라이브러리 설치 중...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ 오류: 라이브러리 설치 실패
        pause
        exit /b 1
    )
    echo.
    echo ✅ 라이브러리 설치 완료
)

echo ✅ 라이브러리 확인 완료
echo.

:: config.json 확인
if not exist config.json (
    echo ❌ 오류: config.json 파일이 없습니다.
    echo.
    echo config.json 파일을 생성하고 API 키를 입력하세요.
    echo.
    pause
    exit /b 1
)

:: API 키 설정 확인
findstr /C:"여기에_업비트" config.json >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ⚠️  경고: API 키가 설정되지 않았습니다.
    echo.
    echo config.json 파일을 열어 API 키를 입력하세요.
    echo 연습 모드로는 실행 가능하지만, 실전 모드는 API 키 필요합니다.
    echo.
    echo [Enter]를 눌러 계속...
    pause >nul
)

echo.
echo ═══════════════════════════════════════════════════
echo 🚀 봇 시작 중...
echo ═══════════════════════════════════════════════════
echo.
echo 웹 대시보드: http://localhost:5000
echo.
echo 봇을 중지하려면 Ctrl+C를 누르세요.
echo.

:: 봇 실행
python upbit-smart-bot-v8.0-ULTIMATE.py

echo.
echo ═══════════════════════════════════════════════════
echo 봇이 종료되었습니다.
echo ═══════════════════════════════════════════════════
pause
