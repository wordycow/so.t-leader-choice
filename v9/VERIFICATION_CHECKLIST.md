# ✅ v9 검증 체크리스트

## 📋 노트북에서 실행 전 확인사항

### 1. Git 동기화 확인
```bash
cd C:\Windows\System32\webapp
git status
git pull origin main
```

**예상 결과**: 
- `Already up to date.` 또는 파일 업데이트 메시지
- 최신 커밋: `ccb34c3` (검증 준비 완료)

---

### 2. 핵심 파일 존재 확인
```bash
cd v9
dir START_EVERYTHING.bat
dir STOP_EVERYTHING.bat
dir signal_engine\main_loop.py
dir execution_engine\main_loop.py
```

**예상 결과**: 모든 파일이 존재해야 함

---

### 3. START_EVERYTHING.bat 내용 확인
```bash
type START_EVERYTHING.bat | findstr "main_loop"
```

**예상 결과**:
```
start "Signal Engine" cmd /k "cd /d %~dp0 && python signal_engine/main_loop.py > logs/signal_engine.log 2>&1"
start "Execution Engine" cmd /k "cd /d %~dp0 && python execution_engine/main_loop.py > logs/execution_engine.log 2>&1"
```

---

## 🚀 봇 실행 (노트북에서)

### 단계 1: 기존 프로세스 정리
```bash
cd C:\Windows\System32\webapp\v9
STOP_EVERYTHING.bat
```

### 단계 2: 전체 시스템 시작
```bash
START_EVERYTHING.bat
```

**예상 결과**: 5개 창이 열림
1. Ollama Server (localhost:11434)
2. Signal Engine (Top20 스캔)
3. Execution Engine (WebSocket 8765)
4. Dashboard (http://localhost:5000) ← 자동으로 브라우저 열림
5. IMEI System (http://localhost:5001)

---

## 🎯 검증 체크 (5개 항목)

### ✅ 1. /api/top20 실데이터
```bash
curl http://localhost:5000/api/top20
```

**기대값**:
- `"source": "upbit"`
- `"ticker": "KRW-CYBER"`, `"KRW-ETH"` 등 실제 티커
- `KRW-MOCK` 절대 없어야 함

---

### ✅ 2. /api/watch_state 갱신
```bash
curl http://localhost:5000/api/watch_state
```

**기대값**:
- `"tracked_tickers": 20` (또는 > 0)
- `"last_top20_scan_at": "2026-02-18T21:XX:XX"` (60초마다 갱신)
- `"condition_checklists": { ... }` (조건 체크리스트 존재)

**판단 방법**: 
- 60초 기다린 후 다시 호출 → `last_top20_scan_at` 시간 변경 확인
- 신호가 없어도 이 값이 계속 갱신되면 **Signal Engine 정상**

---

### ✅ 3. /health 확장 지표
```bash
curl http://localhost:5000/health
```

**기대값**:
```json
{
  "signal_engine": {
    "last_top20_scan_at": "2026-02-18T21:XX:XX",
    "signal_sent_count": 0,
    "tracked_tickers": 20
  },
  "execution_engine": {
    "execution_received_count": 0,
    "paper_fill_count": 0,
    "last_trade_at": null
  }
}
```

**판단 방법**:
- `last_top20_scan_at`가 60초마다 갱신 → Signal Engine 정상
- `signal_sent_count` 증가 → 신호 발생 확인
- `paper_fill_count` 증가 → PAPER 체결 확인

---

### ✅ 4. /api/trades (신호 발생 시)
```bash
curl http://localhost:5000/api/trades
```

**기대값** (신호 발생 전):
```json
{
  "items": [],
  "source": "empty"
}
```

**기대값** (신호 발생 후):
```json
{
  "items": [
    {
      "ticker": "KRW-CYBER",
      "side": "BUY",
      "strategy_name": "SurgeHunter",
      "why": "급등 포착: 20.4% 상승, 거래대금 153.3억",
      "trigger_conditions": ["변동률 +10% 이상", "거래대금 100억 이상"],
      "price": 1005.0,
      "order_id": "paper-abc123"
    }
  ]
}
```

**판단 방법**:
- 신호가 없어도 정상 (조건 미충족)
- `why`, `strategy_name`, `trigger_conditions` 필수 확인

---

### ✅ 5. IMEI 에코 제거
```
브라우저: http://localhost:5001
```

**테스트**:
1. IMEI 채팅창에서 "안녕하세요" 입력
2. 응답 확인

**기대값**:
- ❌ "I received your message..." (에코 응답) → 절대 나오면 안 됨
- ✅ "IMEI AI가 현재 비활성화되어 있습니다..." (Ollama 없을 때)
- ✅ 한국어 답변 (Ollama 연결 시)

**판단 방법**:
- Ollama 서버가 없으면 비활성화 메시지만 표시
- Ollama 연결 시 실제 한국어 답변

---

## 🛑 문제 발생 시 디버깅

### Signal Engine 로그 확인
```bash
type logs\signal_engine.log
```

**정상 로그 예시**:
```
📊 Fetching Top20 data...
✅ Top20 fetched: 20 items
⏳ No signals (conditions not met)
```

### Execution Engine 로그 확인
```bash
type logs\execution_engine.log
```

**정상 로그 예시**:
```
✅ WebSocket server started
```

### Dashboard 로그 확인
```bash
type logs\dashboard.log
```

**정상 로그 예시**:
```
 * Running on http://0.0.0.0:5000
```

---

## 📊 GitHub 커밋 히스토리

```bash
git log --oneline -5
```

**최신 커밋**:
```
ccb34c3 feat: ✅ 검증 준비 완료 (START/STOP 스크립트 확정 + 조건 체크리스트)
3d87f6b feat: 🎯 실데이터 기반 운영 시스템 완성 (Mock 완전 제거)
abfc967 feat: 🎯 Top20 Watchlist UI 추가 (실데이터 기반 추적)
59f9351 feat: 🚀 실제 Upbit Top20 데이터 연동 (KRW-MOCK* 제거)
```

---

## ✅ 검증 통과 조건

| 항목 | 조건 |
|------|------|
| 1. /api/top20 | `source: "upbit"`, 실제 티커 |
| 2. /api/watch_state | `last_top20_scan_at` 60초마다 갱신 |
| 3. /health | Signal/Execution 엔진 지표 존재 |
| 4. /api/trades | (신호 발생 시) `why`/`strategy` 포함 |
| 5. IMEI | 에코 응답 없음 |

**모든 항목 통과 시 → 운영 가능 판정**
