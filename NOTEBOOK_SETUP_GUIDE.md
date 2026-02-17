# 🎯 노트북 설정 가이드 (필수!)

> **현재 상태: 노트북 IP 확인 완료 (72.14.201.167)**

---

## ⚠️ 지금 해야 할 것

노트북에서 **3단계만** 하면 됩니다!

---

## 📋 노트북에서 할 일 (Windows PowerShell)

### Step 1: Ollama 서버 시작

```powershell
# Windows + X → Windows PowerShell

# 1. 환경 변수 설정 (모든 IP에서 접근 가능하게)
$env:OLLAMA_HOST = "0.0.0.0:11434"

# 2. Ollama 서버 시작
ollama serve
```

**✅ 성공 시 출력:**
```
Listening on 0.0.0.0:11434
```

**❌ 만약 "command not found" 에러:**
```powershell
# Ollama 설치 확인
ollama --version

# 없으면 설치:
# https://ollama.com/download/windows
```

---

### Step 2: 방화벽 포트 열기

```powershell
# 관리자 권한 PowerShell 실행
# Windows + X → Windows PowerShell (관리자)

# 포트 11434 열기
New-NetFirewallRule `
    -DisplayName "Ollama API" `
    -Direction Inbound `
    -LocalPort 11434 `
    -Protocol TCP `
    -Action Allow

# ✅ 성공 메시지 확인
```

**GUI 방법 (더 쉬움):**
```
1. Windows 검색: "방화벽"
2. "Windows Defender 방화벽"
3. 좌측: "고급 설정"
4. 좌측: "인바운드 규칙"
5. 우측: "새 규칙"
6. "포트" 선택 → 다음
7. "TCP" 선택
8. "특정 로컬 포트": 11434 입력
9. "연결 허용" → 다음
10. 모두 체크 → 다음
11. 이름: "Ollama" → 완료
```

---

### Step 3: 모델 다운로드 (처음만!)

```powershell
# 새 PowerShell 창 열기 (ollama serve는 계속 실행 중)

# 한국어 최고 모델
ollama pull qwen2.5:7b

# 다운로드 중... (약 4.7GB, 5-10분)
# ████████████████ 100%
# success ✅

# 확인
ollama list

# 출력:
# NAME              SIZE
# qwen2.5:7b        4.7GB
```

---

## ✅ 확인 방법

### 노트북에서 자체 테스트

```powershell
# 노트북 PowerShell

# 로컬 테스트
curl http://localhost:11434/api/tags

# 출력 (성공):
# {
#   "models": [
#     {"name": "qwen2.5:7b", ...}
#   ]
# }
```

---

## 🎯 완료 후 현재 PC에서

```bash
# 현재 PC (Linux)

cd /home/user/webapp

# 빠른 테스트
./quick_test.sh

# 출력 (성공 시):
# ✅ 연결 성공!
# 📚 사용 가능한 모델:
#    - qwen2.5:7b (4.7GB)
```

---

## 📊 전체 흐름

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
노트북 (72.14.201.167)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: ollama serve ✅
        → Listening on 0.0.0.0:11434

Step 2: 방화벽 열기 ✅
        → 포트 11434 허용

Step 3: 모델 다운로드 ✅
        → qwen2.5:7b (4.7GB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
현재 PC (Linux)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4: 연결 테스트 ✅
        → ./quick_test.sh

Step 5: Flask 실행 ✅
        → pm2 restart upbit-bot

Step 6: 웹 테스트 ✅
        → http://localhost:5000/ai-streamer
```

---

## 🔧 트러블슈팅

### 문제 1: "Listening on 127.0.0.1:11434"

```powershell
# 잘못된 출력:
Listening on 127.0.0.1:11434  ❌
             ^^^^^^^^^^ localhost만 접근 가능

# 올바른 출력:
Listening on 0.0.0.0:11434   ✅
             ^^^^^^^ 모든 IP 접근 가능

# 해결:
$env:OLLAMA_HOST = "0.0.0.0:11434"
ollama serve
```

### 문제 2: "방화벽 규칙 추가 실패"

```powershell
# 관리자 권한 확인
# PowerShell 창 제목에 "Administrator" 있는지 확인

# 없으면:
# Windows + X → Windows PowerShell (관리자)
```

### 문제 3: "curl: command not found"

```powershell
# Windows PowerShell에서는 curl 대신:
Invoke-WebRequest http://localhost:11434/api/tags

# 또는:
Test-NetConnection -ComputerName localhost -Port 11434
```

---

## 💡 요약

### 노트북에서 꼭 해야 할 3가지

```
1. ollama serve 실행
   → 환경 변수: $env:OLLAMA_HOST = "0.0.0.0:11434"

2. 방화벽 포트 11434 열기
   → GUI: 방화벽 → 고급 설정 → 인바운드 규칙

3. 모델 다운로드 (처음만)
   → ollama pull qwen2.5:7b
```

---

## 🚀 다음 단계

```
노트북 설정 완료 후:

1. 현재 PC에서 테스트:
   ./quick_test.sh

2. 성공 시 Flask 실행:
   pm2 restart upbit-bot

3. 웹 브라우저:
   http://localhost:5000/ai-streamer

4. 자이와 대화:
   "안녕 자이!" → 로컬 AI 답변! (비용 $0)
```

---

*Updated: 2026-02-17*
*노트북 IP: 72.14.201.167*
*Status: 노트북 설정 대기 중...*
