"""
🤖 ChatGPT 직접 연동 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

사용자 메시지: wordycow0001@gmail.com
요구사항:
1. ChatGPT API 직접 연동
2. 모든 대화 서버에 저장
3. 빠른 학습 (실시간)

현재 상태:
- OpenAI API 클라이언트 존재 ✅
- 로컬 AI (Ollama) 사용 중
- 백업: OpenAI 폴백 설정됨

해결책:
→ ChatGPT-4를 기본 백엔드로 전환
→ 모든 대화를 emei_memory.db에 즉시 저장
→ 학습 루프 활성화
"""

import os

class OpenAIDirectConfig:
    """ChatGPT 직접 연동"""
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. API 키 (환경 변수 또는 직접 설정)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. 모델 선택
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # gpt-4: 최고 품질 (비쌈, 느림)
    # gpt-4-turbo-preview: 빠른 GPT-4
    # gpt-3.5-turbo: 빠르고 저렴
    MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. 성능 설정
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TEMPERATURE = 0.8          # 창의성 (0~2, 높을수록 창의적)
    MAX_TOKENS = 500           # 최대 응답 길이
    TOP_P = 0.9               # 샘플링 범위
    FREQUENCY_PENALTY = 0.2   # 반복 방지
    PRESENCE_PENALTY = 0.1    # 주제 다양성
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4. 비용 최적화
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 비용 (2024년 기준):
    # GPT-4: $0.03/1K tokens (입력), $0.06/1K tokens (출력)
    # GPT-3.5-turbo: $0.001/1K tokens (입력), $0.002/1K tokens (출력)
    
    # 비용 한도 (월 $10 = 약 5,000 대화)
    MONTHLY_BUDGET = 10.0  # USD
    COST_ALERT_THRESHOLD = 8.0  # 80% 도달 시 알림
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5. 대화 저장 설정
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    SAVE_CONVERSATIONS = True   # 모든 대화 저장
    SAVE_LEARNING_DATA = True   # 학습 데이터 생성
    SAVE_FEEDBACK = True        # 피드백 저장
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 6. 학습 모드
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AUTO_LEARN = True           # 자동 학습
    LEARN_FROM_FEEDBACK = True  # 피드백 기반 학습
    MIN_CONFIDENCE = 0.7        # 최소 신뢰도 (이하면 재학습)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 7. 속도 최적화
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    TIMEOUT = 30  # 초
    RETRY_COUNT = 2
    USE_CACHE = True  # 유사 질문 캐싱
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 8. 로깅
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    LOG_ALL_REQUESTS = True
    LOG_COSTS = True
    LOG_PERFORMANCE = True
    
    @classmethod
    def is_configured(cls):
        """API 키 설정 확인"""
        return bool(cls.OPENAI_API_KEY)
    
    @classmethod
    def estimate_cost(cls, input_tokens, output_tokens):
        """예상 비용 계산"""
        if cls.MODEL.startswith('gpt-4'):
            input_cost = input_tokens / 1000 * 0.03
            output_cost = output_tokens / 1000 * 0.06
        else:  # GPT-3.5-turbo
            input_cost = input_tokens / 1000 * 0.001
            output_cost = output_tokens / 1000 * 0.002
        
        return input_cost + output_cost
    
    def __repr__(self):
        masked_key = f"{self.OPENAI_API_KEY[:8]}..." if self.OPENAI_API_KEY else "NOT SET"
        return f"""
OpenAI Direct Config:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Key: {masked_key}
Model: {self.MODEL}
Temperature: {self.TEMPERATURE}
Max Tokens: {self.MAX_TOKENS}
Auto Learn: {self.AUTO_LEARN}
Save Conversations: {self.SAVE_CONVERSATIONS}
Monthly Budget: ${self.MONTHLY_BUDGET}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# 전역 인스턴스
openai_config = OpenAIDirectConfig()
