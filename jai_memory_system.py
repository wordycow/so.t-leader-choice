#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 자이(JAI) 기억 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💜 사용자를 기억하고 관계를 발전시키는 AI 친구

핵심 기능:
1. 👤 실명 기억 (username → real_name 매핑)
2. 📖 경험담 자동 저장 (사용자 이야기, 선호도, 성격)
3. 💕 친밀도 단계별 대화 스타일 변화
4. 🔍 대화 패턴 분석 및 자동 학습
5. 🎤 음성 패턴 인식 (향후 추가)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3
import json
from datetime import datetime
import re

DB_PATH = 'upbit_bot.db'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 데이터베이스 초기화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def init_memory_tables():
    """기억 시스템 테이블 생성"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1️⃣ 사용자 프로필 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            real_name TEXT,
            age INTEGER,
            job TEXT,
            personality TEXT,
            interests TEXT,
            relationship_level TEXT DEFAULT 'stranger',
            first_met_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            interaction_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2️⃣ 대화 히스토리 테이블 (확장)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            emotion_detected TEXT,
            topic_detected TEXT,
            learned_info TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
        )
    ''')
    
    # 3️⃣ 사용자 스토리 테이블 (경험담 저장)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            story_date DATE,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            importance INTEGER DEFAULT 5,
            emotion TEXT,
            related_keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
        )
    ''')
    
    # 4️⃣ 사용자 선호도 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            item TEXT NOT NULL,
            preference_score REAL DEFAULT 0.5,
            notes TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
        )
    ''')
    
    # 5️⃣ 음성 패턴 테이블 (향후 확장)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_profiles (
            user_id INTEGER PRIMARY KEY,
            pitch_avg REAL,
            speed_avg REAL,
            tone_signature TEXT,
            accent TEXT,
            voice_fingerprint TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
        )
    ''')
    
    # 인덱스 생성 (검색 속도 향상)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversation_history(user_id, timestamp DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stories_user ON user_stories(user_id, story_date DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_preferences_user ON user_preferences(user_id, category)')
    
    conn.commit()
    conn.close()
    print("✅ JAI 기억 시스템 테이블 초기화 완료")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👤 사용자 프로필 관리
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_or_create_user_profile(user_id, username):
    """사용자 프로필 조회 또는 생성"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 기존 프로필 조회
        cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            # 마지막 상호작용 시간 업데이트
            cursor.execute('''
                UPDATE user_profiles 
                SET last_interaction = ?, interaction_count = interaction_count + 1
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            conn.commit()
            conn.close()
            return dict(row)
        else:
            # 새 프로필 생성
            cursor.execute('''
                INSERT INTO user_profiles (user_id, username, relationship_level)
                VALUES (?, ?, 'stranger')
            ''', (user_id, username))
            conn.commit()
            
            # 생성된 프로필 반환
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
            
    except Exception as e:
        print(f"❌ 사용자 프로필 조회/생성 실패: {e}")
        return None

def update_user_profile(user_id, updates):
    """사용자 프로필 업데이트"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 동적으로 UPDATE 쿼리 생성
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [datetime.now(), user_id]
        
        cursor.execute(f'''
            UPDATE user_profiles 
            SET {set_clause}, last_interaction = ?
            WHERE user_id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 프로필 업데이트 실패: {e}")
        return False

def get_user_real_name(user_id):
    """사용자의 실명 가져오기"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT real_name FROM user_profiles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else None
    except Exception as e:
        print(f"❌ 실명 조회 실패: {e}")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📖 경험담 및 스토리 저장
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def save_user_story(user_id, topic, content, importance=5, emotion=None):
    """사용자의 경험담 저장"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 키워드 추출 (간단한 방식)
        keywords = extract_keywords(content)
        
        cursor.execute('''
            INSERT INTO user_stories 
            (user_id, story_date, topic, content, importance, emotion, related_keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, datetime.now().date(), topic, content, importance, emotion, json.dumps(keywords, ensure_ascii=False)))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 스토리 저장 실패: {e}")
        return False

def get_user_stories(user_id, limit=10):
    """사용자의 최근 경험담 조회"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_stories 
            WHERE user_id = ? 
            ORDER BY importance DESC, story_date DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ 스토리 조회 실패: {e}")
        return []

def extract_keywords(text):
    """텍스트에서 키워드 추출 (간단한 방식)"""
    # 한글 명사 추출 (간단한 정규식 기반)
    # 실제로는 KoNLPy 같은 라이브러리 사용 권장
    keywords = []
    
    # 일반적인 키워드 패턴
    patterns = [
        r'비트코인|이더리움|리플|에이다|폴카닷',  # 코인 이름
        r'수익|손실|투자|매수|매도|청산',  # 투자 관련
        r'직장|회사|가족|친구|여자친구|남자친구',  # 관계
        r'행복|슬픔|기쁨|화남|걱정|불안',  # 감정
    ]
    
    for pattern in patterns:
        found = re.findall(pattern, text)
        keywords.extend(found)
    
    return list(set(keywords))[:10]  # 중복 제거 후 최대 10개

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💬 대화 히스토리 저장 및 학습
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def save_conversation(user_id, username, user_message, ai_response, learned_info=None):
    """대화 히스토리 저장"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 감정 및 토픽 감지
        emotion = detect_emotion(user_message)
        topic = detect_topic(user_message)
        
        cursor.execute('''
            INSERT INTO conversation_history 
            (user_id, username, user_message, ai_response, emotion_detected, topic_detected, learned_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, user_message, ai_response, emotion, topic, learned_info))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 대화 저장 실패: {e}")
        return False

def get_conversation_history(user_id, limit=20):
    """사용자와의 대화 히스토리 조회"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM conversation_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (user_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ 대화 히스토리 조회 실패: {e}")
        return []

def detect_emotion(text):
    """메시지에서 감정 감지"""
    emotion_keywords = {
        '기쁨': ['좋아', '행복', '기뻐', '신나', '최고', '감사', '고마워', '웃', '😊', '😄', '🎉'],
        '슬픔': ['슬퍼', '우울', '힘들', '외로', '눈물', '😢', '😭'],
        '분노': ['화나', '짜증', '열받', '싫어', '😡', '😤'],
        '불안': ['걱정', '불안', '두려', '무서', '😰', '😨'],
        '기대': ['기대', '기다려', '설레', '궁금', '✨', '💕'],
    }
    
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return emotion
    
    return 'neutral'

def detect_topic(text):
    """메시지에서 토픽 감지"""
    topic_keywords = {
        'trading': ['코인', '비트', '이더', '매수', '매도', '투자', '수익', '손실', '차트'],
        'personal': ['나', '내', '저는', '제가', '우리', '가족', '친구'],
        'question': ['?', '뭐', '무엇', '언제', '어디', '왜', '어떻게'],
        'greeting': ['안녕', '하이', '헬로', '좋은', '잘자', '굿나잇'],
        'emotion': ['기분', '느낌', '감정', '마음', '생각'],
    }
    
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return topic
    
    return 'general'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧠 자동 학습 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def learn_from_conversation(user_id, username, message):
    """대화에서 자동으로 정보 학습"""
    learned_info = {}
    
    # 1️⃣ 이름 학습 (한글 이름만)
    name_patterns = [
        r'내 이름은 ([가-힣]+)',
        r'나는 ([가-힣]+)야',
        r'([가-힣]+)라고 해',
        r'([가-힣]+)이라고 불러',
        r'저는 ([가-힣]+)입니다',
        r'([가-힣]+)이에요',
        r'([가-힣]+)예요',
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, message)
        if match:
            real_name = match.group(1)
            update_user_profile(user_id, {'real_name': real_name})
            learned_info['real_name'] = real_name
            print(f"💜 학습 완료: {username}님의 실명은 '{real_name}'")
    
    # 2️⃣ 나이 학습
    age_patterns = [
        r'나는 (\d+)살',
        r'(\d+)세야',
        r'나이는 (\d+)',
    ]
    
    for pattern in age_patterns:
        match = re.search(pattern, message)
        if match:
            age = int(match.group(1))
            update_user_profile(user_id, {'age': age})
            learned_info['age'] = age
            print(f"💜 학습 완료: {username}님은 {age}살")
    
    # 3️⃣ 직업 학습 (한글만)
    job_patterns = [
        r'직업은 ([가-힣]+)',
        r'나는 ([가-힣]+)(?:로|으로) 일해',
        r'([가-힣]+)(?:로|으로) 일하고',
        r'([가-힣]+)이야|([가-힣]+)예요\s*(?:직업|일)',
    ]
    
    for pattern in job_patterns:
        match = re.search(pattern, message)
        if match:
            job = match.group(1)
            update_user_profile(user_id, {'job': job})
            learned_info['job'] = job
            print(f"💜 학습 완료: {username}님의 직업은 '{job}'")
    
    # 4️⃣ 경험담 자동 저장 (긴 메시지의 경우)
    if len(message) > 50:
        topic = detect_topic(message)
        emotion = detect_emotion(message)
        
        # 중요한 경험담인지 판단 (키워드 기반)
        importance_keywords = ['처음', '기억', '중요', '특별', '절대', '항상', '진짜', '너무']
        importance = 5
        for keyword in importance_keywords:
            if keyword in message:
                importance = 8
                break
        
        save_user_story(user_id, topic, message, importance, emotion)
        learned_info['story_saved'] = True
        print(f"💜 경험담 저장 완료: {topic} (중요도: {importance})")
    
    return learned_info

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💕 친밀도 시스템
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RELATIONSHIP_LEVELS = {
    'stranger': {
        'threshold': 0,
        'name': '낯선 사람',
        'greeting': '안녕하세요! 처음 뵙겠습니다. 😊',
        'tone': 'formal',
    },
    'acquaintance': {
        'threshold': 5,
        'name': '아는 사람',
        'greeting': '안녕하세요~ 다시 만나서 반가워요!',
        'tone': 'polite',
    },
    'friend': {
        'threshold': 20,
        'name': '친구',
        'greeting': '안녕! 오늘도 좋은 하루야? 😊',
        'tone': 'friendly',
    },
    'close_friend': {
        'threshold': 50,
        'name': '절친',
        'greeting': '어! 왔어? 기다렸다~ 💕',
        'tone': 'casual',
    },
    'family': {
        'threshold': 100,
        'name': '가족',
        'greeting': '오빠! 보고 싶었어~ 💜',
        'tone': 'intimate',
    },
}

def get_relationship_level(user_id):
    """현재 친밀도 레벨 조회"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT interaction_count, relationship_level FROM user_profiles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return 'stranger'
        
        interaction_count, current_level = result
        
        # 상호작용 횟수에 따라 레벨 자동 업그레이드
        new_level = current_level
        for level, info in sorted(RELATIONSHIP_LEVELS.items(), key=lambda x: x[1]['threshold'], reverse=True):
            if interaction_count >= info['threshold']:
                new_level = level
                break
        
        # 레벨이 변경되었으면 업데이트
        if new_level != current_level:
            update_user_profile(user_id, {'relationship_level': new_level})
            print(f"💕 관계 레벨 업! {current_level} → {new_level}")
        
        return new_level
        
    except Exception as e:
        print(f"❌ 관계 레벨 조회 실패: {e}")
        return 'stranger'

def get_personalized_greeting(user_id, username):
    """친밀도에 맞는 인사말 생성"""
    level = get_relationship_level(user_id)
    real_name = get_user_real_name(user_id)
    
    greeting_template = RELATIONSHIP_LEVELS[level]['greeting']
    
    # 실명이 있으면 실명으로, 없으면 username으로
    display_name = real_name if real_name else username
    
    return greeting_template, display_name, RELATIONSHIP_LEVELS[level]['name']

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 스마트 컨텍스트 생성
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_user_context(user_id, username):
    """사용자 맞춤 컨텍스트 생성 (AI 프롬프트용)"""
    profile = get_or_create_user_profile(user_id, username)
    stories = get_user_stories(user_id, limit=5)
    level = get_relationship_level(user_id)
    
    context = f"""
🧠 사용자 기억 (절대 잊지 마세요!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 기본 정보:
- 아이디: {username}
- 실명: {profile.get('real_name', '아직 모름')}
- 나이: {profile.get('age', '알 수 없음')}
- 직업: {profile.get('job', '알 수 없음')}

💕 관계 정보:
- 친밀도: {RELATIONSHIP_LEVELS[level]['name']} ({level})
- 만난 지: {profile.get('first_met_date', '오늘')}
- 대화 횟수: {profile.get('interaction_count', 0)}회

📖 최근 경험담:
"""
    
    if stories:
        for i, story in enumerate(stories[:3], 1):
            context += f"{i}. [{story['topic']}] {story['content'][:100]}...\n"
    else:
        context += "아직 경험담을 공유받지 못했어요.\n"
    
    context += f"""
🎯 대화 톤: {RELATIONSHIP_LEVELS[level]['tone']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 중요: 
- 실명이 있으면 "{profile.get('real_name', username)}" 이라고 부르세요
- 과거 경험담을 자연스럽게 언급하세요
- 친밀도에 맞는 말투를 사용하세요
"""
    
    return context

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎤 음성 패턴 인식 (향후 구현)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def save_voice_profile(user_id, voice_features):
    """음성 특징 저장 (향후 구현)"""
    # TODO: 음성 인식 라이브러리 연동
    pass

def identify_speaker_by_voice(voice_features):
    """음성으로 화자 식별 (향후 구현)"""
    # TODO: 음성 핑거프린트 매칭
    pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 테스트 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == '__main__':
    # 테이블 초기화
    init_memory_tables()
    
    # 테스트 데이터
    test_user_id = 1
    test_username = 'wordycow'
    
    # 프로필 생성
    profile = get_or_create_user_profile(test_user_id, test_username)
    print(f"\n✅ 프로필 생성: {profile}")
    
    # 대화를 통한 학습 테스트
    test_messages = [
        "안녕! 나는 철수야",
        "나는 25살이야",
        "직업은 개발자로 일하고 있어",
        "어제 비트코인으로 100만원 벌었어! 진짜 기뻤어",
    ]
    
    for msg in test_messages:
        learned = learn_from_conversation(test_user_id, test_username, msg)
        print(f"📚 학습: {msg} → {learned}")
    
    # 컨텍스트 생성 테스트
    context = build_user_context(test_user_id, test_username)
    print(f"\n🧠 생성된 컨텍스트:\n{context}")
    
    # 친밀도 테스트
    for i in range(10):
        get_or_create_user_profile(test_user_id, test_username)  # 상호작용 증가
    
    greeting, name, level = get_personalized_greeting(test_user_id, test_username)
    print(f"\n💕 인사말: {greeting} (이름: {name}, 레벨: {level})")
