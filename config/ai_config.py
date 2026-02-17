"""
🔧 AI 백엔드 통합 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

로컬 AI (Ollama) + GenSpark 풀스택 통합
"""

import os

class AIConfig:
    """AI 백엔드 설정"""
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1. AI 백엔드 선택
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AI_BACKEND = os.getenv('AI_BACKEND', 'local')  # 'local' or 'openai'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2. 로컬 AI (Ollama) 설정
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # 노트북 Ollama (Cloudflare Tunnel)
    LOCAL_AI_HOST = os.getenv('LOCAL_AI_HOST', 'https://infinite-keno-casinos-constantly.trycloudflare.com')
    LOCAL_AI_PORT = os.getenv('LOCAL_AI_PORT', '')
    LOCAL_AI_MODEL = os.getenv('LOCAL_AI_MODEL', 'qwen2.5:7b')
    
    @property
    def local_ai_url(self):
        """로컬 AI URL"""
        # Cloudflare Tunnel uses HTTPS with no port
        if self.LOCAL_AI_HOST.startswith('http'):
            return self.LOCAL_AI_HOST
        return f"http://{self.LOCAL_AI_HOST}:{self.LOCAL_AI_PORT}"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3. OpenAI 설정 (백업용)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4. 자동 폴백 (로컬 실패 시 OpenAI 사용)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    AUTO_FALLBACK = os.getenv('AUTO_FALLBACK', 'true').lower() == 'true'
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5. GenSpark 통합 설정
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    GENSPARK_VIDEO_ENABLED = True      # 영상 생성
    GENSPARK_AUDIO_ENABLED = True      # 음성 생성
    GENSPARK_IMAGE_ENABLED = True      # 이미지 생성
    GENSPARK_SEARCH_ENABLED = True     # 웹 검색
    GENSPARK_ANALYZE_ENABLED = True    # 이미지 분석
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 6. 성능 설정
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    DEFAULT_TEMPERATURE = 0.7          # 창의성 (0~1)
    DEFAULT_MAX_TOKENS = 500           # 최대 토큰
    REQUEST_TIMEOUT = 60               # 타임아웃 (초)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 7. 로깅
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    LOG_AI_REQUESTS = True             # AI 요청 로그
    LOG_COSTS = True                   # 비용 추적
    
    def __repr__(self):
        return f"""
AIConfig:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backend: {self.AI_BACKEND}
Local AI: {self.local_ai_url}
Model: {self.LOCAL_AI_MODEL}
Auto Fallback: {self.AUTO_FALLBACK}
GenSpark Video: {self.GENSPARK_VIDEO_ENABLED}
GenSpark Audio: {self.GENSPARK_AUDIO_ENABLED}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
