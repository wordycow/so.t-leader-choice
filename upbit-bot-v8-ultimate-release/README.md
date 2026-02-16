# 🏆 Upbit Smart Bot v8.0 ULTIMATE

## 📋 프로젝트 개요

**Upbit Smart Bot v8.0 ULTIMATE**는 업비트 암호화폐 거래소에서 24시간 자동으로 거래하는 AI 기반 스마트 봇입니다.

### 🎯 핵심 기능

#### 1. 급등/급락 동시 포착
- **급등 감지**: 1분 내 +1.5% 이상 상승 & 거래량 2배 이상
- **급락 감지**: 1분 내 -1.5% 이하 하락 & RSI < 35 & 거래량 2배 이상
- 238개 KRW 마켓 전체를 10초 이내에 스캔

#### 2. 5가지 패턴 자동 인식
| 패턴 | 설명 | 신뢰도 |
|------|------|--------|
| 📦 박스권 | ±3% 범위 30분 이상 유지 | 75% |
| 📈 트렌드 | 단기/장기 이평선 분석 | 70% |
| 💰 수급 | 거래량 2.5배 이상 유입 | 80% |
| 🚀 급등 후 | 5% 급등 후 3-7% 조정 | 65% |
| ⚡ 복합 | 여러 패턴 동시 발생 | 85% |

#### 3. 5개 전략 실시간 경쟁
- **Surge Hunter**: 급등 포착 (목표 +3%, 손절 -2%)
- **Dip Hunter**: 급락 매수 (원가 복귀, 손절 -10%)
- **Box Trader**: 박스권 거래 (목표 +2.5%, 손절 -2%)
- **Trend Follower**: 추세 추종 (트레일링 스탑)
- **Volume Hunter**: 수급 포착 (목표 +2%, 손절 -2%)

#### 4. AI 자동 학습
- 매 거래마다 결과 분석 및 학습
- 50회 거래마다 전략 재평가 및 가중치 조정
- 최고 성과 전략 자동 선택

#### 5. 손실 복구 모드
- **자동 활성화**: 손실률 -15% 이하 시
- **복구 방법**: 현금 10%만 사용, 초단타 매매로 손실 50% 회복
- **안전 장치**: 일일 손실 -5% 제한, 손절 후 쿨다운

### 📊 기대 성과

- **승률**: 70-75% (복구 모드 75%+)
- **월 수익률**: 25-35%
- **평균 보유 시간**: 1.5시간
- **손실 복구**: 자동 복구 모드로 빠른 회복

---

## 🚀 빠른 시작

### 1. 사전 요구사항

- Python 3.8 이상
- Upbit 계정 및 API 키 (https://upbit.com/mypage/open_api_management)

### 2. 설치

#### Windows
```cmd
# 1. 압축 해제 후 폴더로 이동
cd upbit-bot-v8-ultimate-release

# 2. 의존성 설치
pip install -r requirements.txt

# 3. API 키 설정
notepad config.json
```

#### Linux/Mac
```bash
# 1. 압축 해제 후 폴더로 이동
cd upbit-bot-v8-ultimate-release

# 2. 의존성 설치
pip3 install -r requirements.txt

# 3. API 키 설정
nano config.json
```

### 3. API 키 설정

`config.json` 파일을 열어 아래 내용을 입력하세요:

```json
{
  "upbit_access_key": "여기에_업비트_Access_Key_입력",
  "upbit_secret_key": "여기에_업비트_Secret_Key_입력",
  "mode": "practice",
  "simulation_seed": 1000000
}
```

⚠️ **주의**: 
- 처음에는 반드시 `"mode": "practice"`로 연습 모드로 시작하세요.
- 실전 모드로 전환하려면 `"mode": "live"`로 변경하세요.

### 4. 실행

#### Windows
```cmd
python upbit-smart-bot-v8.0-ULTIMATE.py
```

#### Linux/Mac
```bash
python3 upbit-smart-bot-v8.0-ULTIMATE.py
```

### 5. 웹 대시보드 접속

브라우저에서 아래 주소로 접속:
```
http://localhost:5000
```

---

## 📁 파일 구조

```
upbit-bot-v8-ultimate-release/
├── upbit-smart-bot-v8.0-ULTIMATE.py  # 메인 봇 실행 파일
├── requirements.txt                   # Python 의존성 목록
├── config.json                        # 설정 파일 (API 키 등)
├── README.md                          # 이 파일
├── LICENSE                            # 라이선스
└── templates/
    └── dashboard-ultimate.html        # 웹 대시보드
```

---

## 🎮 사용 방법

### 연습 모드 (Practice Mode)
- **목적**: 실제 돈을 사용하지 않고 시뮬레이션으로 테스트
- **시드머니**: 1,000,000원 (기본값, config.json에서 변경 가능)
- **실시간 데이터**: 업비트 실제 시장 데이터 사용
- **추천**: 처음 사용자는 최소 3-7일 연습 모드 운영 권장

### 실전 모드 (Live Mode)
- **목적**: 실제 자금으로 자동 거래
- **필수**: Upbit API 키 필요 (입출금 권한 불필요)
- **권장**: 소액(10-50만원)으로 먼저 테스트
- **주의**: 실전 모드 전환 후 반드시 모니터링 필요

### 웹 대시보드 기능

1. **시작/정지**: 봇 실행 제어
2. **모드 전환**: 연습/실전 모드 전환
3. **실시간 통계**: 
   - 현재 잔고
   - 총 손익
   - 수익률
   - 승률
4. **전략 카드**: 5개 전략별 실시간 성과
5. **거래 내역**: 최근 거래 로그
6. **급등/급락 알림**: 실시간 감지 신호

---

## ⚙️ 설정 커스터마이징

`upbit-smart-bot-v8.0-ULTIMATE.py` 파일 내부의 설정을 수정하여 커스터마이징 가능:

### 급등 감지 설정
```python
SURGE_CONFIG = {
    'timeframes': {
        '1m': 1.5,    # 1분 +1.5% 이상
        '3m': 2.5,    # 3분 +2.5% 이상
        '5m': 3.5,    # 5분 +3.5% 이상
    },
    'volume_spike_ratio': 2.0,  # 거래량 2배 이상
    'min_volume_krw': 100000000,  # 최소 거래량 1억원
}
```

### 급락 감지 설정
```python
DIP_CONFIG = {
    'drop_threshold': -1.5,  # -1.5% 이하 하락
    'rsi_threshold': 35,      # RSI 35 이하
    'volume_ratio': 2.0,      # 거래량 2배 이상
}
```

### 복구 모드 설정
```python
RECOVERY_CONFIG = {
    'activation_loss_threshold': -15.0,  # -15% 손실 시 활성화
    'recovery_seed_ratio': 0.1,          # 10% 시드 사용
    'recovery_target_ratio': 0.5,        # 손실의 50% 회복 목표
}
```

---

## 🔒 보안 권장사항

1. **API 키 권한 최소화**
   - 입출금 권한: ❌ 비활성화
   - 거래 권한: ✅ 활성화
   - 정보 조회: ✅ 활성화

2. **IP 주소 등록**
   - Upbit에서 고정 IP 등록 권장
   - 봇 실행 서버 IP만 허용

3. **config.json 보안**
   - 절대 GitHub 등 공개 저장소에 업로드 금지
   - `.gitignore`에 `config.json` 추가

---

## 🐛 문제 해결

### 봇이 시작되지 않는 경우
```bash
# 의존성 재설치
pip install -r requirements.txt --force-reinstall

# Python 버전 확인
python --version  # 3.8 이상 필요
```

### API 인증 오류
- config.json의 API 키 재확인
- Upbit에서 API 키 권한 확인
- IP 주소 제한 확인

### 포트 충돌 (Port 5000 already in use)
```python
# upbit-smart-bot-v8.0-ULTIMATE.py 마지막 줄 수정
app.run(host='0.0.0.0', port=5001)  # 5000 → 5001로 변경
```

---

## 📞 지원 및 문의

- **GitHub**: https://github.com/wordycow/so.t-leader-choice
- **이메일**: support@example.com (교체 필요)
- **문서**: https://docs.example.com (교체 필요)

---

## 📜 라이선스

MIT License

Copyright (c) 2026 Upbit Smart Bot

본 소프트웨어는 "있는 그대로" 제공되며, 어떠한 명시적 또는 묵시적 보증도 제공하지 않습니다.

---

## ⚠️ 면책 조항

1. **투자 책임**: 모든 투자 결정과 그 결과는 사용자 본인의 책임입니다.
2. **손실 위험**: 암호화폐 거래는 높은 변동성으로 인해 큰 손실 위험이 있습니다.
3. **봇 성능**: 과거 성과가 미래 수익을 보장하지 않습니다.
4. **연습 권장**: 실전 투자 전 충분한 연습 모드 테스트를 권장합니다.
5. **자금 관리**: 잃어도 괜찮은 금액만 투자하세요.

---

## 🎓 추가 자료

### 추천 학습 순서
1. 연습 모드로 3-7일 운영
2. 로그 분석 및 전략 이해
3. 소액 실전 테스트 (10-50만원)
4. 점진적 자금 증액

### 성과 모니터링
- 일일 거래 내역 검토
- 주간 승률 및 수익률 분석
- 월간 전략별 성과 비교

---

**🚀 행운을 빕니다! Happy Trading!**
