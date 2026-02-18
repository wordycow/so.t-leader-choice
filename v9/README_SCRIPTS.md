# 🚀 Upbit Bot v9 - 스크립트 사용 가이드

## 📋 스크립트 목록

### 1. START_EVERYTHING.bat
**전체 시스템 시작**

```cmd
cd C:\Windows\System32\webapp\v9
START_EVERYTHING.bat
```

**실행 내용:**
1. Ollama Server (localhost:11434)
2. Execution Engine (WebSocket 8765) - 5초 대기
3. Signal Engine (Top20 스캔)
4. Dashboard (http://localhost:5000)
5. IMEI System (http://localhost:5001)

**결과:** 5개 창 + 대시보드 자동 오픈

---

### 2. STOP_EVERYTHING.bat
**전체 시스템 종료**

```cmd
cd C:\Windows\System32\webapp\v9
STOP_EVERYTHING.bat
```

**실행 내용:**
- Port 11434, 8765, 5000, 5001 강제 종료
- 남은 python.exe, ollama.exe 정리
- 자동으로 CHECK_STATUS.bat 실행

**결과:** 모든 서비스 종료 + 상태 확인

---

### 3. CHECK_STATUS.bat
**포트 상태 확인 (빠른 체크)**

```cmd
cd C:\Windows\System32\webapp\v9
CHECK_STATUS.bat
```

**확인 항목:**
- ✅/❌ Port 11434 (Ollama Server)
- ✅/❌ Port 8765 (Execution Engine)
- ✅/❌ Port 5000 (Dashboard)
- ✅/❌ Port 5001 (IMEI System)
- 실행 중인 서비스 개수 (X / 4)

**예상 출력:**
```
✅ Port 11434 - Ollama Server          [실행중]
✅ Port 8765  - Execution Engine       [실행중]
✅ Port 5000  - Dashboard              [실행중]
✅ Port 5001  - IMEI System            [실행중]

📈 요약: 4 / 4 서비스 실행 중
✅ 모든 서비스가 정상 실행 중입니다!
```

---

### 4. HEALTH_CHECK.bat
**상세 헬스 체크 (API + 로그)**

```cmd
cd C:\Windows\System32\webapp\v9
HEALTH_CHECK.bat
```

**확인 항목:**
1. 포트 상태 (CHECK_STATUS.bat 호출)
2. /api/top20 - 실데이터 확인
3. /health - Signal/Execution 엔진 상태
4. /api/watch_state - 추적 티커 수
5. /api/trades - 거래 기록
6. 로그 파일 (마지막 10줄)

**예상 출력:**
```
1️⃣  /api/top20 체크...
   ✅ Source: upbit
   ✅ Items: 20
   ✅ Top 3: ['KRW-CYBER', 'KRW-ETH', 'KRW-USDT']

2️⃣  /health 체크...
   Signal Engine:
     - Status: running
     - Last Scan: 2026-02-18T22:30:00
     - Signal Count: 0
   Execution Engine:
     - Status: running
     - Paper Fills: 0
```

---

### 5. RESTART_QUICK.bat
**빠른 재시작**

```cmd
cd C:\Windows\System32\webapp\v9
RESTART_QUICK.bat
```

**실행 내용:**
1. STOP_EVERYTHING.bat 호출
2. 3초 대기
3. START_EVERYTHING.bat 호출

**사용 시점:**
- 봇이 멈춘 것 같을 때
- 설정 변경 후 재시작
- Signal Engine이 reconnecting 상태일 때

---

## 🎯 일반적인 사용 시나리오

### 시나리오 1: 처음 시작
```cmd
cd C:\Windows\System32\webapp\v9
START_EVERYTHING.bat
```
→ 60초 대기 → CHECK_STATUS.bat 실행

---

### 시나리오 2: 제대로 작동하는지 확인
```cmd
HEALTH_CHECK.bat
```

**확인 사항:**
- Signal Engine Status: `running` (not `reconnecting`)
- Last Scan: 60초 이내
- Tracked Tickers: 20

---

### 시나리오 3: 봇이 멈춘 것 같음
```cmd
CHECK_STATUS.bat
```

**결과가 `4 / 4`가 아니면:**
```cmd
RESTART_QUICK.bat
```

---

### 시나리오 4: 깔끔하게 종료
```cmd
STOP_EVERYTHING.bat
```

자동으로 상태 확인 → 모두 `❌`이면 정상 종료

---

## ⚠️ 문제 해결

### 문제 1: Signal Engine이 reconnecting
**원인:** Execution Engine이 먼저 시작 안 됨

**해결:**
```cmd
STOP_EVERYTHING.bat
(3초 대기)
START_EVERYTHING.bat
```

---

### 문제 2: Dashboard 접속 안 됨
**확인:**
```cmd
CHECK_STATUS.bat
```

Port 5000이 `❌`이면:
```cmd
RESTART_QUICK.bat
```

---

### 문제 3: 로그 확인 필요
```cmd
HEALTH_CHECK.bat
```

또는 직접:
```cmd
type logs\signal_engine.log
type logs\execution_engine.log
type logs\dashboard.log
type logs\imei_app.log
```

---

## 📊 검증 체크리스트 (빠른 버전)

```cmd
# 1. 시작
START_EVERYTHING.bat

# 2. 60초 대기
timeout /t 60

# 3. 상태 확인
CHECK_STATUS.bat

# 4. 상세 확인
HEALTH_CHECK.bat
```

**통과 조건:**
- ✅ 4 / 4 서비스 실행 중
- ✅ Signal Engine: `running`
- ✅ Last Scan: 60초 이내
- ✅ Tracked Tickers: 20
- ✅ /api/top20: `source: "upbit"`

---

## 🔄 자동 모니터링 (선택)

60초마다 자동 체크:
```cmd
:loop
CHECK_STATUS.bat
timeout /t 60 /nobreak
goto loop
```

→ `CTRL+C`로 중지

---

## 💡 팁

1. **시작 후 항상 60초 기다리기**
   - Signal Engine이 첫 Top20 스캔 완료까지 시간 필요

2. **CHECK_STATUS.bat을 자주 사용**
   - 가장 빠른 상태 확인 방법

3. **HEALTH_CHECK.bat은 상세 분석용**
   - 문제 발생 시 로그 확인

4. **RESTART_QUICK.bat은 만능 해결사**
   - 대부분의 문제는 재시작으로 해결

---

## 📂 파일 구조

```
v9/
├── START_EVERYTHING.bat      ← 전체 시작
├── STOP_EVERYTHING.bat        ← 전체 종료
├── CHECK_STATUS.bat           ← 빠른 상태 확인
├── HEALTH_CHECK.bat           ← 상세 헬스 체크
├── RESTART_QUICK.bat          ← 빠른 재시작
├── VERIFICATION_CHECKLIST.md  ← 검증 가이드
└── README_SCRIPTS.md          ← 이 파일
```

---

**모든 스크립트는 `v9` 폴더에서 실행하세요!**
