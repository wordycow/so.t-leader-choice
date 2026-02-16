"""
🚀 업비트 AI 트레이딩 봇 v8.0 ULTIMATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 완전체: 급등/급락 + AI학습 + 손실복구 통합

📦 설치 및 실행 가이드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 1. 필수 요구사항

### Python 버전
- Python 3.8 이상 (권장: 3.10+)

### 운영체제
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 20.04+)

## 2. 설치 방법

### Windows

1. Python 설치 확인:
   ```
   python --version
   ```
   없으면 https://www.python.org/downloads/ 에서 설치

2. 패키지 설치:
   ```
   python -m pip install -r requirements.txt
   ```

3. 봇 실행:
   ```
   python upbit-smart-bot-v8.0-ULTIMATE.py
   ```

4. 웹 브라우저에서 접속:
   ```
   http://localhost:5000
   ```

### macOS / Linux

1. Python 설치 확인:
   ```bash
   python3 --version
   ```

2. 패키지 설치:
   ```bash
   pip3 install -r requirements.txt
   ```

3. 봇 실행:
   ```bash
   python3 upbit-smart-bot-v8.0-ULTIMATE.py
   ```

4. 웹 브라우저에서 접속:
   ```
   http://localhost:5000
   ```

## 3. 빠른 시작

### 연습 모드 (추천)

1. 봇 실행
2. 웹 브라우저 열기 (http://localhost:5000)
3. "연습 모드" 선택
4. 시뮬레이션 시드 입력 (기본: 1,000,000원)
5. "🚀 봇 시작" 클릭
6. 자동 매매 시작!

### 실전 모드

⚠️ 주의: 실전 모드는 실제 자금이 사용됩니다!

1. Upbit API 키 발급:
   - Upbit 로그인
   - 고객센터 > Open API 관리
   - API 키 생성 (자산조회, 주문하기 권한 필요)

2. API 키 설정:
   - 웹 대시보드에서 "API 설정" 클릭
   - Access Key, Secret Key 입력
   - 저장

3. "실전 모드" 선택 후 시작

## 4. 주요 기능

### 🚀 급등/급락 동시 포착
- 급등: +1.5% 이상 → 즉시 진입
- 급락: -1.5% 이하 → 저점 매수 → 원가 복귀

### 📊 5가지 패턴 자동 인식
- 박스권, 추세, 수급, 급등후, 과매도

### 🏆 멀티 전략 경쟁
- 5개 전략 동시 실행
- AI가 최적 전략 자동 선택

### 🧠 자동 학습
- 매 거래마다 성과 기록
- 50개 거래마다 재학습
- 가중치 자동 조정

### 🛡️ 손실 복구 모드
- -15% 손실 시 자동 활성화
- 10% 시드로 초단타
- 손실의 50% 자동 복구

## 5. 설정 변경 (고급)

### 파일 열기
```python
upbit-smart-bot-v8.0-ULTIMATE.py
```

### 주요 설정 위치 (라인 45~100)

```python
# 급등/급락 감지
SURGE_CONFIG = {
    'surge_threshold_1m': 1.5,      # 급등 임계값 (%)
    'dip_threshold_1m': -1.5,       # 급락 임계값 (%)
    'stop_loss': -2.0,              # 손절 (%)
}

# 손실 복구
RECOVERY_CONFIG = {
    'activate_loss_threshold': -15.0,  # 복구 모드 활성화 (%)
    'recovery_cash_ratio': 0.10,       # 복구 시드 비율 (10%)
}
```

## 6. 문제 해결

### 포트 충돌 오류
```
Address already in use
```
→ 해결: 다른 프로그램이 5000번 포트 사용 중
→ 봇 파일에서 포트 변경:
  app.run(host='0.0.0.0', port=5001)  # 5000 → 5001

### 패키지 설치 오류
```
ERROR: Could not find a version that satisfies...
```
→ 해결: pip 업그레이드
```bash
python -m pip install --upgrade pip
```

### API 연결 오류
```
Upbit API Error
```
→ 확인사항:
  1. 인터넷 연결 확인
  2. API 키 권한 확인 (자산조회, 주문하기)
  3. IP 주소 제한 확인 (모든 IP 허용 권장)

## 7. 성능 최적화

### 메모리 사용량 줄이기
```python
# 라인 90 수정
LEARNING_CONFIG = {
    'pattern_history_size': 200,  # 500 → 200
}
```

### 스캔 속도 조정
```python
# 라인 940 수정
time.sleep(30)  # 20 → 30 (느리게)
```

## 8. 안전 수칙

✅ 연습 모드로 먼저 테스트
✅ 소액으로 시작 (10만원~50만원)
✅ 손실 한도 설정
✅ 24시간 방치 금지 (초기)
✅ 정기적 수익 확인

❌ 전 재산 투자 금지
❌ 빚내서 투자 금지
❌ 맹신 금지

## 9. 지원

### GitHub
https://github.com/wordycow/so.t-leader-choice

### 이슈 등록
버그 발견 시 GitHub Issues에 등록

### 업데이트 확인
```bash
git pull origin main
```

## 10. 라이선스

MIT License - 자유롭게 사용 및 수정 가능

⚠️ 면책 조항:
본 소프트웨어는 교육 목적으로 제공됩니다.
투자 손실에 대한 책임은 사용자에게 있습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
