@echo off
REM ============================================================
REM Lee May Control Center - BOTS START
REM ============================================================
REM 목적: 선택적으로 켜고 끄는 봇들 시작
REM - AI Trading Bot (포트 5000) - 현재 비활성
REM - YouTube Learner (수동 실행)
REM - 기타 학습 봇들
REM ============================================================

echo.
echo ========================================
echo Lee May Control Center - BOTS START
echo ========================================
echo.

REM 작업 디렉토리 이동
cd /d C:\leemay_project

REM ============================================================
REM 1. AI Trading Bot (포트 5000) - 현재 비활성
REM ============================================================
echo [1/2] AI Trading Bot 확인 중...
echo 파일: upbit-smart-bot-v8.0-ULTIMATE.py
echo 포트: 5000
echo.

REM 파일 존재 여부 확인
if exist "upbit-smart-bot-v8.0-ULTIMATE.py" (
    echo [WARN] Trading Bot 파일 존재하지만 현재 비활성 상태
    echo        복구 계획: docs/AI_TRADING_RECOVERY_PLAN.md 참조
    echo        수동 실행: python upbit-smart-bot-v8.0-ULTIMATE.py
) else (
    echo [INFO] Trading Bot 파일 없음
)
echo.

REM ============================================================
REM 2. 기타 봇 상태 확인
REM ============================================================
echo [2/2] 기타 봇 상태 확인...
echo.

echo [INFO] YouTube Learner (수동 실행):
echo        - python leemay/learning/youtube_learner.py
echo        - 또는 http://localhost:5001 웹 UI 사용
echo.

echo [INFO] 전략 학습 봇 (수동 실행):
echo        - python upbit-smart-bot-v8.0-LEARNING.py
echo        - python upbit-backtest.py
echo.

REM ============================================================
REM 완료
REM ============================================================
echo ========================================
echo BOTS START 완료
echo ========================================
echo.
echo 현재 자동 시작되는 봇: 없음
echo 수동 실행 가능한 봇: YouTube Learner, 전략 학습
echo.
echo AI Trading Bot 복구:
echo   docs/AI_TRADING_RECOVERY_PLAN.md 참조
echo.

pause
