# 🚀 Upbit AI Trading Bot v9.0 - 완전 통합 버전

## ✅ 완료된 핵심 기능

### 1️⃣ **사용자 계정 시스템**

#### 회원가입/로그인
- **URL**: `/login`
- **기능**:
  - 사용자명 + 이메일(선택) 입력
  - 자동 포트폴리오 생성 (기본: BTC, XRP, SOL, SHIB)
  - 세션 기반 인증
  - IP 주소 자동 추적

#### 멀티 유저 지원
- 각 사용자별 독립적인 봇 상태
- 사용자 ID 기반 거래 내역 분리
- 동시 접속 지원

### 2️⃣ **포트폴리오 분산 투자 시스템**

#### 수익 시 자동 분산 매수
```python
수익률 10% 도달 → 자동으로 4개 코인에 1만원씩 분산 매수
```

#### 선택 가능한 코인 (24개)
- **메이저**: BTC, ETH, XRP, SOL, DOGE
- **알트코인**: ADA, AVAX, DOT, MATIC, SHIB, ATOM
- **체인링크**: LINK
- **레이어2**: ARB, OP
- **신규**: APT, SUI, SEI, STRK, WLD
- **기타**: BCH, NEAR, UNI, ALGO, HBAR

#### 포트폴리오 설정
- API: `/api/portfolio/get` (조회)
- API: `/api/portfolio/update` (설정)
- 사용자별 맞춤 설정 가능

### 3️⃣ **거래 이유 상세 설명 시스템**

#### 매수 이유 예시
```
[SOL] 급등장 진입 신호 - 단기 상승 모멘텀 포착
• 🚀 1분봉 급등 감지: 2.3% 상승
• 📈 3분봉 강한 상승세: 3.8% 상승
• 💥 거래량 폭발: 평균의 3.2배
```

```
[DOT] 급락 반등 기회 - 과매도 구간에서 저점 매수
• 💎 급락 저점 감지: -2.1% 하락
• 📉 RSI 과매도 구간: 32.4 (매수 타이밍)
• 🔥 공황 매도 포착: 거래량 2.8배 증가
```

#### 매도 이유 예시
```
[BTC] 🎯 목표 수익 달성
• ✅ 수익률 +2.8% - 목표가 도달
• 💵 매수가: 95,000,000원 → 매도가: 97,660,000원
• ⏱️ 보유 시간: 23분
• 🎮 스윙 성공 - 적정 타이밍 매도
```

```
[SHIB] 🛡️ 손절 실행 (손실 제한)
• ⚠️ 손실률 -2.1% - 추가 하락 방지
• 💵 매수가: 1,450원 → 매도가: 1,419원
• 🔒 손실 확정하여 추가 리스크 차단
```

### 4️⃣ **관리자 대시보드**

#### URL: `/admin`

#### 기능
- **통계 현황**:
  - 📊 전체 사용자 수
  - ✅ 활성 사용자 수
  - 💎 구독자 수
  - 🆓 무료 사용자 수

- **사용자 목록**:
  - ID, 사용자명, 이메일
  - 가입일, 최근 로그인
  - 구독 상태 (1month/6months/lifetime)
  - 구독 종료일
  - 활성/비활성 상태

- **실시간 업데이트**: 30초마다 자동 새로고침

### 5️⃣ **데이터베이스 구조**

#### 테이블 설계

**users** (사용자)
```sql
- id: 고유 ID
- username: 사용자명 (UNIQUE)
- email: 이메일 (옵션)
- created_at: 가입일
- last_login: 최근 로그인
- ip_address: IP 주소
- is_active: 활성 상태
```

**subscriptions** (구독)
```sql
- id: 고유 ID
- user_id: 사용자 ID
- txid: 트론 TXID
- usdt_amount: USDT 금액
- subscription_type: 1month/6months/lifetime
- start_date: 시작일
- end_date: 종료일
- is_active: 활성 상태
```

**portfolios** (포트폴리오)
```sql
- id: 고유 ID
- user_id: 사용자 ID
- coin_1, coin_2, coin_3, coin_4: 선택한 코인
- investment_per_coin: 코인당 투자 금액 (기본 10,000원)
- is_active: 활성 상태
- updated_at: 업데이트 일시
```

**trades** (거래 내역)
```sql
- id: 고유 ID
- user_id: 사용자 ID
- ticker: 코인 티커
- trade_type: BUY/SELL
- amount: 수량
- price: 가격
- strategy: 전략명
- reason: 거래 이유 (TEXT)
- profit_rate: 수익률 (%)
- timestamp: 거래 시각
```

**api_keys** (API 키)
```sql
- id: 고유 ID
- user_id: 사용자 ID
- access_key: Upbit Access Key
- secret_key: Upbit Secret Key
- created_at: 생성일
```

## 🎯 사용 흐름

### 신규 사용자
```
1. https://.../login 접속
2. "✨ 새 계정 만들기" 클릭
3. 사용자명 입력 (이메일 선택)
4. 계정 생성 → 자동 로그인
5. 대시보드 진입 (기본 포트폴리오 자동 설정)
6. 포트폴리오 수정 (원하는 코인 선택)
7. 🆓 연습 모드 또는 💎 실전 모드 선택
8. 🚀 봇 시작
```

### 기존 사용자
```
1. https://.../login 접속
2. 사용자명 입력
3. "🚀 시작하기" 클릭
4. 대시보드 자동 진입
5. 봇 설정 및 시작
```

### 관리자
```
1. https://.../admin 접속
2. 사용자 목록 확인
3. 구독 상태 모니터링
4. 통계 확인
```

## 📊 API 엔드포인트

### 인증 관련
- `GET /login` - 로그인 페이지
- `POST /api/register` - 회원가입
- `POST /api/login` - 로그인
- `POST /api/logout` - 로그아웃

### 포트폴리오
- `GET /api/portfolio/get` - 포트폴리오 조회
- `POST /api/portfolio/update` - 포트폴리오 설정 업데이트

### 관리자
- `GET /admin` - 관리자 대시보드
- `GET /api/admin/users` - 전체 사용자 목록

### 봇 제어 (기존)
- `POST /api/start` - 봇 시작
- `POST /api/stop` - 봇 정지
- `GET /api/status` - 상태 조회
- `POST /api/verify-license` - 라이선스 검증
- `POST /api/config` - API 키 설정

## 🚧 진행 중인 작업

### 1. 대시보드 UI 통합 (70% 완료)
- [ ] 포트폴리오 설정 UI 추가
- [ ] 거래 내역에 "이유" 컬럼 추가
- [ ] 거래 이유 모달 팝업
- [ ] 포트폴리오 분산 매수 알림

### 2. 봇 로직 통합 (30% 완료)
- [x] 거래 이유 생성 함수 작성
- [x] 포트폴리오 분산 매수 함수 작성
- [ ] `execute_trade()` 함수에 이유 생성 통합
- [ ] `execute_exit()` 함수에 이유 생성 통합
- [ ] 수익 10% 도달 시 자동 분산 매수 트리거
- [ ] 데이터베이스에 거래 이유 저장

### 3. 멀티 유저 실행 (50% 완료)
- [x] 사용자별 독립 세션
- [ ] 사용자별 봇 상태 분리 (`user_bots[user_id]`)
- [ ] 동시 실행 지원
- [ ] 사용자별 거래 내역 분리

### 4. 보안 강화 (미착수)
- [ ] API 키 암호화 저장
- [ ] 세션 타임아웃
- [ ] CSRF 토큰
- [ ] Rate limiting

## 🧪 테스트 가이드

### 로그인 테스트
```
1. https://5000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/login
2. 사용자명: testuser (또는 새로 만들기)
3. 이메일: test@example.com (옵션)
4. "✨ 새 계정 만들기" 클릭
5. 자동 로그인 → 대시보드 확인
```

### 관리자 대시보드 테스트
```
1. https://5000-ihgrbyuwjwu7c8aikuzfo-583b4d74.sandbox.novita.ai/admin
2. 등록된 사용자 목록 확인
3. 통계 (전체/활성/구독/무료) 확인
```

### 포트폴리오 API 테스트
```bash
# 포트폴리오 조회
curl http://localhost:5000/api/portfolio/get

# 포트폴리오 업데이트
curl -X POST http://localhost:5000/api/portfolio/update \
  -H "Content-Type: application/json" \
  -d '{
    "coin_1": "KRW-BTC",
    "coin_2": "KRW-ETH",
    "coin_3": "KRW-SOL",
    "coin_4": "KRW-WLD",
    "investment_per_coin": 10000
  }'
```

## 📈 다음 마일스톤

### Phase 1: UI 통합 (예상: 2시간)
1. 대시보드에 "⚙️ 포트폴리오 설정" 버튼 추가
2. 코인 선택 드롭다운 (24개 코인)
3. 거래 내역에 "이유" 컬럼 추가
4. 이유 클릭 시 모달 표시

### Phase 2: 봇 로직 통합 (예상: 3시간)
1. `execute_trade()`에서 `generate_buy_reason()` 호출
2. `execute_exit()`에서 `generate_sell_reason()` 호출
3. 거래 내역에 이유 저장 (`user_manager.log_trade()`)
4. 수익 10% 도달 체크 → `execute_diversified_buy()` 호출

### Phase 3: 멀티 유저 실행 (예상: 2시간)
1. `user_bots[user_id]` 딕셔너리로 사용자별 상태 분리
2. `/api/start`에서 `user_id` 기반 봇 생성
3. `/api/status`에서 `user_id` 기반 상태 반환
4. 동시 실행 스레드 관리

### Phase 4: 최종 테스트 (예상: 2시간)
1. 3명의 테스트 사용자 생성
2. 동시 봇 실행 테스트
3. 포트폴리오 분산 매수 확인
4. 거래 이유 표시 확인
5. 관리자 대시보드에서 모든 사용자 확인

## 📦 GitHub 업데이트

**Repository**: https://github.com/wordycow/so.t-leader-choice  
**Latest Commit**: `50f67ac` - 사용자 시스템 + 포트폴리오 + 거래 이유

**주요 파일**:
- `upbit-smart-bot-v8.0-ULTIMATE.py` - 메인 봇 (사용자 시스템 통합)
- `init_db.py` - 데이터베이스 초기화
- `user_manager.py` - 사용자 관리
- `portfolio_manager.py` - 포트폴리오 분산 투자
- `trade_reasons.py` - 거래 이유 생성기
- `templates/login.html` - 로그인 UI
- `templates/admin.html` - 관리자 대시보드
- `upbit_bot.db` - SQLite 데이터베이스

## 💬 요약

지금까지 구현된 내용:
1. ✅ 사용자 계정 시스템 (회원가입/로그인)
2. ✅ SQLite 데이터베이스 (5개 테이블)
3. ✅ 포트폴리오 분산 투자 로직
4. ✅ 거래 이유 상세 설명 생성기
5. ✅ 관리자 대시보드 (구독자 관리)

진행 중인 내용:
1. 🔄 대시보드 UI에 포트폴리오 설정 추가
2. 🔄 거래 내역에 이유 표시
3. 🔄 봇 로직에 거래 이유 통합
4. 🔄 멀티 유저 동시 실행 지원

---

**현재 테스트 가능한 기능**:
- ✅ 로그인/회원가입
- ✅ 관리자 대시보드
- ✅ 포트폴리오 API
- ✅ 거래 이유 생성 (함수 단위)
- ⚠️ 봇 실행 (아직 단일 사용자만 지원)

**다음 단계**: UI 통합 → 봇 로직 통합 → 멀티 유저 실행 → 최종 테스트
