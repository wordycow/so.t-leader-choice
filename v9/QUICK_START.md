# 🚀 빠른 시작 가이드

## ⚠️ 중요: 관리자 권한 필수!

모든 BAT 파일은 **마우스 우클릭 → 관리자 권한으로 실행** 해야 합니다!

---

## 📋 실행 방법

### 1. 시작
```
START_EVERYTHING.bat 우클릭 → 관리자 권한으로 실행
```

**예상 결과**: 6개 창 열림
- Cloudflare Tunnel
- Ollama Server
- Execution Engine
- Signal Engine
- Dashboard (자동 브라우저 오픈)
- IMEI System

---

### 2. 60초 대기 후 확인
```
CHECK_STATUS.bat 우클릭 → 관리자 권한으로 실행
```

**통과 조건**:
```
✅ Cloudflare Tunnel                  [실행중]
✅ Port 11434 - Ollama Server          [실행중]
✅ Port 8765  - Execution Engine       [실행중]
✅ Port 5000  - Dashboard              [실행중]
✅ Port 5001  - IMEI System            [실행중]

📈 요약: 5 / 5 서비스 실행 중
```

---

### 3. 종료
```
STOP_EVERYTHING.bat 우클릭 → 관리자 권한으로 실행
```

---

## 🔧 문제 해결

### "액세스가 거부되었습니다"
**원인**: 관리자 권한 없이 실행

**해결**:
1. BAT 파일 우클릭
2. **"관리자 권한으로 실행"** 선택
3. UAC 팝업에서 "예" 클릭

---

### 자동으로 관리자 권한 요청
모든 BAT 파일에 관리자 권한 자동 요청 코드가 들어있습니다.
더블클릭하면 자동으로 권한 상승 팝업이 뜹니다!

---

## 📊 검증 체크리스트

```cmd
# 1. 시작 (관리자 권한)
START_EVERYTHING.bat

# 2. 60초 대기
(브라우저에서 Dashboard 확인)

# 3. 상태 확인 (관리자 권한)
CHECK_STATUS.bat

# 4. 종료 (관리자 권한)
STOP_EVERYTHING.bat
```

---

## 💡 팁

1. **항상 관리자 권한으로 실행**
   - 포트 종료(taskkill)에 관리자 권한 필요

2. **더블클릭도 가능**
   - 자동으로 UAC 팝업 뜸 → "예" 클릭

3. **문제 발생 시**
   - STOP → 3초 대기 → START 재실행

---

## 🎯 한 줄 요약

**모든 BAT 파일을 관리자 권한으로 실행하세요!**
