# -*- coding: utf-8 -*-
"""
Lee May Training Center - Main API Server
모든 기능을 제공하는 메인 API
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.append(str(Path(__file__).parent.parent))

from bots.bot_manager import BotManager

app = Flask(__name__, static_folder='../web/static', template_folder='../web')
CORS(app)

# Bot Manager 초기화
bot_manager = BotManager()

# ============================================================
# 대시보드
# ============================================================

@app.route('/')
def index():
    """메인 대시보드"""
    return send_from_directory('../web', 'dashboard.html')

# ============================================================
# 봇 제어 API
# ============================================================

@app.route('/api/bots/status', methods=['GET'])
def get_bots_status():
    """모든 봇 상태 조회"""
    return jsonify(bot_manager.get_status())

@app.route('/api/bots/<bot_name>/start', methods=['POST'])
def start_bot(bot_name):
    """봇 시작"""
    result = bot_manager.start_bot(bot_name)
    return jsonify(result)

@app.route('/api/bots/<bot_name>/stop', methods=['POST'])
def stop_bot(bot_name):
    """봇 중지"""
    result = bot_manager.stop_bot(bot_name)
    return jsonify(result)

@app.route('/api/bots/<bot_name>/restart', methods=['POST'])
def restart_bot(bot_name):
    """봇 재시작"""
    result = bot_manager.restart_bot(bot_name)
    return jsonify(result)

# ============================================================
# 능력치 API (임시 - 나중에 실제 계산)
# ============================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Lee May & Trading Bot 능력치"""
    # TODO: 실제 계산 로직 추가
    return jsonify({
        "leemay": {
            "emotion_expression": 85,
            "conversation_understanding": 72,
            "memory": 90,
            "humor": 45,
            "empathy": 68
        },
        "trading": {
            "technical_analysis": 65,
            "strategy": 72,
            "risk_management": 58,
            "market_understanding": 70
        }
    })

# ============================================================
# 시스템 정보 API
# ============================================================

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """시스템 리소스 정보"""
    import psutil
    
    return jsonify({
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    })

# ============================================================
# 학습 API
# ============================================================

@app.route('/api/learning/youtube', methods=['POST'])
def learn_youtube():
    """유튜브 학습 시작"""
    data = request.get_json()
    url = data.get('url')
    
    # TODO: 실제 학습 로직 추가
    return jsonify({
        "success": True,
        "message": f"유튜브 학습 시작: {url}"
    })

# ============================================================
# 채팅 API
# ============================================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Lee May 채팅"""
    data = request.get_json()
    message = data.get('message')
    
    # TODO: 실제 Ollama 연동
    return jsonify({
        "reply": f"Lee May: {message}에 대한 답변입니다!"
    })

# ============================================================
# 서버 실행
# ============================================================

if __name__ == '__main__':
    print("=" * 50)
    print("🤖 Lee May Training Center API Server")
    print("=" * 50)
    print("📍 http://localhost:7000")
    print("🌐 https://leemay.더유니크.com")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=7000, debug=True)
