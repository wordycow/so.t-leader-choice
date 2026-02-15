# 🚀 업비트 스마트 봇 v5.0 - 빠른 시작 가이드

## 📦 다운로드

### 전체 패키지 (권장)
```
https://github.com/wordycow/so.t-leader-choice/raw/main/upbit-smart-bot-v5.0-complete.tar.gz
```
**크기**: 17KB  
**포함 파일**: 봇 프로그램, 웹 대시보드, 자동 설치 스크립트, 가이드

---

## 💻 시스템 요구사항

### 필수
- **Python 3.8 이상** (없으면 자동 설치 안내)
- **인터넷 연결** (처음 실행 시 라이브러리 다운로드)
- **업비트 API 키** (웹 대시보드에서 설정 가능)

### 권장
- **운영체제**: Windows 10/11, macOS, Linux
- **메모리**: 최소 2GB RAM
- **저장공간**: 100MB 이상

---

## 🎯 설치 및 실행 (3단계)

### Windows 사용자 ⭐ 가장 쉬움

#### 1단계: 압축 해제
```
upbit-smart-bot-v5.0-complete.tar.gz 우클릭
→ 압축 풀기 (7-Zip, WinRAR 등)
```

#### 2단계: 폴더 열기
```
upbit-smart-bot-v5.0 폴더 열기
```

#### 3단계: 실행
```
install-and-run.bat 더블클릭!
```

**끝!** 브라우저가 자동으로 열립니다. 🎉

---

### Mac / Linux 사용자

#### 1단계: 압축 해제
```bash
tar -xzf upbit-smart-bot-v5.0-complete.tar.gz
cd upbit-smart-bot-v5.0
```

#### 2단계: 실행 권한 부여
```bash
chmod +x install-and-run.sh
```

#### 3단계: 실행
```bash
./install-and-run.sh
```

**끝!** 브라우저가 자동으로 열립니다. 🎉

---

## 🌐 웹 대시보드 사용

### 1. 브라우저 접속
```
자동으로 열립니다
또는 직접 접속: http://localhost:5000
```

### 2. API 키 설정
```
1. "⚙️ 설정" 버튼 클릭
2. 업비트에서 발급한 API 키 입력
   - Access Key
   - Secret Key
3. "저장" 클릭
```

**API 키 발급 방법**:
1. https://upbit.com 로그인
2. 프로필 → Open API 관리
3. API 키 발급
4. 권한: ✅ 자산조회, ✅ 주문조회, ✅ 주문하기
5. 권한: ❌ 출금하기 (절대 체크 금지!)

### 3. 봇 시작
```
"▶ 봇 시작" 버튼 클릭
```

### 4. 모니터링
```
실시간으로 표시되는 정보:
• 💰 원화 잔고
• 🏦 초기 시드 (보호됨)
• 📈 총 수익
• 📊 보유 코인 (수량, 가격, 수익률)
• 💎 수익 투자 (SOL, XRP, BTC, HBAR)
• 📜 거래 이력
```

---

## 📖 주요 기능

### 1. 자동 매수/매도
```
5단계 매수: 6천원 → 1만원(x3) → 10만원
3단계 익절: 50% → 30% → 20%
```

### 2. 수익 분산 투자
```
3단계 익절 완료 시 자동으로:
1순위: SOL (솔라나)   - 10,000원
2순위: XRP (리플)     - 10,000원
3순위: BTC (비트코인) - 10,000원
4순위: HBAR (헤데라)  - 10,000원
```

### 3. 시드 보호
```
초기 시드는 절대 건드리지 않음
현재 원화 < 초기 시드 → 매수 금지
```

### 4. 웹 제어
```
• 봇 켜기/끄기: 버튼 클릭
• API 설정: 웹에서 입력
• 실시간 통계: 3초마다 자동 업데이트
```

---

## ⚠️ 중요 안내

### 시뮬레이션 모드
```
기본적으로 시뮬레이션 모드로 실행됩니다
→ 실제 주문은 하지 않음
→ 로그로 전략만 확인 가능
```

### 실전 모드 전환
```
웹 대시보드에서:
1. "⚙️ 설정" → "실전 모드" 체크
2. 확인 후 저장
```

또는 코드에서:
```python
upbit-smart-bot-v5.py 파일 열기
→ 주석 해제 (# 제거):
   - 442번째 줄: 매수 주문
   - 476번째 줄: 매도 주문
   - 252번째 줄: 수익 투자
```

### 보안
```
✅ API 키는 로컬 파일(api_keys.json)에만 저장
✅ 출금 권한은 절대 활성화 금지
✅ API 키 파일은 Git에 올리지 않음 (.gitignore 포함)
```

---

## 🐛 문제 해결

### Python이 없다고 나옵니다
```
해결:
1. https://www.python.org/downloads/ 접속
2. Python 최신 버전 다운로드
3. 설치 시 "Add Python to PATH" 체크 필수!
4. 설치 후 컴퓨터 재시작
5. 다시 install-and-run 실행
```

### 라이브러리 설치 실패
```
해결:
수동 설치:
pip install pyupbit pandas numpy flask flask-cors

또는:
python -m pip install pyupbit pandas numpy flask flask-cors
```

### 포트 충돌 (Address already in use)
```
해결:
다른 프로그램이 5000 포트 사용 중

Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

### 대시보드 접속 안 됨
```
해결:
1. 방화벽에서 5000 포트 허용
2. http://127.0.0.1:5000 으로 시도
3. 봇이 정상 실행 중인지 확인
```

---

## 📱 모바일에서 접속

### 같은 Wi-Fi 환경
```
1. PC에서 봇 실행
2. PC의 IP 주소 확인
   - Windows: cmd → ipconfig
   - Mac: 시스템 설정 → 네트워크
   - Linux: ifconfig 또는 ip addr
3. 모바일 브라우저에서 http://PC_IP:5000 접속
```

예시:
```
PC IP: 192.168.0.100
모바일: http://192.168.0.100:5000
```

---

## 💡 사용 팁

### 초보자
```
1. 24시간 시뮬레이션 먼저 실행
2. 로그 확인하며 전략 이해
3. 소액(10만원)으로 실전 테스트
4. 점진적으로 금액 증액
```

### 중급자
```
1. 수익 투자 대상 변경 가능
   (코드에서 PROFIT_TARGETS 수정)
2. 투자 금액 조정 가능
   (PROFIT_INVEST_AMOUNT 수정)
3. 매수/매도 단계 커스터마이징
```

### 고급자
```
1. 백그라운드 실행
2. 서버 배포
3. 알림 기능 추가 (텔레그램 등)
4. 멀티 코인 동시 관리
```

---

## 📞 지원

### GitHub
```
저장소: https://github.com/wordycow/so.t-leader-choice
Issues: 버그 리포트
Discussions: 질문 및 아이디어
```

### 문서
```
완전 가이드: UPBIT-BOT-V5-GUIDE.md
버전 비교: BOT-VERSION-COMPARISON.md
배포 요약: DEPLOYMENT-SUMMARY-V4.md
```

---

## 🎉 시작하기

```
1. 다운로드: upbit-smart-bot-v5.0-complete.tar.gz
2. 압축 해제
3. install-and-run 실행 (Windows: .bat, Mac/Linux: .sh)
4. 브라우저 자동으로 열림
5. API 키 설정
6. 봇 시작 버튼 클릭
7. 완료! 🚀
```

---

**버전**: v5.0.0  
**날짜**: 2026-02-15  
**제작**: so.t Team  
**라이선스**: MIT

**행운을 빕니다! 📈💰🚀**
