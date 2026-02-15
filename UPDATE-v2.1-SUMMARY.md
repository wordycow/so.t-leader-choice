# ✅ 업비트 스마트 봇 v2.1 - 안전 기능 업데이트 완료

## 🎯 요청사항 완료 체크리스트

### ✅ 완료된 항목

1. **✅ 상장폐지 코인 모니터링 제거**
   - KRW-AXS, KRW-WAXP, KRW-STEEM, KRW-SBD, KRW-SC, KRW-POWR, KRW-STORJ, KRW-RFR
   - 자동으로 확인 리스트에서 제외
   - 거래 시도 시 에러 메시지 표시

2. **✅ USDT 마켓 제외**
   - USDT-BTC, USDT-ETH 등 모든 USDT 마켓 차단
   - 이유: 변동성 패턴이 KRW 마켓과 다름

3. **✅ BTC 마켓 제외**
   - BTC-ETH, BTC-XRP 등 모든 BTC 마켓 차단
   - 이유: 이중 리스크 (BTC 가격 + 해당 코인 가격)

4. **✅ 설정 파일 시스템**
   - `delisted_coins.json` 파일로 쉽게 관리
   - 코드 수정 없이 코인 추가/제거 가능

5. **✅ 자동 감지 기능**
   - 거래 중단 코인 자동 감지
   - 자동으로 제외 목록에 추가

6. **✅ 주석 유지**
   - 실전 모드는 주석으로 남겨둠
   - 나중에 활성화 가능

---

## 📦 새로 생성된 파일

### 1. `upbit-smart-bot.py` (업데이트)
```python
# 주요 변경사항:
- load_delisted_coins_config() 함수 추가
- is_valid_market() 함수 개선
- DELISTED_COINS, EXCLUDED_MARKETS 전역 변수
- 포트폴리오 분석 시 자동 필터링
- 전략 수립 시 유효성 재검증
```

### 2. `delisted_coins.json` (신규)
```json
{
  "delisted_coins": [
    "KRW-AXS", "KRW-WAXP", "KRW-STEEM", "KRW-SBD",
    "KRW-SC", "KRW-POWR", "KRW-STORJ", "KRW-RFR"
  ],
  "excluded_markets": ["USDT", "BTC"],
  "last_updated": "2026-02-16",
  "notes": "이 파일을 수정하여 상장폐지 예정 코인을 추가/제거할 수 있습니다"
}
```

### 3. `SAFETY-FEATURES.md` (신규)
- 안전 기능 상세 가이드 (4KB)
- 제외 대상 설명
- 설정 방법
- 작동 방식
- 고급 사용법
- 문제 해결

### 4. `download-bot.html` (업데이트)
- v2.1 버전 표시
- 새 기능 설명 추가
- 다운로드 링크 업데이트

### 5. `upbit-smart-bot-v2.1-safe.tar.gz` (신규)
- 14KB 압축 파일
- 모든 필수 파일 포함
- 다운로드 준비 완료

---

## 🔍 작동 방식

### 봇 시작 시
```
═════════════════════════════════════════════════════════════════════════════════

  🤖 업비트 스마트 스캘핑 봇 v2.1
  🛡️  안전 모드: 상장폐지 코인 자동 차단
  🚫 제외 마켓: USDT, BTC

═════════════════════════════════════════════════════════════════════════════════

2026-02-16 02:30:00 [SUCCESS] 📋 상장폐지 코인 설정 로드 완료
2026-02-16 02:30:00 [INFO]    제외 코인: 8개
2026-02-16 02:30:00 [INFO]    제외 마켓: USDT, BTC

═════════════════════════════════════════════════════════════════════════════════

2026-02-16 02:30:00 [INFO] 🚫 제외 대상 필터링 설정:

2026-02-16 02:30:00 [WARNING] 📋 상장폐지 코인 (8개):
2026-02-16 02:30:00 [WARNING]    ❌ KRW-AXS
2026-02-16 02:30:00 [WARNING]    ❌ KRW-POWR
2026-02-16 02:30:00 [WARNING]    ❌ KRW-RFR
2026-02-16 02:30:00 [WARNING]    ❌ KRW-SBD
2026-02-16 02:30:00 [WARNING]    ❌ KRW-SC
2026-02-16 02:30:00 [WARNING]    ❌ KRW-STEEM
2026-02-16 02:30:00 [WARNING]    ❌ KRW-STORJ
2026-02-16 02:30:00 [WARNING]    ❌ KRW-WAXP

2026-02-16 02:30:00 [WARNING] 🚫 제외 마켓:
2026-02-16 02:30:00 [WARNING]    ❌ BTC-* (예: BTC-BTC, BTC-ETH 등)
2026-02-16 02:30:00 [WARNING]    ❌ USDT-* (예: USDT-BTC, USDT-ETH 등)
```

### 포트폴리오 분석 시
```
2026-02-16 02:30:01 [INFO] 💼 포트폴리오 분석 시작...
2026-02-16 02:30:01 [INFO] 💰 보유 원화: 500,000 KRW

2026-02-16 02:30:01 [INFO] 📊 보유 코인: DOGE
2026-02-16 02:30:01 [INFO]    • 티커: KRW-DOGE
2026-02-16 02:30:01 [INFO]    • 보유 수량: 8.75400642 DOGE
2026-02-16 02:30:01 [INFO]    • 평균 매수가: 132 KRW
2026-02-16 02:30:01 [INFO]    • 현재 가격: 158 KRW
2026-02-16 02:30:01 [SUCCESS]    • 수익: +225 KRW (+19.40%)

2026-02-16 02:30:01 [WARNING] ⏩️  [KRW-AXS] 모니터링 제외 - 건너뜀
```

### 거래 중단 코인 자동 감지
```
2026-02-16 02:30:02 [WARNING] ⚠️  [KRW-AXS] 가격 조회 실패: Code not found
2026-02-16 02:30:02 [WARNING]    코인이 상장폐지되었거나 거래 중단되었을 수 있습니다
2026-02-16 02:30:02 [INFO]    ➕ [KRW-AXS]를 상장폐지 목록에 추가했습니다
```

---

## 📥 다운로드 링크

### 🌐 프로덕션 (GitHub Pages)
- **다운로드 페이지**: https://wordycow.github.io/so.t-leader-choice/download-bot.html
- **직접 다운로드**: https://wordycow.github.io/so.t-leader-choice/upbit-smart-bot-v2.1-safe.tar.gz

### 📂 GitHub 저장소
- https://github.com/wordycow/so.t-leader-choice

---

## ⚙️ 설정 방법

### 1️⃣ 코인 추가하기
```bash
# delisted_coins.json 파일 열기
nano delisted_coins.json

# 또는 VSCode에서
code delisted_coins.json
```

```json
{
  "delisted_coins": [
    "KRW-AXS",
    "KRW-NEWCOIN"  ← 새로 추가
  ]
}
```

### 2️⃣ 코인 제거하기
```json
{
  "delisted_coins": [
    "KRW-AXS"  ← KRW-WAXP 제거함
  ]
}
```

### 3️⃣ 마켓 설정 변경
```json
{
  "excluded_markets": [
    "USDT",
    "BTC",
    "ETH"  ← ETH 마켓도 제외
  ]
}
```

---

## 🧪 테스트 방법

### 1. 로컬에서 테스트
```bash
# 다운로드 및 압축 해제
curl -o upbit-smart-bot-v2.1-safe.tar.gz https://wordycow.github.io/so.t-leader-choice/upbit-smart-bot-v2.1-safe.tar.gz
tar -xzf upbit-smart-bot-v2.1-safe.tar.gz
cd upbit-smart-bot-v2.1-safe/

# 의존성 설치
pip install pyupbit pandas numpy

# API 키 설정
cp api_keys.json.example api_keys.json
nano api_keys.json  # 실제 키 입력

# 실행
python3 upbit-smart-bot.py
```

### 2. 제외 기능 확인
- 봇 시작 시 로그에서 제외 목록 확인
- 상장폐지 코인 보유 시 "모니터링 제외" 메시지 확인
- USDT/BTC 마켓 코인 확인 시 경고 메시지

### 3. 설정 파일 수정 테스트
```bash
# delisted_coins.json 수정
echo '{
  "delisted_coins": ["KRW-TEST"],
  "excluded_markets": ["USDT"]
}' > delisted_coins.json

# 봇 재시작
python3 upbit-smart-bot.py
```

---

## 🔐 보안 사항

### ✅ 안전한 점
- API 키는 로컬 파일에만 저장
- `.gitignore`에 `api_keys.json` 포함
- 출금 권한 불필요 (거래만)
- 시뮬레이션 모드 기본 활성화

### ⚠️ 주의사항
- `delisted_coins.json`은 Git에 커밋됨 (민감 정보 없음)
- API 키는 절대 Git에 올리지 말 것
- 실전 모드는 충분한 테스트 후 사용
- 소액으로 먼저 테스트

---

## 📊 Git 커밋 정보

### Commit Hash
`7799840`

### 커밋 메시지
```
feat(bot): v2.1 안전 기능 추가 - 상장폐지 코인 자동 차단

🛡️ 주요 개선사항:
- 상장폐지 예정 코인 8개 자동 제외
- USDT 마켓 자동 차단
- BTC 마켓 자동 차단
- delisted_coins.json 설정 파일 추가
- 거래 중단 코인 자동 감지
- SAFETY-FEATURES.md 가이드 추가
```

### 변경된 파일
- `upbit-smart-bot.py` (+152 lines)
- `delisted_coins.json` (신규)
- `SAFETY-FEATURES.md` (신규, 284 lines)
- `download-bot.html` (업데이트)
- `upbit-smart-bot-v2.1-safe.tar.gz` (신규, 14KB)

### 브랜치
- ✅ `main` - 푸시 완료
- ✅ `genspark_ai_developer` - 동기화 및 푸시 완료

---

## 🎯 다음 단계 (선택사항)

### 즉시 가능
1. ✅ 로컬에서 봇 실행 및 테스트
2. ✅ `delisted_coins.json` 파일 수정하여 코인 추가/제거
3. ✅ 실시간 로그 모니터링

### 추후 개선
- [ ] 업비트 공지사항 API 크롤링 (자동 업데이트)
- [ ] 화이트리스트 기능 (특정 코인만 거래)
- [ ] 웹 대시보드 (실시간 모니터링)
- [ ] 텔레그램 알림 연동

---

## 💡 사용 팁

### 상장폐지 공지 확인
- 업비트 공지사항: https://upbit.com/service_center/notice
- 정기적으로 확인하여 `delisted_coins.json` 업데이트

### 거래량 감소 코인
- 거래량이 급감하는 코인도 수동으로 제외 고려
- 봇 로그에서 가격 조회 실패가 자주 나타나면 제외

### 백업
```bash
# 설정 파일 백업
cp delisted_coins.json delisted_coins.json.backup

# 전체 백업
tar -czf my-bot-backup.tar.gz *.py *.json *.md *.sh
```

---

## 📞 문제 해결

### Q1: "Code not found" 에러가 계속 나와요
**A**: 해당 코인이 상장폐지되었습니다. 자동으로 제외 목록에 추가됩니다.

### Q2: 제외 코인이 여전히 나타나요
**A**: 봇을 재시작하세요 (`Ctrl+C` → 재실행)

### Q3: 파일 수정이 반영 안 돼요
**A**: JSON 문법 오류 확인 (https://jsonlint.com/)

### Q4: 모든 코인이 제외됐어요
**A**: `delisted_coins.json` 확인 - 와일드카드 패턴 사용 금지

---

## ✅ 완료 요약

| 항목 | 상태 | 설명 |
|------|------|------|
| 상장폐지 코인 제외 | ✅ | 8개 코인 자동 차단 |
| USDT 마켓 제외 | ✅ | 모든 USDT-* 차단 |
| BTC 마켓 제외 | ✅ | 모든 BTC-* 차단 |
| 설정 파일 시스템 | ✅ | delisted_coins.json |
| 자동 감지 | ✅ | 거래 중단 자동 추가 |
| 가이드 문서 | ✅ | SAFETY-FEATURES.md |
| 다운로드 페이지 | ✅ | v2.1 업데이트 |
| Git 커밋 | ✅ | 7799840 |
| GitHub 푸시 | ✅ | main + genspark_ai_developer |
| 주석 유지 | ✅ | 실전 모드 주석 |

---

**모든 요청사항이 완료되었습니다! 🎉**

**다운로드 페이지**: https://wordycow.github.io/so.t-leader-choice/download-bot.html
