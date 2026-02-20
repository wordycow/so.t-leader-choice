# -*- coding: utf-8 -*-
"""
Emay API 서버
Flask 기반 REST API 서버 (포트: 5001)
감정 기반 이미지 응답 포함
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import sys

# Emay 모듈 임포트
sys.path.append(os.path.dirname(__file__))
from emay_brain import EmayBrain
from emotion_mapper import detect_emotion, get_emotion_image_path

app = Flask(__name__)
CORS(app)  # CORS 활성화

# Emay 인스턴스 생성
emay = EmayBrain()

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

if __name__ == '__main__':
    print("=" * 50)
    print("🌸 이메이 API 서버 시작")
    print("=" * 50)
    print(f"📍 주소: http://localhost:5001")
    print(f"🔗 엔드포인트:")
    print(f"   - POST /chat : 채팅")
    print(f"   - GET  /image/<emotion> : 감정 이미지")
    print(f"   - GET  /introduce : 자기소개")
    print(f"   - GET  /emotions : 감정 목록")
    print(f"   - GET  /health : 헬스체크")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
