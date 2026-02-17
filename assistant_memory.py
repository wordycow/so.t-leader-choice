#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Claude Assistant Memory System
저(Claude)와 사용자의 대화를 영구 저장하여 리셋 후에도 기억 유지
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "assistant_memory.db"

def init_assistant_db():
    """어시스턴트 대화 저장용 DB 초기화"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 대화 내역 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS assistant_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            assistant_response TEXT NOT NULL,
            context TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 프로젝트 상태 테이블 (중요 정보 요약)
    c.execute('''
        CREATE TABLE IF NOT EXISTS project_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 작업 이력 테이블
    c.execute('''
        CREATE TABLE IF NOT EXISTS work_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'completed',
            files_changed TEXT,
            commit_hash TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Assistant Memory DB 초기화 완료")

def save_conversation(session_id: str, user_msg: str, assistant_resp: str, context: dict = None):
    """대화 저장"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    context_json = json.dumps(context, ensure_ascii=False) if context else None
    
    c.execute('''
        INSERT INTO assistant_conversations 
        (session_id, user_message, assistant_response, context)
        VALUES (?, ?, ?, ?)
    ''', (session_id, user_msg, assistant_resp, context_json))
    
    conn.commit()
    conn.close()

def get_recent_conversations(limit: int = 20):
    """최근 대화 N개 가져오기"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT user_message, assistant_response, context, timestamp
        FROM assistant_conversations
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = c.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        conversations.append({
            'user': row[0],
            'assistant': row[1],
            'context': json.loads(row[2]) if row[2] else None,
            'timestamp': row[3]
        })
    
    return list(reversed(conversations))  # 시간순 정렬

def save_project_state(key: str, value: str):
    """프로젝트 상태 저장 (키-값 저장소)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT OR REPLACE INTO project_state (key, value, updated_at)
        VALUES (?, ?, datetime('now'))
    ''', (key, value))
    
    conn.commit()
    conn.close()

def get_project_state(key: str):
    """프로젝트 상태 가져오기"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT value FROM project_state WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    
    return row[0] if row else None

def save_work(task_type: str, description: str, files_changed: list = None, 
              commit_hash: str = None, status: str = 'completed'):
    """작업 이력 저장"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    files_json = json.dumps(files_changed, ensure_ascii=False) if files_changed else None
    
    c.execute('''
        INSERT INTO work_history 
        (task_type, description, status, files_changed, commit_hash)
        VALUES (?, ?, ?, ?, ?)
    ''', (task_type, description, status, files_json, commit_hash))
    
    conn.commit()
    conn.close()

def get_work_summary(days: int = 7):
    """최근 N일간 작업 요약"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT task_type, description, status, timestamp
        FROM work_history
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
    ''', (days,))
    
    rows = c.fetchall()
    conn.close()
    
    return [{
        'type': row[0],
        'description': row[1],
        'status': row[2],
        'timestamp': row[3]
    } for row in rows]

def generate_context_summary():
    """현재 프로젝트 컨텍스트 요약 생성"""
    recent_convs = get_recent_conversations(10)
    recent_work = get_work_summary(7)
    
    summary = {
        'last_conversations': [
            f"User: {c['user'][:100]}... → Assistant: {c['assistant'][:100]}..."
            for c in recent_convs[-5:]
        ],
        'recent_work': [
            f"{w['type']}: {w['description']}"
            for w in recent_work[:10]
        ],
        'project_state': {
            'progress': get_project_state('overall_progress'),
            'last_feature': get_project_state('last_completed_feature'),
            'next_priority': get_project_state('next_priority')
        }
    }
    
    return summary

# 초기화
if __name__ == "__main__":
    init_assistant_db()
    
    # 테스트
    save_conversation(
        session_id="test_session",
        user_msg="이메이 대화 능력을 빠르게 발전시키고 싶어요",
        assistant_resp="좋습니다! 3가지 방법을 제안드립니다...",
        context={'feature': 'emei_development'}
    )
    
    save_project_state('overall_progress', '35%')
    save_project_state('last_completed_feature', 'Long-term Memory System')
    save_project_state('next_priority', 'Dialog Quality Improvement')
    
    save_work(
        task_type='feature',
        description='Add emotion system with 9 expressions',
        files_changed=['emotion_system.py', 'upbit-smart-bot-v8.0-ULTIMATE.py'],
        commit_hash='738f409'
    )
    
    print("\n📊 최근 대화:")
    for conv in get_recent_conversations(5):
        print(f"  {conv['timestamp']} - User: {conv['user'][:50]}...")
    
    print("\n📊 최근 작업:")
    for work in get_work_summary(7):
        print(f"  {work['timestamp']} - {work['type']}: {work['description']}")
    
    print("\n📊 컨텍스트 요약:")
    print(json.dumps(generate_context_summary(), indent=2, ensure_ascii=False))
    
    print("\n✅ Assistant Memory System 테스트 완료!")
