# 🚀 업비트 스마트 봇 v5.0 - 사용 설명서

## ⚠️ **중요: 먼저 읽어주세요!**

Python이 설치되어 있어야 합니다.

### Python 설치 확인
```
명령 프롬프트(cmd)에서:
python --version

버전이 나오면 OK! (예: Python 3.11.0)
안 나오면 Python 설치 필요
```

### Python 설치 방법
1. https://www.python.org/downloads/ 접속
2. "Download Python" 클릭
3. ⚠️ **설치 시 "Add Python to PATH" 반드시 체크!**
4. 설치 완료

---

## 📦 **사용법 (2단계)**

### 1️⃣ **INSTALL.bat 실행** (처음 한 번만)

```
INSTALL.bat 더블 클릭

Python 확인 중...
Python 3.11.0

[1/2] 라이브러리 설치 중...
  - pip 업그레이드
  - pyupbit 설치
  - pandas 설치
  - numpy 설치
  - flask 설치
  - flask-cors 설치

[2/2] 설치 확인...
  flask, pyupbit, pandas 확인됨

설치 완료!
이제 START.bat을 실행하세요!
```

### 2️⃣ **START.bat 실행** (매번)

```
START.bat 더블 클릭

→ 2초 후 웹 브라우저 자동 열림
→ http://localhost:5000
→ API 키 입력
→ [▶ 봇 시작] 클릭
```

---

## 🛑 **봇 중지 방법**

### 방법 1: 웹 대시보드 (추천 ⭐)
```
웹 브라우저에서 [⏸ 봇 중지] 클릭
```

### 방법 2: 터미널 창 닫기
```
START.bat 실행 시 나타난 검은색 창 닫기
```

### 방법 3: Ctrl+C
```
터미널 창에서 Ctrl+C 누르기
```

---

## 🔄 **재시작**

```
START.bat 다시 더블 클릭
```

---

## ❓ **문제 해결**

### Q1. "Python이 설치되지 않았습니다" 오류
**A:** Python을 설치하세요.
```
https://www.python.org/downloads/
설치 시 "Add Python to PATH" 체크 필수!
```

### Q2. "pip를 찾을 수 없습니다" 오류
**A:** 명령 프롬프트를 **관리자 권한**으로 실행 후:
```bash
cd C:\Users\wordy\Downloads\upbit-bot-v5.0-COMPLETE

python -m pip install --upgrade pip
python -m pip install pyupbit pandas numpy flask flask-cors
```

### Q3. INSTALL.bat 실행 시 오류 발생
**A:** 수동으로 설치하세요.
```
1. 명령 프롬프트(cmd)를 관리자 권한으로 실행
2. cd 명령어로 폴더 이동
3. 아래 명령어 실행:

python -m pip install pyupbit pandas numpy flask flask-cors
```

### Q4. 웹 페이지가 안 열려요
**A:** 브라우저에서 직접 입력:
```
http://localhost:5000
```

---

## ✅ **API 키 입력 방법**

### 1단계: 업비트 API 키 발급
1. https://upbit.com 로그인
2. 마이페이지 → Open API 관리
3. API 키 발급 클릭
4. **권한 설정:**
   - ✅ 자산 조회
   - ✅ 주문 조회
   - ✅ 주문하기
   - ❌ 출금하기 (절대 체크 금지!)
5. Access Key, Secret Key 복사

### 2단계: 웹 대시보드에 입력
1. http://localhost:5000 접속
2. 우측 상단 **⚙️ 설정** 클릭
3. Access Key 붙여넣기
4. Secret Key 붙여넣기
5. **저장** 클릭

### 3단계: 봇 시작
1. **▶ 봇 시작** 클릭
2. 상태가 **🟢 실행중**으로 변경
3. 실시간 모니터링 시작!

---

## 💡 **핵심 기능**

### 💰 5단계 분할 매수
- 1단계: 6,000원
- 2-4단계: 각 10,000원
- 5단계: 100,000원

### 📈 3단계 분할 익절
- 1차: 50% @ +2.5%
- 2차: 30% @ +2.0%
- 3차: 20% @ +1.5%

### 💎 수익 자동 재투자
- SOL, XRP, BTC, HBAR 각 10,000원

### 🛡️ 시드 보호
- 초기 자본 절대 보존

---

## ⚠️ **안전 수칙**

✅ **반드시 지키세요:**
1. API 키 출금 권한 절대 금지
2. 소액으로 시작 (10만원 이하)
3. 시뮬레이션 24시간 이상
4. API 키 절대 공유 금지

---

## 📞 **지원**

- GitHub: https://github.com/wordycow/so.t-leader-choice
- Issues: https://github.com/wordycow/so.t-leader-choice/issues

---

## 🎉 **완료!**

**다시 한 번 요약:**
1. INSTALL.bat 더블 클릭 (처음 한 번만)
2. START.bat 더블 클릭 (매번)
3. 웹에서 API 키 입력
4. 봇 시작!

**봇 중지:**
- 웹에서 [⏸ 봇 중지] 클릭
- 또는 터미널 창 닫기
