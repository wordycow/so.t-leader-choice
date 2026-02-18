# 🚀 원클릭 봇 시작/종료 가이드

## 📦 **파일 목록**

v9 디렉토리에 다음 4개의 스크립트가 생성되었습니다:

### Windows:
- `START_ALL_BOTS.bat` - 모든 봇 시작 (원클릭)
- `STOP_ALL_BOTS.bat` - 모든 봇 종료 (원클릭)

### Linux/Mac:
- `start_all_bots.sh` - 모든 봇 시작 (원클릭)
- `stop_all_bots.sh` - 모든 봇 종료 (원클릭)

---

## 🖥️ **Windows 사용법**

### 1️⃣ **모든 봇 시작하기**

#### 방법 1: 더블클릭
```
v9 폴더에서 START_ALL_BOTS.bat 파일을 더블클릭
```

#### 방법 2: 명령 프롬프트
```cmd
cd v9
START_ALL_BOTS.bat
```

**결과:**
- 4개의 새 창이 열립니다:
  1. **Signal Engine** - 신호 생성 (WebSocket Emitter)
  2. **Execution Engine** - 주문 실행 (WebSocket Receiver)
  3. **Dashboard** - 대시보드 (http://localhost:5000)
  4. **IMEI Main App** - IMEI 앱 (http://localhost:5001)

- 각 창은 독립적으로 실행됩니다
- 로그 파일이 `logs/` 폴더에 자동 저장됩니다

### 2️⃣ **모든 봇 종료하기**

#### 방법 1: 더블클릭
```
v9 폴더에서 STOP_ALL_BOTS.bat 파일을 더블클릭
```

#### 방법 2: 명령 프롬프트
```cmd
cd v9
STOP_ALL_BOTS.bat
```

#### 방법 3: 개별 창 닫기
- 각 봇 창에서 `Ctrl + C` 누르거나 창을 닫으면 됩니다

---

## 🐧 **Linux/Mac 사용법**

### 1️⃣ **모든 봇 시작하기**

```bash
cd v9
./start_all_bots.sh
```

**결과:**
- 4개의 서비스가 백그라운드에서 시작됩니다
- 각 서비스의 PID가 `pids/` 폴더에 저장됩니다
- 로그 파일이 `logs/` 폴더에 자동 저장됩니다

**로그 실시간 보기:**
```bash
# Signal Engine 로그
tail -f logs/signal_engine.log

# Execution Engine 로그
tail -f logs/execution_engine.log

# Dashboard 로그
tail -f logs/dashboard.log

# IMEI App 로그
tail -f logs/imei_app.log
```

### 2️⃣ **모든 봇 종료하기**

```bash
cd v9
./stop_all_bots.sh
```

---

## 📊 **시작된 서비스 확인**

### Windows:
작업 관리자를 열어 Python 프로세스 확인:
```
Ctrl + Shift + Esc → 프로세스 탭 → "python" 검색
```

### Linux/Mac:
```bash
# PID 확인
cat pids/*.pid

# 프로세스 확인
ps aux | grep python

# 포트 확인
lsof -i:5000  # Dashboard
lsof -i:5001  # IMEI App
```

---

## 🌐 **대시보드 접속**

봇이 시작되면 브라우저에서 다음 주소로 접속:

- **Trading Dashboard**: http://localhost:5000
- **IMEI Dashboard**: http://localhost:5000/imei_dashboard.html (or http://localhost:5001)

---

## 📁 **자동 생성되는 폴더**

스크립트 실행 시 다음 폴더가 자동으로 생성됩니다:

```
v9/
├── logs/                    # 로그 파일
│   ├── signal_engine.log
│   ├── execution_engine.log
│   ├── dashboard.log
│   └── imei_app.log
│
└── pids/                    # PID 파일 (Linux/Mac만)
    ├── signal_engine.pid
    ├── execution_engine.pid
    ├── dashboard.pid
    └── imei_app.pid
```

---

## ⚠️ **첫 실행 전 준비사항**

### 1. Python 설치 확인
```bash
# Windows
python --version

# Linux/Mac
python3 --version
```

**필요 버전**: Python 3.8 이상

### 2. 필요한 패키지 설치
```bash
pip install flask flask-cors pyupbit pandas numpy websockets
```

### 3. .env 파일 설정
```bash
# .env.example을 복사하여 .env 만들기
cp .env.example .env

# .env 파일 편집하여 API 키 입력
nano .env  # 또는 메모장으로 열기
```

**.env 파일 내용:**
```env
# Upbit API Keys
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here

# Trading Settings
ENABLE_REAL_TRADING=false
FIRST_PHASE_EXPOSURE_LIMIT=100000
DAILY_DRAWDOWN_LIMIT_PCT=2.0
```

---

## 🔧 **문제 해결**

### 문제 1: "Python을 찾을 수 없습니다"
**해결책:**
- Python이 설치되어 있는지 확인
- Python이 시스템 PATH에 추가되어 있는지 확인

### 문제 2: 포트가 이미 사용 중입니다
**해결책 (Windows):**
```cmd
# 포트 5000 사용 중인 프로세스 종료
netstat -ano | findstr :5000
taskkill /PID [프로세스ID] /F
```

**해결책 (Linux/Mac):**
```bash
# 포트 5000 사용 중인 프로세스 종료
lsof -ti:5000 | xargs kill -9
```

### 문제 3: 봇이 시작되지 않습니다
**확인사항:**
1. 로그 파일 확인: `logs/` 폴더의 로그 파일을 열어 오류 메시지 확인
2. .env 파일이 제대로 설정되었는지 확인
3. 필요한 Python 패키지가 모두 설치되었는지 확인

---

## 🎯 **자동 시작 설정 (Windows)**

### 노트북 부팅 시 자동 실행:

1. `Win + R` 키를 눌러 실행 창 열기
2. `shell:startup` 입력 후 Enter
3. 시작 폴더가 열리면, `START_ALL_BOTS.bat`의 바로가기를 이 폴더에 복사
4. 이제 Windows 부팅 시 자동으로 모든 봇이 시작됩니다!

**바로가기 만들기:**
```
START_ALL_BOTS.bat 파일 우클릭 
→ 바로가기 만들기 
→ 바로가기를 시작 폴더로 이동
```

---

## 🎯 **자동 시작 설정 (Linux/Mac)**

### 방법 1: crontab 사용
```bash
# crontab 편집
crontab -e

# 다음 줄 추가 (부팅 시 실행)
@reboot cd /path/to/webapp/v9 && ./start_all_bots.sh
```

### 방법 2: systemd 서비스 (Linux)
```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/upbit-bot.service
```

내용:
```ini
[Unit]
Description=Upbit Bot v9 + IMEI v3.0
After=network.target

[Service]
Type=forking
User=your_username
WorkingDirectory=/path/to/webapp/v9
ExecStart=/path/to/webapp/v9/start_all_bots.sh
ExecStop=/path/to/webapp/v9/stop_all_bots.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

활성화:
```bash
sudo systemctl daemon-reload
sudo systemctl enable upbit-bot.service
sudo systemctl start upbit-bot.service
```

---

## 📝 **스크립트 동작 흐름**

### START_ALL_BOTS.bat/sh:
```
1. 현재 디렉토리 확인
2. Python 설치 확인
3. .env 파일 확인 (없으면 경고)
4. logs/ 폴더 생성
5. pids/ 폴더 생성 (Linux/Mac)
6. Signal Engine 시작
7. Execution Engine 시작
8. Dashboard 시작 (port 5000)
9. IMEI Main App 시작 (port 5001)
10. 상태 메시지 출력
```

### STOP_ALL_BOTS.bat/sh:
```
1. Signal Engine 종료
2. Execution Engine 종료
3. Dashboard 종료
4. IMEI Main App 종료
5. 포트 5000, 5001 정리
6. 완료 메시지 출력
```

---

## ✅ **실행 확인 체크리스트**

봇이 정상적으로 시작되었는지 확인:

- [ ] 4개의 프로세스가 실행 중입니다 (Windows: 4개 창, Linux/Mac: 4개 PID)
- [ ] `logs/` 폴더에 4개의 로그 파일이 생성되었습니다
- [ ] http://localhost:5000 접속 시 대시보드가 보입니다
- [ ] http://localhost:5001/health 접속 시 JSON 응답이 옵니다
- [ ] 로그 파일에 오류 메시지가 없습니다

---

## 📞 **추가 도움말**

문제가 해결되지 않으면:
1. 로그 파일 확인: `logs/` 폴더의 모든 로그 파일 열어보기
2. Python 버전 확인: `python --version` (3.8 이상 필요)
3. 패키지 재설치: `pip install -r requirements.txt`
4. GitHub Issues: https://github.com/wordycow/so.t-leader-choice/issues

---

**Created**: 2026-02-18  
**Version**: v9 + IMEI v3.0  
**작성자**: Yusong + Claude
