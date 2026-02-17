#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 이메이 학습 실험
실시간으로 이메이가 대화를 통해 학습하는지 테스트
"""

import requests
import json
import time
from datetime import datetime

# 테스트 URL
BASE_URL = "https://5000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai"
LOGIN_URL = f"{BASE_URL}/login"
CHAT_URL = f"{BASE_URL}/api/ai-chat"

# 로그인 정보
USERNAME = "wordycow"
PASSWORD = "1234"

# 테스트 질문 (10개)
TEST_QUESTIONS = [
    # 1. 코인 관련
    {"question": "비트코인 반감기가 정확히 뭐야?", "category": "coin", "expected_persona": "teacher"},
    
    # 2. 전략 관련
    {"question": "RSI 30 이하면 무조건 사야 해?", "category": "strategy", "expected_persona": "mentor"},
    
    # 3. 감정 관련
    {"question": "오늘 10% 손실 나서 너무 속상해...", "category": "emotion", "expected_persona": "friend"},
    
    # 4. 성공 관련
    {"question": "와! 오늘 30% 수익 났어!", "category": "success", "expected_persona": "cheerleader"},
    
    # 5. 위험 관련
    {"question": "대출받아서 비트코인 올인하려고", "category": "danger", "expected_persona": "guardian"},
    
    # 6. 분석 관련
    {"question": "이더리움 현재 차트 분석 부탁해", "category": "analysis", "expected_persona": "analyst"},
    
    # 7. 일반 질문
    {"question": "코인 투자 처음인데 뭐부터 해야 돼?", "category": "general", "expected_persona": "teacher"},
    
    # 8. 전략 심화
    {"question": "MACD와 RSI를 같이 보는 방법은?", "category": "strategy", "expected_persona": "teacher"},
    
    # 9. 감정 지지
    {"question": "계속 손실만 나는데 투자 그만둘까...", "category": "emotion", "expected_persona": "friend"},
    
    # 10. 유머
    {"question": "ㅋㅋㅋ 코인 하니까 머리 아파", "category": "humor", "expected_persona": "comedian"}
]

class EmeiLearningExperiment:
    """이메이 학습 실험 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.results = []
    
    def login(self):
        """로그인 (세션 쿠키 설정)"""
        print("🔐 로그인 설정 중...")
        
        try:
            # Flask 세션 쿠키를 직접 설정하는 대신
            # 먼저 메인 페이지 접근해서 세션 생성
            response = self.session.get(BASE_URL, timeout=10)
            
            # API 테스트 (로그인 없이도 작동하는지 확인)
            test_response = self.session.post(
                CHAT_URL,
                json={'message': '안녕'},
                timeout=10
            )
            
            if test_response.status_code == 200:
                data = test_response.json()
                if data.get('success') or 'message' in data:
                    print("✅ 세션 준비 완료!")
                    return True
            
            print("⚠️ 로그인 필요할 수 있음, 일단 진행...")
            return True  # 일단 진행
            
        except Exception as e:
            print(f"❌ 세션 오류: {e}")
            return False
    
    def ask_emei(self, question: str, round_num: int = 1):
        """이메이에게 질문"""
        print(f"\n{'='*60}")
        print(f"🗣️  질문 #{round_num}: {question}")
        
        start_time = time.time()
        
        try:
            response = self.session.post(
                CHAT_URL,
                json={'message': question},
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    reply = data.get('reply', '')
                    learned = data.get('learned', False)
                    persona = data.get('persona', 'unknown')
                    persona_name = data.get('persona_name', 'Unknown')
                    emotion = data.get('emotion', 'neutral')
                    
                    print(f"🎭 페르소나: {persona_name} ({persona})")
                    print(f"😊 감정: {emotion}")
                    print(f"📚 학습: {'✅ 새로 학습!' if learned else '❌ 기존 지식'}")
                    print(f"⏱️  응답 시간: {duration:.2f}초")
                    print(f"💬 답변: {reply[:200]}{'...' if len(reply) > 200 else ''}")
                    
                    return {
                        'success': True,
                        'reply': reply,
                        'learned': learned,
                        'persona': persona,
                        'persona_name': persona_name,
                        'emotion': emotion,
                        'duration': duration,
                        'question': question,
                        'round': round_num
                    }
                else:
                    print(f"❌ 응답 실패: {data.get('message', 'Unknown error')}")
                    return {'success': False, 'error': data.get('message')}
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}"}
        
        except Exception as e:
            print(f"❌ 요청 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_learning(self, question_data: dict):
        """학습 테스트 (같은 질문 2번)"""
        question = question_data['question']
        
        print(f"\n{'#'*60}")
        print(f"🧪 실험: {question_data['category']} 카테고리")
        print(f"#{'#'*60}")
        
        # 1차: 처음 질문 (학습 안 됨)
        result1 = self.ask_emei(question, round_num=1)
        time.sleep(2)  # 서버 부하 방지
        
        # 2차: 같은 질문 (학습됨 or 기존 지식)
        result2 = self.ask_emei(question, round_num=2)
        
        # 결과 비교
        if result1['success'] and result2['success']:
            learned_first = result1.get('learned', False)
            learned_second = result2.get('learned', False)
            
            print(f"\n📊 학습 결과:")
            print(f"  1차 학습: {'✅' if learned_first else '❌'}")
            print(f"  2차 학습: {'✅' if learned_second else '❌'}")
            
            if learned_first and not learned_second:
                print(f"  ✅ 학습 성공! (1차 학습 → 2차 재사용)")
            elif not learned_first and not learned_second:
                print(f"  ℹ️  기존 지식 사용")
            
            # 응답 시간 비교
            if result2['duration'] < result1['duration']:
                speedup = (result1['duration'] - result2['duration']) / result1['duration'] * 100
                print(f"  ⚡ 응답 속도 {speedup:.1f}% 향상!")
        
        self.results.append({
            'question': question,
            'category': question_data['category'],
            'expected_persona': question_data['expected_persona'],
            'actual_persona': result1.get('persona', 'unknown'),
            'learned_first': result1.get('learned', False),
            'learned_second': result2.get('learned', False),
            'duration_first': result1.get('duration', 0),
            'duration_second': result2.get('duration', 0)
        })
        
        time.sleep(3)  # 다음 질문 전 대기
    
    def run_experiment(self):
        """전체 실험 실행"""
        print("\n" + "="*60)
        print("🧪 이메이 학습 실험 시작")
        print("="*60)
        
        # 로그인
        if not self.login():
            print("❌ 로그인 실패로 실험 중단")
            return
        
        # 각 질문 테스트
        for i, question_data in enumerate(TEST_QUESTIONS, 1):
            print(f"\n\n{'='*60}")
            print(f"테스트 {i}/{len(TEST_QUESTIONS)}")
            print(f"{'='*60}")
            
            self.test_learning(question_data)
        
        # 최종 결과
        self.print_summary()
    
    def print_summary(self):
        """최종 요약"""
        print("\n\n" + "="*60)
        print("📊 실험 결과 요약")
        print("="*60)
        
        total = len(self.results)
        learned_count = sum(1 for r in self.results if r['learned_first'])
        persona_correct = sum(1 for r in self.results if r['expected_persona'] == r['actual_persona'])
        
        avg_duration_first = sum(r['duration_first'] for r in self.results) / total
        avg_duration_second = sum(r['duration_second'] for r in self.results) / total
        
        print(f"\n총 질문: {total}개")
        print(f"학습 성공: {learned_count}개 ({learned_count/total*100:.1f}%)")
        print(f"페르소나 정확도: {persona_correct}개 ({persona_correct/total*100:.1f}%)")
        print(f"\n평균 응답 시간:")
        print(f"  1차: {avg_duration_first:.2f}초")
        print(f"  2차: {avg_duration_second:.2f}초")
        print(f"  향상: {(avg_duration_first - avg_duration_second) / avg_duration_first * 100:.1f}%")
        
        print(f"\n📋 세부 결과:")
        for i, r in enumerate(self.results, 1):
            status = "✅ 학습" if r['learned_first'] else "❌ 실패"
            persona_match = "✅" if r['expected_persona'] == r['actual_persona'] else "❌"
            print(f"  {i}. {r['category']:10s} - {status} | 페르소나 {persona_match} ({r['actual_persona']})")
        
        print("\n" + "="*60)
        print("✅ 실험 완료!")
        print("="*60)


if __name__ == "__main__":
    experiment = EmeiLearningExperiment()
    experiment.run_experiment()
