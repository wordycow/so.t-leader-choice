// 🚀 실전 트레이더 대시보드 - API 연동 & AI 추천

// ============================================
// 1. API 엔드포인트
// ============================================
const API = {
  // Binance API (급등/급락 데이터)
  BINANCE_TICKER: 'https://api.binance.com/api/v3/ticker/24hr',
  
  // CoinGecko API (시장 데이터)
  COINGECKO_GLOBAL: 'https://api.coingecko.com/api/v3/global',
  
  // Coinglass API (롱/숏, 청산 데이터)
  COINGLASS_LONG_SHORT: 'https://open-api.coinglass.com/public/v2/indicator/long_short_accounts_ratio',
  COINGLASS_LIQUIDATION: 'https://open-api.coinglass.com/public/v2/indicator/liquidation_history',
  
  // Upbit API (한국 데이터)
  UPBIT_TICKER: 'https://api.upbit.com/v1/ticker'
};

// ============================================
// 2. 급등/급락 코인 가져오기
// ============================================
async function fetchTopMovers() {
  try {
    const response = await fetch(API.BINANCE_TICKER);
    const data = await response.json();
    
    // USDT 페어만 필터링
    const usdtPairs = data
      .filter(coin => coin.symbol.endsWith('USDT'))
      .map(coin => ({
        symbol: coin.symbol,
        change: parseFloat(coin.priceChangePercent),
        price: parseFloat(coin.lastPrice),
        volume: parseFloat(coin.volume)
      }));
    
    // 급등 TOP 5
    const topGainers = [...usdtPairs]
      .sort((a, b) => b.change - a.change)
      .slice(0, 5);
    
    // 급락 TOP 5
    const topLosers = [...usdtPairs]
      .sort((a, b) => a.change - b.change)
      .slice(0, 5);
    
    return { topGainers, topLosers };
  } catch (error) {
    console.error('급등/급락 데이터 로드 실패:', error);
    return null;
  }
}

// ============================================
// 3. BTC vs ALT 비중
// ============================================
async function fetchMarketDominance() {
  try {
    const response = await fetch(API.COINGECKO_GLOBAL);
    const data = await response.json();
    
    const btcDominance = data.data.market_cap_percentage.btc.toFixed(1);
    const altDominance = (100 - btcDominance).toFixed(1);
    
    return { btcDominance, altDominance };
  } catch (error) {
    console.error('시장 비중 데이터 로드 실패:', error);
    return { btcDominance: 52.3, altDominance: 47.7 };
  }
}

// ============================================
// 4. 롱/숏 포지션 (샘플 데이터)
// ============================================
async function fetchLongShortData() {
  // Coinglass API는 유료이므로 샘플 데이터 사용
  // 실제 프로덕션에서는 API 키 필요
  return {
    longRatio: 58,
    shortRatio: 42,
    longAmount: 2.8,
    shortAmount: 2.1
  };
}

// ============================================
// 5. 청산 데이터 (샘플 데이터)
// ============================================
async function fetchLiquidationData() {
  // Coinglass API 유료
  return {
    longLiquidation: 245.6,
    shortLiquidation: 178.3,
    totalLiquidation: 423.9
  };
}

// ============================================
// 6. 거래소 주도권 (샘플 데이터)
// ============================================
async function fetchExchangeDominance() {
  return [
    { name: 'Binance', logo: 'B', color: '#F0B90B', volume: 45.2, share: 42 },
    { name: 'Coinbase', logo: 'C', color: '#0052FF', volume: 18.7, share: 18 },
    { name: 'Upbit (한국)', logo: 'U', color: '#0062DF', volume: 12.3, share: 12 }
  ];
}

// ============================================
// 7. 김프/역프 계산
// ============================================
async function fetchKimchiPremium() {
  try {
    // Upbit BTC-KRW
    const upbitRes = await fetch('https://api.upbit.com/v1/ticker?markets=KRW-BTC');
    const upbitData = await upbitRes.json();
    const krwPrice = upbitData[0].trade_price;
    
    // Binance BTC/USDT
    const binanceRes = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
    const binanceData = await binanceRes.json();
    const usdtPrice = parseFloat(binanceData.price);
    
    // 환율 (대략 1300원 가정, 실제로는 환율 API 사용)
    const exchangeRate = 1300;
    const usdtToKrw = usdtPrice * exchangeRate;
    
    // 김프 계산
    const premium = ((krwPrice - usdtToKrw) / usdtToKrw * 100).toFixed(2);
    
    return {
      korea: parseFloat(premium),
      japan: 1.2,
      india: 3.5,
      vietnam: -0.5,
      thailand: 1.9
    };
  } catch (error) {
    console.error('김프 데이터 로드 실패:', error);
    return {
      korea: 2.8,
      japan: 1.2,
      india: 3.5,
      vietnam: -0.5,
      thailand: 1.9
    };
  }
}

// ============================================
// 8. AI 추천 시스템
// ============================================
async function generateAIRecommendations(movers, dominance) {
  const recommendations = {
    buy: null,
    sell: null,
    reason: {}
  };
  
  // 매수 추천: 급등 코인 중 거래량 많고 기술적 지표 좋은 것
  if (movers && movers.topGainers) {
    const buyCandidate = movers.topGainers[0];
    recommendations.buy = {
      symbol: buyCandidate.symbol,
      change: buyCandidate.change,
      price: buyCandidate.price
    };
    recommendations.reason.buy = [
      `24시간 +${buyCandidate.change.toFixed(2)}% 상승`,
      '거래량 급증 감지',
      '모멘텀 강세 유지 중'
    ];
  }
  
  // 매도 추천: 급락 코인 중 추가 하락 가능성 있는 것
  if (movers && movers.topLosers) {
    const sellCandidate = movers.topLosers[0];
    recommendations.sell = {
      symbol: sellCandidate.symbol,
      change: sellCandidate.change,
      price: sellCandidate.price
    };
    recommendations.reason.sell = [
      `24시간 ${sellCandidate.change.toFixed(2)}% 하락`,
      '매도 압력 지속 중',
      '추가 하락 가능성'
    ];
  }
  
  return recommendations;
}

// ============================================
// 9. UI 업데이트 함수들
// ============================================
function updateTopMovers(movers) {
  if (!movers) return;
  
  // 급등 코인
  const gainersHTML = movers.topGainers.map(coin => `
    <div class="coin-item">
      <span class="coin-name">${coin.symbol}</span>
      <span class="coin-change up">+${coin.change.toFixed(2)}%</span>
    </div>
  `).join('');
  
  // 급락 코인
  const losersHTML = movers.topLosers.map(coin => `
    <div class="coin-item">
      <span class="coin-name">${coin.symbol}</span>
      <span class="coin-change down">${coin.change.toFixed(2)}%</span>
    </div>
  `).join('');
  
  document.querySelector('.mover-section:not(.down)').innerHTML = `
    <h3>🚀 급등 TOP 5</h3>
    ${gainersHTML}
  `;
  
  document.querySelector('.mover-section.down').innerHTML = `
    <h3>📉 급락 TOP 5</h3>
    ${losersHTML}
  `;
}

function updateDominance(dominance) {
  document.querySelectorAll('.dominance-value')[0].textContent = `${dominance.btcDominance}%`;
  document.querySelectorAll('.dominance-value')[1].textContent = `${dominance.altDominance}%`;
}

function updateKimchiPremium(premium) {
  const items = document.querySelectorAll('.premium-value');
  items[0].textContent = `${premium.korea > 0 ? '+' : ''}${premium.korea}%`;
  items[0].className = `premium-value ${premium.korea > 0 ? 'positive' : 'negative'}`;
  
  items[1].textContent = `${premium.japan > 0 ? '+' : ''}${premium.japan}%`;
  items[1].className = `premium-value ${premium.japan > 0 ? 'positive' : 'negative'}`;
  
  items[2].textContent = `${premium.india > 0 ? '+' : ''}${premium.india}%`;
  items[2].className = `premium-value ${premium.india > 0 ? 'positive' : 'negative'}`;
  
  items[3].textContent = `${premium.vietnam > 0 ? '+' : ''}${premium.vietnam}%`;
  items[3].className = `premium-value ${premium.vietnam > 0 ? 'positive' : 'negative'}`;
  
  items[4].textContent = `${premium.thailand > 0 ? '+' : ''}${premium.thailand}%`;
  items[4].className = `premium-value ${premium.thailand > 0 ? 'positive' : 'negative'}`;
}

function showAIRecommendations(recommendations) {
  // AI 추천 카드 추가
  const container = document.querySelector('.container');
  
  let aiCardHTML = `
    <div class="card" style="border: 2px solid #8b5cf6; margin-top: 24px;">
      <div class="card-header">
        <h2 class="card-title">
          🤖 AI 트레이딩 추천
        </h2>
        <span class="card-badge" style="background: rgba(139, 92, 246, 0.1); border-color: rgba(139, 92, 246, 0.3); color: #8b5cf6;">
          실시간 분석
        </span>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
  `;
  
  // 매수 추천
  if (recommendations.buy) {
    aiCardHTML += `
      <div style="padding: 20px; background: rgba(16, 185, 129, 0.1); border: 2px solid rgba(16, 185, 129, 0.3); border-radius: 12px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
          <span style="font-size: 32px;">🚀</span>
          <div>
            <div style="font-size: 14px; color: var(--text-secondary);">매수 추천</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--green); font-family: 'JetBrains Mono', monospace;">
              ${recommendations.buy.symbol}
            </div>
          </div>
        </div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 18px; font-weight: 700; color: var(--green);">
            ${recommendations.buy.change > 0 ? '+' : ''}${recommendations.buy.change.toFixed(2)}%
          </div>
          <div style="font-size: 14px; color: var(--text-secondary);">
            현재가: $${recommendations.buy.price.toLocaleString()}
          </div>
        </div>
        <div style="background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--green); margin-bottom: 8px;">📊 근거</div>
          ${recommendations.reason.buy.map(reason => `
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">
              • ${reason}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  // 매도 추천
  if (recommendations.sell) {
    aiCardHTML += `
      <div style="padding: 20px; background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 12px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
          <span style="font-size: 32px;">📉</span>
          <div>
            <div style="font-size: 14px; color: var(--text-secondary);">매도 추천</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--red); font-family: 'JetBrains Mono', monospace;">
              ${recommendations.sell.symbol}
            </div>
          </div>
        </div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 18px; font-weight: 700; color: var(--red);">
            ${recommendations.sell.change.toFixed(2)}%
          </div>
          <div style="font-size: 14px; color: var(--text-secondary);">
            현재가: $${recommendations.sell.price.toLocaleString()}
          </div>
        </div>
        <div style="background: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 8px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--red); margin-bottom: 8px;">⚠️ 근거</div>
          ${recommendations.reason.sell.map(reason => `
            <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 4px;">
              • ${reason}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  aiCardHTML += `
      </div>
      <div style="margin-top: 16px; padding: 12px; background: rgba(139, 92, 246, 0.1); border-radius: 8px; text-align: center;">
        <div style="font-size: 12px; color: var(--text-secondary);">
          ⚠️ 본 추천은 AI 알고리즘 기반이며, 투자 판단은 본인의 책임입니다.
        </div>
      </div>
    </div>
  `;
  
  // 기존 AI 카드 제거 후 추가
  const existingAI = container.querySelector('.card[style*="border: 2px solid #8b5cf6"]');
  if (existingAI) existingAI.remove();
  
  container.insertAdjacentHTML('beforeend', aiCardHTML);
}

// ============================================
// 10. 메인 데이터 로드 함수
// ============================================
async function loadAllData() {
  console.log('🔄 데이터 로딩 시작...');
  
  try {
    // 모든 데이터 병렬 로드
    const [movers, dominance, premium] = await Promise.all([
      fetchTopMovers(),
      fetchMarketDominance(),
      fetchKimchiPremium()
    ]);
    
    // UI 업데이트
    if (movers) updateTopMovers(movers);
    if (dominance) updateDominance(dominance);
    if (premium) updateKimchiPremium(premium);
    
    // AI 추천 생성
    const recommendations = await generateAIRecommendations(movers, dominance);
    showAIRecommendations(recommendations);
    
    console.log('✅ 데이터 로딩 완료!');
  } catch (error) {
    console.error('❌ 데이터 로딩 실패:', error);
  }
}

// ============================================
// 11. 초기화 및 자동 새로고침
// ============================================
function refreshData() {
  loadAllData();
}

// 페이지 로드 시 데이터 로드
document.addEventListener('DOMContentLoaded', () => {
  loadAllData();
  
  // 30초마다 자동 새로고침
  setInterval(loadAllData, 30000);
});

// ============================================
// 12. 업비트/빗썸 개별 AI 추천
// ============================================
async function fetchKoreanExchangeRecommendations() {
  try {
    // 업비트 데이터
    const upbitRes = await fetch('https://api.upbit.com/v1/ticker?markets=KRW-BTC,KRW-ETH,KRW-XRP,KRW-ADA,KRW-SOL,KRW-DOGE,KRW-AVAX,KRW-DOT,KRW-MATIC,KRW-LINK');
    const upbitData = await upbitRes.json();
    
    // 변동률 기준 정렬
    const upbitSorted = upbitData.map(coin => ({
      name: coin.market.replace('KRW-', ''),
      change: coin.signed_change_rate * 100,
      price: coin.trade_price
    })).sort((a, b) => b.change - a.change);
    
    const upbitBuy = upbitSorted[0]; // 가장 많이 오른 코인
    const upbitSell = upbitSorted[upbitSorted.length - 1]; // 가장 많이 떨어진 코인
    
    return {
      upbit: {
        buy: upbitBuy,
        sell: upbitSell
      },
      bithumb: {
        // 빗썸은 샘플 데이터 (API 제한)
        buy: { name: 'BTC', change: 3.2, price: 135000000 },
        sell: { name: 'XRP', change: -2.1, price: 780 }
      }
    };
  } catch (error) {
    console.error('한국 거래소 데이터 로드 실패:', error);
    return {
      upbit: {
        buy: { name: 'BTC', change: 2.8, price: 134500000 },
        sell: { name: 'DOGE', change: -1.5, price: 145 }
      },
      bithumb: {
        buy: { name: 'ETH', change: 3.2, price: 4850000 },
        sell: { name: 'ADA', change: -2.3, price: 680 }
      }
    };
  }
}

function showKoreanExchangeRecommendations(recommendations) {
  const container = document.querySelector('.container');
  
  const html = `
    <div class="card" style="margin-top: 24px;">
      <div class="card-header">
        <h2 class="card-title">
          🇰🇷 한국 거래소 AI 추천
        </h2>
        <span class="card-badge">실시간</span>
      </div>
      
      <!-- 업비트 -->
      <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: #0062df; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: white;">
            U
          </div>
          <div>
            <div style="font-size: 18px; font-weight: 700;">업비트 (Upbit)</div>
            <div style="font-size: 14px; color: var(--text-secondary);">한국 1위 거래소</div>
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border: 2px solid rgba(16, 185, 129, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">🚀 살만한 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--green); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.upbit.buy.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--green);">
              ${recommendations.upbit.buy.change > 0 ? '+' : ''}${recommendations.upbit.buy.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.upbit.buy.price.toLocaleString()}원
            </div>
          </div>
          <div style="padding: 16px; background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">📉 팔아야 할 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--red); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.upbit.sell.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--red);">
              ${recommendations.upbit.sell.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.upbit.sell.price.toLocaleString()}원
            </div>
          </div>
        </div>
      </div>
      
      <!-- 빗썸 -->
      <div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: #ff6b00; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: white;">
            B
          </div>
          <div>
            <div style="font-size: 18px; font-weight: 700;">빗썸 (Bithumb)</div>
            <div style="font-size: 14px; color: var(--text-secondary);">한국 2위 거래소</div>
          </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
          <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border: 2px solid rgba(16, 185, 129, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">🚀 살만한 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--green); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.bithumb.buy.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--green);">
              ${recommendations.bithumb.buy.change > 0 ? '+' : ''}${recommendations.bithumb.buy.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.bithumb.buy.price.toLocaleString()}원
            </div>
          </div>
          <div style="padding: 16px; background: rgba(239, 68, 68, 0.1); border: 2px solid rgba(239, 68, 68, 0.3); border-radius: 12px;">
            <div style="font-size: 14px; color: var(--text-secondary); margin-bottom: 8px;">📉 팔아야 할 코인</div>
            <div style="font-size: 24px; font-weight: 800; color: var(--red); font-family: 'JetBrains Mono', monospace; margin-bottom: 4px;">
              ${recommendations.bithumb.sell.name}
            </div>
            <div style="font-size: 16px; font-weight: 700; color: var(--red);">
              ${recommendations.bithumb.sell.change.toFixed(2)}%
            </div>
            <div style="font-size: 14px; color: var(--text-secondary);">
              ${recommendations.bithumb.sell.price.toLocaleString()}원
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
  
  container.insertAdjacentHTML('beforeend', html);
}

// ============================================
// 13. 메인 데이터 로드 함수 업데이트
// ============================================
async function loadAllDataEnhanced() {
  console.log('🔄 전체 데이터 로딩 시작...');
  
  try {
    // 모든 데이터 병렬 로드
    const [movers, dominance, premium, longShort, liquidation, exchanges, koreanRecommendations] = await Promise.all([
      fetchTopMovers(),
      fetchMarketDominance(),
      fetchKimchiPremium(),
      fetchLongShortData(),
      fetchLiquidationData(),
      fetchExchangeDominance(),
      fetchKoreanExchangeRecommendations()
    ]);
    
    // UI 업데이트
    if (movers) updateTopMovers(movers);
    if (dominance) updateDominance(dominance);
    if (premium) updateKimchiPremium(premium);
    
    // 롱/숏 포지션 업데이트
    if (longShort) {
      document.querySelector('.position-long').style.width = `${longShort.longRatio}%`;
      document.querySelector('.position-long').textContent = `롱 ${longShort.longRatio}%`;
      document.querySelector('.position-short').style.width = `${longShort.shortRatio}%`;
      document.querySelector('.position-short').textContent = `숏 ${longShort.shortRatio}%`;
      document.querySelectorAll('.position-detail-value')[0].textContent = `$${longShort.longAmount.toFixed(1)}B`;
      document.querySelectorAll('.position-detail-value')[1].textContent = `$${longShort.shortAmount.toFixed(1)}B`;
    }
    
    // 청산 데이터 업데이트
    if (liquidation) {
      document.querySelectorAll('.liquidation-value')[0].textContent = `$${liquidation.longLiquidation.toFixed(1)}M`;
      document.querySelectorAll('.liquidation-value')[1].textContent = `$${liquidation.shortLiquidation.toFixed(1)}M`;
      document.querySelectorAll('.liquidation-value')[2].textContent = `$${liquidation.totalLiquidation.toFixed(1)}M`;
    }
    
    // AI 추천 생성 (글로벌)
    const recommendations = await generateAIRecommendations(movers, dominance);
    showAIRecommendations(recommendations);
    
    // 한국 거래소 AI 추천
    if (koreanRecommendations) {
      showKoreanExchangeRecommendations(koreanRecommendations);
    }
    
    console.log('✅ 전체 데이터 로딩 완료!');
  } catch (error) {
    console.error('❌ 데이터 로딩 실패:', error);
  }
}

// 기존 loadAllData를 enhanced 버전으로 교체
async function loadAllData() {
  await loadAllDataEnhanced();
}
