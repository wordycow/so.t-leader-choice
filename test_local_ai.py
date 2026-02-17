#!/usr/bin/env python3
"""
🧪 로컬 AI 연결 테스트 스크립트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

노트북 Ollama가 제대로 연결되었는지 테스트!
"""

import requests
import json
import time
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 설정 (노트북 IP 주소 입력!)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OLLAMA_URL = "https://infinite-keno-casinos-constantly.trycloudflare.com"  # Cloudflare Tunnel
MODEL = "qwen2.5:7b"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 테스트 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def print_header(text):
    """헤더 출력"""
    print("\n" + "━" * 60)
    print(f"  {text}")
    print("━" * 60)

def test_connection():
    """1. 연결 테스트"""
    print_header("1️⃣ Ollama 서버 연결 테스트")
    
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ 연결 성공!")
            print(f"   URL: {OLLAMA_URL}")
            
            data = response.json()
            models = data.get('models', [])
            
            print(f"\n📚 사용 가능한 모델 ({len(models)}개):")
            for model in models:
                print(f"   - {model['name']} ({model['size'] / 1e9:.1f}GB)")
            
            return True
        else:
            print(f"❌ 연결 실패! 상태 코드: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"❌ 연결 실패! Ollama 서버가 실행 중인지 확인하세요.")
        print(f"\n💡 해결 방법:")
        print(f"   1. 노트북에서: ollama serve")
        print(f"   2. IP 주소 확인: ipconfig (Windows) or ifconfig (Mac/Linux)")
        print(f"   3. 방화벽 포트 11434 열기")
        return False
    
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_model():
    """2. 모델 테스트"""
    print_header(f"2️⃣ AI 모델 테스트 ({MODEL})")
    
    prompt = "안녕? 간단히 자기소개해줘! (2문장)"
    
    print(f"📝 질문: {prompt}")
    print(f"\n⏳ AI 응답 생성 중...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                'model': MODEL,
                'prompt': prompt,
                'stream': False
            },
            timeout=60
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', '')
            
            print(f"\n✅ 응답 받음! (소요 시간: {duration:.2f}초)")
            print(f"\n💬 AI 답변:")
            print(f"   {answer}")
            
            return True
        else:
            print(f"❌ 모델 실행 실패! 상태 코드: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_ai_client():
    """3. AI 클라이언트 테스트"""
    print_header("3️⃣ AI 클라이언트 통합 테스트")
    
    try:
        import sys
        sys.path.insert(0, '/home/user/webapp')
        
        from ai_client import ai_client
        
        print("✅ ai_client 모듈 import 성공!")
        
        # 건강 체크
        print("\n📊 건강 체크...")
        status = ai_client.health_check()
        
        print(f"\n상태: {status['status']}")
        print(f"백엔드: {status['backend']}")
        
        if status['status'] == 'online':
            print(f"URL: {status.get('url', 'N/A')}")
            print(f"모델: {', '.join(status.get('models', []))}")
            print(f"비용: {status.get('cost', 'N/A')}")
        else:
            print(f"오류: {status.get('error', 'Unknown')}")
            return False
        
        # 대화 테스트
        print("\n💬 대화 테스트...")
        messages = [
            {
                'role': 'system',
                'content': '당신은 자이, 친근한 AI입니다.'
            },
            {
                'role': 'user',
                'content': 'BTC 지금 매수하면 어떨까?'
            }
        ]
        
        print("   질문: BTC 지금 매수하면 어떨까?")
        print("\n   ⏳ 응답 생성 중...")
        
        result = ai_client.chat(messages, temperature=0.7, max_tokens=200)
        
        print(f"\n   ✅ 응답 완료!")
        print(f"   백엔드: {result['backend']}")
        print(f"   모델: {result['model']}")
        print(f"   비용: ${result['cost']:.4f}")
        print(f"   소요 시간: {result.get('duration', 0):.2f}초")
        print(f"\n   💬 AI 답변:")
        print(f"   {result['content'][:200]}...")
        
        return True
    
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🧪 로컬 AI (Ollama) 연결 테스트")
    print("="*60)
    print(f"\n🎯 테스트 대상:")
    print(f"   Ollama URL: {OLLAMA_URL}")
    print(f"   모델: {MODEL}")
    print(f"\n⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        '연결 테스트': test_connection(),
        '모델 테스트': False,
        'AI 클라이언트 테스트': False
    }
    
    if results['연결 테스트']:
        results['모델 테스트'] = test_model()
        results['AI 클라이언트 테스트'] = test_ai_client()
    
    # 결과 요약
    print_header("📊 테스트 결과 요약")
    
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "="*60)
        print("  🎉 모든 테스트 통과!")
        print("="*60)
        print("\n✅ 로컬 AI가 정상적으로 연결되었습니다!")
        print("\n🚀 다음 단계:")
        print("   1. Flask 서버 실행: python upbit-smart-bot-v8.0-ULTIMATE.py")
        print("   2. 웹 브라우저: http://localhost:5000/ai-streamer")
        print("   3. 자이와 대화 → 로컬 AI 답변! (비용 $0)")
    else:
        print("\n" + "="*60)
        print("  ⚠️ 일부 테스트 실패")
        print("="*60)
        print("\n💡 해결 방법:")
        print("   1. 노트북에서 Ollama 실행: ollama serve")
        print("   2. 방화벽 포트 11434 열기")
        print("   3. IP 주소 확인: ipconfig (Windows)")
        print("   4. 노트북과 같은 네트워크인지 확인")
    
    print(f"\n⏰ 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
