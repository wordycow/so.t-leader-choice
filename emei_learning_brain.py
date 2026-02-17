#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 이메이 학습 두뇌 (Learning Brain)
아이처럼 질문하고, 웹 검색으로 배우고, 영구 저장하는 시스템
"""

import sqlite3
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re

DB_PATH = Path(__file__).parent / "emei_memory.db"

class EmeiLearningBrain:
    """이메이의 학습 두뇌"""
    
    def __init__(self):
        self.init_learning_tables()
    
    def init_learning_tables(self):
        """학습 관련 테이블 초기화"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 학습된 지식 테이블
        c.execute('''
            CREATE TABLE IF NOT EXISTS learned_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                source TEXT,
                confidence REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 0,
                last_used DATETIME,
                learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT,
                keywords TEXT
            )
        ''')
        
        # 학습 과정 로그
        c.execute('''
            CREATE TABLE IF NOT EXISTS learning_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                search_query TEXT,
                search_results_count INTEGER,
                learned BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 이메이가 모르는 것 (추후 학습 대상)
        c.execute('''
            CREATE TABLE IF NOT EXISTS unknown_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                asked_count INTEGER DEFAULT 1,
                first_asked DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_asked DATETIME DEFAULT CURRENT_TIMESTAMP,
                priority INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Learning Brain 초기화 완료")
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """웹 검색 (DuckDuckGo HTML 스크래핑)"""
        try:
            # DuckDuckGo HTML 검색
            url = "https://html.duckduckgo.com/html/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            data = {'q': query}
            
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 간단한 파싱 (정규표현식)
                results = []
                
                # 제목과 스니펫 추출
                title_pattern = r'<a class="result__a" href="[^"]*">([^<]+)</a>'
                snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+)</a>'
                
                titles = re.findall(title_pattern, response.text)
                snippets = re.findall(snippet_pattern, response.text)
                
                for i in range(min(len(titles), len(snippets), max_results)):
                    results.append({
                        'title': titles[i].strip(),
                        'snippet': snippets[i].strip()
                    })
                
                return results
            
            return []
        except Exception as e:
            print(f"⚠️ 웹 검색 실패: {e}")
            return []
    
    def learn_from_web(self, question: str) -> Optional[str]:
        """웹에서 학습 (질문 → 검색 → 답변 생성 → 저장)"""
        
        # 1. 웹 검색
        search_results = self.search_web(question, max_results=3)
        
        if not search_results:
            # 모르는 질문 저장
            self.save_unknown_question(question)
            return None
        
        # 2. 검색 결과를 기반으로 답변 생성
        answer_parts = []
        for i, result in enumerate(search_results[:3], 1):
            snippet = result['snippet'][:200]  # 처음 200자만
            answer_parts.append(f"{snippet}")
        
        answer = " ".join(answer_parts)
        
        # 3. 학습 저장
        self.save_learned_knowledge(
            question=question,
            answer=answer,
            source="web_search",
            confidence=0.7,
            category=self.categorize_question(question)
        )
        
        # 4. 학습 로그
        self.log_learning(question, question, len(search_results), learned=True)
        
        print(f"📚 학습 완료: {question[:30]}...")
        return answer
    
    def categorize_question(self, question: str) -> str:
        """질문 카테고리 분류"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['비트코인', '이더리움', '리플', '코인', '암호화폐']):
            return 'coin'
        elif any(word in question_lower for word in ['rsi', 'macd', '볼린저', '전략', '지표']):
            return 'strategy'
        elif any(word in question_lower for word in ['사야', '팔아야', '매수', '매도', '투자']):
            return 'trading'
        elif any(word in question_lower for word in ['손실', '수익', '불안', '우울', '기분']):
            return 'emotion'
        elif any(word in question_lower for word in ['이메이', '너', '당신']):
            return 'personal'
        else:
            return 'general'
    
    def save_learned_knowledge(self, question: str, answer: str, source: str, 
                                confidence: float = 0.5, category: str = 'general'):
        """학습한 지식 저장"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 키워드 추출
        keywords = self.extract_keywords(question)
        
        c.execute('''
            INSERT INTO learned_knowledge 
            (question, answer, source, confidence, category, keywords)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (question, answer, source, confidence, category, json.dumps(keywords)))
        
        conn.commit()
        conn.close()
    
    def extract_keywords(self, text: str) -> List[str]:
        """키워드 추출 (간단한 방법)"""
        # 한글 단어 추출
        korean_words = re.findall(r'[가-힣]+', text)
        # 2글자 이상만
        keywords = [w for w in korean_words if len(w) >= 2]
        return keywords[:5]  # 최대 5개
    
    def get_learned_answer(self, question: str) -> Optional[str]:
        """학습된 지식에서 답변 찾기"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 정확히 일치하는 질문 찾기
        c.execute('''
            SELECT answer, confidence
            FROM learned_knowledge
            WHERE question = ?
            ORDER BY confidence DESC, usage_count DESC
            LIMIT 1
        ''', (question,))
        
        row = c.fetchone()
        
        if row:
            answer, confidence = row
            
            # 사용 횟수 증가
            c.execute('''
                UPDATE learned_knowledge
                SET usage_count = usage_count + 1,
                    last_used = datetime('now')
                WHERE question = ?
            ''', (question,))
            
            conn.commit()
            conn.close()
            
            return answer if confidence > 0.3 else None
        
        # 유사한 질문 찾기 (키워드 기반)
        keywords = self.extract_keywords(question)
        
        if keywords:
            keyword_pattern = '%' + '%'.join(keywords[:3]) + '%'
            c.execute('''
                SELECT answer, confidence
                FROM learned_knowledge
                WHERE question LIKE ? OR keywords LIKE ?
                ORDER BY confidence DESC, usage_count DESC
                LIMIT 1
            ''', (keyword_pattern, keyword_pattern))
            
            row = c.fetchone()
            conn.close()
            
            if row:
                return row[0] if row[1] > 0.3 else None
        
        conn.close()
        return None
    
    def save_unknown_question(self, question: str):
        """모르는 질문 저장 (추후 학습)"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 이미 있는지 확인
        c.execute('''
            SELECT id, asked_count FROM unknown_questions
            WHERE question = ?
        ''', (question,))
        
        row = c.fetchone()
        
        if row:
            # 카운트 증가
            c.execute('''
                UPDATE unknown_questions
                SET asked_count = asked_count + 1,
                    last_asked = datetime('now'),
                    priority = asked_count + 1
                WHERE id = ?
            ''', (row[0],))
        else:
            # 새로 추가
            c.execute('''
                INSERT INTO unknown_questions (question)
                VALUES (?)
            ''', (question,))
        
        conn.commit()
        conn.close()
    
    def log_learning(self, question: str, search_query: str, 
                     results_count: int, learned: bool):
        """학습 과정 로그"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO learning_log
            (question, search_query, search_results_count, learned)
            VALUES (?, ?, ?, ?)
        ''', (question, search_query, results_count, learned))
        
        conn.commit()
        conn.close()
    
    def get_learning_stats(self) -> Dict:
        """학습 통계"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # 총 학습 개수
        c.execute('SELECT COUNT(*) FROM learned_knowledge')
        total_learned = c.fetchone()[0]
        
        # 카테고리별 학습 개수
        c.execute('''
            SELECT category, COUNT(*) 
            FROM learned_knowledge
            GROUP BY category
            ORDER BY COUNT(*) DESC
        ''')
        categories = dict(c.fetchall())
        
        # 모르는 질문 개수
        c.execute('SELECT COUNT(*) FROM unknown_questions')
        unknown_count = c.fetchone()[0]
        
        # 가장 많이 사용된 지식 TOP 5
        c.execute('''
            SELECT question, usage_count
            FROM learned_knowledge
            ORDER BY usage_count DESC
            LIMIT 5
        ''')
        top_knowledge = c.fetchall()
        
        conn.close()
        
        return {
            'total_learned': total_learned,
            'categories': categories,
            'unknown_count': unknown_count,
            'top_knowledge': [{'question': q, 'usage': c} for q, c in top_knowledge]
        }
    
    def ask_and_learn(self, question: str) -> str:
        """질문 → 학습된 지식 확인 → 없으면 웹 검색 → 저장"""
        
        # 1. 이미 학습한 지식인지 확인
        learned_answer = self.get_learned_answer(question)
        if learned_answer:
            print(f"💡 학습된 지식 사용: {question[:30]}...")
            return learned_answer
        
        # 2. 웹에서 학습
        web_answer = self.learn_from_web(question)
        if web_answer:
            print(f"🌐 웹에서 학습 완료: {question[:30]}...")
            return web_answer
        
        # 3. 학습 실패
        print(f"❓ 학습 실패: {question[:30]}...")
        return None


# 테스트
if __name__ == "__main__":
    brain = EmeiLearningBrain()
    
    print("\n🧠 이메이 학습 두뇌 테스트\n")
    
    # 테스트 질문들
    test_questions = [
        "비트코인 반감기가 뭐야?",
        "RSI 지표는 어떻게 봐?",
        "손실 났을 때 어떻게 대처해?"
    ]
    
    for q in test_questions:
        print(f"\n❓ 질문: {q}")
        answer = brain.ask_and_learn(q)
        if answer:
            print(f"✅ 답변: {answer[:100]}...")
        else:
            print("❌ 답변 없음 (추후 학습 필요)")
    
    print("\n📊 학습 통계:")
    stats = brain.get_learning_stats()
    print(f"  총 학습: {stats['total_learned']}개")
    print(f"  카테고리: {stats['categories']}")
    print(f"  모르는 질문: {stats['unknown_count']}개")
    print(f"  TOP 지식: {stats['top_knowledge']}")
