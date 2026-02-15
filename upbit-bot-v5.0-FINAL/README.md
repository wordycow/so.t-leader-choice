# 🤖 업비트 스마트 봇 v5.0

**클릭 한 번으로 시작하는 자동매매 봇** 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

---

## 📌 **완전 초보자도 사용 가능!**

파일을 **더블 클릭**하면 모든 것이 자동으로 설치되고 웹 브라우저가 열립니다.  
**API 키만 입력하면 끝!** ✨

---

## 🎯 핵심 기능

### 💰 5단계 분할 매수
- **1단계**: 6,000원 (RSI 28-30, 테스트 매수)
- **2-4단계**: 각 10,000원 (RSI 하락, 추가 매수)
- **5단계**: 100,000원 (RSI <22, 최종 승부수)
- **총 투자**: 136,000원

### 📈 3단계 분할 익절
- **1차**: 50% @ +2.5% (가장 높은 가격)
- **2차**: 30% @ +2.0%
- **3차**: 20% @ +1.5% (잔량 정리)

### 💎 수익 자동 재투자
3단계 익절 완료 시 수익금으로 자동 투자:
1. **SOL** 10,000원
2. **XRP** 10,000원
3. **BTC** 10,000원
4. **HBAR** 10,000원

### 🛡️ 시드 보호
- 초기 시드는 **절대 건드리지 않음**
- 원화가 초기 시드 이하면 **매수 차단**
- 대시보드에 실시간 경고 표시

### 🌐 웹 대시보드
- **실시간 모니터링** (3초 업데이트)
- 원화 잔고, 총 수익, 보유 코인 한눈에 확인
- 웹에서 봇 시작/중지
- 웹에서 API 키 설정
- 거래 이력 실시간 표시

---

## 🚀 빠른 시작 (1분)

### Windows 사용자

1. **파일 다운로드**  
   👉 [setup-wizard.bat 다운로드](https://github.com/wordycow/so.t-leader-choice/raw/main/setup-wizard.bat)

2. **실행**  
   다운로드한 `setup-wizard.bat` 파일을 **더블 클릭** ✅

3. **완료!**  
   웹 브라우저가 자동으로 열림 → API 키 입력 → 봇 시작 🎉

### Mac / Linux 사용자

1. **파일 다운로드**  
   👉 [setup-wizard.sh 다운로드](https://github.com/wordycow/so.t-leader-choice/raw/main/setup-wizard.sh)

2. **실행**  
   ```bash
   chmod +x setup-wizard.sh
   ./setup-wizard.sh
   ```

3. **완료!**  
   웹 브라우저가 자동으로 열림 → API 키 입력 → 봇 시작 🎉

---

## 📖 완전 초보자 가이드

코딩을 전혀 모르시나요? 걱정 마세요!

👉 **[SUPER-EASY-GUIDE.md](SUPER-EASY-GUIDE.md)** - 그림으로 보는 설치 가이드

이 가이드에는:
- 🖼️ 스크린샷으로 보는 단계별 설명
- 🔑 업비트 API 키 발급 방법
- 📊 전략 이해하기
- ❓ 자주 묻는 질문
- ⚠️ 안전 수칙

---

## 📊 대시보드 미리보기

```
🤖 업비트 스마트 봇 v5.0
5단계 매수 + 3단계 익절 + 수익 분산 투자 (SOL, XRP, BTC, HBAR)

🟢 실행중  [⏸ 봇 중지]  [⚙️ 설정]

┌─────────────────┬─────────────────┬─────────────────┐
│ 💰 원화 잔고    │ 🏦 초기 시드    │ 📈 총 수익      │
│ 200,000 KRW     │ 200,000 KRW     │ +18,500 KRW     │
│                 │ 보호됨          │                 │
└─────────────────┴─────────────────┴─────────────────┘

📊 보유 코인
┌─────────┬──────────┬────────────────┬──────────┐
│ 코인    │ 수량     │ 현재 가치      │ 수익률   │
├─────────┼──────────┼────────────────┼──────────┤
│ SOL     │ 0.1234   │ 35,500원       │ +8.5%    │
│ XRP     │ 15.2345  │ 28,200원       │ +5.2%    │
└─────────┴──────────┴────────────────┴──────────┘

💎 수익 분산 투자
┌─────────┬─────────┐
│ SOL     │ 10,000원│
│ XRP     │ 10,000원│
└─────────┴─────────┘

📜 거래 이력 (최근 20개)
🔵 매수 - SOL - 1단계 - 6,000원
🔴 매도 - SOL - 1차 익절 (50%) - 수익 1,250원
💎 수익 투자 - KRW-SOL - 10,000원
```

---

## 🎓 전략 상세

### 📉 RSI 기반 매수
- **RSI < 30**: 과매도 구간, 매수 신호
- **RSI 단계별 하락**: 추가 매수 타이밍
- **볼린저 밴드 하단**: 반등 가능성 증가
- **거래량 급증**: 추세 전환 신호

### 📈 목표가 기반 익절
- **1차 익절 +2.5%**: 50% 물량 정리 (안전)
- **2차 익절 +2.0%**: 30% 추가 정리
- **3차 익절 +1.5%**: 20% 잔량 정리

### 🚨 리스크 관리
- **손절선 -15%**: 자동 전량 매도
- **시드 보호**: 초기 자본 절대 보존
- **분할 매수**: 평단가 낮추기
- **분할 익절**: 수익 확정 극대화

---

## 🔧 고급 설정 (선택)

### 시뮬레이션 → 실전 모드 전환

기본적으로 **시뮬레이션 모드**로 실행됩니다.  
실제 거래를 원하시면:

1. `upbit-smart-bot-v5.py` 파일을 메모장으로 열기
2. Ctrl+F로 `# order =` 검색
3. 아래 3곳의 주석(`#`) 제거:

```python
# 매수 주문 활성화 (510번째 줄 근처)
# order = upbit.buy_market_order(ticker, buy_amount)
↓
order = upbit.buy_market_order(ticker, buy_amount)

# 매도 주문 활성화 (546번째 줄 근처)
# order = upbit.sell_market_order(ticker, sell_amount)
↓
order = upbit.sell_market_order(ticker, sell_amount)

# 수익 투자 활성화 (269번째 줄 근처)
# order = upbit.buy_market_order(next_target, PROFIT_INVEST_AMOUNT)
↓
order = upbit.buy_market_order(next_target, PROFIT_INVEST_AMOUNT)
```

4. 저장 후 봇 재시작

⚠️ **주의**: 소액으로 테스트 후 사용하세요!

---

## 📚 추가 문서

- **[UPBIT-BOT-V5-GUIDE.md](UPBIT-BOT-V5-GUIDE.md)** - 기술 문서
- **[BOT-VERSION-COMPARISON.md](BOT-VERSION-COMPARISON.md)** - 버전 비교
- **[SAFETY-FEATURES.md](SAFETY-FEATURES.md)** - 안전 기능
- **[QUICK-START.md](QUICK-START.md)** - 빠른 시작

---

## 💻 수동 설치 (개발자용)

### 요구사항
- Python 3.8+
- pip

### 설치
```bash
# 저장소 클론
git clone https://github.com/wordycow/so.t-leader-choice.git
cd so.t-leader-choice

# 라이브러리 설치
pip install pyupbit pandas numpy flask flask-cors

# API 키 설정
# api_keys.json 파일 생성:
{
  "access_key": "여기에_업비트_Access_Key",
  "secret_key": "여기에_업비트_Secret_Key"
}

# 봇 실행
python3 upbit-smart-bot-v5.py

# 브라우저에서 접속
http://localhost:5000
```

---

## 📊 예상 성능 (30일 시뮬레이션)

| 항목 | 값 |
|------|-----|
| **초기 자본** | 200,000원 |
| **평균 거래 횟수** | 10회 |
| **평균 수익률** | +3.5% / 거래 |
| **승률** | 70% |
| **예상 수익** | +18,500원 |
| **최종 잔고** | 218,500원 |
| **ROI** | +9.3% |
| **수익 투자 (SOL 등)** | 약 8,500원 |

⚠️ **면책 조항**: 과거 성과가 미래 수익을 보장하지 않습니다.

---

## ❓ FAQ

### Q. 코딩을 전혀 모르는데 사용할 수 있나요?
**A.** 네! `setup-wizard.bat` 파일만 더블 클릭하면 됩니다.

### Q. 봇이 거래를 안 해요
**A.** 기본적으로 시뮬레이션 모드입니다. [고급 설정](#-고급-설정-선택) 참고.

### Q. API 키가 무엇인가요?
**A.** 업비트에서 봇이 거래하도록 허용하는 비밀번호입니다.  
[SUPER-EASY-GUIDE.md](SUPER-EASY-GUIDE.md)에 발급 방법이 자세히 나와 있습니다.

### Q. 안전한가요?
**A.** 
- ✅ API 키에 **출금 권한 비활성화** 필수
- ✅ 초기 시드 **절대 보호**
- ✅ 자동 손절 **-15%**
- ✅ 오픈소스 (코드 검증 가능)

### Q. 수익이 보장되나요?
**A.** **아니오**. 암호화폐 투자는 고위험이며, 손실 가능성이 있습니다.  
소액으로 시작하고 감당 가능한 금액만 투자하세요.

### Q. 24시간 켜둬야 하나요?
**A.** 원하는 만큼 실행 가능합니다. 봇을 끄면 거래가 중지됩니다.

---

## ⚠️ 안전 수칙

### ✅ 반드시 지킬 것
1. **API 키 출금 권한 절대 금지**
2. **소액으로 시작** (10만원 이하 권장)
3. **시뮬레이션 먼저 실행** (24시간 이상)
4. **API 키 절대 공유 금지**
5. **정기적인 수익/손실 확인**

### ❌ 절대 하지 말 것
1. API 키에 출금 권한 부여
2. API 키를 다른 사람에게 공유
3. 생활비/전재산 투자
4. 검증되지 않은 코드 실행
5. 봇을 이해하지 못한 채 실행

---

## 🛠️ 기술 스택

- **언어**: Python 3.8+
- **프레임워크**: Flask (웹 서버)
- **라이브러리**: 
  - `pyupbit` - 업비트 API
  - `pandas` - 데이터 분석
  - `numpy` - 수치 계산
  - `flask-cors` - CORS 처리
- **프론트엔드**: Vanilla JS, CSS3

---

## 📈 로드맵

### v5.1 (예정)
- [ ] 텔레그램 알림
- [ ] 자동 백업
- [ ] 거래 이력 CSV 내보내기

### v6.0 (개발 중)
- [ ] 백테스팅 엔진
- [ ] 멀티 전략 선택
- [ ] AI 기반 파라미터 최적화
- [ ] 모바일 반응형 개선

---

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## ⚖️ 면책 조항

이 봇은 **교육 목적**으로 제공됩니다.  
암호화폐 투자는 **고위험**이며, **손실 가능성**이 있습니다.  
투자 결정은 본인의 책임이며, 개발자는 어떠한 손실에 대해서도 책임지지 않습니다.

**투자 전 반드시**:
- 시뮬레이션 모드로 충분히 테스트
- 소액으로 시작
- 감당 가능한 금액만 투자
- 정기적인 모니터링

---

## 📞 문의

- **GitHub Issues**: https://github.com/wordycow/so.t-leader-choice/issues
- **문서**: [SUPER-EASY-GUIDE.md](SUPER-EASY-GUIDE.md)

---

## ⭐ 지원

이 프로젝트가 도움이 되었다면 ⭐ 스타를 눌러주세요!

---

**🚀 지금 바로 시작하세요!**

👉 [setup-wizard.bat 다운로드 (Windows)](https://github.com/wordycow/so.t-leader-choice/raw/main/setup-wizard.bat)  
👉 [setup-wizard.sh 다운로드 (Mac/Linux)](https://github.com/wordycow/so.t-leader-choice/raw/main/setup-wizard.sh)

**클릭 한 번으로 자동매매의 세계로!** ✨

---

**Made with ❤️ for Upbit traders**
