"""
🤖 통합 AI 클라이언트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

로컬 AI (Ollama) + OpenAI + 자동 폴백
"""

import requests
import openai
import json
import time
from datetime import datetime
from config.ai_config import AIConfig

class AIClient:
    """통합 AI 클라이언트"""
    
    def __init__(self):
        self.config = AIConfig()
        
        # OpenAI 설정
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
        
        # 통계
        self.stats = {
            'local_calls': 0,
            'openai_calls': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'errors': 0
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 메인 대화 함수
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def chat(self, messages, temperature=None, max_tokens=None, stream=False):
        """
        AI 대화 (자동 폴백)
        
        Args:
            messages: OpenAI 포맷 메시지
                [
                    {"role": "system", "content": "..."},
                    {"role": "user", "content": "..."}
                ]
            temperature: 창의성 (0~1)
            max_tokens: 최대 토큰
            stream: 스트리밍 여부
        
        Returns:
            {
                'content': '답변 내용',
                'backend': 'local' or 'openai',
                'model': '모델명',
                'cost': 비용,
                'tokens': 토큰 수,
                'duration': 소요 시간(초)
            }
        """
        
        temperature = temperature or self.config.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or self.config.DEFAULT_MAX_TOKENS
        
        start_time = time.time()
        
        # 1차: 로컬 AI 시도
        if self.config.AI_BACKEND == 'local':
            try:
                result = self._chat_local(messages, temperature, max_tokens, stream)
                duration = time.time() - start_time
                result['duration'] = duration
                
                self.stats['local_calls'] += 1
                
                if self.config.LOG_AI_REQUESTS:
                    self._log_request('local', messages, result)
                
                return result
                
            except Exception as e:
                print(f"⚠️ 로컬 AI 오류: {e}")
                self.stats['errors'] += 1
                
                if self.config.AUTO_FALLBACK:
                    print("🔄 OpenAI로 폴백...")
                    result = self._chat_openai(messages, temperature, max_tokens, stream)
                    duration = time.time() - start_time
                    result['duration'] = duration
                    result['fallback'] = True
                    
                    self.stats['openai_calls'] += 1
                    
                    return result
                else:
                    raise
        
        # 2차: OpenAI
        else:
            result = self._chat_openai(messages, temperature, max_tokens, stream)
            duration = time.time() - start_time
            result['duration'] = duration
            
            self.stats['openai_calls'] += 1
            
            if self.config.LOG_AI_REQUESTS:
                self._log_request('openai', messages, result)
            
            return result
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 로컬 AI (Ollama)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _chat_local(self, messages, temperature, max_tokens, stream):
        """로컬 AI (Ollama) 호출"""
        
        # 메시지 포맷 변환
        prompt = self._messages_to_prompt(messages)
        
        # Ollama API 호출
        url = f"{self.config.local_ai_url}/api/generate"
        
        payload = {
            'model': self.config.LOCAL_AI_MODEL,
            'prompt': prompt,
            'stream': stream,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        }
        
        response = requests.post(
            url,
            json=payload,
            timeout=self.config.REQUEST_TIMEOUT
        )
        
        response.raise_for_status()
        
        data = response.json()
        answer = data.get('response', '')
        
        return {
            'content': answer,
            'backend': 'local',
            'model': self.config.LOCAL_AI_MODEL,
            'cost': 0.0,
            'tokens': len(answer.split()),  # 대략적인 토큰 수
            'url': self.config.local_ai_url
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # OpenAI
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _chat_openai(self, messages, temperature, max_tokens, stream):
        """OpenAI 호출"""
        
        response = openai.ChatCompletion.create(
            model=self.config.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        if stream:
            # TODO: 스트리밍 처리
            return response
        
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens
        
        # 비용 계산 (GPT-4 기준)
        cost = tokens * 0.00003
        
        self.stats['total_cost'] += cost
        self.stats['total_tokens'] += tokens
        
        return {
            'content': answer,
            'backend': 'openai',
            'model': self.config.OPENAI_MODEL,
            'cost': cost,
            'tokens': tokens
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 헬퍼 함수
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def _messages_to_prompt(self, messages):
        """OpenAI 메시지 → Ollama 프롬프트"""
        
        prompt = ""
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                prompt += f"System: {content}\n\n"
            elif role == 'user':
                prompt += f"User: {content}\n\n"
            elif role == 'assistant':
                prompt += f"Assistant: {content}\n\n"
        
        prompt += "Assistant: "
        
        return prompt
    
    def _log_request(self, backend, messages, result):
        """요청 로그"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'backend': backend,
            'model': result['model'],
            'cost': result.get('cost', 0),
            'tokens': result.get('tokens', 0),
            'duration': result.get('duration', 0),
            'user_message': messages[-1]['content'][:100] if messages else ''
        }
        
        print(f"📊 AI Request: {json.dumps(log_entry, ensure_ascii=False)}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 상태 확인
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def health_check(self):
        """AI 서버 상태 확인"""
        
        if self.config.AI_BACKEND == 'local':
            try:
                url = f"{self.config.local_ai_url}/api/tags"
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                
                data = response.json()
                models = data.get('models', [])
                
                return {
                    'status': 'online',
                    'backend': 'local',
                    'url': self.config.local_ai_url,
                    'models': [m['name'] for m in models],
                    'cost': '$0/month',
                    'stats': self.stats
                }
            except Exception as e:
                return {
                    'status': 'offline',
                    'backend': 'local',
                    'url': self.config.local_ai_url,
                    'error': str(e),
                    'fallback_available': self.config.AUTO_FALLBACK
                }
        
        else:
            return {
                'status': 'online',
                'backend': 'openai',
                'model': self.config.OPENAI_MODEL,
                'cost': f'${self.stats["total_cost"]:.2f}',
                'stats': self.stats
            }
    
    def get_stats(self):
        """통계 조회"""
        return {
            **self.stats,
            'cost_saved': self.stats['local_calls'] * 0.002,  # 로컬 사용으로 절약한 비용
            'total_calls': self.stats['local_calls'] + self.stats['openai_calls']
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 전역 인스턴스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ai_client = AIClient()
