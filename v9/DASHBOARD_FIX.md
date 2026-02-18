# 🔧 Dashboard 접속 오류 해결 완료!

## ❌ **문제**
- `localhost:5000`에 접속 시 "사이트에 연결할 수 없음" 오류 (ERR_CONNECTION_REFUSED)
- Dashboard가 실행되지 않음

## ✅ **해결책**
- **독립 실행 가능한 Dashboard 추가**: `standalone_dashboard.py`
- **시작 스크립트 업데이트**: `START_ALL_BOTS.bat`, `start_all_bots.sh`

---

## 🚀 **지금 바로 사용하기**

### **Windows (노트북):**

1. **코드 업데이트**:
```cmd
cd v9
git pull origin main
```

2. **봇 시작**:
```cmd
START_ALL_BOTS.bat 더블클릭
```

3. **브라우저 접속**:
- Main Dashboard: http://localhost:5000
- IMEI Dashboard: http://localhost:5000/imei_dashboard.html

---

### **Linux/Mac (서버):**

1. **코드 업데이트**:
```bash
cd v9
git pull origin main
```

2. **봇 시작**:
```bash
./start_all_bots.sh
```

3. **브라우저 접속**:
- Main Dashboard: http://localhost:5000

---

## 📦 **변경 사항**

### 새로 추가된 파일:
- `v9/dashboard/standalone_dashboard.py` - 독립 실행 가능한 Dashboard

### 수정된 파일:
- `v9/START_ALL_BOTS.bat` - Windows 시작 스크립트
- `v9/start_all_bots.sh` - Linux/Mac 시작 스크립트

---

## 🎯 **Standalone Dashboard 기능**

### ✨ **Mock 데이터로 즉시 테스트 가능**
- Python 패키지만 설치하면 바로 실행
- Signal Engine/Execution Engine 없이도 UI 테스트 가능

### 📊 **API Endpoints (8개)**:
```
GET /health              - 헬스 체크
GET /api/kpis            - 시스템 KPI (자산, 손익, 포지션 수)
GET /api/top20           - TOP 20 후보 종목
GET /api/holdings        - 보유 포지션
GET /api/trades          - 최근 거래 내역
GET /api/safety          - 안전 게이트 상태
GET /api/recovery        - 회복 엔진 상태
GET /api/btc_stacking    - BTC 스태킹 상태
```

### 🎨 **UI 페이지**:
```
GET /                           - Main Dashboard
GET /imei_dashboard.html        - IMEI Dashboard
```

---

## 🧪 **테스트 방법**

### 1. Dashboard만 단독 실행:
```bash
cd v9
python3 dashboard/standalone_dashboard.py
```

### 2. Health Check:
```bash
curl http://localhost:5000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "Standalone Dashboard",
  "version": "v9",
  "timestamp": "2026-02-18T15:31:49.299825"
}
```

### 3. KPIs 조회:
```bash
curl http://localhost:5000/api/kpis
```

**Expected Output:**
```json
{
  "mode": "PRACTICE",
  "equity": 1000000,
  "realized_pnl": 0,
  "unrealized_pnl": 0,
  "position_count": 0,
  "timestamp": "2026-02-18T15:31:55.709436"
}
```

---

## 🔄 **실제 거래 데이터 보기**

Mock 데이터가 아닌 **실제 거래 데이터**를 보려면:

### 전체 시스템 실행:
```
1. Signal Engine (websocket_emitter.py)
2. Execution Engine (websocket_receiver.py)
3. Dashboard (standalone_dashboard.py)
4. IMEI Main App (main_app.py)
```

**방법**: `START_ALL_BOTS.bat` 또는 `./start_all_bots.sh` 실행

---

## 📝 **실행 순서**

### Windows:
```
1. cd v9
2. git pull origin main  (최신 코드 가져오기)
3. START_ALL_BOTS.bat 더블클릭
4. 브라우저에서 http://localhost:5000 접속
```

### Linux/Mac:
```bash
1. cd v9
2. git pull origin main
3. ./start_all_bots.sh
4. 브라우저에서 http://localhost:5000 접속
```

---

## ⚠️ **주의사항**

### Mock 데이터 vs 실제 데이터:

| 항목 | Standalone Dashboard | 전체 시스템 |
|------|---------------------|------------|
| 실행 방법 | `python3 standalone_dashboard.py` | `START_ALL_BOTS.bat` 실행 |
| 데이터 | Mock 데이터 (테스트용) | 실제 Upbit API 데이터 |
| 목적 | UI 개발/테스트 | 실거래/연습 모드 |
| 필요 구성요소 | Dashboard만 | Signal + Execution + Dashboard + IMEI |

---

## 🎉 **해결 완료!**

이제 `START_ALL_BOTS.bat`를 더블클릭하면:
- ✅ Dashboard가 정상적으로 시작됩니다
- ✅ http://localhost:5000 접속 시 UI가 보입니다
- ✅ Mock 데이터로 즉시 테스트 가능합니다
- ✅ 전체 시스템 실행 시 실제 거래 데이터 표시

---

**Repository**: https://github.com/wordycow/so.t-leader-choice  
**Latest Commit**: `de13748`  
**Fixed**: 2026-02-18

**문제가 해결되었습니다!** 🚀
