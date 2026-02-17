#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 이메이 학습 실험 (로컬 버전)
Flask 서버를 거치지 않고 직접 Learning Brain 테스트
"""

from emei_learning_brain import EmeiLearningBrain
from emei_persona_system import PersonaSystem
import time

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


class LocalLearningExperiment:
    """로컬 학습 실험"""
    
    def __init__(self):
        self.brain = EmeiLearningBrain()
        self.persona_system = PersonaSystem()
        self.results = []
    
    def test_question(self, question_data: dict):
        """질문 테스트"""
        question = question_data['question']
        
        print(f"\n{'='*70}")
        print(f"🧪 실험: {question_data['category']} 카테고리")
        print(f"❓ 질문: {question}")
        print(f"{'='*70}")
        
        # 페르소나 감지
        detected_persona = self.persona_system.detect_persona(question)
        persona_info = self.persona_system.get_persona_info(detected_persona)
        
        print(f"🎭 감지된 페르소나: {persona_info['name']} ({detected_persona.value})")
        print(f"📝 예상 페르소나: {question_data['expected_persona']}")
        
        persona_match = detected_persona.value == question_data['expected_persona']
        print(f"✅ 페르소나 매칭: {'성공' if persona_match else '실패'}")
        
        # 1차: 학습된 지식 확인
        print(f"\n--- 1차 시도 (학습 전) ---")
        start_time = time.time()
        learned_answer_1 = self.brain.get_learned_answer(question)
        duration_1 = time.time() - start_time
        
        if learned_answer_1:
            print(f"📚 학습된 답변 발견! (응답 시간: {duration_1:.4f}초)")
            print(f"💬 답변: {learned_answer_1[:150]}...")
            already_learned = True
        else:
            print(f"❌ 학습된 답변 없음 (응답 시간: {duration_1:.4f}초)")
            print(f"🔍 웹 검색 시도...")
            
            # 웹 검색 + 학습
            start_learn = time.time()
            web_answer = self.brain.learn_from_web(question)
            learn_duration = time.time() - start_learn
            
            if web_answer:
                print(f"✅ 웹 학습 성공! (학습 시간: {learn_duration:.4f}초)")
                print(f"💬 답변: {web_answer[:150]}...")
                already_learned = False
            else:
                print(f"❌ 웹 학습 실패")
                already_learned = False
                web_answer = None
        
        # 2차: 같은 질문 반복 (학습 확인)
        print(f"\n--- 2차 시도 (학습 후) ---")
        time.sleep(1)  # 잠시 대기
        
        start_time_2 = time.time()
        learned_answer_2 = self.brain.get_learned_answer(question)
        duration_2 = time.time() - start_time_2
        
        if learned_answer_2:
            print(f"📚 학습된 답변 발견! (응답 시간: {duration_2:.4f}초)")
            print(f"💬 답변: {learned_answer_2[:150]}...")
            
            # 속도 비교
            if not already_learned:
                speedup = ((learn_duration + duration_1) - duration_2) / (learn_duration + duration_1) * 100
                print(f"⚡ 응답 속도 {speedup:.1f}% 향상!")
                print(f"   (1차: {learn_duration + duration_1:.4f}초 → 2차: {duration_2:.4f}초)")
            
            learning_success = True
        else:
            print(f"❌ 학습된 답변 없음")
            learning_success = False
        
        # 결과 저장
        self.results.append({
            'question': question,
            'category': question_data['category'],
            'expected_persona': question_data['expected_persona'],
            'actual_persona': detected_persona.value,
            'persona_match': persona_match,
            'already_learned': already_learned,
            'learning_success': learning_success,
            'duration_first': duration_1 + (learn_duration if not already_learned and web_answer else 0),
            'duration_second': duration_2
        })
    
    def run_experiment(self):
        """전체 실험 실행"""
        print("\n" + "="*70)
        print("🧪 이메이 로컬 학습 실험 시작")
        print("="*70)
        
        # 초기 상태 확인
        stats_before = self.brain.get_learning_stats()
        print(f"\n📊 실험 전 학습 상태:")
        print(f"  총 학습: {stats_before['total_learned']}개")
        print(f"  모르는 질문: {stats_before['unknown_count']}개")
        
        # 각 질문 테스트
        for i, question_data in enumerate(TEST_QUESTIONS, 1):
            print(f"\n\n{'#'*70}")
            print(f"테스트 {i}/{len(TEST_QUESTIONS)}")
            print(f"{'#'*70}")
            
            self.test_question(question_data)
            
            time.sleep(2)  # 다음 질문 전 대기
        
        # 최종 상태 확인
        stats_after = self.brain.get_learning_stats()
        
        # 최종 요약
        self.print_summary(stats_before, stats_after)
    
    def print_summary(self, stats_before: dict, stats_after: dict):
        """최종 요약"""
        print("\n\n" + "="*70)
        print("📊 실험 결과 요약")
        print("="*70)
        
        total = len(self.results)
        persona_correct = sum(1 for r in self.results if r['persona_match'])
        learning_success = sum(1 for r in self.results if r['learning_success'])
        already_learned = sum(1 for r in self.results if r['already_learned'])
        
        print(f"\n총 질문: {total}개")
        print(f"페르소나 정확도: {persona_correct}개 ({persona_correct/total*100:.1f}%)")
        print(f"학습 성공: {learning_success}개 ({learning_success/total*100:.1f}%)")
        print(f"이미 학습됨: {already_learned}개")
        print(f"새로 학습: {learning_success - already_learned}개")
        
        print(f"\n📊 학습 통계 변화:")
        print(f"  실험 전: {stats_before['total_learned']}개")
        print(f"  실험 후: {stats_after['total_learned']}개")
        print(f"  증가: +{stats_after['total_learned'] - stats_before['total_learned']}개")
        
        if stats_after['categories']:
            print(f"\n📚 카테고리별 학습:")
            for cat, count in stats_after['categories'].items():
                print(f"  {cat}: {count}개")
        
        if stats_after['top_knowledge']:
            print(f"\n🏆 가장 많이 사용된 지식 TOP 5:")
            for i, knowledge in enumerate(stats_after['top_knowledge'], 1):
                print(f"  {i}. {knowledge['question'][:50]}... (사용: {knowledge['usage']}회)")
        
        print(f"\n📋 세부 결과:")
        for i, r in enumerate(self.results, 1):
            persona_icon = "✅" if r['persona_match'] else "❌"
            learn_status = "✅ 학습 성공" if r['learning_success'] else "❌ 학습 실패"
            speedup = (r['duration_first'] - r['duration_second']) / r['duration_first'] * 100 if r['duration_first'] > 0 else 0
            
            print(f"  {i}. {r['category']:10s} - {learn_status} | 페르소나 {persona_icon} ({r['actual_persona']}) | 속도 {speedup:+.1f}%")
        
        print("\n" + "="*70)
        print("✅ 실험 완료!")
        print("="*70)


if __name__ == "__main__":
    experiment = LocalLearningExperiment()
    experiment.run_experiment()
