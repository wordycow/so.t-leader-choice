"""
🆓 완전 무료 학습 시스템
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

비용: $0
속도: 빠름
제한: 없음

전략:
1. 로컬 AI (Ollama) 사용 - 무료!
2. 모든 대화 DB 저장 - 무료!
3. 학습된 답변 재사용 - 무료!
4. 웹 검색으로 정보 수집 - 무료!
"""

import sqlite3
import time
import requests
from datetime import datetime
import json

class FreeLearningSystem:
    """100% 무료 학습 시스템"""
    
    def __init__(self, db_path='emei_memory.db'):
        self.db_path = db_path
        self.local_ai_url = "https://infinite-keno-casinos-constantly.trycloudflare.com"
        self.model = "qwen2.5:7b"
        
        self.stats = {
            'total_learned': 0,
            'total_reused': 0,
            'total_searches': 0,
            'total_cost': 0.0  # 항상 $0!
        }
        
        self._init_db()
        print("✅ 무료 학습 시스템 초기화 완료")
        print(f"   로컬 AI: {self.local_ai_url}")
        print(f"   모델: {self.model}")
        print(f"   비용: $0 (100% 무료!)")
    
    def _init_db(self):
        """DB 초기화"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 무료 학습 데이터
        c.execute('''
            CREATE TABLE IF NOT EXISTS free_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE,
                answer TEXT,
                source TEXT DEFAULT 'local_ai',
                quality_score REAL DEFAULT 0.8,
                use_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 웹 검색 캐시 (무료 정보 수집)
        c.execute('''
            CREATE TABLE IF NOT EXISTS web_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT UNIQUE,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 대화 기록
        c.execute('''
            CREATE TABLE IF NOT EXISTS free_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                user_message TEXT,
                ai_response TEXT,
                response_time REAL,
                cost REAL DEFAULT 0.0,
                learned BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_learned_answer(self, question):
        """학습된 답변 찾기 (무료!)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 정확히 같은 질문
        c.execute('''
            SELECT answer, use_count, quality_score 
            FROM free_learning 
            WHERE question = ?
        ''', (question,))
        
        row = c.fetchone()
        
        if row:
            # 사용 횟수 증가
            c.execute('''
                UPDATE free_learning 
                SET use_count = use_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE question = ?
            ''', (question,))
            conn.commit()
            conn.close()
            
            self.stats['total_reused'] += 1
            
            return {
                'answer': row[0],
                'use_count': row[1] + 1,
                'quality': row[2],
                'cached': True,
                'cost': 0.0
            }
        
        conn.close()
        return None
    
    def call_local_ai(self, question, context=None):
        """로컬 AI 호출 (무료!)"""
        try:
            # 시스템 프롬프트
            system_prompt = """당신은 "이메이(Emei)"입니다. 25세 여성 AI 트레이딩 스트리머.

핵심 특징:
- 구체적이고 실용적인 답변 (숫자, 지표 포함)
- 친근하고 격려하는 말투
- 투자 위험 경고

예시:
질문: "비트코인 지금 사도 돼?"
답변: "비트코인 현재 RSI 35로 과매도 구간이에요! 매수 타이밍입니다. 목표가 1억원, 손절가 9천만원 추천해요. 💪"
"""
            
            # 컨텍스트 추가 (웹 검색 결과 등)
            if context:
                system_prompt += f"\n\n참고 정보:\n{context}"
            
            # Ollama API 호출
            url = f"{self.local_ai_url}/api/generate"
            
            payload = {
                'model': self.model,
                'prompt': f"System: {system_prompt}\n\nUser: {question}\n\nAssistant:",
                'stream': False,
                'options': {
                    'temperature': 0.8,
                    'num_predict': 300
                }
            }
            
            start_time = time.time()
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            answer = data.get('response', '').strip()
            
            response_time = time.time() - start_time
            
            return {
                'answer': answer,
                'response_time': response_time,
                'cost': 0.0,  # 무료!
                'model': self.model,
                'source': 'local_ai'
            }
        
        except Exception as e:
            print(f"⚠️ 로컬 AI 오류: {e}")
            return None
    
    def search_web(self, query):
        """웹 검색으로 무료 정보 수집"""
        # 캐시 확인
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT results FROM web_cache WHERE query = ?', (query,))
        row = c.fetchone()
        
        if row:
            conn.close()
            return json.loads(row[0])
        
        conn.close()
        
        # 실제 검색 (DuckDuckGo - 무료!)
        try:
            # 간단한 HTML 파싱으로 무료 검색
            search_url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # 간단한 텍스트 추출 (정규식 사용)
                import re
                
                # <a class="result__snippet"> 태그에서 텍스트 추출
                snippets = re.findall(r'result__snippet">(.*?)</a>', response.text, re.DOTALL)
                
                if snippets:
                    results = [re.sub(r'<.*?>', '', s).strip() for s in snippets[:3]]
                    
                    # 캐시에 저장
                    conn = sqlite3.connect(self.db_path)
                    c = conn.cursor()
                    
                    c.execute('''
                        INSERT OR REPLACE INTO web_cache (query, results)
                        VALUES (?, ?)
                    ''', (query, json.dumps(results, ensure_ascii=False)))
                    
                    conn.commit()
                    conn.close()
                    
                    self.stats['total_searches'] += 1
                    
                    return results
            
            return []
        
        except Exception as e:
            print(f"⚠️ 웹 검색 오류: {e}")
            return []
    
    def learn_answer(self, question, answer, quality_score=0.8):
        """답변 학습 (DB에 저장 - 무료!)"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT OR REPLACE INTO free_learning 
                (question, answer, quality_score, use_count, last_used)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
            ''', (question, answer, quality_score))
            
            conn.commit()
            conn.close()
            
            self.stats['total_learned'] += 1
            
            print(f"  📚 학습 완료: '{question[:30]}...'")
            return True
        
        except Exception as e:
            print(f"⚠️ 학습 오류: {e}")
            return False
    
    def save_conversation(self, user_id, user_message, ai_response, response_time, learned):
        """대화 저장 (무료!)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO free_conversations
            (user_id, user_message, ai_response, response_time, cost, learned)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, user_message, ai_response, response_time, 0.0, learned))
        
        conn.commit()
        conn.close()
    
    def chat(self, question, user_id='default'):
        """
        무료 대화 + 학습
        
        1. 캐시 확인 (학습된 답변)
        2. 로컬 AI 호출 (무료)
        3. 필요시 웹 검색 (무료)
        4. DB 저장 (무료)
        """
        
        print(f"\n{'='*60}")
        print(f"👤 사용자: {question}")
        print(f"{'='*60}")
        
        # 1. 캐시 확인
        print("\n[1단계] 캐시 확인...")
        cached = self.get_learned_answer(question)
        
        if cached:
            print(f"  ✅ 캐시 발견! (사용: {cached['use_count']}회)")
            print(f"  ⚡ 0.1초 | $0 (무료!)")
            print(f"\n🤖 이메이: {cached['answer']}")
            
            self.save_conversation(user_id, question, cached['answer'], 0.1, False)
            
            return {
                'reply': cached['answer'],
                'cached': True,
                'cost': 0.0,
                'response_time': 0.1
            }
        
        print("  ❌ 캐시 없음")
        
        # 2. 로컬 AI 호출
        print("\n[2단계] 로컬 AI 호출...")
        result = self.call_local_ai(question)
        
        if not result:
            return {'reply': '죄송해요, 지금 답변하기 어려워요 😢', 'cost': 0.0}
        
        answer = result['answer']
        response_time = result['response_time']
        
        print(f"  ✅ 응답 완료!")
        print(f"  ⏱️  {response_time:.1f}초 | $0 (무료!)")
        
        # 3. 품질 체크 (모호하면 웹 검색)
        uncertain_keywords = ['잘 모르', '확실하지', '정확히는', '아마도']
        needs_search = any(kw in answer for kw in uncertain_keywords)
        
        if needs_search:
            print("\n[3단계] 웹 검색으로 정보 수집...")
            web_results = self.search_web(question)
            
            if web_results:
                # 웹 정보 추가해서 재생성
                context = "\n".join(web_results[:2])
                result = self.call_local_ai(question, context)
                
                if result:
                    answer = result['answer']
                    response_time += result['response_time']
                    print(f"  ✅ 웹 정보 반영 완료!")
        
        # 4. 학습 (DB 저장)
        print("\n[4단계] 학습...")
        learned = self.learn_answer(question, answer)
        
        # 5. 대화 저장
        self.save_conversation(user_id, question, answer, response_time, learned)
        
        print(f"\n🤖 이메이: {answer}")
        
        return {
            'reply': answer,
            'cached': False,
            'learned': learned,
            'cost': 0.0,
            'response_time': response_time
        }
    
    def get_stats(self):
        """통계 조회"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 학습된 질문 수
        c.execute('SELECT COUNT(*) FROM free_learning')
        total_learned = c.fetchone()[0]
        
        # 총 대화 수
        c.execute('SELECT COUNT(*) FROM free_conversations')
        total_conversations = c.fetchone()[0]
        
        # 캐시 히트율
        c.execute('SELECT SUM(use_count) FROM free_learning')
        total_reuses = c.fetchone()[0] or 0
        
        cache_hit_rate = (total_reuses / total_conversations * 100) if total_conversations > 0 else 0
        
        # 인기 질문
        c.execute('''
            SELECT question, use_count 
            FROM free_learning 
            ORDER BY use_count DESC 
            LIMIT 5
        ''')
        
        top_questions = c.fetchall()
        
        conn.close()
        
        return {
            'total_learned': total_learned,
            'total_conversations': total_conversations,
            'total_reuses': total_reuses,
            'cache_hit_rate': cache_hit_rate,
            'total_cost': 0.0,  # 항상 $0!
            'top_questions': top_questions
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 전역 인스턴스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

free_learning_system = FreeLearningSystem()
