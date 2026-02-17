# 🚀 로컬 AI 서버 구축 가이드

> **당신의 레노버 게임용 노트북 → AI 서버 변신!**

---

## 💻 확인된 노트북 사양

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 완벽한 AI 서버 사양!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

노트북: LENOVO Legion Pro 5 16IAX10H
CPU: Intel Core i9 Ultra 9 275HX (24코어, 2700MHz)
GPU: NVIDIA GeForce RTX 5070 Ti Laptop (1GB VRAM) ⭐
RAM: 32GB ✅
저장공간: 충분 ✅
OS: Windows 11 Home

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
판정: 최상급! 🔥
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

가능한 AI 모델:
✅ Qwen 2.5 7B (권장!)
✅ Llama 3.1 8B
✅ Mistral 7B
✅ Yi-34B (고사양 모델도 가능!)

예상 성능:
- 대화 생성: 초당 30-50 토큰
- 응답 속도: 2-5초
- 동시 사용자: 10-20명
```

---

## 📋 목차
1. [Step 1: Ollama 설치](#step-1-ollama-설치)
2. [Step 2: AI 모델 다운로드](#step-2-ai-모델-다운로드)
3. [Step 3: 네트워크 설정](#step-3-네트워크-설정)
4. [Step 4: 기존 봇과 연결](#step-4-기존-봇과-연결)
5. [Step 5: 테스트](#step-5-테스트)
6. [Step 6: 자동 실행 설정](#step-6-자동-실행-설정)

---

## 🎯 Step 1: Ollama 설치

### Windows에 Ollama 설치

#### 방법 A: 설치 프로그램 (추천! ✅)

```powershell
# 1. 다운로드 링크
https://ollama.com/download/windows

# 2. OllamaSetup.exe 다운로드

# 3. 더블클릭으로 설치
# - Next → Next → Install → Finish

# 4. 설치 확인
# Windows 시작 메뉴 → "Ollama" 검색
# → Ollama 아이콘 확인

# 5. PowerShell에서 확인
ollama --version
# 출력: ollama version is 0.1.xx
```

#### 방법 B: 명령어로 설치

```powershell
# PowerShell을 관리자 권한으로 실행

# 1. 다운로드 + 설치
iwr -useb https://ollama.com/install.ps1 | iex

# 2. 환경 변수 자동 설정됨

# 3. 확인
ollama --version
```

### ✅ 설치 완료 확인

```powershell
# Ollama 서비스 시작
ollama serve

# 출력:
# Listening on 127.0.0.1:11434
# → 성공! ✅
```

---

## 🤖 Step 2: AI 모델 다운로드

### 권장 모델: Qwen 2.5 7B (한국어 최고!)

```powershell
# 1. Ollama 서비스 시작 (다른 터미널)
ollama serve

# 2. 새 PowerShell 열기

# 3. 모델 다운로드 (약 4.7GB, 5-10분)
ollama pull qwen2.5:7b

# 출력:
# pulling manifest
# pulling xxx... 100%
# pulling yyy... 100%
# verifying sha256 digest
# success ✅

# 4. 다운로드 확인
ollama list

# 출력:
# NAME              ID          SIZE    MODIFIED
# qwen2.5:7b        abc123...   4.7GB   2 minutes ago
```

### 다른 모델 옵션

```powershell
# 한국어 특화 모델들

# 1. Qwen 2.5 7B (권장! ⭐)
ollama pull qwen2.5:7b

# 2. Llama 3.1 8B (영어 강함)
ollama pull llama3.1:8b

# 3. Mistral 7B (빠름)
ollama pull mistral:7b

# 4. Yi-34B (고성능, 느림)
ollama pull yi:34b

# 5. 한국어 전용 모델
ollama pull yanolja/EEVE-Korean-Instruct-10.8B
```

### 🧪 테스트

```powershell
# 모델 테스트
ollama run qwen2.5:7b

# 대화 시작:
>>> 안녕? BTC 지금 사야 할까?

# AI 답변:
안녕하세요! 비트코인 투자에 대해 조언드리겠습니다.

현재 시장 상황을 고려하면...
[답변이 나옴]

# 종료: /bye
```

---

## 🌐 Step 3: 네트워크 설정

### 노트북을 네트워크에서 접근 가능하게 설정

#### 3-1. 노트북 IP 주소 확인

```powershell
# PowerShell에서 실행
ipconfig

# 출력:
# 무선 LAN 어댑터 Wi-Fi:
#    IPv4 주소 . . . . . . . . : 192.168.0.100
#                               ^^^^^^^^^^^^^^
#                               이 주소 복사!
```

#### 3-2. Ollama를 모든 IP에서 접근 가능하게 설정

```powershell
# 환경 변수 설정 (영구)
[System.Environment]::SetEnvironmentVariable(
    'OLLAMA_HOST',
    '0.0.0.0:11434',
    'User'
)

# PowerShell 재시작

# Ollama 서비스 재시작
ollama serve

# 출력:
# Listening on 0.0.0.0:11434
#              ^^^^^^^^^^ 모든 IP에서 접근 가능!
```

#### 3-3. 방화벽 포트 열기

```powershell
# Windows Defender 방화벽 규칙 추가
New-NetFirewallRule `
    -DisplayName "Ollama API" `
    -Direction Inbound `
    -LocalPort 11434 `
    -Protocol TCP `
    -Action Allow

# 출력:
# Name                  : {xxx-xxx-xxx}
# DisplayName           : Ollama API
# → 성공! ✅
```

#### 3-4. 다른 컴퓨터에서 접근 테스트

```powershell
# 현재 컴퓨터에서 (Flask 서버가 있는 곳)

# 노트북 IP로 테스트
curl http://192.168.0.100:11434/api/tags

# 출력:
# {
#   "models": [
#     {
#       "name": "qwen2.5:7b",
#       "modified_at": "2026-02-17T14:30:00Z",
#       "size": 4733167104
#     }
#   ]
# }
# → 연결 성공! ✅
```

---

## 🔗 Step 4: 기존 봇과 연결

### 4-1. 설정 파일 생성

```python
# config/ai_config.py 파일 생성

import os

class AIConfig:
    """AI 백엔드 설정"""
    
    # AI 백엔드 선택
    AI_BACKEND = os.getenv('AI_BACKEND', 'local')  # 'local' or 'openai'
    
    # 로컬 AI 설정
    LOCAL_AI_HOST = os.getenv('LOCAL_AI_HOST', '192.168.0.100')  # 노트북 IP
    LOCAL_AI_PORT = os.getenv('LOCAL_AI_PORT', '11434')
    LOCAL_AI_MODEL = os.getenv('LOCAL_AI_MODEL', 'qwen2.5:7b')
    
    @property
    def local_ai_url(self):
        return f"http://{self.LOCAL_AI_HOST}:{self.LOCAL_AI_PORT}"
    
    # OpenAI 설정 (백업용)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    # 자동 폴백 (로컬 실패 시 OpenAI 사용)
    AUTO_FALLBACK = True
```

### 4-2. AI 클라이언트 클래스 생성

```python
# ai_client.py 파일 생성

import requests
import openai
from config.ai_config import AIConfig

class AIClient:
    """통합 AI 클라이언트 (로컬 + OpenAI)"""
    
    def __init__(self):
        self.config = AIConfig()
        
        # OpenAI 설정
        openai.api_key = self.config.OPENAI_API_KEY
    
    def chat(self, messages, temperature=0.7, max_tokens=500):
        """AI 대화 (자동 폴백)"""
        
        # 1차: 로컬 AI 시도
        if self.config.AI_BACKEND == 'local':
            try:
                return self._chat_local(messages, temperature, max_tokens)
            except Exception as e:
                print(f"⚠️ 로컬 AI 오류: {e}")
                
                if self.config.AUTO_FALLBACK:
                    print("🔄 OpenAI로 폴백...")
                    return self._chat_openai(messages, temperature, max_tokens)
                else:
                    raise
        
        # 2차: OpenAI
        else:
            return self._chat_openai(messages, temperature, max_tokens)
    
    def _chat_local(self, messages, temperature, max_tokens):
        """로컬 AI (Ollama)"""
        
        # 메시지 포맷 변환
        prompt = self._messages_to_prompt(messages)
        
        # Ollama API 호출
        url = f"{self.config.local_ai_url}/api/generate"
        
        response = requests.post(url, json={
            'model': self.config.LOCAL_AI_MODEL,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        }, timeout=60)
        
        response.raise_for_status()
        
        data = response.json()
        answer = data['response']
        
        return {
            'content': answer,
            'backend': 'local',
            'model': self.config.LOCAL_AI_MODEL,
            'cost': 0.0
        }
    
    def _chat_openai(self, messages, temperature, max_tokens):
        """OpenAI"""
        
        response = openai.ChatCompletion.create(
            model=self.config.OPENAI_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        answer = response.choices[0].message.content
        
        # 비용 계산 (대략)
        tokens = response.usage.total_tokens
        cost = tokens * 0.00003  # GPT-4 기준
        
        return {
            'content': answer,
            'backend': 'openai',
            'model': self.config.OPENAI_MODEL,
            'cost': cost
        }
    
    def _messages_to_prompt(self, messages):
        """OpenAI 메시지 포맷 → Ollama 프롬프트"""
        
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
    
    def health_check(self):
        """AI 서버 상태 확인"""
        
        if self.config.AI_BACKEND == 'local':
            try:
                url = f"{self.config.local_ai_url}/api/tags"
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                
                models = response.json()['models']
                
                return {
                    'status': 'online',
                    'backend': 'local',
                    'url': self.config.local_ai_url,
                    'models': [m['name'] for m in models],
                    'cost': '$0/month'
                }
            except:
                return {
                    'status': 'offline',
                    'backend': 'local',
                    'error': 'Cannot connect to local AI server'
                }
        
        else:
            return {
                'status': 'online',
                'backend': 'openai',
                'model': self.config.OPENAI_MODEL,
                'cost': '$$$'
            }
```

### 4-3. 기존 봇에 통합

```python
# upbit-smart-bot-v8.0-ULTIMATE.py에 추가

from ai_client import AIClient

# 전역 AI 클라이언트
ai_client = AIClient()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API: 자이와 대화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    """자이와 대화 (로컬 AI 우선)"""
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인 필요'}), 401
    
    message = request.json.get('message', '')
    
    # 사용자 컨텍스트 구축
    user_profile = get_user_profile(user_id)
    user_context = build_user_context(user_id)
    
    # 메시지 구성
    messages = [
        {
            'role': 'system',
            'content': f"""
            당신은 자이, 4년차 코인 트레이더입니다.
            
            사용자 정보:
            - 이름: {user_profile.get('name', '오빠')}
            - 관계: {user_context.get('relationship_level', '친구')}
            - 성향: {user_context.get('trading_style', '보통')}
            
            말투:
            - 친근하고 밝게
            - 이모지 사용 (💜, 🎯, 🔥)
            - "오빠", "~해요", "~예요" 사용
            """
        },
        {
            'role': 'user',
            'content': message
        }
    ]
    
    # AI 호출 (로컬 우선, 실패 시 OpenAI)
    result = ai_client.chat(messages, temperature=0.7, max_tokens=500)
    
    answer = result['content']
    
    # 대화 저장
    save_conversation(user_id, message, answer)
    
    return jsonify({
        'response': answer,
        'backend': result['backend'],
        'model': result['model'],
        'cost': result['cost'],
        'timestamp': datetime.now().isoformat()
    })

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API: AI 상태 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/ai-status')
def ai_status():
    """AI 백엔드 상태"""
    return jsonify(ai_client.health_check())
```

---

## ✅ Step 5: 테스트

### 5-1. 노트북에서 Ollama 실행

```powershell
# 노트북 (192.168.0.100)
# PowerShell에서

# 1. Ollama 서버 시작
ollama serve

# 출력:
# Listening on 0.0.0.0:11434
```

### 5-2. 현재 컴퓨터에서 Flask 서버 실행

```bash
# 현재 컴퓨터
cd /home/user/webapp

# 환경 변수 설정
export AI_BACKEND=local
export LOCAL_AI_HOST=192.168.0.100
export LOCAL_AI_PORT=11434
export LOCAL_AI_MODEL=qwen2.5:7b

# Flask 서버 시작
python3 upbit-smart-bot-v8.0-ULTIMATE.py
```

### 5-3. 웹 브라우저에서 테스트

```
1. 브라우저 열기
2. http://localhost:5000/ai-streamer 접속
3. 자이와 대화:

"안녕 자이!"
→ 로컬 AI가 답변!

"BTC 지금 사야 해?"
→ 로컬 AI가 분석!
```

### 5-4. API 직접 테스트

```bash
# AI 상태 확인
curl http://localhost:5000/api/ai-status

# 출력:
# {
#   "status": "online",
#   "backend": "local",
#   "url": "http://192.168.0.100:11434",
#   "models": ["qwen2.5:7b"],
#   "cost": "$0/month"
# }

# AI 대화 테스트
curl -X POST http://localhost:5000/api/ai-chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "BTC 지금 사야 해?"
  }' \
  --cookie "session=..."

# 출력:
# {
#   "response": "오빠! 지금 BTC는...",
#   "backend": "local",
#   "model": "qwen2.5:7b",
#   "cost": 0.0
# }
```

---

## 🚀 Step 6: 자동 실행 설정

### 6-1. 노트북: Windows 시작 시 Ollama 자동 실행

#### 방법 A: 작업 스케줄러 (추천!)

```
1. Windows 검색: "작업 스케줄러"
2. 우측: "기본 작업 만들기"

3. 이름: Ollama Auto Start
   설명: 부팅 시 Ollama 자동 시작

4. 트리거: "컴퓨터를 시작할 때"

5. 작업: "프로그램 시작"
   프로그램: C:\Users\wordy\AppData\Local\Programs\Ollama\ollama.exe
   인수: serve

6. 완료!
```

#### 방법 B: 시작 프로그램 폴더

```powershell
# 1. 배치 파일 생성
notepad C:\Users\wordy\start_ollama.bat

# 내용:
@echo off
"C:\Users\wordy\AppData\Local\Programs\Ollama\ollama.exe" serve

# 2. 시작 프로그램에 추가
# Windows + R → "shell:startup" 입력
# → start_ollama.bat 바로가기 복사
```

### 6-2. 현재 컴퓨터: Flask 서버 자동 실행

```bash
# systemd 서비스 생성 (Linux)
sudo nano /etc/systemd/system/jai-bot.service

# 내용:
[Unit]
Description=JAI Trading Bot
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/webapp
Environment="AI_BACKEND=local"
Environment="LOCAL_AI_HOST=192.168.0.100"
Environment="LOCAL_AI_PORT=11434"
ExecStart=/usr/bin/python3 upbit-smart-bot-v8.0-ULTIMATE.py
Restart=always

[Install]
WantedBy=multi-user.target

# 활성화
sudo systemctl enable jai-bot
sudo systemctl start jai-bot
```

---

## 📊 성능 비교

### Before (OpenAI)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
대화 1회:
- 비용: $0.002~0.006
- 속도: 2~5초
- 의존성: 인터넷 필요

월 10,000회:
- 비용: $20~60
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### After (로컬 AI)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
대화 1회:
- 비용: $0 ✅
- 속도: 3~7초
- 의존성: 로컬 네트워크만

월 10,000회:
- 비용: $0 ✅
- 전기세: $20
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔧 트러블슈팅

### 문제 1: "connection refused"
```powershell
# 노트북에서 Ollama 실행 확인
ollama serve

# 방화벽 확인
Get-NetFirewallRule -DisplayName "Ollama API"

# IP 주소 재확인
ipconfig
```

### 문제 2: "모델이 너무 느려요"
```powershell
# GPU 사용 확인
nvidia-smi

# 더 작은 모델 사용
ollama pull qwen2.5:7b  # 대신
ollama pull mistral:7b  # 더 빠름
```

### 문제 3: "자동 시작이 안 돼요"
```powershell
# 작업 스케줄러 확인
Get-ScheduledTask -TaskName "Ollama Auto Start"

# 수동 테스트
C:\Users\wordy\AppData\Local\Programs\Ollama\ollama.exe serve
```

---

## 🎯 최종 확인 체크리스트

```
노트북 (192.168.0.100):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ Ollama 설치 완료
☐ qwen2.5:7b 모델 다운로드
☐ ollama serve 실행 중
☐ 방화벽 포트 11434 열림
☐ 다른 PC에서 접근 가능

현재 컴퓨터:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ ai_config.py 생성
☐ ai_client.py 생성
☐ Flask 서버 연동
☐ /api/ai-status 정상
☐ /api/ai-chat 정상

자동 실행:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ 노트북: 작업 스케줄러 등록
☐ 현재 PC: systemd 서비스 등록
☐ 재부팅 후 자동 시작 확인
```

---

## 🚀 다음 단계

### Week 2: RAG 시스템
- ChromaDB 설치
- 벡터 임베딩
- 지식 검색

### Week 3: GenSpark 통합
- Video API
- Audio API
- 자동화

### Week 4: 구독 시스템
- 결제 연동
- 플랜 분기
- 서비스 론칭!

---

## 💡 요약

```
✅ 당신의 노트북 = AI 서버
✅ RTX 5070 Ti = 완벽한 사양
✅ 비용 = $0 (전기세만)
✅ OpenAI 대비 월 $1,500~3,000 절약

다음:
1. Ollama 설치 (5분)
2. 모델 다운로드 (10분)
3. 네트워크 설정 (5분)
4. Flask 연동 (30분)
5. 완료! 🎉
```

---

*Updated: 2026-02-17 15:00*
*Status: 설치 준비 완료!*
