#!/usr/bin/env python3
"""
🤖 자동 학습 스크립트
테스터들이 노가다로 대화 데이터 축적
"""

import random
import time
import requests
from conversation_templates import QUESTIONS

# 설정
BASE_URL = "http://localhost:5000"
DELAY_SECONDS = 3  # 질문 간 대기 시간

def login():
    """로그인 세션 생성"""
    session = requests.Session()
    
    response = session.post(f"{BASE_URL}/api/login", json={
        'username': 'wordycow',
        'password': '1234'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ 로그인 성공!")
            return session
        else:
            print(f"❌ 로그인 실패: {data.get('message')}")
            return None
    else:
        print(f"❌ 로그인 실패: HTTP {response.status_code}")
        return None

def ask_question(session, question):
    """이메이에게 질문"""
    try:
        response = session.post(
            f"{BASE_URL}/api/ai-chat",
            json={'message': question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('reply', '(답변 없음)')
            else:
                return f"❌ 오류: {data.get('message', '알 수 없음')}"
        else:
            return f"❌ HTTP {response.status_code}"
            
    except Exception as e:
        return f"❌ 예외: {e}"

def auto_conversation(num_questions=100, category=None):
    """
    자동 대화 생성
    
    Args:
        num_questions: 질문 개수
        category: 특정 카테고리 집중 (None이면 랜덤)
    """
    print("="*60)
    print("🤖 자동 학습 시작")
    print("="*60)
    
    # 로그인
    session = login()
    if not session:
        return
    
    # 질문 선택
    if category and category in QUESTIONS:
        questions = QUESTIONS[category]
        print(f"📌 카테고리: {category} ({len(questions)}개 질문)")
    else:
        questions = []
        for cat_questions in QUESTIONS.values():
            questions.extend(cat_questions)
        print(f"📌 모든 카테고리 ({len(questions)}개 질문)")
    
    # 랜덤 셔플
    random.shuffle(questions)
    
    # 대화 시작
    success_count = 0
    fail_count = 0
    
    for i, question in enumerate(questions[:num_questions], 1):
        print(f"\n[{i}/{num_questions}] Q: {question}")
        
        answer = ask_question(session, question)
        
        if answer.startswith("❌"):
            fail_count += 1
            print(f"         ❌ 실패")
        else:
            success_count += 1
            # 답변 앞 50자만 출력
            preview = answer[:50] + "..." if len(answer) > 50 else answer
            print(f"         A: {preview}")
        
        # 진행률
        progress = (i / num_questions) * 100
        print(f"         진행률: {progress:.1f}% (성공: {success_count}, 실패: {fail_count})")
        
        # 대기
        if i < num_questions:
            time.sleep(DELAY_SECONDS)
    
    # 결과 요약
    print("\n" + "="*60)
    print("✅ 학습 완료!")
    print("="*60)
    print(f"📊 통계:")
    print(f"  - 총 질문: {num_questions}")
    print(f"  - 성공: {success_count}")
    print(f"  - 실패: {fail_count}")
    print(f"  - 성공률: {(success_count/num_questions)*100:.1f}%")
    print("="*60)

def test_single_question():
    """단일 질문 테스트"""
    session = login()
    if not session:
        return
    
    question = "안녕 이메이!"
    print(f"\n질문: {question}")
    answer = ask_question(session, question)
    print(f"답변: {answer}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # 테스트 모드
            test_single_question()
        elif sys.argv[1] in QUESTIONS:
            # 특정 카테고리만
            category = sys.argv[1]
            num = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            auto_conversation(num, category)
        else:
            print(f"❌ 알 수 없는 카테고리: {sys.argv[1]}")
            print(f"✅ 사용 가능: {', '.join(QUESTIONS.keys())}")
    else:
        # 전체 100개
        auto_conversation(100)
