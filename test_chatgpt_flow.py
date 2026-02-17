"""
🧪 ChatGPT 학습 시스템 동작 방식 데모
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

API 키 없이 동작 원리를 시뮬레이션합니다.
"""

import sqlite3
import time
from datetime import datetime

# 데모 DB
DB_PATH = 'chatgpt_demo.db'

def init_demo_db():
    """데모 DB 초기화"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 학습 데이터 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS learned_knowledge (
            id INTEGER PRIMARY KEY,
            question TEXT UNIQUE,
            answer TEXT,
            use_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 데모 DB 초기화 완료")

def check_cache(question):
    """캐시 확인 (DB에서 학습된 답변 찾기)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT answer, use_count FROM learned_knowledge WHERE question = ?', (question,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {'answer': row[0], 'use_count': row[1], 'cached': True}
    return None

def save_to_cache(question, answer):
    """답변 학습 (DB에 저장)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO learned_knowledge (question, answer, use_count)
            VALUES (?, ?, 1)
        ''', (question, answer))
        conn.commit()
        print(f"  📚 학습 완료: '{question[:30]}...'")
        return True
    except sqlite3.IntegrityError:
        # 이미 존재하는 경우 use_count만 증가
        c.execute('''
            UPDATE learned_knowledge 
            SET use_count = use_count + 1 
            WHERE question = ?
        ''', (question,))
        conn.commit()
        print(f"  🔄 재사용: '{question[:30]}...'")
        return False
    finally:
        conn.close()

def simulate_chatgpt(question):
    """ChatGPT 호출 시뮬레이션"""
    time.sleep(2)  # 2초 지연 (실제 API 호출 시뮬레이션)
    
    # 질문에 따른 답변 생성 (실제로는 GPT-4가 생성)
    answers = {
        "비트코인 지금 사도 돼?": "비트코인 현재 RSI 35로 과매도 구간이에요! 매수 타이밍입니다. 목표가 1억원, 손절가 9천만원 추천해요. 💪",
        "RSI 지표가 뭐야?": "RSI는 상대강도지수로 0~100 사이 값이에요. 30 이하면 과매도(매수 타이밍), 70 이상이면 과매수(매도 고려)입니다. 📊",
        "손실이 나서 우울해...": "손실은 누구나 겪어요 😢 차트 닫고 하루 쉬세요. 감정적으로 거래하면 더 잃어요. 내일 전략 다시 짜면 됩니다! 💪",
        "이더리움 추천해줘": "이더리움 현재 RSI 42, 거래량 증가 중이에요. 상승 가능성 60%로 봅니다. 소액 분할 매수 추천! 🚀",
        "스토캐스틱이 뭐야?": "스토캐스틱은 모멘텀 지표예요. %K와 %D 두 선이 20 이하에서 골든크로스면 매수, 80 이상에서 데드크로스면 매도 신호입니다! 📈"
    }
    
    return answers.get(question, "질문을 이해하지 못했어요. 다시 물어봐주세요! 😅")

def chat_with_emei(question):
    """이메이와 대화 (전체 흐름)"""
    print(f"\n{'='*60}")
    print(f"👤 사용자: {question}")
    print(f"{'='*60}")
    
    # 1. 캐시 확인
    print("\n[1단계] 캐시 확인 중...")
    cached = check_cache(question)
    
    if cached:
        print(f"  ✅ 캐시 발견! (사용 횟수: {cached['use_count']})")
        print(f"  ⚡ 응답 시간: 0.3초 | 비용: $0")
        print(f"\n🤖 이메이: {cached['answer']}")
        
        # use_count 업데이트
        save_to_cache(question, cached['answer'])
        return cached['answer'], 0.3, 0.0, True
    
    # 2. ChatGPT 호출
    print("  ❌ 캐시 없음")
    print("\n[2단계] ChatGPT 호출 중...")
    start_time = time.time()
    
    answer = simulate_chatgpt(question)
    
    response_time = time.time() - start_time
    cost = 0.001  # $0.001 (GPT-3.5-turbo)
    
    print(f"  ✅ 응답 완료!")
    print(f"  ⏱️  응답 시간: {response_time:.1f}초 | 비용: ${cost:.3f}")
    
    # 3. DB에 학습
    print("\n[3단계] 학습 중...")
    save_to_cache(question, answer)
    
    print(f"\n🤖 이메이: {answer}")
    
    return answer, response_time, cost, False

def show_stats():
    """학습 통계"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*), SUM(use_count) FROM learned_knowledge')
    total_learned, total_uses = c.fetchone()
    
    print(f"\n{'='*60}")
    print("📊 학습 통계")
    print(f"{'='*60}")
    print(f"학습된 질문: {total_learned}개")
    print(f"총 재사용: {total_uses}회")
    
    if total_learned > 0:
        c.execute('''
            SELECT question, use_count 
            FROM learned_knowledge 
            ORDER BY use_count DESC 
            LIMIT 5
        ''')
        
        print("\n🔥 인기 질문 TOP 5:")
        for i, (q, count) in enumerate(c.fetchall(), 1):
            print(f"  {i}. {q[:40]}... (사용: {count}회)")
    
    conn.close()

def main():
    """메인 데모"""
    print("\n" + "="*60)
    print("🎉 ChatGPT 학습 시스템 데모")
    print("="*60)
    
    init_demo_db()
    
    # 테스트 시나리오
    questions = [
        "비트코인 지금 사도 돼?",
        "RSI 지표가 뭐야?",
        "비트코인 지금 사도 돼?",  # 같은 질문 반복!
        "손실이 나서 우울해...",
        "비트코인 지금 사도 돼?",  # 또 반복!
        "이더리움 추천해줘",
        "RSI 지표가 뭐야?",  # 반복!
    ]
    
    total_cost = 0
    total_time = 0
    cache_hits = 0
    
    for i, question in enumerate(questions, 1):
        print(f"\n\n{'#'*60}")
        print(f"테스트 {i}/{len(questions)}")
        print(f"{'#'*60}")
        
        answer, time_taken, cost, cached = chat_with_emei(question)
        
        total_cost += cost
        total_time += time_taken
        if cached:
            cache_hits += 1
        
        time.sleep(1)  # 시연을 위한 대기
    
    # 최종 통계
    print(f"\n\n{'='*60}")
    print("🎯 최종 결과")
    print(f"{'='*60}")
    print(f"총 질문: {len(questions)}회")
    print(f"캐시 히트: {cache_hits}회 ({cache_hits/len(questions)*100:.1f}%)")
    print(f"ChatGPT 호출: {len(questions) - cache_hits}회")
    print(f"총 비용: ${total_cost:.3f} (약 {total_cost * 1300:.0f}원)")
    print(f"평균 응답 시간: {total_time/len(questions):.1f}초")
    
    # 절감 효과
    if cache_hits > 0:
        saved_cost = cache_hits * 0.001
        saved_time = cache_hits * 2
        print(f"\n💰 절감 효과:")
        print(f"  비용 절감: ${saved_cost:.3f} (약 {saved_cost * 1300:.0f}원)")
        print(f"  시간 절감: {saved_time:.0f}초")
    
    show_stats()
    
    print(f"\n{'='*60}")
    print("✅ 데모 완료!")
    print(f"{'='*60}")
    print("\n💡 실제 사용 시:")
    print("  1. OpenAI API 키 설정")
    print("  2. 서버 재시작")
    print("  3. 이메이와 대화 시작!")
    print("\n🚀 지금 바로 API 키를 설정하시겠어요? (Y/n)")

if __name__ == '__main__':
    main()
