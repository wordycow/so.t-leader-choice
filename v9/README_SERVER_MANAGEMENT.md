# 🔧 서버 관리 가이드 (노트북 절전/재시작 대응)

## 📋 상황별 대응 방법

### 1️⃣ **노트북이 절전모드에서 깨어났을 때**
```bash
cd v9
RESTART_SERVER.bat
```
- 모든 프로세스 종료 후 재시작
- 포트 충돌 자동 해결
- 로그 백업 후 정리

### 2️⃣ **서버 상태가 궁금할 때**
```bash
cd v9
QUICK_CHECK.bat
```
- Python 프로세스 확인
- 포트 3개 (5000, 5001, 8765) 체크
- 로그 파일 상태 확인

### 3️⃣ **깨끗하게 처음부터 시작**
```bash
cd v9
STOP_ALL_BOTS.bat    # 1단계: 모두 종료
RESTART_SERVER.bat   # 2단계: 재시작
```

---

## 🛠️ BAT 파일 설명

### **RESTART_SERVER.bat** (서버 재시작)
- ✅ 모든 Python 프로세스 강제 종료
- ✅ 포트 5000, 5001, 8765 점유 해제
- ✅ 로그 파일 백업 및 정리
- ✅ SQLite WAL/SHM 파일 정리
- ✅ 4개 봇 자동 재시작

**사용 시점**:
- 노트북 절전모드 이후
- 네트워크 재연결 후
- 봇이 응답하지 않을 때
- 포트 충돌 발생 시

### **QUICK_CHECK.bat** (빠른 상태 확인)
- ✅ Python 프로세스 실행 여부
- ✅ 3개 포트 리스닝 상태
- ✅ 로그 파일 크기 및 수정 시간

**사용 시점**:
- 봇이 작동하는지 확인
- 재시작 필요 여부 판단

### **START_ALL_BOTS.bat** (정상 시작)
- ✅ 처음부터 깨끗하게 시작
- ✅ 환경 체크 (Python, .env)
- ✅ 로그 디렉토리 생성

**사용 시점**:
- 노트북 재부팅 후
- 처음 봇 실행 시

### **STOP_ALL_BOTS.bat** (전체 종료)
- ✅ 모든 봇 안전하게 종료
- ✅ 4개 창 모두 닫기

**사용 시점**:
- 봇 사용 종료 시
- 재시작 전 수동 종료

---

## 🚨 문제 해결 (Troubleshooting)

### **문제 1: "Port already in use" 오류**
**해결**:
```bash
RESTART_SERVER.bat
```
→ 포트 점유 프로세스 자동 종료

### **문제 2: Dashboard/IMEI가 안 열림**
**확인**:
```bash
QUICK_CHECK.bat
```
→ 포트 상태 확인 후 `RESTART_SERVER.bat` 실행

### **문제 3: Python 프로세스가 없음**
**해결**:
1. Python 설치 확인: `python --version`
2. 가상환경 활성화 확인
3. `RESTART_SERVER.bat` 실행

### **문제 4: 로그에 에러가 계속 쌓임**
**해결**:
```bash
RESTART_SERVER.bat
```
→ 로그 자동 백업 후 새로 시작

### **문제 5: 노트북 절전 후 연결 끊김**
**해결**:
```bash
RESTART_SERVER.bat
```
→ WebSocket 재연결 자동 처리

---

## 📊 정상 상태 확인 방법

### **QUICK_CHECK.bat 실행 후 정상 출력**:
```
[CHECK 1] Python processes:
  python.exe                  12345 Console                 1     45,678 K
  python.exe                  12346 Console                 1     38,912 K
  python.exe                  12347 Console                 1     42,156 K
  python.exe                  12348 Console                 1     51,234 K
  [OK] Python is running.

[CHECK 2] Network ports:
  [OK] Port 5000 (Dashboard) - Listening
  [OK] Port 5001 (IMEI) - Listening
  [OK] Port 8765 (WebSocket) - Listening

[CHECK 3] Recent log activity:
  Dashboard log:
    Size: 12345 bytes, Modified: 2026-02-18 18:30
  IMEI log:
    Size: 8912 bytes, Modified: 2026-02-18 18:30
```

### **브라우저 확인**:
- http://localhost:5000 → Dashboard 정상 표시
- http://localhost:5001/health → IMEI 상태 확인

---

## 🔄 일상적인 사용 패턴

### **아침에 노트북 켜면**:
```bash
cd v9
QUICK_CHECK.bat         # 1. 상태 확인
RESTART_SERVER.bat      # 2. 문제 있으면 재시작
```

### **봇 사용 중**:
- 4개 창 열어두기 (최소화 가능)
- Dashboard 브라우저 탭 유지

### **저녁에 노트북 끄기 전**:
```bash
cd v9
STOP_ALL_BOTS.bat
```

---

## 💡 팁

1. **절전모드 설정**: 
   - Windows 설정 → 전원 → 절전모드 시간 늘리기
   - 또는 전원 연결 시 절전 안 함

2. **자동 시작** (선택):
   - `shell:startup` 폴더에 `START_ALL_BOTS.bat` 바로가기 생성
   - 노트북 부팅 시 자동 실행

3. **로그 모니터링**:
   - `logs/` 폴더 정기적으로 확인
   - 백업 폴더 주기적으로 정리

4. **네트워크 문제**:
   - WiFi 재연결 시 `RESTART_SERVER.bat` 실행
   - VPN 사용 시 주의 (포트 차단 가능)

---

**🎯 기본 원칙: 문제 생기면 `RESTART_SERVER.bat` 실행!**
