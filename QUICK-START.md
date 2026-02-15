# 🚀 업비트 스캘핑 봇 - 빠른 시작 가이드

## 📋 5분 만에 시작하기

### 1️⃣ API 키 발급 (2분)
1. https://upbit.com 접속 → 로그인
2. **프로필** → **Open API 관리**
3. **API 키 발급** 클릭
4. **권한 선택**:
   - ✅ 자산 조회
   - ✅ 주문 조회
   - ✅ 주문 하기
   - ❌ 출금 하기 (절대 체크 금지!)
5. OTP 인증 후 **Access Key**와 **Secret Key** 복사

---

### 2️⃣ 패키지 설치 (1분)
```bash
cd /home/user/webapp
pip install -r requirements-bot.txt
```

---

### 3️⃣ API 키 설정 (1분)

#### 방법 A: .env 파일 사용 (추천 ⭐)
```bash
# 템플릿 복사
cp .env.example .env

# 파일 편집
nano .env
```

`.env` 파일 내용:
```
UPBIT_ACCESS_KEY=여기에_실제_Access_Key_붙여넣기
UPBIT_SECRET_KEY=여기에_실제_Secret_Key_붙여넣기
```

저장: `Ctrl + O` → `Enter` → `Ctrl + X`

#### 방법 B: 환경변수 직접 설정
```bash
export UPBIT_ACCESS_KEY="여기에_실제_Access_Key"
export UPBIT_SECRET_KEY="여기에_실제_Secret_Key"
```

---

### 4️⃣ 봇 설정 확인 (30초)

`upbit-scalping-bot.py` 파일 열기:
```bash
nano upbit-scalping-bot.py
```

**26번째 줄 근처** 설정 확인:
```python
TICKER = "KRW-BTC"           # 거래할 코인 (비트코인)
TOTAL_SEED = 1_000_000       # 시드머니 (100만원)
SPLIT_COUNT = 5              # 5단계 분할
TARGET_PROFIT_RATE = 0.015   # 목표 수익률 1.5%
STOP_LOSS_RATE = -0.03       # 손절 -3%
```

필요하면 수정 후 저장

---

### 5️⃣ 봇 실행 (30초)

#### 옵션 1: 간단 실행 (테스트용)
```bash
python3 upbit-scalping-bot.py
```
종료: `Ctrl + C`

#### 옵션 2: 백그라운드 실행 (24시간 운영)
```bash
./bot-manager.sh start
```

---

## 🎛️ 봇 관리 명령어

### 봇 관리 스크립트 사용
```bash
# 봇 시작
./bot-manager.sh start

# 봇 상태 확인
./bot-manager.sh status

# 봇 종료
./bot-manager.sh stop

# 봇 재시작
./bot-manager.sh restart

# 실시간 로그 보기
./bot-manager.sh log
```

### 모니터링 스크립트
```bash
# 현재 상태 + 오늘의 거래 요약
./monitor-bot.sh
```

---

## 📊 모니터링

### 실시간 로그 확인
```bash
tail -f bot.log
```

### 오늘 거래 내역
```bash
grep "$(date +%Y-%m-%d)" bot.log | grep "매수\|매도"
```

### 수익률 확인
```bash
grep "수익률" bot.log | tail -n 10
```

### 에러 확인
```bash
grep "ERROR" bot.log
```

---

## 🚨 문제 해결

### "API 키가 설정되지 않았습니다"
```bash
# 환경변수 확인
echo $UPBIT_ACCESS_KEY

# 없으면 다시 설정
export UPBIT_ACCESS_KEY="..."
export UPBIT_SECRET_KEY="..."
```

### "pyupbit 모듈이 없습니다"
```bash
pip install pyupbit pandas numpy python-dotenv
```

### "잔고가 부족합니다"
- 업비트 계정에 KRW 충전
- 또는 `TOTAL_SEED` 값을 줄이기

### 봇이 거래를 안 함
- 로그 확인: `tail -f bot.log`
- 시장 상황 확인 (횡보장에서는 거래 적음)
- RSI/볼린저밴드 조건 확인

---

## ⚠️ 안전 수칙

1. **소액으로 시작**: 처음엔 10만원 정도로 테스트
2. **출금 권한 금지**: API 키에 출금 권한 절대 부여 금지
3. **API 키 보안**: .env 파일을 Git에 올리지 않기
4. **정기 모니터링**: 하루 3번 이상 상태 체크
5. **손절 준수**: 설정한 손절 라인 지키기

---

## 📞 도움말

### 자세한 가이드
- **API 설정**: `UPBIT-API-SETUP-GUIDE.md`
- **전체 문서**: `UPBIT-BOT-README.md`

### 긴급 중지
```bash
# 프로세스 찾기
ps aux | grep upbit-scalping-bot

# 종료
kill -9 <PID>

# 또는
./bot-manager.sh stop
```

---

## 🎯 다음 단계

1. ✅ 소액으로 24시간 테스트
2. ✅ 수익률 및 승률 분석
3. ✅ 파라미터 최적화 (RSI, 볼린저밴드 기준)
4. ✅ 다른 코인으로 확장 테스트
5. ✅ 텔레그램 알림 추가

---

**✨ 안전하고 수익성 있는 트레이딩 되세요! 화이팅! 🚀**
