#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def login():
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": "wordycow", "password": "1234"}
    )
    return response.cookies

def chat(cookies, message):
    response = requests.post(
        f"{BASE_URL}/api/ai-chat",
        json={"message": message},
        cookies=cookies
    )
    result = response.json()
    print(f"\n{'='*80}")
    print(f"💬 사용자: {message}")
    print(f"{'='*80}")
    print(f"💜 자이: {result.get('reply', '응답 없음')}")
    return result

def main():
    print("\n" + "="*80)
    print("💜 자이(JAI) AI 스트리머 - 종합 테스트")
    print("="*80)
    
    cookies = login()
    print("✅ 로그인 완료")
    
    # 테스트 시나리오
    scenarios = [
        ("처음 인사", "안녕 자이! 처음 뵙는데 인사해줘"),
        ("보유 코인 확인", "지금 보유하고 있는 코인 뭐야?"),
        ("수익률 확인", "현재 수익률 어때?"),
        ("매수 추천", "지금 뭐 사면 좋을까?"),
        ("매도 타이밍", "언제 팔아야 할까?"),
        ("시장 분석", "요즘 시장 어떤 것 같아?"),
        ("손실 위로", "돈 잃어서 속상해"),
    ]
    
    for title, message in scenarios:
        print(f"\n\n🧪 테스트: {title}")
        chat(cookies, message)
    
    print("\n" + "="*80)
    print("✅ 모든 테스트 완료!")
    print("="*80)

if __name__ == "__main__":
    main()
