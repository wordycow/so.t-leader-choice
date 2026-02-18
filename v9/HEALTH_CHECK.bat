@echo off
chcp 65001 > nul
cls

echo ========================================
echo 🩺 상세 헬스 체크
echo ========================================
echo.

echo 🔍 포트 상태...
call CHECK_STATUS.bat

echo.
echo ========================================
echo 📊 API 상세 체크
echo ========================================
echo.

REM Check if Dashboard is running
netstat -aon | find ":5000" | find "LISTENING" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dashboard가 실행되지 않았습니다.
    echo    먼저 START_EVERYTHING.bat을 실행하세요.
    pause
    exit /b 1
)

echo 1️⃣  /api/top20 체크...
curl -s http://localhost:5000/api/top20 2>nul | python -c "import sys, json; d=json.load(sys.stdin); print('   ✅ Source:', d.get('source')); print('   ✅ Items:', len(d.get('items', []))); print('   ✅ Top 3:', [x['ticker'] for x in d['items'][:3]])" 2>nul
if %errorlevel% neq 0 echo    ❌ API 응답 실패

echo.
echo 2️⃣  /health 체크...
curl -s http://localhost:5000/health 2>nul | python -c "import sys, json; d=json.load(sys.stdin); se=d['signal_engine']; ex=d['execution_engine']; print('   Signal Engine:'); print('     - Status:', se['status']); print('     - Last Scan:', se.get('last_top20_scan_at', 'N/A')); print('     - Signal Count:', se.get('signal_sent_count', 0)); print('   Execution Engine:'); print('     - Status:', ex['status']); print('     - Paper Fills:', ex.get('paper_fill_count', 0))" 2>nul
if %errorlevel% neq 0 echo    ❌ Health API 응답 실패

echo.
echo 3️⃣  /api/watch_state 체크...
curl -s http://localhost:5000/api/watch_state 2>nul | python -c "import sys, json; d=json.load(sys.stdin); print('   ✅ Tracked Tickers:', d.get('tracked_tickers', 0)); print('   ✅ Last Scan:', d.get('last_top20_scan_at', 'N/A')); print('   ✅ Signal Count:', d.get('signal_sent_count', 0))" 2>nul
if %errorlevel% neq 0 echo    ❌ Watch State API 응답 실패

echo.
echo 4️⃣  /api/trades 체크...
curl -s http://localhost:5000/api/trades 2>nul | python -c "import sys, json; d=json.load(sys.stdin); items=d.get('items', []); print('   ✅ Total Trades:', len(items)); print('   ✅ Source:', d.get('source')); [print(f'   📊 {t[\"ticker\"]} {t[\"side\"]} - {t[\"strategy_name\"]}') for t in items[:3]]" 2>nul
if %errorlevel% neq 0 echo    ❌ Trades API 응답 실패

echo.
echo ========================================
echo 📂 로그 파일 체크
echo ========================================
echo.

if exist logs\signal_engine.log (
    echo ✅ Signal Engine 로그: logs\signal_engine.log
    echo    마지막 10줄:
    powershell -Command "Get-Content logs\signal_engine.log -Tail 10"
) else (
    echo ❌ Signal Engine 로그 없음
)

echo.
if exist logs\execution_engine.log (
    echo ✅ Execution Engine 로그: logs\execution_engine.log
    echo    마지막 10줄:
    powershell -Command "Get-Content logs\execution_engine.log -Tail 10"
) else (
    echo ❌ Execution Engine 로그 없음
)

echo.
echo ========================================
echo ✅ 헬스 체크 완료
echo ========================================
echo.
pause
