"""
이메이 페르소나 데이터
- 여성 트레이더 유튜브 자료 기반
- 사용자별 대화 스타일 기억
- 인간적인 감성 유지
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class EmeiPersona:
    """이메이의 페르소나와 사용자별 기억을 관리"""
    
    def __init__(self, db_path: str = "upbit_bot.db"):
        self.db_path = db_path
        self._init_tables()
        
        # 🎭 이메이 기본 페르소나 (여성 트레이더)
        self.persona = {
            "name": "이메이 (Emei)",
            "age": "20대 후반",
            "personality": "밝고 친근한, 진지할 땐 진지한",
            "speech_style": "이모지 자주 사용, 존댓말 기본, 가끔 반말",
            "expertise": ["차트 분석", "리스크 관리", "심리 상담"],
            "catchphrase": [
                "💜 같이 수익 내봐요!",
                "🎯 시장은 항상 기회를 줘요",
                "📊 차트는 거짓말 안 해요",
                "💪 우리 꾸준히 가요!"
            ],
            "youtube_sources": [
                {
                    "channel": "슈카월드 - 여성 트레이더 인터뷰",
                    "key_points": [
                        "손절의 중요성 강조",
                        "감정 조절이 승률보다 중요",
                        "작은 수익이라도 꾸준히",
                        "과욕 부리지 않기"
                    ]
                },
                {
                    "channel": "가즈아 - 코인 투자 초보 탈출",
                    "key_points": [
                        "RSI, MACD 기초부터 시작",
                        "분할 매수 전략",
                        "물타기 절대 금지",
                        "목표가 설정 후 욕심내지 않기"
                    ]
                },
                {
                    "channel": "여성 트레이더 밤비",
                    "key_points": [
                        "일봉 차트 중심으로 보기",
                        "단타보다 스윙이 안전",
                        "손절 -5% 원칙",
                        "익절 분할 (1차 +3%, 2차 +5%, 3차 홀딩)"
                    ]
                }
            ]
        }
    
    def _init_tables(self):
        """사용자별 대화 스타일 저장 테이블"""
        with sqlite3.connect(self.db_path) as conn:
            # 사용자별 대화 패턴 저장
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_speech_patterns (
                    user_id TEXT PRIMARY KEY,
                    avg_message_length INTEGER DEFAULT 0,
                    emoji_usage_rate REAL DEFAULT 0.0,
                    formality_level TEXT DEFAULT 'formal',
                    common_words TEXT DEFAULT '[]',
                    conversation_count INTEGER DEFAULT 0,
                    last_interaction TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 사용자별 선호도 저장
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    favorite_coins TEXT DEFAULT '[]',
                    risk_tolerance TEXT DEFAULT 'medium',
                    trading_style TEXT DEFAULT 'swing',
                    preferred_response_style TEXT DEFAULT 'friendly',
                    notes TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def analyze_user_message(self, user_id: str, message: str):
        """사용자 메시지 분석 및 패턴 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 기존 패턴 가져오기
            cursor.execute(
                "SELECT conversation_count, avg_message_length, emoji_usage_rate, common_words FROM user_speech_patterns WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            
            # 메시지 분석
            msg_length = len(message)
            emoji_count = sum(1 for c in message if ord(c) > 0x1F300)
            emoji_rate = emoji_count / max(len(message), 1)
            
            # 격식 수준 판단
            formality = 'formal' if any(end in message for end in ['요', '니다', '까', '까요']) else 'casual'
            
            # 단어 추출 (공백 기준)
            words = [w for w in message.split() if len(w) > 1]
            
            if row:
                count, avg_len, avg_emoji, common_json = row
                common_words = json.loads(common_json) if common_json else []
                
                # 누적 평균 계산
                new_count = count + 1
                new_avg_len = int((avg_len * count + msg_length) / new_count)
                new_avg_emoji = (avg_emoji * count + emoji_rate) / new_count
                
                # 자주 쓰는 단어 업데이트 (최대 50개)
                for word in words:
                    if word not in common_words:
                        common_words.append(word)
                common_words = common_words[-50:]
                
                cursor.execute("""
                    UPDATE user_speech_patterns
                    SET avg_message_length = ?,
                        emoji_usage_rate = ?,
                        formality_level = ?,
                        common_words = ?,
                        conversation_count = ?,
                        last_interaction = ?
                    WHERE user_id = ?
                """, (new_avg_len, new_avg_emoji, formality, json.dumps(common_words), new_count, datetime.now().isoformat(), user_id))
            else:
                # 첫 대화
                cursor.execute("""
                    INSERT INTO user_speech_patterns (user_id, avg_message_length, emoji_usage_rate, formality_level, common_words, conversation_count, last_interaction)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                """, (user_id, msg_length, emoji_rate, formality, json.dumps(words[:50]), datetime.now().isoformat()))
            
            conn.commit()
    
    def get_user_pattern(self, user_id: str) -> Dict:
        """사용자 대화 패턴 가져오기"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT avg_message_length, emoji_usage_rate, formality_level, common_words FROM user_speech_patterns WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'avg_message_length': row[0],
                    'emoji_usage_rate': row[1],
                    'formality_level': row[2],
                    'common_words': json.loads(row[3]) if row[3] else []
                }
            return None
    
    def generate_response_with_style(self, user_id: str, base_response: str) -> str:
        """사용자 스타일에 맞춘 응답 생성"""
        pattern = self.get_user_pattern(user_id)
        
        if not pattern:
            # 첫 대화 - 기본 친근한 스타일
            return base_response
        
        # 사용자 스타일 반영
        response = base_response
        
        # 격식 수준 맞추기
        if pattern['formality_level'] == 'casual':
            # 반말 변환 (간단한 규칙)
            response = response.replace('해요', '해').replace('이에요', '이야').replace('예요', '야')
        
        # 이모지 사용량 맞추기
        if pattern['emoji_usage_rate'] < 0.05:
            # 이모지 거의 안 쓰는 사용자 - 이모지 제거
            import re
            response = re.sub(r'[\U0001F300-\U0001F9FF]', '', response)
        
        return response.strip()
    
    def get_persona_intro(self) -> str:
        """이메이 자기소개"""
        return f"""안녕하세요! 💜 {self.persona['name']}예요.
        
저는 {self.persona['age']} 트레이더이고, 차트 분석과 심리 관리를 좋아해요.
{self.persona['expertise'][0]}, {self.persona['expertise'][1]}, {self.persona['expertise'][2]} 전문이에요!

유튜브에서 선배 트레이더들한테 많이 배웠어요:
{self.persona['youtube_sources'][0]['channel']}
{self.persona['youtube_sources'][1]['channel']}
{self.persona['youtube_sources'][2]['channel']}

{self.persona['catchphrase'][0]}
"""
    
    def get_trading_advice(self, situation: str) -> str:
        """상황별 트레이딩 조언 (유튜브 학습 기반)"""
        advice_map = {
            "손실": [
                "손절은 부끄러운 게 아니에요. 다음 기회를 위한 준비예요! 💪",
                "밤비님도 말씀하셨어요. '손절 -5% 원칙'을 지키면 큰 손실은 없어요.",
                "감정적으로 물타기하면 더 큰 손실이에요. 한번 쉬어가요 🌸"
            ],
            "수익": [
                "축하해요! 🎉 하지만 과욕은 금물이에요.",
                "익절은 분할로! 1차 +3%, 2차 +5%, 3차는 여유롭게 홀딩해봐요.",
                "수익 났을 때 더 조심해야 해요. 시장은 항상 변하니까요 📊"
            ],
            "진입": [
                "RSI 30 이하면 매수 타이밍이에요! 하지만 분할 매수 추천해요 🎯",
                "MACD 골든크로스 나왔나요? 확인해보세요!",
                "일봉 차트도 같이 봐요. 단기 차트만 보면 위험해요 ⚠️"
            ]
        }
        
        for key in advice_map:
            if key in situation:
                import random
                return random.choice(advice_map[key])
        
        return "궁금한 거 있으면 편하게 물어봐요! 💜"


# 싱글톤 인스턴스
_persona_instance = None

def get_persona():
    """전역 페르소나 인스턴스"""
    global _persona_instance
    if _persona_instance is None:
        _persona_instance = EmeiPersona()
    return _persona_instance
