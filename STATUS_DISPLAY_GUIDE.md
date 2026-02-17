# 🎨 실시간 상태 메시지 표시 가이드 (v12.4)

## 📊 API 응답 예시

```json
{
  "running": true,
  "status_message": "🔍 30개 코인 분석 중",
  "status_emoji": "🔍",
  "status_detail": "거래량 상위 코인 패턴 분석 중",
  "current_positions": 7,
  "max_positions": 10,
  "holdings": [
    {
      "ticker": "KRW-PEPE",
      "coin_name": "PEPE",
      "profit_rate": -0.62,
      "avg_price": 0.01,
      "buy_reason": "전략: box_trader | RSI 과매도(28.3) | 거래량 급증 2.8배",
      "strategy": "box_trader",
      "entry_time": "2026-02-17 10:06:04",
      "dca_count": 0
    }
  ]
}
```

## 🎯 대시보드 표시 예시

### 1️⃣ 상단 상태 표시 (실행 중 옆)

```html
<!-- 기존 -->
<div class="status-badge">
  <span class="spinner"></span>
  실행 중
</div>

<!-- v12.4 개선 -->
<div class="status-badge">
  <span class="status-emoji">🔍</span>
  <span class="status-message">30개 코인 분석 중</span>
</div>
<div class="status-detail">거래량 상위 코인 패턴 분석 중</div>
```

### 2️⃣ 상태 종류별 표시

| 상태 | 이모지 | 메시지 예시 | 설명 |
|------|--------|-------------|------|
| 초기화 | ⚙️ | 초기화 중 | 봇 시작 준비 중 |
| 스캔 | 🔍 | 30개 코인 분석 중 | 거래 기회 탐색 |
| 상승장 | 🚀 | 상승장 공격 | 적극 매수 모드 |
| 하락장 | 📉 | 하락장 대응 | 급락 저점 매수 대기 |
| 신중 | ⚠️ | 신중 모드 | 약한 하락, 조심 |
| 보유 | 📊 | 7개 코인 관리 중 | 포지션 모니터링 |
| 매수 | ✨ | SOL 매수 기회! | 매수 신호 감지 |
| 매도 | 💰 | PEPE 매도 중 | 익절/손절 실행 |
| 물타기 | 📉 | BTC 물타기 중 | 평균매수 진행 |
| 대기 | ⏸️ | 좋은 기회 대기 중 | 확실한 신호만 포착 |
| 포지션 Full | ⏸️ | 포지션 가득참 | 보유 10개/10개 |

### 3️⃣ 보유 코인 카드에 매수 이유 추가

```html
<div class="coin-card">
  <div class="coin-header">
    <span class="coin-name">PEPE</span>
    <span class="profit-rate positive">+2.34%</span>
  </div>
  
  <div class="coin-details">
    <div class="detail-row">
      <span>평균가:</span>
      <span>0.01원</span>
    </div>
    <div class="detail-row">
      <span>현재가:</span>
      <span>0.0102원</span>
    </div>
  </div>
  
  <!-- ✨ v12.4 추가 -->
  <div class="buy-reason">
    <div class="reason-label">💡 매수 이유</div>
    <div class="reason-text">
      전략: box_trader | RSI 과매도(28.3) | 거래량 급증 2.8배
    </div>
  </div>
  
  <!-- 물타기 정보 (dca_count > 0일 때만) -->
  <div class="dca-info" v-if="coin.dca_count > 0">
    <span>📈 물타기:</span>
    <span>{{ coin.dca_count }}회</span>
  </div>
</div>
```

### 4️⃣ CSS 스타일 예시

```css
/* 상태 메시지 */
.status-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--surface-color);
  border-radius: 8px;
  animation: pulse 2s ease-in-out infinite;
}

.status-emoji {
  font-size: 20px;
  animation: bounce 1s ease-in-out infinite;
}

.status-message {
  font-weight: 600;
  color: var(--text-color);
}

.status-detail {
  margin-top: 4px;
  font-size: 0.9em;
  color: var(--text-secondary);
  opacity: 0.8;
}

/* 매수 이유 */
.buy-reason {
  margin-top: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border-left: 3px solid var(--accent-color);
}

.reason-label {
  font-size: 0.85em;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.reason-text {
  font-size: 0.9em;
  line-height: 1.4;
  color: var(--text-color);
}

/* 물타기 뱃지 */
.dca-info {
  margin-top: 8px;
  padding: 6px 12px;
  background: var(--warning-light);
  border-radius: 6px;
  font-size: 0.85em;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

/* 애니메이션 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
```

### 5️⃣ JavaScript 업데이트 로직

```javascript
// 상태 업데이트 (2초마다)
setInterval(async () => {
  const response = await fetch('/api/status');
  const data = await response.json();
  
  // 상태 메시지 업데이트
  document.querySelector('.status-emoji').textContent = data.status_emoji;
  document.querySelector('.status-message').textContent = data.status_message;
  document.querySelector('.status-detail').textContent = data.status_detail;
  
  // 포지션 카운트 업데이트
  document.querySelector('.position-count').textContent = 
    `${data.current_positions}/${data.max_positions}`;
  
  // 보유 코인 업데이트
  updateHoldings(data.holdings);
}, 2000);

function updateHoldings(holdings) {
  holdings.forEach(coin => {
    const card = document.querySelector(`[data-ticker="${coin.ticker}"]`);
    
    // 매수 이유 표시
    if (coin.buy_reason) {
      card.querySelector('.reason-text').textContent = coin.buy_reason;
    }
    
    // 물타기 정보 표시
    if (coin.dca_count > 0) {
      card.querySelector('.dca-info').style.display = 'flex';
      card.querySelector('.dca-count').textContent = `${coin.dca_count}회`;
    }
  });
}
```

## 🎯 사용자 경험 개선 포인트

1. **지루하지 않음**: 상태가 계속 바뀌어서 봇이 살아있다는 느낌
2. **투명성**: 왜 사고 팔았는지 이유를 명확하게 표시
3. **신뢰감**: 전문적인 전략과 이유가 있다는 것을 보여줌
4. **교육적**: 사용자가 매매 논리를 이해하고 배울 수 있음
5. **재미**: 이모지와 생동감 있는 메시지로 흥미 유발

## 📝 메시지 작성 가이드

### ✅ 좋은 예시
- "🔍 30개 코인 분석 중" (구체적)
- "🚀 강세장 적극 매수 (BTC +2.3%)" (시장 상황 포함)
- "💡 전략: box_trader | RSI 과매도(28.3)" (근거 명확)

### ❌ 나쁜 예시
- "스캔 중" (너무 단순)
- "매수" (왜 샀는지 모름)
- "대기" (왜 대기하는지 불명확)

## 🚀 다음 단계

1. **프론트엔드 구현**: 위 HTML/CSS/JS를 대시보드에 적용
2. **실시간 업데이트**: WebSocket 또는 2초 폴링으로 상태 갱신
3. **알림**: 매수/매도 시 브라우저 알림 추가
4. **히스토리**: 매수/매도 이유를 거래 히스토리에도 저장
