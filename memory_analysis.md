# 🧠 이메이 장기 기억 시스템 분석

## 현재 구현된 기억 시스템

### 1️⃣ **학습 데이터 (emei_learned_knowledge.json)**
```python
# 위치: /home/user/webapp/emei_learned_knowledge.json
{
  "비트코인 반감기가 뭐야?": {
    "answer": "비트코인 반감기는...",
    "learned_at": "2026-02-17 22:30:00",
    "usage_count": 5
  }
}
```

**용도**: 웹 검색으로 학습한 지식을 영구 저장
**저장 방식**: JSON 파일 (서버 디스크)
**장점**: 
- 재시작 후에도 지식 유지
- 같은 질문 즉답 (0.5초)
- 사용 횟수 추적

**문제점**: ❌ 현재 실제로는 저장 안 됨 (테스트 시 파일 없음)

---

### 2️⃣ **대화 히스토리 (chat_history)**
```python
# 위치: 메모리 (RAM)
chat_history = {
    'wordycow': [
        {'role': 'user', 'content': '안녕'},
        {'role': 'assistant', 'content': '안녕하세요!'}
    ]
}
```

**용도**: 현재 세션의 대화 맥락 유지
**저장 방식**: Python 딕셔너리 (메모리)
**장점**: 빠른 접근, 실시간 대화 가능

**문제점**: ❌ 서버 재시작 시 모두 삭제

---

### 3️⃣ **JAI 기억 시스템 (SQLite DB)**
```python
# 위치: /home/user/webapp/jai_memory.db (추정)
# 테이블: user_profiles, conversations, memories
```

**용도**: 사용자별 프로필, 대화 기록, 장기 기억
**저장 방식**: SQLite 데이터베이스 (서버 디스크)
**장점**: 
- 영구 저장
- 복잡한 쿼리 가능
- 관계형 데이터

**문제점**: ❌ 현재 실제로 사용되고 있는지 불명확

---

## ❌ 현재 문제점

### **장기 기억이 제대로 작동하지 않음**

1. **학습 데이터 미저장**
```bash
$ ls emei_learned_knowledge.json
ls: cannot access 'emei_learned_knowledge.json': No such file or directory
```
→ 학습해도 저장이 안 됨!

2. **대화 히스토리 휘발**
```python
chat_history = {}  # 메모리에만 존재
# 서버 재시작 → 모든 대화 삭제
```

3. **사용자 프로필 미활용**
```python
# jai_memory_system.py 존재하지만
# 실제로 API에서 호출하지 않음
```

---

## 🎯 **서버를 사용하는 진짜 이유**

### **우리가 원하는 것**
```
사용자: "나 어제 비트코인 샀어"
이메이: "기억해요! 어제 비트코인 매수하셨죠 💜"

[3일 후]
사용자: "내가 뭐 샀더라?"
이메이: "3일 전에 비트코인 사셨어요! 지금 수익률 +5%예요 📈"
```

### **현재 실제 상황**
```
사용자: "나 어제 비트코인 샀어"
이메이: "좋은 선택이에요!"

[3일 후 / 서버 재시작 후]
사용자: "내가 뭐 샀더라?"
이메이: "죄송해요, 기억이 안 나요 😢"
```

---

## 🔧 **해결 방법**

### **Option 1: 학습 데이터 저장 수정**
```python
# learned_knowledge.py 수정
def save_learned_answer(question, answer):
    try:
        data = load_data()
        data[question] = {
            'answer': answer,
            'learned_at': datetime.now().isoformat(),
            'usage_count': 0
        }
        with open('emei_learned_knowledge.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 학습 저장 완료: {question}")
    except Exception as e:
        print(f"❌ 학습 저장 실패: {e}")
```

### **Option 2: 대화 히스토리 DB 저장**
```python
# 매 대화마다 SQLite에 저장
def save_conversation_to_db(user_id, user_msg, ai_msg):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations 
        (user_id, user_message, ai_response, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, user_msg, ai_msg, datetime.now()))
    conn.commit()
    conn.close()
```

### **Option 3: 사용자 프로필 활용**
```python
# 사용자별 선호도, 투자 성향, 과거 대화 요약
user_profile = {
    'user_id': 'wordycow',
    'favorite_coins': ['BTC', 'ETH'],
    'risk_level': 'medium',
    'conversation_count': 127,
    'affection_score': 75,
    'last_interaction': '2026-02-17 22:30:00'
}
```

---

## 📊 **현재 vs 이상적인 상태**

| 항목 | 현재 | 이상적 |
|------|------|--------|
| 학습 데이터 | ❌ 저장 안 됨 | ✅ JSON 파일 저장 |
| 대화 히스토리 | ❌ 메모리만 | ✅ DB 저장 |
| 사용자 프로필 | ❌ 미사용 | ✅ DB 활용 |
| 감정 상태 | ✅ 실시간 | ✅ 누적 기록 |
| 호감도 | ❌ 없음 | ✅ 점수 시스템 |
| 투자 기록 | ✅ 트레이딩 봇 | ✅ 이메이 인지 |

---

## 🚀 **우선순위 (다시 정리)**

### 🔥 **High Priority (1주일)**
1. **학습 데이터 저장 수정** (현재 안 됨!)
2. **대화 히스토리 DB 저장**
3. **사용자 프로필 시스템 활성화**

### 🌟 **Medium Priority (2주)**
1. **호감도 시스템** (누적 점수)
2. **투자 기록 연동** (트레이딩 봇 ↔ 이메이)
3. **대화 요약 시스템** (장기 대화 압축)

### 🚀 **Low Priority (1개월+)**
1. **Vector DB** (Pinecone/Chroma)
2. **감정 누적 분석**
3. **개인화된 투자 조언**

---

## 💡 **결론**

**서버를 사용하는 진짜 이유 = 장기 기억**

하지만 현재는:
- ❌ 학습 데이터 저장 안 됨
- ❌ 대화 히스토리 휘발
- ❌ 사용자 프로필 미활용

**즉, 서버가 있지만 장기 기억이 작동하지 않음!**

**다음 액션**: 장기 기억 시스템 제대로 구현! 🧠
