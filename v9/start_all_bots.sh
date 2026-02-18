#!/bin/bash
################################################################################
#  UPBIT BOT v9 + IMEI v3.0 - 전체 시스템 시작 스크립트 (Linux/Mac)
################################################################################
#  이 스크립트는 모든 봇을 한번에 시작합니다:
#  1. Signal Engine (WebSocket Emitter) - 신호 생성 엔진
#  2. Execution Engine (WebSocket Receiver) - 실행 엔진
#  3. Dashboard (Flask App) - 대시보드 (port 5000)
#  4. IMEI Main App (Flask App) - IMEI 앱 (port 5001)
################################################################################

echo ""
echo "========================================================================"
echo "  UPBIT BOT v9 + IMEI v3.0 - Starting All Services"
echo "========================================================================"
echo ""

# 스크립트 디렉토리로 이동
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Current Directory: $PWD"
echo ""

# Python 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3이 설치되어 있지 않습니다."
    echo "Python 3.8 이상을 설치하세요."
    exit 1
fi

echo "[OK] Python 설치 확인됨"
python3 --version
echo ""

# .env 파일 존재 확인
if [ ! -f ".env" ]; then
    echo "[WARNING] .env 파일이 없습니다."
    echo ".env.example을 복사하여 .env를 만들고 API 키를 설정하세요."
    echo ""
    read -p "계속하려면 Enter를 누르세요..."
fi

# 로그 디렉토리 생성
mkdir -p logs
echo "[OK] 로그 디렉토리 준비됨: logs/"
echo ""

# PID 파일 디렉토리
mkdir -p pids
echo "[OK] PID 디렉토리 준비됨: pids/"
echo ""

echo "========================================================================"
echo "  Starting Services..."
echo "========================================================================"
echo ""

# 1. Signal Engine (WebSocket Emitter) - 백그라운드 실행
echo "[1/4] Starting Signal Engine (WebSocket Emitter)..."
nohup python3 signal_engine/websocket_emitter.py > logs/signal_engine.log 2>&1 &
echo $! > pids/signal_engine.pid
sleep 2
echo "      신호 생성 엔진이 시작되었습니다. (PID: $(cat pids/signal_engine.pid))"
echo ""

# 2. Execution Engine (WebSocket Receiver) - 백그라운드 실행
echo "[2/4] Starting Execution Engine (WebSocket Receiver)..."
nohup python3 execution_engine/websocket_receiver.py > logs/execution_engine.log 2>&1 &
echo $! > pids/execution_engine.pid
sleep 2
echo "      실행 엔진이 시작되었습니다. (PID: $(cat pids/execution_engine.pid))"
echo ""

# 3. Dashboard (Flask App) - port 5000 - 백그라운드 실행
echo "[3/4] Starting Dashboard (Flask App - port 5000)..."
nohup python3 dashboard/standalone_dashboard.py > logs/dashboard.log 2>&1 &
echo $! > pids/dashboard.pid
sleep 2
echo "      대시보드가 시작되었습니다. (PID: $(cat pids/dashboard.pid))"
echo "      URL: http://localhost:5000"
echo ""

# 4. IMEI Main App (Flask App) - port 5001 - 백그라운드 실행
echo "[4/4] Starting IMEI Main App (Flask App - port 5001)..."
nohup python3 imei_system/main_app.py > logs/imei_app.log 2>&1 &
echo $! > pids/imei_app.pid
sleep 2
echo "      IMEI 앱이 시작되었습니다. (PID: $(cat pids/imei_app.pid))"
echo "      URL: http://localhost:5001"
echo ""

echo "========================================================================"
echo "  All Services Started Successfully!"
echo "========================================================================"
echo ""
echo "  실행 중인 서비스:"
echo "   1. Signal Engine        - PID: $(cat pids/signal_engine.pid)"
echo "   2. Execution Engine     - PID: $(cat pids/execution_engine.pid)"
echo "   3. Dashboard            - PID: $(cat pids/dashboard.pid) (http://localhost:5000)"
echo "   4. IMEI Main App        - PID: $(cat pids/imei_app.pid) (http://localhost:5001)"
echo ""
echo "  로그 파일:"
echo "   - logs/signal_engine.log"
echo "   - logs/execution_engine.log"
echo "   - logs/dashboard.log"
echo "   - logs/imei_app.log"
echo ""
echo "  로그 실시간 보기:"
echo "   tail -f logs/signal_engine.log"
echo "   tail -f logs/execution_engine.log"
echo "   tail -f logs/dashboard.log"
echo "   tail -f logs/imei_app.log"
echo ""
echo "  종료하려면:"
echo "   ./stop_all_bots.sh"
echo ""
echo "  브라우저에서 대시보드에 접속하세요:"
echo "   http://localhost:5000"
echo ""
echo "========================================================================"
echo ""
