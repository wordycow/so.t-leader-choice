# 🏗️ Upbit Bot v9 + IMEI v3.0 시스템 아키텍처

## ✅ 현재 시스템 구성

### 1. LLM (Large Language Model) - **현재 사용 안 함**
- **IMEI v3.0**은 현재 **Mock Response** 사용 중
- `imei_system/main_app.py`의 `generate_mock_response()` 함수가 간단한 규칙 기반 응답 생성
- **Ollama는 현재 사용하지 않음**

```python
# 현재 IMEI 응답 생성 방식 (Mock)
def generate_mock_response(user_message, context_analysis, trading_data):
    persona = context_analysis.get('primary_persona', 'bold_leader')
    
    # 간단한 키워드 매칭
    if '차트' in user_message or '분석' in user_message:
        return "차트 분석을 도와드리겠습니다..."
    
    if '힘들' in user_message:
        return "함께 할게요. 당신은 충분히 잘하고 있어요..."
    
    return f"({persona}) 잘 이해했어요. 함께 생각해보겠습니다."
```

### 2. 4-Engine 아키텍처 (현재 작동 중)

```
┌─────────────────────────────────────────────────────────────┐
│                    Signal Engine (Port 8765)                 │
│  - 시장 데이터 분석                                            │
│  - 신호 생성 (ULTRA_SCALP_V2_1, DEEP_HUNTER)                 │
│  - WebSocket으로 Execution Engine에 전송                      │
└────────────────────┬────────────────────────────────────────┘
                     │ WebSocket
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                  Execution Engine (Port 8765)                │
│  - 신호 수신 및 검증                                           │
│  - 거래 실행 (PRACTICE/LIVE 모드)                             │
│  - Safety Gate 적용                                           │
│  - 포지션 관리                                                 │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
                     ↓
┌──────────────────────────────┬──────────────────────────────┐
│    Dashboard (Port 5000)     │   IMEI System (Port 5001)    │
│  - 실시간 거래 스트림          │  - 학습 시스템                │
│  - KPI 표시                   │  - 메모리 저장 (SQLite)       │
│  - Upbit 스타일 UI           │  - 4가지 페르소나             │
│  - IMEI 아바타 표시          │  - 트리거 키워드 감지         │
└──────────────────────────────┴──────────────────────────────┘
```

### 3. 데이터 흐름

```
Market Data → Signal Engine → WebSocket → Execution Engine
                                               ↓
                                          Database (SQLite)
                                               ↓
                           ┌──────────────────┴──────────────────┐
                           ↓                                      ↓
                    Dashboard (Read)                    IMEI (Read + Learn)
```

---

## 🚀 시작 방법 (BAT 파일 사용)

### Windows
```bash
cd v9
START_ALL_BOTS.bat
```

### 자동으로 4개 창이 열립니다:
1. **Signal Engine** - 신호 생성
2. **Execution Engine** - 주문 실행
3. **Dashboard** - http://localhost:5000
4. **IMEI** - http://localhost:5001

---

## 🤖 Ollama 관련 FAQ

### Q: Ollama를 사용하나요?
**A: 아니요, 현재는 사용하지 않습니다.**

### Q: 왜 Ollama가 없나요?
**A:** IMEI v3.0은 현재 **Mock Response**로 작동합니다. 프로덕션 환경에서는 다음 중 하나를 선택할 수 있습니다:

1. **OpenAI GPT-4** (추천)
   - API 키만 있으면 바로 사용 가능
   - 높은 품질의 응답
   - 비용: ~$0.03/1K tokens

2. **Ollama (로컬 LLM)**
   - 무료
   - 오프라인 작동
   - 설치 필요: ~10GB+ 모델

3. **Mock Response (현재)**
   - 무료
   - 즉시 작동
   - 제한적인 응답

### Q: Ollama를 추가하고 싶어요!
**A:** 나중에 추가할 수 있습니다:

```python
# imei_system/main_app.py에 추가
import ollama

def generate_llm_response(user_message, context):
    response = ollama.chat(
        model='llama3.2',
        messages=[{
            'role': 'user',
            'content': user_message
        }]
    )
    return response['message']['content']
```

하지만 **지금은 필요 없습니다!** Mock Response로도 충분히 학습 시스템이 작동합니다.

---

## 📊 현재 시스템 상태

### ✅ 작동 중인 기능
- ✅ Signal Engine (신호 생성)
- ✅ Execution Engine (주문 실행)
- ✅ Dashboard (실시간 UI)
- ✅ IMEI 학습 시스템
- ✅ 메모리 저장 (SQLite)
- ✅ 페르소나 전환
- ✅ 트리거 키워드 감지

### ⏳ 미래 개선 계획
- [ ] OpenAI GPT-4 통합 (선택사항)
- [ ] Ollama 로컬 LLM (선택사항)
- [ ] 자가 학습 시스템 (신규 전략 자동 생성)
- [ ] 실전 수익 검증

---

## 🎯 결론

**지금 돌리면 됩니다!**

```bash
cd v9
START_ALL_BOTS.bat  # Windows
```

또는

```bash
cd v9
./start_all_bots.sh  # Linux/Mac
```

**Ollama는 필요 없습니다.** 현재 시스템은 완전히 작동합니다!
