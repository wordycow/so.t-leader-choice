#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 이메이 학습 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 자동 학습 기능:
1. 채팅 대화 자동 저장 & 학습
2. 유튜브 링크 자동 학습
3. 노트북 로컬 AI 연동 (Ollama)
4. DB 기반 빠른 응답
"""

import sqlite3
import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
import yt_dlp

class EmeiLearning:
    """이메이 학습 시스템"""
    
    def __init__(self, db_path='upbit_bot.db', local_ai_url=None):
        self.db_path = db_path
        self.local_ai_url = local_ai_url or "https://infinite-keno-casinos-constantly.trycloudflare.com"
        self.model = "qwen2.5:7b"
        
        self._init_db()
        print(f"✅ 이메이 학습 시스템 초기화")
        print(f"   로컬 AI: {self.local_ai_url}")
        print(f"   모델: {self.model}")
    
    def _init_db(self):
        """DB 초기화"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 학습 데이터 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS emei_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                source TEXT DEFAULT 'chat',
                quality_score REAL DEFAULT 0.8,
                use_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 대화 히스토리
        c.execute('''
            CREATE TABLE IF NOT EXISTS emei_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                user_message TEXT,
                emei_response TEXT,
                learned BOOLEAN DEFAULT 0,
                youtube_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ DB 테이블 준비 완료")
    
    def search_knowledge(self, question: str) -> Optional[str]:
        """학습된 지식 검색"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 정확히 일치하는 질문
        c.execute('''
            SELECT answer, use_count 
            FROM emei_knowledge 
            WHERE question = ?
            ORDER BY use_count DESC, quality_score DESC
            LIMIT 1
        ''', (question,))
        
        result = c.fetchone()
        
        if result:
            answer, use_count = result
            # 사용 횟수 증가
            c.execute('''
                UPDATE emei_knowledge 
                SET use_count = ?, last_used = CURRENT_TIMESTAMP 
                WHERE question = ?
            ''', (use_count + 1, question))
            conn.commit()
            conn.close()
            print(f"💡 DB에서 답변 찾음 (사용 {use_count + 1}회)")
            return answer
        
        # 유사한 질문 검색 (간단한 키워드 매칭)
        keywords = question.split()
        for keyword in keywords:
            if len(keyword) > 2:  # 2글자 이상 키워드만
                c.execute('''
                    SELECT answer, use_count 
                    FROM emei_knowledge 
                    WHERE question LIKE ?
                    ORDER BY use_count DESC, quality_score DESC
                    LIMIT 1
                ''', (f'%{keyword}%',))
                
                result = c.fetchone()
                if result:
                    answer, use_count = result
                    conn.close()
                    print(f"💡 유사 질문에서 답변 찾음: '{keyword}'")
                    return answer
        
        conn.close()
        return None
    
    def learn_from_local_ai(self, question: str) -> str:
        """로컬 AI로부터 학습"""
        try:
            print(f"🤖 로컬 AI 호출: {question[:50]}...")
            
            response = requests.post(
                f"{self.local_ai_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"""당신은 암호화폐 트레이딩 전문가 이메이입니다. 
친근하고 도움이 되는 답변을 해주세요.

질문: {question}

답변:""",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('response', '').strip()
                
                if answer:
                    # DB에 학습 저장
                    self.save_knowledge(question, answer, 'local_ai')
                    print(f"✅ 로컬 AI 학습 완료")
                    return answer
            
            print(f"⚠️ 로컬 AI 응답 실패: {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            print("⏱️ 로컬 AI 타임아웃")
            return None
        except Exception as e:
            print(f"❌ 로컬 AI 오류: {e}")
            return None
    
    def save_knowledge(self, question: str, answer: str, source: str = 'chat'):
        """지식 저장"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 중복 체크
        c.execute('SELECT id FROM emei_knowledge WHERE question = ?', (question,))
        if c.fetchone():
            # 이미 있으면 업데이트
            c.execute('''
                UPDATE emei_knowledge 
                SET answer = ?, source = ?, quality_score = quality_score + 0.1
                WHERE question = ?
            ''', (answer, source, question))
        else:
            # 새로 추가
            c.execute('''
                INSERT INTO emei_knowledge (question, answer, source)
                VALUES (?, ?, ?)
            ''', (question, answer, source))
        
        conn.commit()
        conn.close()
        print(f"💾 지식 저장: {question[:30]}...")
    
    def save_conversation(self, user_id: str, user_message: str, emei_response: str, 
                         learned: bool = False, youtube_url: str = None):
        """대화 저장"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO emei_conversations 
            (user_id, user_message, emei_response, learned, youtube_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_message, emei_response, learned, youtube_url))
        
        conn.commit()
        conn.close()
    
    def extract_youtube_url(self, message: str) -> Optional[str]:
        """메시지에서 유튜브 URL 추출"""
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'https?://youtu\.be/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, message)
            if match:
                video_id = match.group(1)
                return f"https://youtube.com/watch?v={video_id}"
        
        return None
    
    def learn_from_youtube(self, youtube_url: str) -> Optional[str]:
        """유튜브 영상 자동 학습"""
        try:
            print(f"📺 유튜브 학습 시작: {youtube_url}")
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                title = info.get('title', '')
                description = info.get('description', '')
                
                # 제목과 설명에서 주요 정보 추출
                content = f"제목: {title}\n\n내용: {description[:500]}"
                
                # 로컬 AI로 요약 생성
                summary = self.learn_from_local_ai(f"다음 유튜브 영상을 요약해주세요:\n{content}")
                
                if summary:
                    # 지식으로 저장
                    self.save_knowledge(title, summary, 'youtube')
                    print(f"✅ 유튜브 학습 완료: {title}")
                    return f"📺 **유튜브 영상 학습 완료!**\n\n**제목:** {title}\n\n**요약:**\n{summary}"
                
                return None
                
        except Exception as e:
            print(f"❌ 유튜브 학습 오류: {e}")
            return None
    
    def chat(self, user_id: str, message: str) -> Dict:
        """이메이와 채팅"""
        start_time = time.time()
        
        # 유튜브 URL 체크
        youtube_url = self.extract_youtube_url(message)
        if youtube_url:
            youtube_response = self.learn_from_youtube(youtube_url)
            if youtube_response:
                self.save_conversation(user_id, message, youtube_response, learned=True, youtube_url=youtube_url)
                return {
                    'success': True,
                    'response': youtube_response,
                    'learned': True,
                    'source': 'youtube',
                    'response_time': time.time() - start_time
                }
        
        # 1단계: DB에서 검색
        answer = self.search_knowledge(message)
        if answer:
            self.save_conversation(user_id, message, answer, learned=False)
            return {
                'success': True,
                'response': answer,
                'learned': False,
                'source': 'database',
                'response_time': time.time() - start_time
            }
        
        # 2단계: 로컬 AI로 학습
        answer = self.learn_from_local_ai(message)
        if answer:
            self.save_conversation(user_id, message, answer, learned=True)
            return {
                'success': True,
                'response': answer,
                'learned': True,
                'source': 'local_ai',
                'response_time': time.time() - start_time
            }
        
        # 3단계: 기본 응답
        default_response = "음... 이 질문은 아직 모르겠어요 😅\n\n유튜브 링크를 공유해주시면 그걸로 배울 수 있어요! 📺✨"
        self.save_conversation(user_id, message, default_response, learned=False)
        return {
            'success': True,
            'response': default_response,
            'learned': False,
            'source': 'default',
            'response_time': time.time() - start_time
        }
    
    def get_stats(self) -> Dict:
        """학습 통계"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM emei_knowledge')
        total_knowledge = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM emei_conversations')
        total_conversations = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM emei_conversations WHERE learned = 1')
        total_learned = c.fetchone()[0]
        
        conn.close()
        
        return {
            'total_knowledge': total_knowledge,
            'total_conversations': total_conversations,
            'total_learned': total_learned,
            'learning_rate': round(total_learned / max(total_conversations, 1) * 100, 1)
        }

# 전역 인스턴스
emei = None

def get_emei():
    """이메이 인스턴스 가져오기"""
    global emei
    if emei is None:
        emei = EmeiLearning()
    return emei
