#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
👍👎 이메이 피드백 시스템
사용자 피드백을 수집하여 대화 품질 개선
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "emei_memory.db"

def init_feedback_tables():
    """피드백 테이블 초기화"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 피드백 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversation_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            feedback_type TEXT CHECK(feedback_type IN ('like', 'dislike', 'report')),
            feedback_reason TEXT,
            emotion TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 품질 통계 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS quality_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            total_conversations INTEGER DEFAULT 0,
            positive_feedback INTEGER DEFAULT 0,
            negative_feedback INTEGER DEFAULT 0,
            avg_response_quality REAL DEFAULT 0.0,
            improvement_suggestions TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Feedback System 초기화 완료")

def save_feedback(user_id: str, user_message: str, ai_response: str, 
                  feedback_type: str, reason: str = None, emotion: str = None):
    """피드백 저장"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO conversation_feedback 
        (user_id, user_message, ai_response, feedback_type, feedback_reason, emotion)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, user_message, ai_response, feedback_type, reason, emotion))
    
    feedback_id = c.lastrowid
    
    # 오늘 통계 업데이트
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''
        INSERT INTO quality_stats (date, total_conversations)
        VALUES (?, 1)
        ON CONFLICT(date) DO UPDATE SET
        total_conversations = total_conversations + 1
    ''', (today,))
    
    if feedback_type == 'like':
        c.execute('''
            UPDATE quality_stats 
            SET positive_feedback = positive_feedback + 1
            WHERE date = ?
        ''', (today,))
    elif feedback_type == 'dislike':
        c.execute('''
            UPDATE quality_stats 
            SET negative_feedback = negative_feedback + 1
            WHERE date = ?
        ''', (today,))
    
    conn.commit()
    conn.close()
    
    return feedback_id

def get_feedback_stats(days: int = 7):
    """최근 N일간 피드백 통계"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            date,
            total_conversations,
            positive_feedback,
            negative_feedback,
            CASE 
                WHEN total_conversations > 0 
                THEN ROUND(100.0 * positive_feedback / total_conversations, 1)
                ELSE 0
            END as satisfaction_rate
        FROM quality_stats
        WHERE date >= date('now', '-' || ? || ' days')
        ORDER BY date DESC
    ''', (days,))
    
    rows = c.fetchall()
    conn.close()
    
    return [{
        'date': row[0],
        'total': row[1],
        'positive': row[2],
        'negative': row[3],
        'satisfaction_rate': row[4]
    } for row in rows]

def get_negative_feedback_samples(limit: int = 10):
    """부정 피드백 샘플 (개선 포인트 파악)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            user_message,
            ai_response,
            feedback_reason,
            emotion,
            timestamp
        FROM conversation_feedback
        WHERE feedback_type = 'dislike'
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    return [{
        'user_msg': row[0],
        'ai_response': row[1],
        'reason': row[2],
        'emotion': row[3],
        'timestamp': row[4]
    } for row in rows]

def analyze_improvement_areas():
    """개선 영역 분석"""
    negative_samples = get_negative_feedback_samples(50)
    
    # 부정 피드백 이유별 분류
    reasons = {}
    for sample in negative_samples:
        reason = sample['reason'] or '미지정'
        reasons[reason] = reasons.get(reason, 0) + 1
    
    # 가장 많은 불만 사항 TOP 3
    top_issues = sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        'total_negative': len(negative_samples),
        'top_issues': top_issues,
        'samples': negative_samples[:5]  # 최근 5개 샘플
    }

def generate_training_data():
    """피드백 기반 학습 데이터 생성"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 긍정 피드백받은 대화 (좋은 예시)
    c.execute('''
        SELECT user_message, ai_response, emotion
        FROM conversation_feedback
        WHERE feedback_type = 'like'
        ORDER BY timestamp DESC
        LIMIT 100
    ''')
    
    positive_examples = [{
        'input': row[0],
        'output': row[1],
        'emotion': row[2],
        'quality': 'good'
    } for row in c.fetchall()]
    
    # 부정 피드백받은 대화 (개선 필요)
    c.execute('''
        SELECT user_message, ai_response, feedback_reason, emotion
        FROM conversation_feedback
        WHERE feedback_type = 'dislike'
        ORDER BY timestamp DESC
        LIMIT 100
    ''')
    
    negative_examples = [{
        'input': row[0],
        'output': row[1],
        'issue': row[2],
        'emotion': row[3],
        'quality': 'needs_improvement'
    } for row in c.fetchall()]
    
    conn.close()
    
    return {
        'positive_examples': positive_examples,
        'negative_examples': negative_examples,
        'total': len(positive_examples) + len(negative_examples)
    }

# 초기화 및 테스트
if __name__ == "__main__":
    init_feedback_tables()
    
    # 테스트 데이터
    save_feedback(
        user_id='wordycow',
        user_message='비트코인 지금 사야 해?',
        ai_response='지금 RSI가 30 이하라서 과매도 구간이에요. 매수 타이밍으로 보입니다!',
        feedback_type='like',
        emotion='confident'
    )
    
    save_feedback(
        user_id='wordycow',
        user_message='왜 손실이 났어?',
        ai_response='손실은 투자의 일부입니다.',
        feedback_type='dislike',
        reason='너무 일반적인 답변, 구체적인 분석 없음',
        emotion='neutral'
    )
    
    print("\n📊 최근 7일 피드백 통계:")
    for stat in get_feedback_stats(7):
        print(f"  {stat['date']}: {stat['total']}개 대화, 만족도 {stat['satisfaction_rate']}%")
    
    print("\n⚠️ 개선 영역 분석:")
    improvement = analyze_improvement_areas()
    print(f"  총 부정 피드백: {improvement['total_negative']}개")
    print("  주요 문제점:")
    for issue, count in improvement['top_issues']:
        print(f"    - {issue}: {count}회")
    
    print("\n📚 학습 데이터 생성:")
    training_data = generate_training_data()
    print(f"  긍정 예시: {len(training_data['positive_examples'])}개")
    print(f"  개선 예시: {len(training_data['negative_examples'])}개")
    print(f"  총 학습 데이터: {training_data['total']}개")
    
    print("\n✅ Feedback System 테스트 완료!")
