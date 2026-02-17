"""
🚀 ChatGPT 직접 통합 클라이언트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

기능:
1. OpenAI GPT-4/3.5 직접 호출
2. 모든 대화 DB 저장
3. 실시간 학습 (피드백 기반)
4. 비용 추적
5. 성능 모니터링
"""

import openai
import sqlite3
import time
import json
from datetime import datetime
from config.openai_config import openai_config

class ChatGPTClient:
    """ChatGPT 직접 연동 클라이언트"""
    
    def __init__(self, db_path='emei_memory.db'):
        self.config = openai_config
        self.db_path = db_path
        
        # OpenAI API 키 설정
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
        else:
            raise ValueError("❌ OPENAI_API_KEY가 설정되지 않았습니다")
        
        # 통계
        self.stats = {
            'total_calls': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'avg_response_time': 0.0,
            'errors': 0,
            'learned_items': 0
        }
        
        # DB 초기화
        self._init_db()
        
        print(f"✅ ChatGPT 클라이언트 초기화 완료")
        print(f"   모델: {self.config.MODEL}")
        print(f"   자동 학습: {self.config.AUTO_LEARN}")
        print(f"   대화 저장: {self.config.SAVE_CONVERSATIONS}")
    
    def _init_db(self):
        """DB 테이블 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ChatGPT 대화 기록
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatgpt_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                user_message TEXT,
                assistant_reply TEXT,
                model TEXT,
                tokens INTEGER,
                cost REAL,
                response_time REAL,
                emotion TEXT,
                persona TEXT,
                learned BOOLEAN DEFAULT 0,
                feedback INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 비용 추적
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatgpt_costs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_calls INTEGER,
                total_tokens INTEGER,
                total_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 학습 데이터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chatgpt_learning (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE,
                answer TEXT,
                source TEXT DEFAULT 'chatgpt',
                confidence REAL DEFAULT 1.0,
                use_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def chat(self, user_message, system_prompt=None, user_id='default', emotion=None, persona=None):
        """
        ChatGPT 대화
        
        Args:
            user_message: 사용자 메시지
            system_prompt: 시스템 프롬프트 (이메이 페르소나)
            user_id: 사용자 ID
            emotion: 감정 (선택)
            persona: 페르소나 (선택)
        
        Returns:
            {
                'reply': '답변',
                'learned': True/False,
                'cached': True/False,
                'cost': 0.001,
                'tokens': 150,
                'response_time': 1.2,
                'model': 'gpt-3.5-turbo'
            }
        """
        
        start_time = time.time()
        
        # 1. 캐시 확인 (학습된 답변)
        if self.config.USE_CACHE:
            cached_answer = self._get_cached_answer(user_message)
            if cached_answer:
                response_time = time.time() - start_time
                
                self._update_use_count(user_message)
                
                return {
                    'reply': cached_answer,
                    'learned': True,
                    'cached': True,
                    'cost': 0.0,
                    'tokens': 0,
                    'response_time': response_time,
                    'model': 'cache'
                }
        
        # 2. ChatGPT 호출
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": user_message})
            
            response = openai.ChatCompletion.create(
                model=self.config.MODEL,
                messages=messages,
                temperature=self.config.TEMPERATURE,
                max_tokens=self.config.MAX_TOKENS,
                top_p=self.config.TOP_P,
                frequency_penalty=self.config.FREQUENCY_PENALTY,
                presence_penalty=self.config.PRESENCE_PENALTY,
                timeout=self.config.TIMEOUT
            )
            
            # 응답 파싱
            reply = response.choices[0].message.content
            tokens = response.usage.total_tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # 비용 계산
            cost = self.config.estimate_cost(input_tokens, output_tokens)
            
            response_time = time.time() - start_time
            
            # 3. DB 저장
            if self.config.SAVE_CONVERSATIONS:
                self._save_conversation(
                    user_id=user_id,
                    user_message=user_message,
                    assistant_reply=reply,
                    model=self.config.MODEL,
                    tokens=tokens,
                    cost=cost,
                    response_time=response_time,
                    emotion=emotion,
                    persona=persona
                )
            
            # 4. 자동 학습
            learned = False
            if self.config.AUTO_LEARN:
                learned = self._learn_answer(user_message, reply)
                if learned:
                    self.stats['learned_items'] += 1
            
            # 5. 통계 업데이트
            self.stats['total_calls'] += 1
            self.stats['total_tokens'] += tokens
            self.stats['total_cost'] += cost
            self.stats['avg_response_time'] = (
                (self.stats['avg_response_time'] * (self.stats['total_calls'] - 1) + response_time) 
                / self.stats['total_calls']
            )
            
            # 6. 로깅
            if self.config.LOG_ALL_REQUESTS:
                print(f"💬 ChatGPT: {user_message[:50]}...")
                print(f"   응답: {reply[:50]}...")
                print(f"   비용: ${cost:.4f} | 토큰: {tokens} | 시간: {response_time:.2f}s")
                if learned:
                    print(f"   ✅ 학습 완료")
            
            return {
                'reply': reply,
                'learned': learned,
                'cached': False,
                'cost': cost,
                'tokens': tokens,
                'response_time': response_time,
                'model': self.config.MODEL
            }
        
        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ ChatGPT 오류: {e}")
            raise
    
    def _get_cached_answer(self, question):
        """캐시된 답변 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 정확히 같은 질문
        cursor.execute('''
            SELECT answer FROM chatgpt_learning
            WHERE question = ?
            ORDER BY confidence DESC, use_count DESC
            LIMIT 1
        ''', (question,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
        
        return None
    
    def _update_use_count(self, question):
        """사용 횟수 업데이트"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chatgpt_learning
            SET use_count = use_count + 1,
                last_used = CURRENT_TIMESTAMP
            WHERE question = ?
        ''', (question,))
        
        conn.commit()
        conn.close()
    
    def _save_conversation(self, user_id, user_message, assistant_reply, model, tokens, cost, response_time, emotion, persona):
        """대화 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chatgpt_conversations
            (user_id, user_message, assistant_reply, model, tokens, cost, response_time, emotion, persona)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_message, assistant_reply, model, tokens, cost, response_time, emotion, persona))
        
        conn.commit()
        conn.close()
    
    def _learn_answer(self, question, answer, confidence=1.0):
        """답변 학습"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO chatgpt_learning
                (question, answer, confidence, use_count, last_used)
                VALUES (?, ?, ?, COALESCE((SELECT use_count FROM chatgpt_learning WHERE question = ?), 0), CURRENT_TIMESTAMP)
            ''', (question, answer, confidence, question))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"⚠️ 학습 오류: {e}")
            return False
    
    def save_feedback(self, user_message, feedback):
        """피드백 저장 (👍=1, 👎=-1)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE chatgpt_conversations
            SET feedback = ?
            WHERE user_message = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (feedback, user_message))
        
        conn.commit()
        conn.close()
        
        print(f"{'👍' if feedback > 0 else '👎'} 피드백 저장: {user_message[:30]}...")
    
    def get_stats(self):
        """통계 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 오늘 비용
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT SUM(cost), COUNT(*)
            FROM chatgpt_conversations
            WHERE DATE(created_at) = ?
        ''', (today,))
        
        row = cursor.fetchone()
        today_cost = row[0] or 0.0
        today_calls = row[1] or 0
        
        # 학습된 항목 수
        cursor.execute('SELECT COUNT(*) FROM chatgpt_learning')
        learned_count = cursor.fetchone()[0]
        
        # 평균 만족도
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN feedback = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as satisfaction
            FROM chatgpt_conversations
            WHERE feedback != 0
        ''')
        
        row = cursor.fetchone()
        satisfaction = row[0] if row[0] else 0.0
        
        conn.close()
        
        return {
            **self.stats,
            'learned_count': learned_count,
            'today_cost': today_cost,
            'today_calls': today_calls,
            'satisfaction': satisfaction,
            'budget_used': (self.stats['total_cost'] / self.config.MONTHLY_BUDGET) * 100
        }
    
    def get_learning_data(self, limit=100):
        """학습 데이터 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT question, answer, confidence, use_count, created_at
            FROM chatgpt_learning
            ORDER BY use_count DESC, confidence DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'question': row[0],
                'answer': row[1],
                'confidence': row[2],
                'use_count': row[3],
                'created_at': row[4]
            }
            for row in rows
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 전역 인스턴스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# OpenAI API 키가 설정된 경우에만 인스턴스 생성
if openai_config.is_configured():
    chatgpt_client = ChatGPTClient()
    print("✅ ChatGPT 클라이언트 활성화")
else:
    chatgpt_client = None
    print("⚠️ OPENAI_API_KEY가 설정되지 않음 - ChatGPT 비활성화")
