# 🚀 업비트 스마트 봇 v5.0 - 빠른 시작

## 📦 설치 방법 (2단계)

### 1️⃣ **INSTALL.bat 실행** (처음 한 번만)

```
INSTALL.bat 더블 클릭
→ 필수 라이브러리 자동 설치 (2분 소요)
→ 완료!
```

### 2️⃣ **START.bat 실행** (매번)

```
START.bat 더블 클릭
→ 웹 브라우저 자동 열림
→ API 키 입력
→ 봇 시작!
```

---

## 🎯 자세한 사용법

### 📥 **1단계: 다운로드 & 압축 해제**
```
https://github.com/wordycow/so.t-leader-choice/raw/main/upbit-bot-v5.0-FINAL.zip

다운로드 후 압축 해제
```

### 🔧 **2단계: 설치 (처음 한 번만)**
```
폴더 안의 INSTALL.bat 더블 클릭

[1/3] 필수 라이브러리 설치 중...
  - pip 업그레이드
  - pyupbit, pandas, numpy 설치
  - flask, flask-cors 설치

[2/3] 설치 확인 중...
  - flask, pyupbit, pandas 확인

[3/3] 설치 완료!
```

### ▶️ **3단계: 봇 시작**
```
START.bat 더블 클릭

→ 웹 브라우저가 자동으로 열림 (http://localhost:5000)
→ 우측 상단 [⚙️ 설정] 클릭
→ Access Key, Secret Key 입력
→ [저장] 클릭
→ [▶ 봇 시작] 클릭
```

### ⏸️ **봇 중지 (3가지 방법)**

**방법 1: 웹 대시보드** (추천)
```
웹 브라우저에서 [⏸ 봇 중지] 클릭
→ 거래만 중지, 웹은 계속 열려있음
```

**방법 2: 터미널 창 닫기**
```
START.bat 실행 시 열린 검은색 창 닫기
→ 봇 완전 종료
```

**방법 3: Ctrl+C**
```
터미널 창 클릭 → Ctrl+C 누르기
→ 봇 완전 종료
```

### 🔄 **재시작**
```
START.bat 다시 더블 클릭
→ 웹 브라우저 자동 열림
→ [▶ 봇 시작] 클릭
```

---

## 📂 **파일 구조**

```
upbit-bot-v5.0-FINAL/
│
├── INSTALL.bat          ← 처음 한 번만 실행 (라이브러리 설치)
├── START.bat            ← 매번 실행 (봇 시작)
│
├── upbit-smart-bot-v5.py     (봇 메인 코드)
├── templates/
│   └── dashboard.html        (웹 대시보드)
│
├── README.md                 (이 파일)
└── SUPER-EASY-GUIDE.md       (초보자 완전 가이드)
```

---

## ❓ **자주 묻는 질문**

### Q1. INSTALL.bat 실행 시 오류가 나요
**A.** Python이 설치되어 있는지 확인하세요.
```
명령 프롬프트(cmd)에서:
python --version

버전이 나오면 정상, 안 나오면 Python 설치 필요
https://www.python.org/downloads/
설치 시 "Add Python to PATH" 체크 필수!
```

### Q2. START.bat 실행 시 Flask 오류가 나요
**A.** INSTALL.bat을 먼저 실행하세요.
```
INSTALL.bat 더블 클릭 → 설치 완료 후 → START.bat 실행
```

### Q3. 웹 페이지가 안 열려요
**A.** 브라우저에서 직접 입력하세요.
```
http://localhost:5000
```

### Q4. 봇이 거래를 안 해요
**A.** 기본적으로 시뮬레이션 모드입니다.
```
실전 모드로 전환하려면:
1. upbit-smart-bot-v5.py 파일을 메모장으로 열기
2. Ctrl+F로 "# order =" 검색
3. 주석(#) 제거하여 주문 활성화
4. 저장 후 봇 재시작
```

---

## 🛑 **중요: 시뮬레이션 → 실전 모드 전환**

기본적으로 **시뮬레이션 모드**로 실행됩니다 (실제 주문 안 됨).

### 실전 모드로 전환:
1. `upbit-smart-bot-v5.py` 파일을 메모장으로 열기
2. Ctrl+F로 아래 3곳 찾기:

**매수 주문 (약 510번째 줄)**
```python
# order = upbit.buy_market_order(ticker, buy_amount)
↓
order = upbit.buy_market_order(ticker, buy_amount)
```

**매도 주문 (약 546번째 줄)**
```python
# order = upbit.sell_market_order(ticker, sell_amount)
↓
order = upbit.sell_market_order(ticker, sell_amount)
```

**수익 투자 (약 269번째 줄)**
```python
# order = upbit.buy_market_order(next_target, PROFIT_INVEST_AMOUNT)
↓
order = upbit.buy_market_order(next_target, PROFIT_INVEST_AMOUNT)
```

3. 저장 후 START.bat 재실행

⚠️ **주의**: 소액(10만원 이하)으로 먼저 테스트하세요!

---

## ✅ **핵심 기능**

### 💰 5단계 분할 매수
- 1단계: 6,000원 (RSI 28-30)
- 2-4단계: 각 10,000원
- 5단계: 100,000원
- **총 투자: 136,000원**

### 📈 3단계 분할 익절
- 1차: 50% @ +2.5%
- 2차: 30% @ +2.0%
- 3차: 20% @ +1.5%

### 💎 수익 자동 재투자
3단계 익절 완료 시:
- SOL 10,000원
- XRP 10,000원
- BTC 10,000원
- HBAR 10,000원

### 🛡️ 시드 보호
- 초기 원화 잔고 기록
- 현재 원화 < 초기 시드 → 매수 차단
- 대시보드에 실시간 경고

---

## ⚠️ **안전 수칙**

✅ **반드시 지키세요**
1. API 키 출금 권한 절대 금지
2. 소액으로 시작 (10만원 이하)
3. 시뮬레이션 먼저 24시간 이상
4. API 키 절대 공유 금지
5. 정기적인 수익/손실 확인

---

## 📞 **지원**

- **GitHub**: https://github.com/wordycow/so.t-leader-choice
- **초보자 가이드**: SUPER-EASY-GUIDE.md
- **Issues**: https://github.com/wordycow/so.t-leader-choice/issues

---

## 🎉 **완료!**

이제 자동매매를 시작할 준비가 되었습니다! 🚀

**다시 한 번 요약:**
1. **INSTALL.bat** 더블 클릭 (처음 한 번만)
2. **START.bat** 더블 클릭 (매번)
3. 웹에서 API 키 입력
4. 봇 시작!
