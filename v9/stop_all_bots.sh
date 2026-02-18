#!/bin/bash
################################################################################
#  UPBIT BOT v9 + IMEI v3.0 - 전체 시스템 종료 스크립트 (Linux/Mac)
################################################################################

echo ""
echo "========================================================================"
echo "  UPBIT BOT v9 + IMEI v3.0 - Stopping All Services"
echo "========================================================================"
echo ""

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# PID 파일이 있는지 확인
if [ ! -d "pids" ]; then
    echo "[WARNING] pids 디렉토리가 없습니다. 서비스가 실행 중이 아닐 수 있습니다."
    echo ""
fi

# 1. Signal Engine 종료
echo "[1/4] Stopping Signal Engine..."
if [ -f "pids/signal_engine.pid" ]; then
    PID=$(cat pids/signal_engine.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "      Signal Engine (PID: $PID) 종료됨"
    else
        echo "      Signal Engine이 실행 중이 아닙니다."
    fi
    rm -f pids/signal_engine.pid
else
    echo "      Signal Engine PID 파일이 없습니다."
fi
echo ""

# 2. Execution Engine 종료
echo "[2/4] Stopping Execution Engine..."
if [ -f "pids/execution_engine.pid" ]; then
    PID=$(cat pids/execution_engine.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "      Execution Engine (PID: $PID) 종료됨"
    else
        echo "      Execution Engine이 실행 중이 아닙니다."
    fi
    rm -f pids/execution_engine.pid
else
    echo "      Execution Engine PID 파일이 없습니다."
fi
echo ""

# 3. Dashboard 종료
echo "[3/4] Stopping Dashboard..."
if [ -f "pids/dashboard.pid" ]; then
    PID=$(cat pids/dashboard.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "      Dashboard (PID: $PID) 종료됨"
    else
        echo "      Dashboard가 실행 중이 아닙니다."
    fi
    rm -f pids/dashboard.pid
else
    echo "      Dashboard PID 파일이 없습니다."
fi
echo ""

# 4. IMEI Main App 종료
echo "[4/4] Stopping IMEI Main App..."
if [ -f "pids/imei_app.pid" ]; then
    PID=$(cat pids/imei_app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "      IMEI Main App (PID: $PID) 종료됨"
    else
        echo "      IMEI Main App이 실행 중이 아닙니다."
    fi
    rm -f pids/imei_app.pid
else
    echo "      IMEI Main App PID 파일이 없습니다."
fi
echo ""

# 포트로 남아있는 프로세스 정리
echo "Cleaning up any remaining Python processes on ports 5000 and 5001..."
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null
echo ""

echo "========================================================================"
echo "  All Services Stopped"
echo "========================================================================"
echo ""
