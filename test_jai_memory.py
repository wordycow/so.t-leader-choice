#!/usr/bin/env python3
"""
자이 기억 시스템 테스트
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

# 1️⃣ 로그인
print("="*60)
print("🔐 1단계: 로그인 테스트")
print("="*60)

response = session.post(f"{BASE_URL}/api/login", json={
    "username": "wordycow"
})

if response.status_code == 200 and response.json().get('success'):
    print("✅ 로그인 성공!")
    user_data = response.json()
    print(f"   user_id: {user_data['user_id']}")
    print(f"   username: {user_data['username']}")
else:
    print(f"❌ 로그인 실패: {response.text}")
    exit(1)

# 2️⃣ 이름 알려주기
print("\n" + "="*60)
print("👤 2단계: 이름 알려주기")
print("="*60)

test_messages = [
    "안녕! 나는 철수야",
    "나는 28살이야",
    "직업은 개발자로 일하고 있어",
    "너 이름이 뭐야?",
]

for msg in test_messages:
    print(f"\n💬 사용자: {msg}")
    
    response = session.post(
        f"{BASE_URL}/api/ai-chat",
        json={"message": msg}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"💜 자이: {data.get('reply', '')}")
        if data.get('learned_info'):
            print(f"📚 학습 완료: {data['learned_info']}")
    else:
        print(f"❌ 오류: {response.status_code} - {response.text[:200]}")

# 3️⃣ 재접속 후 기억 확인
print("\n" + "="*60)
print("🔄 3단계: 기억 확인")
print("="*60)

test_messages_2 = [
    "내 이름 기억해?",
    "내가 몇 살이지?",
    "내 직업 알아?",
]

for msg in test_messages_2:
    print(f"\n💬 사용자: {msg}")
    
    response = session.post(
        f"{BASE_URL}/api/ai-chat",
        json={"message": msg}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"💜 자이: {data.get('reply', '')}")
    else:
        print(f"❌ 오류: {response.status_code}")

print("\n" + "="*60)
print("✅ 테스트 완료!")
print("="*60)
