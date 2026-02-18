#!/usr/bin/env python3
"""
IMEI Trading Integration v3.0

Connects IMEI with trading system to provide:
- Trading status summaries
- Portfolio analysis
- Entry/exit reason explanations
- BTC regime status
- Performance metrics
"""

import logging
import requests
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TradingIntegration:
    """
    Bridge between IMEI and Trading System
    """
    
    def __init__(self, dashboard_url: str = "http://localhost:5000"):
        self.dashboard_url = dashboard_url
    
    def get_system_status(self) -> Optional[Dict]:
        """
        Get overall system status
        
        Returns:
            System status dict or None if unavailable
        """
        try:
            response = requests.get(
                f"{self.dashboard_url}/api/kpis",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ System status unavailable: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Failed to get system status: {e}")
            return None
    
    def get_top20_candidates(self) -> Optional[list]:
        """
        Get TOP 20 candidates
        
        Returns:
            List of candidate dicts or None
        """
        try:
            response = requests.get(
                f"{self.dashboard_url}/api/top20",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            logger.error(f"❌ Failed to get TOP 20: {e}")
            return None
    
    def get_portfolio(self) -> Optional[list]:
        """
        Get current holdings
        
        Returns:
            List of position dicts or None
        """
        try:
            response = requests.get(
                f"{self.dashboard_url}/api/holdings",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            logger.error(f"❌ Failed to get portfolio: {e}")
            return None
    
    def get_btc_regime(self) -> Optional[Dict]:
        """
        Get BTC regime status
        
        Returns:
            Regime dict with status or None
        """
        # This would call a dedicated regime endpoint
        # For now, mock implementation
        return {
            "regime": "BULL",
            "btc_1h_trend": "bullish",
            "btc_4h_trend": "bullish",
            "full_downtrend": False,
            "last_updated": datetime.now().isoformat()
        }
    
    def summarize_status(self) -> str:
        """
        Generate human-readable status summary for IMEI
        
        Returns:
            Korean summary text
        """
        status = self.get_system_status()
        candidates = self.get_top20_candidates()
        portfolio = self.get_portfolio()
        regime = self.get_btc_regime()
        
        if not status:
            return "현재 트레이딩 시스템 상태를 확인할 수 없습니다. 시스템이 실행 중인지 확인해주세요."
        
        # Build summary
        summary_parts = []
        
        # Mode & equity
        mode = "실전" if status.get("real_trading_enabled", False) else "연습"
        equity = status.get("total_equity", 0)
        daily_pnl = status.get("daily_pnl", 0)
        daily_pnl_pct = status.get("daily_pnl_pct", 0)
        
        summary_parts.append(f"**현재 상태** ({mode} 모드)")
        summary_parts.append(f"- 총 자산: {equity:,.0f} KRW")
        summary_parts.append(f"- 오늘 손익: {daily_pnl:+,.0f} KRW ({daily_pnl_pct:+.2f}%)")
        
        # Holdings
        if portfolio:
            position_count = len(portfolio)
            summary_parts.append(f"\n**보유 포지션** ({position_count}개)")
            
            for pos in portfolio[:3]:  # Show top 3
                ticker = pos.get('ticker', 'N/A')
                strategy = pos.get('strategy', 'N/A')
                profit_pct = pos.get('profit_pct', 0)
                time_held = pos.get('time_held_min', 0)
                
                summary_parts.append(
                    f"- {ticker}: {profit_pct:+.2f}% "
                    f"(전략: {strategy}, {time_held:.0f}분)"
                )
        
        # TOP 20 candidates
        if candidates:
            summary_parts.append(f"\n**TOP 20 후보** (현재 {len(candidates)}개)")
            top3 = candidates[:3]
            for c in top3:
                ticker = c.get('ticker', 'N/A')
                score = c.get('score', 0)
                price_change = c.get('price_change_pct', 0)
                
                summary_parts.append(
                    f"- {ticker}: 점수 {score:.2f}, 가격 변화 {price_change:+.2f}%"
                )
        
        # BTC regime
        if regime:
            regime_status = regime.get('regime', 'UNKNOWN')
            full_down = regime.get('full_downtrend', False)
            
            summary_parts.append(f"\n**BTC 시장 상태**: {regime_status}")
            if full_down:
                summary_parts.append("⚠️ FULL_DOWNTREND - 신규 진입 차단됨")
        
        return "\n".join(summary_parts)
    
    def explain_entry(self, ticker: str, reason: str, strategy: str) -> str:
        """
        Explain why a trade entry was made
        
        Args:
            ticker: Coin ticker
            reason: Entry reason from executor
            strategy: Strategy name
        
        Returns:
            Human-readable explanation
        """
        explanations = {
            "RSI_BELOW_20": "RSI 지표가 20 미만으로 과매도 구간에 진입했습니다.",
            "VOLUME_SPIKE": "거래량이 급증하여 시장 관심이 증가했습니다.",
            "BOLLINGER_BREAK": "볼린저 밴드 하단을 돌파하여 반등 가능성이 있습니다.",
            "SUPPORT_LEVEL": "지지선 근처에서 가격이 안정되었습니다."
        }
        
        explanation = f"{ticker} 진입 이유:\n"
        explanation += f"전략: {strategy}\n\n"
        
        # Parse reason keywords
        for key, desc in explanations.items():
            if key in reason:
                explanation += f"- {desc}\n"
        
        return explanation
    
    def explain_exit(self, ticker: str, exit_reason: str, profit_pct: float) -> str:
        """
        Explain why a trade exit occurred
        
        Args:
            ticker: Coin ticker
            exit_reason: Exit reason from executor
            profit_pct: Final profit %
        
        Returns:
            Human-readable explanation
        """
        explanations = {
            "PARTIAL_3": "목표가 +3%에 도달하여 30%를 부분 매도했습니다.",
            "PARTIAL_5": "목표가 +5%에 도달하여 40%를 부분 매도했습니다.",
            "TRAIL_7": "+7% 도달 후 트레일링 스탑이 작동하여 청산했습니다.",
            "TIME_STOP": "6분 타임스탑이 작동하여 포지션을 정리했습니다.",
            "RECOVERY": "회복 모드에서 자동으로 청산되었습니다."
        }
        
        explanation = f"{ticker} 청산 이유:\n"
        explanation += f"최종 손익: {profit_pct:+.2f}%\n\n"
        
        desc = explanations.get(exit_reason, "알 수 없는 사유로 청산되었습니다.")
        explanation += f"{desc}\n"
        
        return explanation


if __name__ == "__main__":
    # Test trading integration
    logging.basicConfig(level=logging.INFO)
    
    integration = TradingIntegration()
    
    print("\n=== Test 1: Get system status ===")
    status = integration.get_system_status()
    if status:
        print(f"Equity: {status.get('total_equity', 'N/A')}")
    else:
        print("Status unavailable")
    
    print("\n=== Test 2: Summarize status ===")
    summary = integration.summarize_status()
    print(summary)
    
    print("\n=== Test 3: Explain entry ===")
    entry_explanation = integration.explain_entry(
        "KRW-BTC",
        "RSI_BELOW_20_VOLUME_SPIKE",
        "ULTRA_SCALP"
    )
    print(entry_explanation)
    
    print("\n=== Test 4: Explain exit ===")
    exit_explanation = integration.explain_exit(
        "KRW-DOGE",
        "PARTIAL_3",
        +3.2
    )
    print(exit_explanation)
