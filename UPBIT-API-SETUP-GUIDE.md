# 🔐 업비트 API 안전 설정 및 모니터링 가이드

## 📌 목차
1. [업비트 API 발급 방법](#1-업비트-api-발급-방법)
2. [API 키 안전하게 관리하기](#2-api-키-안전하게-관리하기)
3. [환경변수로 API 키 숨기기](#3-환경변수로-api-키-숨기기)
4. [봇 실행 방법](#4-봇-실행-방법)
5. [실시간 모니터링 방법](#5-실시간-모니터링-방법)
6. [안전 체크리스트](#6-안전-체크리스트)

---

## 1. 업비트 API 발급 방법

### 📱 Step 1: 업비트 웹사이트 접속
1. **업비트 공식 사이트** 접속: https://upbit.com
2. 로그인 (본인인증 완료된 계정 필요)

### 🔑 Step 2: API 키 발급 페이지 이동
1. 우측 상단 **프로필 아이콘** 클릭
2. **Open API 관리** 클릭
3. 또는 직접 링크: https://upbit.com/mypage/open_api_management

### ⚙️ Step 3: API 키 생성
1. **"Open API Key 발급"** 버튼 클릭
2. **권한 설정** (⚠️ 중요!):
   ```
   ✅ 자산 조회 (Assets: View)
   ✅ 주문 조회 (Orders: View)
   ✅ 주문 하기 (Orders: Trade)
   ❌ 출금 하기 (Withdraws) ⛔ 절대 체크하지 마세요!
   ```

3. **IP 주소 화이트리스트** (선택사항):
   - 고정 IP가 있다면 등록 (더 안전)
   - 없으면 "특정 IP 주소에서만 사용" 체크 해제

4. **OTP 인증** 후 **API 키 발급**

### 📋 Step 4: API 키 저장
발급 받은 정보를 **안전한 곳에 메모**:
```
Access Key: xxxxxxxxxxxxxxxxxxxxxxxx
Secret Key: yyyyyyyyyyyyyyyyyyyyyyyy
```

⚠️ **경고**: Secret Key는 **딱 한 번만** 보여줍니다! 즉시 안전한 곳에 저장하세요!

---

## 2. API 키 안전하게 관리하기

### 🚫 절대 하지 말아야 할 것:
```python
# ❌ 나쁜 예시 - 코드에 직접 입력
access_key = "abcd1234efgh5678"  # 노출 위험!
secret_key = "wxyz9876stuv5432"  # 절대 금지!
```

### ✅ 안전한 방법:

#### 방법 1: 환경변수 사용 (권장 ⭐)
```bash
# API 키를 코드가 아닌 시스템 환경변수에 저장
export UPBIT_ACCESS_KEY="여기에_실제_Access_Key"
export UPBIT_SECRET_KEY="여기에_실제_Secret_Key"
```

#### 방법 2: .env 파일 사용 (편리함 ⭐⭐)
```bash
# .env 파일 생성 (Git에 절대 올리지 않음)
UPBIT_ACCESS_KEY=여기에_실제_Access_Key
UPBIT_SECRET_KEY=여기에_실제_Secret_Key
```

#### 방법 3: 별도 config 파일 (암호화)
```python
# config.json (암호화해서 저장)
{
  "access_key": "암호화된_키",
  "secret_key": "암호화된_키"
}
```

---

## 3. 환경변수로 API 키 숨기기

### 🖥️ Linux/Mac 환경변수 설정

#### 방법 A: 터미널에서 직접 설정 (임시)
```bash
# 현재 터미널 세션에만 유효
export UPBIT_ACCESS_KEY="abcd1234..."
export UPBIT_SECRET_KEY="wxyz5678..."

# 확인
echo $UPBIT_ACCESS_KEY
```

#### 방법 B: ~/.bashrc 또는 ~/.zshrc에 영구 설정
```bash
# 홈 디렉토리의 .bashrc 파일 편집
nano ~/.bashrc

# 파일 맨 아래에 추가:
export UPBIT_ACCESS_KEY="여기에_실제_Access_Key"
export UPBIT_SECRET_KEY="여기에_실제_Secret_Key"

# 저장 후 적용
source ~/.bashrc
```

#### 방법 C: .env 파일 + python-dotenv 사용 (가장 편리 ⭐⭐⭐)

**1단계: python-dotenv 설치**
```bash
pip install python-dotenv
```

**2단계: .env 파일 생성**
```bash
# 봇 파일과 같은 폴더에 .env 파일 생성
nano .env
```

**3단계: .env 파일 내용**
```
UPBIT_ACCESS_KEY=abcd1234efgh5678ijklmnop
UPBIT_SECRET_KEY=wxyz9876stuv5432qrstuvwx
```

**4단계: .gitignore에 .env 추가**
```bash
echo ".env" >> .gitignore
```

**5단계: Python 코드에서 불러오기**
```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경변수에서 API 키 가져오기
access_key = os.getenv("UPBIT_ACCESS_KEY")
secret_key = os.getenv("UPBIT_SECRET_KEY")

print(f"API 키 로드 완료: {access_key[:4]}****")
```

---

### 🪟 Windows 환경변수 설정

#### 방법 A: 명령 프롬프트 (임시)
```cmd
set UPBIT_ACCESS_KEY=abcd1234...
set UPBIT_SECRET_KEY=wxyz5678...
```

#### 방법 B: PowerShell (임시)
```powershell
$env:UPBIT_ACCESS_KEY="abcd1234..."
$env:UPBIT_SECRET_KEY="wxyz5678..."
```

#### 방법 C: 시스템 환경변수 (영구)
1. **시작** → **"환경 변수"** 검색
2. **"시스템 환경 변수 편집"** 클릭
3. **"환경 변수"** 버튼 클릭
4. **"사용자 변수"**에서 **"새로 만들기"**:
   - 변수 이름: `UPBIT_ACCESS_KEY`
   - 변수 값: `실제_Access_Key`
5. 다시 **"새로 만들기"**:
   - 변수 이름: `UPBIT_SECRET_KEY`
   - 변수 값: `실제_Secret_Key`
6. **확인** 후 터미널 재시작

---

## 4. 봇 실행 방법

### 🚀 기본 실행

#### 옵션 1: 포그라운드 실행 (테스트용)
```bash
# 터미널에서 직접 실행
python3 upbit-scalping-bot.py

# 종료: Ctrl + C
```

#### 옵션 2: 백그라운드 실행 (24시간 운영)
```bash
# nohup으로 백그라운드 실행
nohup python3 upbit-scalping-bot.py > bot.log 2>&1 &

# 프로세스 ID 확인
echo $!

# 또는 프로세스 찾기
ps aux | grep upbit-scalping-bot
```

#### 옵션 3: screen 사용 (추천 ⭐⭐)
```bash
# screen 세션 생성
screen -S upbit_bot

# 봇 실행
python3 upbit-scalping-bot.py

# 세션에서 빠져나오기 (봇은 계속 실행)
Ctrl + A, 그 다음 D

# 다시 세션 접속
screen -r upbit_bot

# 세션 목록 보기
screen -ls
```

#### 옵션 4: systemd 서비스 등록 (고급)
```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/upbit-bot.service
```

서비스 파일 내용:
```ini
[Unit]
Description=Upbit Scalping Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/webapp
Environment="UPBIT_ACCESS_KEY=your_access_key"
Environment="UPBIT_SECRET_KEY=your_secret_key"
ExecStart=/usr/bin/python3 /home/user/webapp/upbit-scalping-bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 실행:
```bash
sudo systemctl daemon-reload
sudo systemctl start upbit-bot
sudo systemctl enable upbit-bot  # 부팅시 자동 시작
sudo systemctl status upbit-bot
```

---

## 5. 실시간 모니터링 방법

### 📊 로그 파일 모니터링

#### 방법 1: tail -f (실시간 로그 확인)
```bash
# 로그 실시간 확인
tail -f bot.log

# 마지막 100줄 확인
tail -n 100 bot.log

# 특정 키워드 필터링
tail -f bot.log | grep "매수"
tail -f bot.log | grep "ERROR"
```

#### 방법 2: less (로그 스크롤)
```bash
# 로그 파일 열기
less bot.log

# 단축키:
# Space: 다음 페이지
# b: 이전 페이지
# /검색어: 검색
# q: 종료
```

#### 방법 3: grep으로 특정 내용 검색
```bash
# 매수 기록만 보기
grep "매수" bot.log

# 에러 기록만 보기
grep "ERROR" bot.log

# 오늘 날짜 기록만 보기
grep "2025-02-15" bot.log

# 수익 기록만 보기
grep "수익률" bot.log
```

### 📈 프로세스 상태 확인

```bash
# 봇이 실행 중인지 확인
ps aux | grep upbit-scalping-bot

# CPU/메모리 사용량 실시간 확인
top -p $(pgrep -f upbit-scalping-bot)

# 또는 htop (더 보기 좋음)
htop -p $(pgrep -f upbit-scalping-bot)
```

### 🔔 알림 설정 (고급)

#### 텔레그램 봇으로 알림 받기
```python
import requests

def send_telegram(message):
    bot_token = "YOUR_TELEGRAM_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

# 매수/매도 시 알림
send_telegram(f"🚀 매수 체결! 가격: {price}원")
```

#### 이메일 알림
```python
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    sender = "your_email@gmail.com"
    receiver = "your_email@gmail.com"
    password = "your_app_password"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)
```

### 📊 대시보드 웹 페이지 만들기 (고급)

```python
from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    # 로그 파일 읽어서 통계 생성
    with open('bot.log', 'r') as f:
        logs = f.readlines()
    
    stats = {
        'total_trades': len([l for l in logs if '매수' in l or '매도' in l]),
        'total_profit': 0,  # 계산 필요
        'win_rate': 0,  # 계산 필요
    }
    
    return render_template('dashboard.html', stats=stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 6. 안전 체크리스트

### ✅ 실행 전 확인사항

- [ ] **API 키가 코드에 직접 입력되어 있지 않은가?**
- [ ] **환경변수 또는 .env 파일로 관리하고 있는가?**
- [ ] **.env 파일이 .gitignore에 포함되어 있는가?**
- [ ] **출금 권한이 API 키에 포함되어 있지 않은가?**
- [ ] **초기 투자금액이 감당 가능한 수준인가?**
- [ ] **손절 로직이 제대로 작동하는가?**
- [ ] **로그 파일 경로가 올바른가?**

### 🔒 보안 베스트 프랙티스

1. **API 키는 절대 GitHub/공개 저장소에 올리지 않기**
2. **출금 권한은 절대 부여하지 않기**
3. **IP 화이트리스트 사용 (가능하면)**
4. **정기적으로 API 키 재발급**
5. **로그 파일에도 API 키가 출력되지 않도록 주의**
6. **테스트는 소액으로 시작**

### 🚨 비상 상황 대처

#### 봇 긴급 중지
```bash
# 프로세스 찾기
ps aux | grep upbit-scalping-bot

# 프로세스 종료
kill -9 <PID>

# 또는 모든 관련 프로세스 종료
pkill -f upbit-scalping-bot
```

#### API 키 무효화
1. 업비트 웹사이트 접속
2. Open API 관리 페이지
3. 해당 API 키 **삭제**

---

## 📞 문제 발생 시

### 자주 발생하는 오류

#### 1. "API Key가 없습니다"
```bash
# 환경변수 확인
echo $UPBIT_ACCESS_KEY
echo $UPBIT_SECRET_KEY

# 없으면 다시 설정
export UPBIT_ACCESS_KEY="..."
export UPBIT_SECRET_KEY="..."
```

#### 2. "잔고가 부족합니다"
- 업비트 계정에 충분한 KRW가 있는지 확인
- 봇 설정의 `SEED_AMOUNT`를 줄이기

#### 3. "pyupbit 모듈을 찾을 수 없습니다"
```bash
pip install pyupbit pandas numpy
```

#### 4. 봇이 거래를 안 함
- 로그 확인: `tail -f bot.log`
- RSI/볼린저밴드 조건 확인
- 시장 상황 확인 (횡보장에서는 거래 적음)

---

## 🎯 추천 모니터링 루틴

### 하루 3번 체크 (아침/점심/저녁)
```bash
# 1. 봇 실행 확인
ps aux | grep upbit-scalping-bot

# 2. 최근 로그 확인 (마지막 50줄)
tail -n 50 bot.log

# 3. 오늘의 거래 기록
grep "$(date +%Y-%m-%d)" bot.log | grep "매수\|매도"

# 4. 수익률 확인
grep "수익률" bot.log | tail -n 10
```

### 주간 리포트 생성
```bash
# 이번 주 모든 거래 기록
grep "매수\|매도" bot.log | grep "2025-02-1[0-5]"

# 통계 계산
# 총 거래 횟수
grep "매수" bot.log | wc -l
grep "매도" bot.log | wc -l
```

---

## 📚 추가 학습 자료

- **업비트 공식 API 문서**: https://docs.upbit.com/
- **pyupbit 라이브러리**: https://github.com/sharebook-kr/pyupbit
- **암호화폐 트레이딩 전략**: https://www.investopedia.com/
- **백테스팅 도구**: https://www.backtrader.com/

---

**✨ 안전하고 수익성 있는 트레이딩 되세요! 화이팅! 🚀**
