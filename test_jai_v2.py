#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

BASE_URL = "https://5000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai"

def login():
    """로그인"""
    try:
        response = requests.post(f"{BASE_URL}/login", data={
            "username": "wordycow",
            "password": "1234"
        }, timeout=10)
        result = response.json()
        print("✅ 로그인 성공:", result)
        return response.cookies
    except Exception as e:
        print(f"❌ 로그인 실패: {e}")
        return None

def chat_with_jai(cookies, message):
    """자이와 대화"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai-chat",
            json={"message": message},
            cookies=cookies,
            timeout=15
        )
        result = response.json()
        print(f"\n💬 사용자: {message}")
        print(f"💜 자이: {result.get('reply', '응답 없음')}")
        print("-" * 80)
        return result
    except Exception as e:
        print(f"❌ 대화 실패: {e}")
        return None

def main():
    print("="*80)
    print("💜 자이(JAI) AI 스트리머 챗봇 테스트")
    print("="*80)
    
    # 1. 로그인
    cookies = login()
    if not cookies:
        return
    
    # 2. 다양한 대화 시나리오
    test_cases = [
        "안녕 자이! 처음 뵙는데 인사해줘",
        "지금 보유하고 있는 코인 뭐야?",
        "현재 수익률 어때?",
        "지금 뭐 사면 좋을까? 추천 좀",
        "언제 팔아야 할까?",
        "요즘 코인 시장 어떤 것 같아?",
    ]
    
    for message in test_cases:
        chat_with_jai(cookies, message)
        print()

if __name__ == "__main__":
    main()
