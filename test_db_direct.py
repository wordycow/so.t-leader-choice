"""
이메이 무료 학습 시스템 직접 테스트
"""
import sqlite3

def test_direct():
    # 1. DB에서 직접 답변 가져오기
    conn = sqlite3.connect('emei_memory.db')
    c = conn.cursor()
    
    test_questions = [
        "이더리움 추천해줘",
        "RSI 지표가 뭐야?",
        "안녕"
    ]
    
    print("="*60)
    print("🧪 무료 학습 시스템 직접 테스트")
    print("="*60)
    
    for question in test_questions:
        print(f"\n질문: {question}")
        
        # DB 검색
        c.execute('SELECT answer FROM free_learning WHERE question = ?', (question,))
        row = c.fetchone()
        
        if row:
            print(f"✅ DB에 답변 있음:")
            print(f"   {row[0]}")
        else:
            print(f"❌ DB에 답변 없음")
    
    conn.close()
    
    print("\n" + "="*60)
    print("📊 전체 학습 데이터")
    print("="*60)
    
    conn = sqlite3.connect('emei_memory.db')
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) FROM free_learning')
    count = c.fetchone()[0]
    
    c.execute('SELECT question FROM free_learning LIMIT 10')
    questions = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    print(f"총 {count}개 학습됨")
    print(f"\n처음 10개:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")

if __name__ == '__main__':
    test_direct()
