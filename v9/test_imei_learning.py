#!/usr/bin/env python3
"""
Test IMEI Learning - 실제 시나리오로 학습 테스트
"""

import requests
import json
from datetime import datetime

IMEI_URL = "http://localhost:5001"

def test_chat(message, user_id="test_user"):
    """Test IMEI chat"""
    response = requests.post(
        f"{IMEI_URL}/api/imei/chat",
        json={"message": message, "user_id": user_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n{'='*60}")
        print(f"USER: {message}")
        print(f"IMEI: {data.get('response', 'N/A')}")
        print(f"Persona: {data.get('primary_persona', 'N/A')}")
        print(f"Memory Triggered: {data.get('memory_triggered', False)}")
        if data.get('memory_card'):
            print(f"Memory ID: {data['memory_card'].get('memory_id')}")
        print(f"{'='*60}")
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        return None

def test_memories(user_id="test_user"):
    """Get user memories"""
    response = requests.get(
        f"{IMEI_URL}/api/imei/memories",
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        memories = response.json().get('memories', [])
        print(f"\n📚 User Memories ({len(memories)} total):")
        for mem in memories:
            print(f"  - {mem.get('summary')} [{mem.get('memory_id')}]")
        return memories
    else:
        print(f"❌ Error: {response.status_code}")
        return []

if __name__ == "__main__":
    print("🤖 IMEI Learning Test - Starting...")
    
    # Test 1: 일반 대화
    test_chat("안녕? 처음 만나는데 반가워!")
    
    # Test 2: 트레이딩 분석 요청
    test_chat("지금 BTC 차트 어떻게 보여?")
    
    # Test 3: 학습 트리거 - 매매 규칙
    test_chat("학습해: RSI 30 이하면 매수, 70 이상이면 매도하는 게 좋대")
    
    # Test 4: 감정적 지지
    test_chat("오늘 거래에서 -50만원 손실을 봤어... 너무 힘들다")
    
    # Test 5: 학습 트리거 - 전략
    test_chat("기억해줘: ULTRA_SCALP_V2_1은 단기 매매용, 1-5분 내 청산")
    
    # Test 6: 메모리 회상
    test_chat("RSI 관련해서 뭐 배운 거 있지?")
    
    # Test 7: 저장된 메모리 확인
    test_memories("test_user")
    
    print("\n✅ IMEI Learning Test - Complete!")
