# 🚀 Upbit Bot v9 - 궁극의 간단 가이드

## ✅ 핵심 답변: 단 하나의 명령어

```bash
cd v9
START_EVERYTHING.bat
```

**끝!** 🎉

이 한 줄로:
- ✅ Ollama 서버 자동 시작 (`localhost:11434`)
- ✅ 4개 봇 자동 시작 (Signal, Execution, Dashboard, IMEI)
- ✅ 5초 후 대시보드 자동 오픈 (`http://localhost:5000`)

---

## 🔥 Cloudflare Tunnel은?

**실행 불필요!** ❌

- Named Tunnel (영구 고정): `http://ollama.thetheunique.com`
- 노트북을 껐다 켜도 URL이 안 바뀜
- 한 번 설정하면 끝!

---

## 📦 필요한 것

1. **Python 3.8+** ✅
2. **Ollama 설치** ✅
   - 다운로드: https://ollama.com/download
   - 모델: `qwen2.5:7b` (자동 다운로드)
3. **Internet** ✅

---

## 🎯 일일 사용 패턴

### **아침 (노트북 켤 때)**

```bash
cd v9
START_EVERYTHING.bat
```

→ **5초 후 대시보드 자동 오픈!**

---

### **저녁 (노트북 끄기 전)**

```bash
cd v9
STOP_EVERYTHING.bat
```

→ **모든 프로세스 종료!**

---

## 🛠 문제 해결

### 1. "Ollama가 없습니다" 오류

**해결**:
1. https://ollama.com/download 에서 Ollama 설치
2. 설치 후 `START_EVERYTHING.bat` 재실행

---

### 2. 봇이 실행 안 됨

**해결**:
```bash
cd v9
STOP_EVERYTHING.bat
```

2초 대기 후:
```bash
cd v9
START_EVERYTHING.bat
```

---

### 3. 포트 충돌 (Port already in use)

**해결**:
```bash
cd v9
RESTART_SERVER.bat
```

이 스크립트가:
- 모든 프로세스 강제 종료
- 포트 5000/5001/8765 강제 해제
- 로그 백업
- 모든 봇 재시작

---

### 4. Dashboard/IMEI 페이지가 안 열림

**해결**:
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

### 5. IMEI가 응답 안 함 (Ollama 연결 실패)

**증상**: IMEI가 Mock Response만 출력

**원인**: Ollama 서버가 안 켜짐

**해결**:
```bash
cd v9
STOP_EVERYTHING.bat
START_EVERYTHING.bat
```

---

## 🎉 실행 중 화면

`START_EVERYTHING.bat` 실행 시 **6개 창**이 열립니다:

1. **Main 창** - 실행 진행 상황 표시 (닫지 마세요!)
2. **Ollama Server** - `localhost:11434` (모델 로딩)
3. **Signal Engine** - 시그널 생성
4. **Execution Engine** - 주문 실행
5. **Dashboard** - `http://localhost:5000`
6. **IMEI System** - `http://localhost:5001`

**+ 브라우저** - 대시보드 자동 오픈

---

## 📊 시스템 구조

```
START_EVERYTHING.bat
├── Ollama Server (port 11434)
│   └── Named Tunnel → http://ollama.thetheunique.com
├── Signal Engine (WebSocket Emitter)
├── Execution Engine (WebSocket Receiver, port 8765)
├── Dashboard (Flask, port 5000)
└── IMEI System (Flask, port 5001)
    └── → Ollama Router → localhost:11434
```

---

## 💡 Pro Tips

### 1. 자동 시작 설정

Windows 시작 프로그램에 추가:

1. `Win + R` → `shell:startup`
2. `START_EVERYTHING.bat`의 바로가기 생성
3. 시작 폴더에 복사

→ PC 켤 때마다 자동 실행!

---

### 2. 노트북 절전 모드 방지

**설정 > 전원 관리**

- 배터리: 5분
- 전원 연결: **절대 안 함** ✅

---

### 3. 슬립 모드 후 재시작

```bash
cd v9
RESTART_SERVER.bat
```

---

## 📁 BAT 파일 전체 목록

| 파일 | 용도 | 언제 사용? |
|------|------|----------|
| `START_EVERYTHING.bat` | **완전 자동 시작** ⭐ | 노트북 켤 때 (가장 중요!) |
| `STOP_EVERYTHING.bat` | 완전 종료 | 노트북 끄기 전 |
| `RESTART_SERVER.bat` | 문제 해결용 재시작 | 슬립 모드 후 / 오류 발생 시 |
| `QUICK_CHECK.bat` | 봇 상태 확인 | 봇이 제대로 실행 중인지 체크 |
| `LAPTOP_SERVER_START.bat` | 봇만 시작 (Ollama 제외) | Ollama가 이미 실행 중일 때 |
| `START_ALL_BOTS.bat` | 봇만 시작 (구버전) | 레거시 호환용 |
| `STOP_ALL_BOTS.bat` | 봇만 종료 | Ollama는 남기고 봇만 종료 |

---

## ❓ FAQ

### Q: Ollama Named Tunnel은 어떻게 설정했나요?

A: 이미 설정 완료! (`http://ollama.thetheunique.com`)

한 번만 설정하면 영구적으로 작동합니다.

---

### Q: Ollama 모델은 어디서 다운로드하나요?

A: **자동 다운로드!**

`START_EVERYTHING.bat` 실행 시 Ollama가 자동으로 `qwen2.5:7b` 모델을 다운로드합니다.

(처음 실행 시 약 5분 소요)

---

### Q: `.env` 파일이 필요한가요?

A: **Practice 모드는 불필요!**

Live 모드 (실전 거래) 시에만 필요합니다.

---

### Q: Cloudflare Tunnel을 다시 실행해야 하나요?

A: **아니요!** ❌

Named Tunnel은 영구 고정이므로 재실행 불필요합니다.

---

### Q: 봇이 안 켜질 때는?

A:
```bash
cd v9
STOP_EVERYTHING.bat
# 2초 대기
START_EVERYTHING.bat
```

---

### Q: Ollama가 너무 느린데요?

A: **GPU 사용 권장!**

Ollama는 GPU가 있으면 훨씬 빠릅니다.

CPU만 사용 시 응답이 느릴 수 있습니다.

---

## 🎯 체크리스트

### 최초 설정 (한 번만)
- [ ] Python 3.8+ 설치
- [ ] Ollama 설치 (https://ollama.com/download)
- [ ] Cloudflare Named Tunnel 설정 완료 ✅ (이미 완료!)

### 매일 아침
- [ ] `cd v9 && START_EVERYTHING.bat`
- [ ] 6개 창 + 브라우저 확인
- [ ] Dashboard 접속 확인 (http://localhost:5000)

### 매일 저녁
- [ ] `cd v9 && STOP_EVERYTHING.bat`
- [ ] 모든 창 닫힘 확인

---

## 🔥 요약

### **단 하나의 명령어**

```bash
cd v9 && START_EVERYTHING.bat
```

### **실행되는 것들**
1. Ollama Server (`localhost:11434`)
2. Signal Engine (시그널 생성)
3. Execution Engine (주문 실행)
4. Dashboard (`http://localhost:5000`)
5. IMEI System (`http://localhost:5001`)

### **Cloudflare Tunnel**
- 영구 고정: `http://ollama.thetheunique.com`
- **실행 불필요!** ❌

---

✅ **이제 정말로 한 줄이면 끝입니다!** 🎉

```bash
cd v9 && START_EVERYTHING.bat
```
