"""
이메이 장기 기억 시스템
- 대화 히스토리 저장
- 사용자 프로필 관리
- 호감도 시스템
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

DB_FILE = "emei_memory.db"

def init_memory_database():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 대화 히스토리 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            emotion TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 사용자 프로필 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            affection_score INTEGER DEFAULT 50,
            conversation_count INTEGER DEFAULT 0,
            favorite_coins TEXT,
            risk_level TEXT DEFAULT 'medium',
            last_interaction DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 호감도 이벤트 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS affection_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            score_change INTEGER NOT NULL,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 이메이 장기 기억 DB 초기화 완료")


def save_conversation(user_id: str, user_msg: str, ai_response: str, emotion: str = 'neutral'):
    """대화 저장"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (user_id, user_message, ai_response, emotion)
        VALUES (?, ?, ?, ?)
    ''', (user_id, user_msg, ai_response, emotion))
    
    # 사용자 프로필 업데이트
    cursor.execute('''
        INSERT INTO user_profiles (user_id, conversation_count, last_interaction)
        VALUES (?, 1, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            conversation_count = conversation_count + 1,
            last_interaction = ?
    ''', (user_id, datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()


def get_recent_conversations(user_id: str, limit: int = 10) -> List[Dict]:
    """최근 대화 가져오기"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_message, ai_response, emotion, timestamp
        FROM conversations
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (user_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'user_message': row[0],
            'ai_response': row[1],
            'emotion': row[2],
            'timestamp': row[3]
        }
        for row in results
    ]


def get_user_profile(user_id: str) -> Optional[Dict]:
    """사용자 프로필 가져오기"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_id, username, affection_score, conversation_count,
               favorite_coins, risk_level, last_interaction, created_at
        FROM user_profiles
        WHERE user_id = ?
    ''', (user_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'user_id': row[0],
            'username': row[1],
            'affection_score': row[2],
            'conversation_count': row[3],
            'favorite_coins': json.loads(row[4]) if row[4] else [],
            'risk_level': row[5],
            'last_interaction': row[6],
            'created_at': row[7]
        }
    return None


def update_affection(user_id: str, event_type: str, score_change: int, description: str = ""):
    """호감도 업데이트"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 호감도 이벤트 기록
    cursor.execute('''
        INSERT INTO affection_events (user_id, event_type, score_change, description)
        VALUES (?, ?, ?, ?)
    ''', (user_id, event_type, score_change, description))
    
    # 사용자 프로필 업데이트
    cursor.execute('''
        UPDATE user_profiles
        SET affection_score = affection_score + ?
        WHERE user_id = ?
    ''', (score_change, user_id))
    
    conn.commit()
    conn.close()


def analyze_affection_from_message(message: str) -> int:
    """메시지에서 호감도 변화 분석"""
    message_lower = message.lower()
    
    # 긍정 키워드
    positive_keywords = ['감사', '고마워', '최고', '사랑', '이뻐', '예뻐', '좋아', '훌륭', '멋져']
    # 부정 키워드
    negative_keywords = ['화나', '짜증', '싫어', '최악', '바보', '멍청']
    
    score = 0
    for keyword in positive_keywords:
        if keyword in message_lower:
            score += 2
    
    for keyword in negative_keywords:
        if keyword in message_lower:
            score -= 5
    
    return max(min(score, 10), -10)  # -10 ~ +10 사이


def get_personalized_greeting(user_id: str) -> str:
    """사용자별 맞춤 인사"""
    profile = get_user_profile(user_id)
    
    if not profile:
        return "안녕하세요! 이메이예요 💜"
    
    affection = profile['affection_score']
    count = profile['conversation_count']
    
    if affection >= 80:
        return f"안녕하세요~ 오랜만이에요! {count}번째 대화네요 💕"
    elif affection >= 50:
        return f"안녕하세요! 이메이예요 💜 함께 {count}번 대화했네요!"
    else:
        return "안녕하세요. 이메이입니다."


def get_memory_context(user_id: str) -> str:
    """사용자 기억 맥락 생성"""
    profile = get_user_profile(user_id)
    recent = get_recent_conversations(user_id, limit=3)
    
    if not profile:
        return ""
    
    context = f"""
# 사용자 정보
- 총 대화: {profile['conversation_count']}회
- 호감도: {profile['affection_score']}/100
- 위험 성향: {profile['risk_level']}
"""
    
    if recent:
        context += "\n# 최근 대화 요약\n"
        for conv in recent[:3]:
            context += f"- 사용자: {conv['user_message'][:50]}...\n"
            context += f"  이메이: {conv['ai_response'][:50]}...\n"
    
    return context


# 초기화
init_memory_database()
