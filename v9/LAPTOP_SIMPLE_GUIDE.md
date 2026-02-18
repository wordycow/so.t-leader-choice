# 🚀 Upbit Bot v9 노트북 서버 간단 가이드

## ✅ 핵심 답변: 필요한 것들

1. **Python 3.8+** ✅ (필수)
2. **Internet** ✅ (시장 데이터용)
3. **🔥 Ollama 터널** ✅ (IMEI 학습용 LLM - 필수!)
   - URL: `http://ollama.thetheunique.com`
   - Named Tunnel (영구 고정)
   - 노트북에서 실행 필요:
     ```bash
     # 터미널 1: Ollama 서버
     ollama serve
     
     # 터미널 2: Cloudflare Tunnel
     cloudflared tunnel run ollama-stable
     ```

## ❓ Cloudflare Tunnel이 필요한가요?

**네, IMEI 학습을 위해 필요합니다!**

- **Ollama 터널**: IMEI가 성장하려면 LLM이 필요합니다
- **영구 Named Tunnel**: `ollama.thetheunique.com` (고정 URL, 재시작 불필요)
- **노트북에서 실행**: 
  1. `ollama serve` - Ollama 서버 시작
  2. `cloudflared tunnel run ollama-stable` - 터널 시작

## 🎯 한 줄 명령어

```bash
cd v9
LAPTOP_SERVER_START.bat
```

이 한 줄로 끝! 5초 내 모든 봇이 실행되고 브라우저가 자동 오픈됩니다.

---

## 📦 필수 BAT 파일들

### 1️⃣ `LAPTOP_SERVER_START.bat` - 시작 (가장 중요! ⭐)

**용도**: 노트북 켤 때 이것만 실행
**기능**:
- Python 환경 체크
- 기존 프로세스 종료
- 4개 봇 순차 실행:
  1. Signal Engine (시그널 생성)
  2. Execution Engine (주문 실행)
  3. Dashboard (포트 5000)
  4. IMEI System (포트 5001 + Ollama Router)
- 5초 후 대시보드 자동 오픈

**실행 시 나타나는 창**: 4개 (Signal, Execution, Dashboard, IMEI)

---

### 2️⃣ `STOP_ALL_BOTS.bat` - 종료

**용도**: 노트북 끄기 전 실행
**기능**:
- 모든 python.exe 프로세스 강제 종료
- 로그 파일 백업 (선택사항)

---

### 3️⃣ `QUICK_CHECK.bat` - 상태 체크

**용도**: 봇이 제대로 실행 중인지 확인
**체크 항목**:
- Python 프로세스 실행 여부
- 포트 5000 (Dashboard) 리스닝 여부
- 포트 5001 (IMEI) 리스닝 여부
- 포트 8765 (WebSocket) 리스닝 여부
- 최근 로그 파일 크기 및 시간

---

### 4️⃣ `RESTART_SERVER.bat` - 문제 발생 시

**용도**: 슬립 모드 후 / 네트워크 재연결 시
**기능**:
- 모든 프로세스 강제 종료
- 포트 5000, 5001, 8765 해제
- 로그 백업 (`logs/backup/<날짜>/`)
- SQLite WAL/SHM 파일 삭제 (DB 정리)
- 4개 봇 재시작

---

## 🔥 일일 사용 패턴

### 아침 (노트북 켤 때)

**시나리오 1: 처음 시작**
```bash
# 1. Ollama 터널 시작 (터미널 1)
ollama serve

# 2. Cloudflare Tunnel 시작 (터미널 2)
cloudflared tunnel run ollama-stable

# 3. Bot 시작
cd v9
LAPTOP_SERVER_START.bat
```

**시나리오 2: 정상 실행 확인**
```bash
cd v9
QUICK_CHECK.bat
```

모두 OK면 → 그대로 사용  
하나라도 문제면 → `RESTART_SERVER.bat` 실행

---

### 오후 (슬립 모드 후 재부팅)

```bash
cd v9
RESTART_SERVER.bat
```

노트북 절전 모드에서 깨어날 때마다 실행 추천!

---

### 저녁 (노트북 끄기 전)

```bash
cd v9
STOP_ALL_BOTS.bat
```

---

## 🛠 문제 해결

### 1. "Port already in use" 오류

```bash
cd v9
RESTART_SERVER.bat
```

포트 5000/5001/8765이 이미 사용 중일 때 발생합니다.

---

### 2. Dashboard/IMEI 페이지가 안 열림

```bash
cd v9
QUICK_CHECK.bat
```

→ 문제 확인 후:

```bash
cd v9
RESTART_SERVER.bat
```

---

### 3. Python 프로세스가 하나도 없음

- Python 설치 확인: `python --version`
- Virtual Environment 활성화 확인
- 재시작: `RESTART_SERVER.bat`

---

### 4. 로그 파일에 에러가 계속 쌓임

```bash
cd v9
RESTART_SERVER.bat
```

로그를 `logs/backup/`로 백업하고 새로 시작합니다.

---

### 5. WebSocket 연결 끊김 (슬립 모드 후)

```bash
cd v9
RESTART_SERVER.bat
```

---

### 6. Ollama Router 연결 실패

**증상**: IMEI 대화가 Mock Response만 나옴

**해결**:
1. 터미널 1: `ollama serve` 확인
2. 터미널 2: `cloudflared tunnel run ollama-stable` 확인
3. 브라우저 테스트: `http://ollama.thetheunique.com` 접속
4. Bot 재시작: `RESTART_SERVER.bat`

---

## 💡 Pro Tips

### 1. 자동 시작 설정 (선택사항)

Windows 시작 시 자동 실행:

1. `Win + R` → `shell:startup`
2. `LAPTOP_SERVER_START.bat`의 바로가기 생성
3. 시작 폴더에 복사

→ PC 켤 때마다 자동으로 봇 실행!

---

### 2. Windows 절전 모드 방지

**설정 > 전원 관리 > 절전 모드**

- 배터리 사용 시: 5분
- 전원 연결 시: **절대 안 함** ✅

---

### 3. 로그 주기적 청소

```bash
cd v9\logs
del /q *.log  # 오래된 로그 삭제
```

또는 `RESTART_SERVER.bat` 실행 시 자동 백업됩니다.

---

### 4. Wi-Fi 재연결 시

```bash
cd v9
RESTART_SERVER.bat
```

---

### 5. VPN 사용 시

VPN 연결 후:
```bash
cd v9
RESTART_SERVER.bat
```

---

## 📊 시스템 구조

```
노트북 서버 (로컬)
├── Terminal 1: ollama serve (port 11434)
├── Terminal 2: cloudflared tunnel run ollama-stable
│   └── → http://ollama.thetheunique.com (외부 접근용)
└── v9 시스템
    ├── Signal Engine (WebSocket Emitter)
    ├── Execution Engine (WebSocket Receiver, port 8765)
    ├── Dashboard (Flask, port 5000)
    └── IMEI System (Flask + Ollama Router, port 5001)
        └── → EmeiRouter → ollama.thetheunique.com
```

---

## 📝 체크리스트

### 봇 시작 전:
- [ ] Ollama 서버 실행 (`ollama serve`)
- [ ] Cloudflare Tunnel 실행 (`cloudflared tunnel run ollama-stable`)
- [ ] Python 3.8+ 설치 확인
- [ ] Internet 연결 확인

### 봇 시작:
- [ ] `cd v9`
- [ ] `LAPTOP_SERVER_START.bat`
- [ ] 4개 창 확인 (Signal, Execution, Dashboard, IMEI)
- [ ] 브라우저 자동 오픈 (http://localhost:5000)

### 종료:
- [ ] `STOP_ALL_BOTS.bat` 실행
- [ ] 4개 창 모두 닫혔는지 확인
- [ ] (선택) Ollama 서버 종료 (`Ctrl+C`)
- [ ] (선택) Cloudflare Tunnel 종료 (`Ctrl+C`)

---

## ❓ FAQ

### Q: `.env` 파일이 없어도 되나요?

A: **Practice 모드**는 가능, **Live 모드**는 필수입니다.

### Q: Ollama 없이 실행할 수 있나요?

A: Mock Response만 사용 가능하지만, **IMEI 학습 기능이 작동하지 않습니다.**

### Q: Cloudflare Tunnel은 왜 필요한가요?

A: Ollama를 외부에서 접속하기 위해 필요합니다 (Named Tunnel: 영구 URL).

### Q: BAT 파일이 너무 많은데요?

A: **하나만 기억하세요**: `LAPTOP_SERVER_START.bat` (시작)

---

## 🔐 보안 주의사항

1. `.env` 파일에 API 키 입력 후 Git에 커밋하지 마세요
2. Live 모드는 `/enable_live.flag` 파일이 있어야 활성화
3. Ollama 터널은 인증되지 않은 외부 접근 불가

---

## 📚 참고 문서

- `README_SERVER_MANAGEMENT.md` - 서버 관리 상세 가이드
- `SYSTEM_ARCHITECTURE.md` - 시스템 아키텍처
- `QUICK_START_GUIDE.md` - 빠른 시작 가이드

---

## 🎯 요약

**핵심 명령어**:
```bash
# 시작
cd v9 && LAPTOP_SERVER_START.bat

# 문제 발생 시
cd v9 && RESTART_SERVER.bat

# 종료
cd v9 && STOP_ALL_BOTS.bat
```

**3개 터미널 필요**:
1. `ollama serve`
2. `cloudflared tunnel run ollama-stable`
3. Bot 시스템 (LAPTOP_SERVER_START.bat)

---

✅ 이제 시작할 준비가 되었습니다!
