# -*- coding: utf-8 -*-
"""
Emay API 서버
Flask 기반 REST API 서버 (포트: 5001)
감정 기반 이미지 응답 포함
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import sys

# Emay 모듈 임포트
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), 'leemay', 'core'))

from leemay.core.emay_brain import EmayBrain
from emotion_mapper import detect_emotion, get_emotion_image_path

app = Flask(__name__, static_folder='web/static', template_folder='web')
CORS(app)  # CORS 활성화

# Emay 인스턴스 생성
emay = EmayBrain()

@app.route('/')
def index():
    """메인 대시보드"""
    return send_from_directory('web', 'dashboard.html')

@app.route('/health', methods=['GET'])
def health():
    """헬스체크 엔드포인트"""
    return jsonify({"status": "healthy", "message": "Emay API is running"}), 200

@app.route('/introduce', methods=['GET'])
def introduce():
    """이메이 자기소개"""
    intro = emay.introduce()
    return jsonify({"message": intro, "emotion": "neutral"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    """
    채팅 엔드포인트
    - 사용자 메시지를 받아 Emay 응답 생성
    - 감정 분석 및 이미지 경로 반환
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({"error": "메시지가 필요합니다"}), 400
        
        user_message = data['message']
        user_id = data.get('user_id', 'default_user')
        
        # Emay 응답 생성
        response = emay.chat(user_message, user_id)
        
        # 감정 감지
        emotion = detect_emotion(user_message)
        
        # 이미지 경로
        image_path = get_emotion_image_path(emotion)
        
        return jsonify({
            "response": response,
            "emotion": emotion,
            "image_url": f"/image/{emotion}"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/image/<emotion>', methods=['GET'])
def get_emotion_image(emotion):
    """
    감정별 이미지 파일 제공
    예: /image/happy → happy.png 반환
    """
    try:
        image_path = get_emotion_image_path(emotion)
        
        if not os.path.exists(image_path):
            # 이미지가 없으면 neutral 반환
            image_path = get_emotion_image_path("neutral")
        
        return send_file(image_path, mimetype='image/png')
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/emotions', methods=['GET'])
def list_emotions():
    """사용 가능한 모든 감정 목록 반환"""
    from emotion_mapper import EMOTION_KEYWORDS
    emotions = list(EMOTION_KEYWORDS.keys())
    return jsonify({"emotions": emotions, "count": len(emotions)}), 200

# ============================================================
# Training Center 전용 API
# ============================================================

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """시스템 리소스 정보"""
    try:
        import psutil
        return jsonify({
            "cpu": round(psutil.cpu_percent(interval=1), 1),
            "memory": round(psutil.virtual_memory().percent, 1),
            "disk": round(psutil.disk_usage('/').percent, 1)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bots/status', methods=['GET'])
def get_bots_status():
    """봇 상태 조회"""
    try:
        import psutil
        
        # API 서버 자신의 상태
        current_process = psutil.Process()
        
        # Ollama 터널 확인
        ollama_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'cloudflared' in proc.info['name'].lower():
                    ollama_running = True
                    break
            except:
                pass
        
        return jsonify({
            "leemay_api": {
                "running": True,
                "pid": current_process.pid,
                "cpu": round(current_process.cpu_percent(), 1),
                "memory": round(current_process.memory_percent(), 1),
                "uptime": int(psutil.boot_time())
            },
            "ollama_tunnel": {
                "running": ollama_running
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Lee May 능력치"""
    # TODO: 실제 계산 로직 추가
    return jsonify({
        "leemay": {
            "emotion_expression": 85,
            "conversation_understanding": 72,
            "memory": 90,
            "humor": 45,
            "empathy": 68
        }
    }), 200

@app.route('/api/learning/youtube', methods=['POST'])
def learn_youtube():
    """유튜브 학습 시작"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({"success": False, "error": "URL이 필요합니다"}), 400
        
        # TODO: 백그라운드로 학습 실행
        return jsonify({
            "success": True,
            "message": f"유튜브 학습 시작: {url}"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 Lee May Training Center API Server")
    print("=" * 60)
    print(f"📍 로컬: http://localhost:5001")
    print(f"🌐 외부: https://leemay.더유니크.com")
    print("=" * 60)
    print(f"🔗 주요 엔드포인트:")
    print(f"   - GET  / : Training Center 대시보드")
    print(f"   - POST /chat : Lee May 채팅")
    print(f"   - GET  /image/<emotion> : 감정 이미지")
    print(f"   - GET  /api/bots/status : 봇 상태")
    print(f"   - GET  /api/system/status : 시스템 상태")
    print(f"   - GET  /api/stats : 능력치")
    print(f"   - POST /api/learning/youtube : 유튜브 학습")
    print(f"   - GET  /health : 헬스체크")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
