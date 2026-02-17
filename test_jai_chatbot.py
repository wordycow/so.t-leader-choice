#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def login():
    """로그인"""
    response = requests.post(f"{BASE_URL}/login", data={
        "username": "wordycow",
        "password": "1234"
    })
    print("✅ 로그인:", response.json())
    return response.cookies

def chat_with_jai(cookies, message):
    """자이와 대화"""
    response = requests.post(
        f"{BASE_URL}/api/ai-chat",
        json={"message": message},
        cookies=cookies
    )
    result = response.json()
    print(f"\n💬 사용자: {message}")
    print(f"💜 자이: {result.get('reply', '응답 없음')}\n")
    return result

def main():
    # 1. 로그인
    cookies = login()
    
    # 2. 다양한 대화 테스트
    print("\n" + "="*80)
    print("💜 자이(JAI) 챗봇 테스트")
    print("="*80)
    
    # 인사
    chat_with_jai(cookies, "안녕하세요!")
    
    # 보유 코인 확인
    chat_with_jai(cookies, "지금 보유 코인 뭐야?")
    
    # 추천 요청
    chat_with_jai(cookies, "지금 뭐 사야 돼?")
    
    # 매도 타이밍
    chat_with_jai(cookies, "언제 팔아야 해?")
    
    # 일반 질문
    chat_with_jai(cookies, "요즘 시장 어때?")

if __name__ == "__main__":
    main()
