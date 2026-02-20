# 🤖 Lee May Training Center

**Lee May AI 훈련소 - 통합 관리 대시보드**

---

## 📋 개요

Lee May와 Trading Bot을 한 곳에서 관리하고 훈련시키는 통합 플랫폼입니다.

### 주요 기능
- 🤖 **봇 관리**: Lee May API, Trading Bot, YouTube Learner 실시간 제어
- 📊 **능력치 모니터링**: 감정 표현, 대화 이해도, 기억력, 유머 등
- 💬 **실시간 채팅**: Lee May와 직접 대화
- ⚙️ **시스템 모니터링**: CPU, 메모리, 디스크 사용량

---

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/wordycow/so.t-leader-choice.git
cd so.t-leader-choice
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. API 서버 실행
```bash
python api/main_api.py
```

### 4. 접속
- 로컬: http://localhost:6000
- 외부: https://leemay.더유니크.com

---

## 📁 프로젝트 구조

```
so.t-leader-choice/
├── api/
│   └── main_api.py          # 메인 API 서버
├── bots/
│   ├── bot_manager.py       # 봇 제어 관리자
│   ├── leemay/
│   │   ├── leemay_api.py    # Lee May 핵심 봇
│   │   └── youtube_learner.py  # 유튜브 학습 봇
│   └── trading/
│       └── trading_bot.py   # 트레이딩 봇
├── web/
│   └── dashboard.html       # 메인 대시보드
├── data/
│   └── pids.json            # 봇 프로세스 정보
└── scripts/
    ├── START.bat            # 시작 스크립트
    └── STOP.bat             # 종료 스크립트
```

---

## 🔌 API 엔드포인트

### 봇 제어
- `GET /api/bots/status` - 모든 봇 상태 조회
- `POST /api/bots/<bot_name>/start` - 봇 시작
- `POST /api/bots/<bot_name>/stop` - 봇 중지
- `POST /api/bots/<bot_name>/restart` - 봇 재시작

### 능력치
- `GET /api/stats` - Lee May & Trading Bot 능력치

### 시스템
- `GET /api/system/status` - CPU, 메모리, 디스크 사용량

### 채팅
- `POST /api/chat` - Lee May와 대화

---

## 🌐 도메인 연결 (Cloudflare Tunnel)

### 1. Cloudflare Tunnel 설치
```bash
# Windows
winget install cloudflare.cloudflared
```

### 2. 터널 생성
```bash
cloudflared tunnel create leemay-server
```

### 3. 설정 파일 (`config.yml`)
```yaml
tunnel: <TUNNEL_ID>
credentials-file: C:\Users\wordy\.cloudflared\<TUNNEL_ID>.json

ingress:
  - hostname: leemay.더유니크.com
    service: http://localhost:6000
  - service: http_status:404
```

### 4. DNS 설정
Cloudflare Dashboard에서 CNAME 레코드 추가:
- `leemay` → `<TUNNEL_ID>.cfargotunnel.com`

### 5. 터널 실행
```bash
cloudflared tunnel run leemay-server
```

---

## 📦 필수 요구사항

- Python 3.8+
- Flask 2.3.0+
- psutil 5.9.0+

---

## 🛠️ 개발

### 봇 추가하기
1. `bots/` 폴더에 새 봇 스크립트 추가
2. `bot_manager.py`의 `bot_paths`에 경로 등록
3. API 재시작

### 능력치 계산 로직 추가
`api/main_api.py`의 `/api/stats` 엔드포인트 수정

---

## 📄 라이선스

MIT License

---

## 👤 작성자

**wordycow**
- GitHub: [@wordycow](https://github.com/wordycow)
- Website: https://더유니크.com
