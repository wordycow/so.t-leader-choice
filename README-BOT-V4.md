# 🤖 업비트 스마트 스캘핑 봇 v4.0

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

업비트 자동 매매 봇 - 5단계 분할 매수 + 3단계 익절 전략 + SOL 수익 전환

---

## 🌟 주요 특징

### ⭐ v4.0 신기능
- **5단계 분할 매수**: 6천원 → 1만원(×3) → 10만원 (총 136,000원)
- **3단계 익절 매도**: 가장 높은 가격에서 가장 큰 금액(50%) 우선 매도
- **수익 SOL 전환**: 3단계 익절 완료 시 수익금 자동 솔라나 매수
- **NOW 독립 운영**: 24시간 자체 로직으로 작동 (NOW는 참고용)
- **스마트 손절**: -15% 이하 시 자동 전량 매도

### 🛡️ 안전 기능
- 상장폐지 코인 자동 차단
- USDT/BTC 마켓 제외
- 시뮬레이션 모드 기본 제공
- 상세한 로그 기록

---

## 📊 전략 요약

### 매수 전략 (5단계)

| 단계 | 금액 | RSI 조건 | 하락률 | 설명 |
|------|------|----------|--------|------|
| 1 | 6,000원 | 28~30 | 0% | 첫 진입 (테스트) |
| 2 | 10,000원 | 26~28 | -3% | 추가 매수 |
| 3 | 10,000원 | 24~26 | -5% | 본격 매수 |
| 4 | 10,000원 | 22~24 | -7% | 집중 매수 |
| 5 | 100,000원 | <22 | -10% | 최종 승부수 |

### 매도 전략 (3단계)

| 단계 | 비율 | 목표 수익률 | 설명 |
|------|------|-------------|------|
| 1차 | 50% | +2.5% | 고가에서 최대 물량 매도 |
| 2차 | 30% | +2.0% | 중간 수익 확정 |
| 3차 | 20% | +1.5% | 잔량 정리 |

---

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/wordycow/so.t-leader-choice.git
cd so.t-leader-choice

# 필수 라이브러리 설치
pip3 install pyupbit pandas numpy
```

### 2. API 키 설정

`api_keys.json` 파일 생성:

```json
{
  "access_key": "여기에_실제_Access_Key_입력",
  "secret_key": "여기에_실제_Secret_Key_입력"
}
```

**API 키 발급 방법:**
1. [업비트](https://upbit.com) 로그인
2. 프로필 → Open API 관리 → API 키 발급
3. 권한: ✅ 자산조회, ✅ 주문조회, ✅ 주문하기 (❌ 출금하기 금지!)

### 3. 실행

#### 방법 1: 빠른 시작 스크립트 (추천)
```bash
./start-bot-v4.sh
```

#### 방법 2: 직접 실행
```bash
python3 upbit-smart-bot-v4.py
```

---

## 📖 문서

- **[v4.0 완전 가이드](UPBIT-BOT-V4-GUIDE.md)**: 설치부터 실전까지 모든 것
- **[버전 비교표](BOT-VERSION-COMPARISON.md)**: v2.1 vs v3.0 vs v4.0 비교
- **[안전 기능](SAFETY-FEATURES.md)**: 상장폐지 차단 등

---

## 🎯 사용 예시

### 성공적인 5단계 매수 + 3단계 익절 시나리오

```
[초기 자금] 200,000원

[1단계] BTC 매수 6,000원 @ 50,000,000원
[2단계] BTC 추가 10,000원 @ 48,500,000원 (-3%)
[3단계] BTC 추가 10,000원 @ 47,500,000원 (-5%)
[4단계] BTC 추가 10,000원 @ 46,500,000원 (-7%)
[5단계] BTC 최종 100,000원 @ 45,000,000원 (-10%)

[평단가] 약 45,735,294원
[총 투자] 136,000원
[보유량] 0.00297 BTC

[상승] BTC 가격 46,878,676원 도달 (+2.5%)
[1차 익절] 50% 매도 → 수익 약 1,700원

[상승] BTC 가격 46,650,000원 (+2.0%)
[2차 익절] 30% 매도 → 추가 수익 약 550원

[상승] BTC 가격 46,422,324원 (+1.5%)
[3차 익절] 20% 매도 → 추가 수익 약 410원

[총 수익] 약 2,660원 (+2.0%)
[SOL 전환] ❌ (5,000원 미만)
```

---

## ⚙️ 고급 설정

### 시뮬레이션 → 실전 모드 전환

1. `upbit-smart-bot-v4.py` 파일 열기
2. 주석 해제:

```python
# 매수 주문 (약 646번째 줄)
order = upbit.buy_market_order(ticker, buy_amount)  # 이 줄 활성화

# 매도 주문 (약 680번째 줄)
order = upbit.sell_market_order(ticker, sell_amount)  # 이 줄 활성화

# SOL 전환 (약 733번째 줄)
order = upbit.buy_market_order(sol_ticker, profit_krw)  # 이 줄 활성화
```

### 백그라운드 실행

#### Linux/Mac
```bash
nohup python3 upbit-smart-bot-v4.py > output.log 2>&1 &

# 로그 확인
tail -f bot.log

# 종료
kill <PID>
```

#### Windows PowerShell
```powershell
Start-Process python -ArgumentList "upbit-smart-bot-v4.py" -WindowStyle Hidden

# 로그 확인
Get-Content bot.log -Wait -Tail 20

# 종료
Stop-Process -Name python
```

---

## 🔍 모니터링

### 로그 확인

```bash
# 전체 로그
cat bot.log

# 최근 50줄
tail -n 50 bot.log

# 실시간 로그
tail -f bot.log

# 에러만 검색
grep ERROR bot.log
```

### 주요 로그 레벨

- `[INFO]`: 일반 정보
- `[SUCCESS]`: 성공한 작업
- `[WARNING]`: 주의 필요
- `[ERROR]`: 오류 발생
- `[STRATEGY]`: 전략 판단
- `[REASON]`: 매수/매도 이유

---

## ⚠️ 주의사항

### 필수 확인 사항

1. **자금 관리**
   - 최소 권장 자금: 200,000원
   - 실제 투자: 136,000원 (5단계 완료 시)
   - 잔여 자금: 긴급 상황 대비

2. **리스크**
   - 가상화폐 거래는 고위험
   - 손실 가능성 항상 존재
   - 반드시 여유 자금으로만 운영

3. **보안**
   - API 키 절대 공유 금지
   - 출금 권한 절대 활성화 금지
   - `api_keys.json` 파일 Git 업로드 금지

4. **테스트**
   - 실전 전 최소 24시간 시뮬레이션
   - 소액으로 먼저 테스트
   - 로그 주기적 확인

---

## 📈 버전 히스토리

### v4.0 (2026-02-15) ⭐ Current
- ✨ 5단계 분할 매수 (6천→1만×3→10만)
- 📈 3단계 익절 매도 (50%→30%→20%)
- 🔄 수익 자동 SOL 전환
- ⏰ 24시간 독립 운영
- 📋 NOW 상태 참고용 분리

### v3.0 (2026-02-14)
- 보수적 전략 + 마틴게일
- 5단계 매수 (1만×4 + 10만)
- 관망 우선 전략 (85~90%)

### v2.1 (2026-02-13)
- 상장폐지 코인 자동 차단
- USDT/BTC 마켓 제외
- 안전 기능 강화

---

## 🤝 기여

버그 리포트, 기능 제안, Pull Request 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 📞 지원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discussions**: 질문 및 아이디어 공유
- **Wiki**: 상세 문서 (작성 예정)

---

## ⚖️ 면책 조항

```
⚠️  중요 공지:
• 본 봇은 교육/학습 목적으로 제공됩니다.
• 투자 손실에 대한 책임은 사용자 본인에게 있습니다.
• 가상화폐 거래는 높은 리스크를 동반합니다.
• 반드시 여유 자금으로만 운영하세요.
• 과거 수익률이 미래를 보장하지 않습니다.
```

---

## 🔗 관련 링크

- **업비트 API 문서**: https://docs.upbit.com/
- **pyupbit 라이브러리**: https://github.com/sharebook-kr/pyupbit
- **GitHub 저장소**: https://github.com/wordycow/so.t-leader-choice

---

**마지막 업데이트**: 2026-02-15  
**작성자**: so.t Team  
**버전**: 4.0.0

---

## 🌟 Star History

도움이 되셨다면 ⭐ Star를 눌러주세요!

[![Star History Chart](https://api.star-history.com/svg?repos=wordycow/so.t-leader-choice&type=Date)](https://star-history.com/#wordycow/so.t-leader-choice&Date)
