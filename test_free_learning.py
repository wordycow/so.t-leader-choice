"""
🆓 무료 학습 시스템 테스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

100% 무료로 이메이 학습시키기!
"""

from free_learning_system import FreeLearningSystem
import time

def main():
    print("\n" + "="*60)
    print("🆓 100% 무료 학습 시스템 테스트")
    print("="*60)
    print("\n💰 비용: $0 (무료!)")
    print("🚀 속도: 빠름")
    print("📚 학습: 자동")
    print("")
    
    # 시스템 초기화
    system = FreeLearningSystem(db_path='free_learning_test.db')
    
    # 테스트 질문들
    questions = [
        "비트코인 지금 사도 돼?",
        "RSI 지표가 뭐야?",
        "손실이 나서 우울해...",
        "비트코인 지금 사도 돼?",  # 반복!
        "이더리움 추천해줘",
        "RSI 지표가 뭐야?",  # 반복!
        "스토캐스틱이 뭐야?",
        "비트코인 지금 사도 돼?",  # 또 반복!
    ]
    
    total_time = 0
    cache_hits = 0
    
    for i, question in enumerate(questions, 1):
        print(f"\n\n{'#'*60}")
        print(f"테스트 {i}/{len(questions)}")
        print(f"{'#'*60}")
        
        start = time.time()
        result = system.chat(question)
        duration = time.time() - start
        
        total_time += duration
        
        if result.get('cached'):
            cache_hits += 1
        
        time.sleep(0.5)  # 시연용 대기
    
    # 최종 통계
    stats = system.get_stats()
    
    print(f"\n\n{'='*60}")
    print("🎯 최종 결과")
    print(f"{'='*60}")
    print(f"총 질문: {len(questions)}회")
    print(f"학습된 질문: {stats['total_learned']}개")
    print(f"캐시 히트: {cache_hits}회 ({cache_hits/len(questions)*100:.1f}%)")
    print(f"총 비용: $0 (무료!) 💰")
    print(f"평균 응답 시간: {total_time/len(questions):.1f}초")
    
    print(f"\n💡 무료 장점:")
    print(f"  ✅ API 키 불필요")
    print(f"  ✅ 비용 $0")
    print(f"  ✅ 제한 없음")
    print(f"  ✅ 계속 학습")
    
    if stats['top_questions']:
        print(f"\n🔥 인기 질문:")
        for i, (q, count) in enumerate(stats['top_questions'], 1):
            print(f"  {i}. {q[:40]}... (사용: {count}회)")
    
    print(f"\n{'='*60}")
    print("✅ 테스트 완료!")
    print(f"{'='*60}")
    
    print("\n🎉 결론:")
    print("  - 로컬 AI 사용 → 무료!")
    print("  - 대화 저장 → 학습!")
    print("  - 같은 질문 → 즉시 답변!")
    print("  - 웹 검색 → 정보 수집!")
    print("\n💪 100% 무료로 이메이를 천재로 만들 수 있습니다!")

if __name__ == '__main__':
    main()
