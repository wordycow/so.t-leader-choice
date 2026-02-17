# 📦 전략별 아이콘 + 보유 개수 표시 가이드 (v12.4.1)

## 🎯 요구사항 (스크린샷 기준)

### ✅ 1️⃣ 상단 전략 카드에 보유 개수 표시

```
┌─────────────────────┐
│ 📦 Box Trader       │  ACTIVE
│ 0%    +0.0%    [6]  │  ← 현재 이 전략으로 보유 중인 코인 개수
└─────────────────────┘
```

### ✅ 2️⃣ 보유 코인 카드에 전략 정보 표시

```
┌─────────────────────────────┐
│ 🪙 보유 코인                 │
├─────────────────────────────┤
│ 💰 PEPE                     │
│ 📦 박스권 매매로 매수       │ ← 전략 아이콘 + 이름
│ 진입: 0.0100원 (2024...)    │
│ 현재: 0.0099원 (-1.00%)     │
│ 💡 매수 이유:               │
│    전략: box_trader         │
│    RSI 과매도(28.3)         │
│    거래량 급증 2.8배        │
└─────────────────────────────┘
```

---

## 📊 API 응답 구조

### 전체 응답 예시:
```json
{
  "running": true,
  "current_positions": 6,
  "max_positions": 10,
  
  "strategy_holdings": {
    "box_trader": 6,
    "surge_hunter": 0,
    "dip_hunter": 0,
    "trend_follower": 0,
    "volume_hunter": 0
  },
  
  "holdings": [
    {
      "ticker": "KRW-PEPE",
      "coin_name": "PEPE",
      "profit_rate": -0.16,
      "avg_price": 0.01,
      "current_price": 0.0099,
      
      "strategy": "box_trader",
      "strategy_name": "박스권 매매",
      "strategy_icon": "📦",
      
      "buy_reason": "전략: box_trader | RSI 과매도(28.3) | 거래량 급증 2.8배",
      "entry_time": "2026-02-17 10:06:04",
      "dca_count": 0
    }
  ]
}
```

---

## 🎨 프론트엔드 구현

### 1️⃣ 상단 전략 카드 (Vue.js 예시)

```html
<template>
  <div class="strategy-grid">
    <!-- Surge Hunter -->
    <div class="strategy-card" :class="{ active: strategyHoldings.surge_hunter > 0 }">
      <div class="strategy-header">
        <span class="icon">🔥</span>
        <span class="name">Surge Hunter</span>
        <span class="badge">ACTIVE</span>
      </div>
      <div class="strategy-stats">
        <div class="stat">
          <div class="label">승률</div>
          <div class="value">{{ strategies.surge_hunter?.win_rate || 0 }}%</div>
        </div>
        <div class="stat">
          <div class="label">수익</div>
          <div class="value positive">+{{ strategies.surge_hunter?.profit || 0 }}%</div>
        </div>
        <div class="stat">
          <div class="label">보유</div>
          <div class="value holdings-count">{{ strategyHoldings.surge_hunter || 0 }}</div>
        </div>
      </div>
    </div>

    <!-- Box Trader -->
    <div class="strategy-card" :class="{ active: strategyHoldings.box_trader > 0 }">
      <div class="strategy-header">
        <span class="icon">📦</span>
        <span class="name">Box Trader</span>
        <span class="badge" v-if="strategyHoldings.box_trader > 0">ACTIVE</span>
      </div>
      <div class="strategy-stats">
        <div class="stat">
          <div class="label">승률</div>
          <div class="value">{{ strategies.box_trader?.win_rate || 0 }}%</div>
        </div>
        <div class="stat">
          <div class="label">수익</div>
          <div class="value positive">+{{ strategies.box_trader?.profit || 0 }}%</div>
        </div>
        <div class="stat">
          <div class="label">보유</div>
          <div class="value holdings-count">{{ strategyHoldings.box_trader || 0 }}</div>
        </div>
      </div>
    </div>

    <!-- 나머지 전략 카드들... -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      strategyHoldings: {},
      strategies: {}
    };
  },
  
  methods: {
    async updateStatus() {
      const res = await fetch('/api/status');
      const data = await res.json();
      
      this.strategyHoldings = data.strategy_holdings || {};
      this.strategies = data.strategies || {};
    }
  },
  
  mounted() {
    this.updateStatus();
    setInterval(this.updateStatus, 2000); // 2초마다 갱신
  }
};
</script>
```

### 2️⃣ 보유 코인 카드

```html
<template>
  <div class="holdings-section">
    <h3>💼 보유 코인 ({{ holdings.length }}/{{ maxPositions }})</h3>
    
    <div class="coin-cards">
      <div 
        v-for="coin in holdings" 
        :key="coin.ticker"
        class="coin-card"
        :class="{ profit: coin.profit_rate > 0, loss: coin.profit_rate < 0 }"
      >
        <!-- 상단: 코인 이름 + 수익률 -->
        <div class="coin-header">
          <div class="coin-info">
            <span class="coin-name">{{ coin.coin_name }}</span>
            <span class="strategy-badge">
              {{ coin.strategy_icon }} {{ coin.strategy_name }}
            </span>
          </div>
          <div class="profit-rate" :class="{ positive: coin.profit_rate > 0, negative: coin.profit_rate < 0 }">
            {{ coin.profit_rate > 0 ? '+' : '' }}{{ coin.profit_rate.toFixed(2) }}%
          </div>
        </div>

        <!-- 가격 정보 -->
        <div class="coin-prices">
          <div class="price-row">
            <span class="label">진입가:</span>
            <span class="value">{{ coin.avg_price.toLocaleString() }}원</span>
          </div>
          <div class="price-row">
            <span class="label">현재가:</span>
            <span class="value">{{ coin.current_price.toLocaleString() }}원</span>
          </div>
        </div>

        <!-- 매수 이유 -->
        <div class="buy-reason">
          <div class="reason-label">💡 매수 이유</div>
          <div class="reason-content">{{ coin.buy_reason }}</div>
        </div>

        <!-- 물타기 정보 (있을 경우만) -->
        <div v-if="coin.dca_count > 0" class="dca-badge">
          📈 물타기 {{ coin.dca_count }}회
        </div>

        <!-- 진입 시간 -->
        <div class="entry-time">
          진입: {{ formatTime(coin.entry_time) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    holdings: Array,
    maxPositions: Number
  },
  
  methods: {
    formatTime(timestamp) {
      if (!timestamp) return 'N/A';
      return new Date(timestamp).toLocaleString('ko-KR', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
};
</script>
```

---

## 🎨 CSS 스타일

```css
/* 전략 카드 */
.strategy-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.strategy-card.active {
  border-color: var(--accent-color);
  background: var(--card-bg-active);
  box-shadow: 0 4px 12px rgba(var(--accent-rgb), 0.2);
}

.strategy-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.strategy-header .icon {
  font-size: 24px;
}

.strategy-header .name {
  flex: 1;
  font-weight: 600;
  font-size: 14px;
}

.strategy-header .badge {
  padding: 4px 8px;
  background: var(--success-color);
  color: white;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.strategy-stats {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.stat {
  text-align: center;
}

.stat .label {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.stat .value {
  font-size: 16px;
  font-weight: 600;
}

.stat .holdings-count {
  color: var(--accent-color);
  font-size: 20px;
}

/* 코인 카드 */
.coin-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid var(--border-color);
  transition: all 0.3s ease;
}

.coin-card.profit {
  border-left-color: var(--success-color);
}

.coin-card.loss {
  border-left-color: var(--danger-color);
}

.coin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.coin-name {
  font-size: 18px;
  font-weight: 700;
  display: block;
  margin-bottom: 4px;
}

.strategy-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: var(--badge-bg);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.profit-rate {
  font-size: 20px;
  font-weight: 700;
}

.profit-rate.positive {
  color: var(--success-color);
}

.profit-rate.negative {
  color: var(--danger-color);
}

.buy-reason {
  margin-top: 12px;
  padding: 12px;
  background: var(--reason-bg);
  border-radius: 8px;
  border-left: 3px solid var(--accent-color);
}

.reason-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.reason-content {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-primary);
}

.dca-badge {
  margin-top: 8px;
  padding: 6px 12px;
  background: var(--warning-bg);
  border-radius: 6px;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.entry-time {
  margin-top: 8px;
  font-size: 11px;
  color: var(--text-tertiary);
}
```

---

## 🎯 전략 아이콘 매핑

| 전략 ID | 아이콘 | 한글명 |
|---------|--------|--------|
| surge_hunter | 🔥 | 급등 포착 |
| dip_hunter | 📉 | 급락 저점 → 원가 복귀 |
| box_trader | 📦 | 박스권 매매 |
| trend_follower | 📈 | 추세 추종 |
| volume_hunter | 🔊 | 수급 기반 |
| gap_down_reversal | ⚡ | BNF 급락 반등 |
| squeeze_momentum | 💥 | 압축 모멘텀 |
| ema_squeeze | 🎯 | 200/20 이평선 스퀴즈 |
| testa_3sma | 🎪 | 테스타 3중 이평선 |
| rsi_reversal | 🔄 | RSI 필터 반전 |
| volume_breakout_v2 | 💪 | 거래량 돌파 |
| mach7_pullback | 🚀 | 마하7 이평선 눌림목 |

---

## ✅ 구현 체크리스트

- [x] 백엔드: 전략별 아이콘 추가 (STRATEGIES)
- [x] 백엔드: strategy_holdings 계산 로직
- [x] 백엔드: holdings에 strategy_name, strategy_icon 추가
- [x] API: /api/status에 strategy_holdings 포함
- [ ] 프론트엔드: 상단 전략 카드에 보유 개수 표시
- [ ] 프론트엔드: 보유 코인 카드에 전략 정보 표시
- [ ] 프론트엔드: 실시간 업데이트 (2초 폴링)

---

## 🚀 테스트 결과

```
✨ v12.4.1 전략별 아이콘 + 보유 개수 테스트
================================================================================

📊 전략별 보유 코인 개수:
  • box_trader: 6개

💼 보유 코인 상세:

  🪙 PEPE:
     📦 박스권 매매
     수익률: -0.16%
     💡 매수 이유: 매수 신호 감지

  🪙 MOVE:
     📦 박스권 매매
     수익률: +0.00%
     💡 매수 이유: 매수 신호 감지

(... 나머지 코인들)
```

---

## 📝 사용자 피드백 예상

> "오! Box Trader로 6개 코인을 보유하고 있구나. 한눈에 보이네!"

> "PEPE를 왜 샀는지 궁금했는데, 박스권 매매 전략이었구나!"

> "전략마다 아이콘이 있으니까 직관적이고 좋네요!"

---

## 🎁 보너스: 전략별 필터링

```javascript
// 특정 전략으로 산 코인만 보기
const boxTraderCoins = holdings.filter(h => h.strategy === 'box_trader');

// 전략별 평균 수익률
const avgProfitByStrategy = {};
Object.keys(strategyHoldings).forEach(strategy => {
  const coins = holdings.filter(h => h.strategy === strategy);
  const totalProfit = coins.reduce((sum, c) => sum + c.profit_rate, 0);
  avgProfitByStrategy[strategy] = coins.length > 0 ? totalProfit / coins.length : 0;
});
```
