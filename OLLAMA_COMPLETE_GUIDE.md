# 🎯 Ollama 완벽 이해 + 전체 연결 가이드

> **Ollama가 뭐고, 어떻게 연결하고, GenSpark 풀스택을 다 쓰는지!**

---

## 📋 목차
1. [Ollama가 하는 일](#ollama가-하는-일)
2. [지금 바로 연결하기](#지금-바로-연결하기)
3. [GenSpark 풀스택 연결](#genspark-풀스택-연결)
4. [통합 시스템 구축](#통합-시스템-구축)

---

## 🤔 Ollama가 하는 일

### 쉬운 비유

```
Ollama = AI 모델을 위한 "서버 프로그램"

비유:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MySQL = 데이터베이스 서버
  → 데이터를 저장하고 검색

Nginx = 웹 서버
  → 웹페이지를 제공

Ollama = AI 서버
  → AI 모델을 실행하고 답변 제공
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

역할:
1. AI 모델 저장 (Qwen, Llama 등)
2. 모델 실행 (GPU 활용)
3. API 제공 (HTTP 요청/응답)
4. 리소스 관리 (메모리, GPU)
```

### 구체적인 작동 방식

```
[당신의 노트북]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ollama serve 실행
   ↓
   [Ollama 서버 시작]
   - 포트: 11434
   - AI 모델 로드 준비
   ↓
2. 다른 프로그램에서 요청
   POST http://노트북IP:11434/api/generate
   {
     "model": "qwen2.5:7b",
     "prompt": "BTC 분석해줘"
   }
   ↓
3. Ollama가 AI 모델 실행
   - GPU로 추론
   - 답변 생성
   ↓
4. 응답 반환
   {
     "response": "BTC는 현재..."
   }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
결과: OpenAI처럼 사용하지만 로컬에서!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Ollama vs OpenAI

```
┌──────────────────────────────────────────┐
│ OpenAI API                               │
├──────────────────────────────────────────┤
│ 인터넷 → OpenAI 서버 → 답변              │
│ 비용: $$$                                │
│ 속도: 빠름                               │
│ 제한: API 요청 제한                      │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ Ollama (로컬)                            │
├──────────────────────────────────────────┤
│ 로컬 네트워크 → 노트북 → 답변             │
│ 비용: $0                                 │
│ 속도: 보통                               │
│ 제한: 없음! 무제한!                      │
└──────────────────────────────────────────┘
```

---

## 🔗 지금 바로 연결하기

### Step 1: 노트북 IP 주소 확인

```powershell
# 노트북에서 PowerShell 실행
ipconfig

# 출력에서 찾기:
# 무선 LAN 어댑터 Wi-Fi:
#    IPv4 주소 . . . . . . . . : 192.168.0.100
#                               ^^^^^^^^^^^^^^
#                               이 주소 복사!
```

### Step 2: Ollama 서버 시작

```powershell
# 노트북 PowerShell

# 환경 변수 설정 (모든 IP에서 접근 가능하게)
$env:OLLAMA_HOST = "0.0.0.0:11434"

# 서버 시작
ollama serve

# 출력:
# Listening on 0.0.0.0:11434
# → 성공! ✅
```

### Step 3: 모델 다운로드 (다른 PowerShell 창)

```powershell
# 새 PowerShell 창 열기

# 한국어 최고 모델
ollama pull qwen2.5:7b

# 다운로드 진행...
# pulling manifest
# pulling xxx... 100%
# success ✅

# 확인
ollama list

# 출력:
# NAME              SIZE
# qwen2.5:7b        4.7GB
```

### Step 4: 빠른 테스트

```powershell
# 노트북에서 테스트
ollama run qwen2.5:7b

>>> 안녕? BTC 지금 사야 해?

[AI 답변이 나옵니다!]

>>> /bye
```

### Step 5: 방화벽 설정

```powershell
# 관리자 권한 PowerShell

# 방화벽 규칙 추가
New-NetFirewallRule `
    -DisplayName "Ollama API" `
    -Direction Inbound `
    -LocalPort 11434 `
    -Protocol TCP `
    -Action Allow

# 성공 확인
Get-NetFirewallRule -DisplayName "Ollama API"
```

---

## 🚀 GenSpark와 연결 (지금 바로!)

제가 지금 **모든 파일**을 만들어드리겠습니다!

