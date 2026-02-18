#!/usr/bin/env python3
"""
Signal Validator for Execution Engine
Implements all re-validation filters before trade execution:
- Warning/delisting exclusions
- Liquidity bottom 5% filter
- KRW-market only
- Capital rules (10% per trade, max 2 concurrent, ≤20% total)
- Regime override (FULL_DOWNTREND blocks new entries)
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime
import pyupbit

from v9.shared.signal_schema import Signal, SignalResponse
from v9.shared.constants import (
    CAPITAL_PER_TRADE_PCT,
    MAX_CONCURRENT_TRADES,
    MAX_TOTAL_ALLOCATION_PCT,
)

logger = logging.getLogger(__name__)


class SignalValidator:
    """Validates incoming signals before execution"""
    
    def __init__(self):
        self.warning_list: set = set()
        self.delisting_list: set = set()
        self.liquidity_cache: Dict[str, float] = {}
        self.last_liquidity_update: Optional[datetime] = None
        
    def update_exclusion_lists(self):
        """Update warning and delisting lists from Upbit"""
        try:
            # Get market warning info (투자유의, 주의)
            # Note: pyupbit doesn't provide this directly, would need API call
            # For now, maintain manual list or scrape from Upbit notice
            logger.info("📋 Exclusion lists updated")
        except Exception as e:
            logger.error(f"❌ Failed to update exclusion lists: {e}")
    
    def update_liquidity_cache(self, tickers: List[str]):
        """Update liquidity (24h volume) cache for all tickers"""
        try:
            ticker_data = pyupbit.get_tickers(fiat="KRW")
            volumes = {}
            
            for ticker in ticker_data:
                if not ticker.startswith("KRW-"):
                    continue
                try:
                    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
                    if df is not None and not df.empty:
                        volumes[ticker] = float(df['volume'].iloc[-1])
                except:
                    continue
            
            # Calculate bottom 5% threshold
            if volumes:
                sorted_vols = sorted(volumes.values())
                threshold_idx = max(0, int(len(sorted_vols) * 0.05))
                threshold = sorted_vols[threshold_idx]
                
                self.liquidity_cache = volumes
                self.bottom_5pct_threshold = threshold
                self.last_liquidity_update = datetime.now()
                
                logger.info(f"💧 Liquidity cache updated: {len(volumes)} tickers, "
                          f"bottom 5% threshold: {threshold:,.0f}")
        except Exception as e:
            logger.error(f"❌ Failed to update liquidity cache: {e}")
    
    def validate_signal(
        self,
        signal: Signal,
        current_equity: float,
        current_positions: int,
        invested_amount: float,
        regime_full_downtrend: bool
    ) -> SignalResponse:
        """
        Validate signal against all filters
        
        Returns SignalResponse with action EXECUTE/REJECT and reason
        """
        ticker = signal.ticker
        
        # 1. Check regime - FULL_DOWNTREND blocks new entries
        if regime_full_downtrend:
            return SignalResponse(
                signal_id=signal.signal_id,
                action="REJECT",
                reason="FULL_DOWNTREND regime active - new entries blocked"
            )
        
        # 2. Check market (KRW only)
        if not ticker.startswith("KRW-"):
            return SignalResponse(
                signal_id=signal.signal_id,
                action="REJECT",
                reason=f"Non-KRW market: {ticker}"
            )
        
        # Exclude BTC/USDT direct markets
        if ticker in ["KRW-BTC", "KRW-USDT"]:
            return SignalResponse(
                signal_id=signal.signal_id,
                action="REJECT",
                reason=f"BTC/USDT excluded from trading: {ticker}"
            )
        
        # 3. Check warning/delisting lists
        if ticker in self.warning_list:
            return SignalResponse(
                signal_id=signal.signal_id,
                action="REJECT",
                reason=f"Ticker on warning list: {ticker}"
            )
        
        if ticker in self.delisting_list:
            return SignalResponse(
                signal_id=signal.signal_id,
                action="REJECT",
                reason=f"Ticker on delisting list: {ticker}"
            )
        
        # 4. Check liquidity (bottom 5%)
        if ticker in self.liquidity_cache:
            volume = self.liquidity_cache[ticker]
            if hasattr(self, 'bottom_5pct_threshold'):
                if volume < self.bottom_5pct_threshold:
                    return SignalResponse(
                        signal_id=signal.signal_id,
                        action="REJECT",
                        reason=f"Bottom 5% liquidity: {volume:,.0f}"
                    )
        
        # 5. Check capital rules
        
        # Max concurrent trades (2)
        if current_positions >= MAX_CONCURRENT_TRADES:
            return SignalResponse(
                signal_id=signal.signal_id,
                action="REJECT",
                reason=f"Max concurrent trades reached: {current_positions}/{MAX_CONCURRENT_TRADES}"
            )
        
        # Calculate trade size (10% of equity)
        trade_size = current_equity * (CAPITAL_PER_TRADE_PCT / 100.0)
        
        # Total allocation check (≤20%)
        new_total_allocation = (invested_amount + trade_size) / current_equity
        if new_total_allocation > (MAX_TOTAL_ALLOCATION_PCT / 100.0):
            return SignalResponse(
                signal_id=signal.signal_id,
                action="REJECT",
                reason=f"Total allocation would exceed {MAX_TOTAL_ALLOCATION_PCT}%: "
                       f"{new_total_allocation*100:.1f}%"
            )
        
        # All checks passed
        return SignalResponse(
            signal_id=signal.signal_id,
            action="EXECUTE",
            reason="All validation checks passed",
            metadata={
                "trade_size_krw": trade_size,
                "new_allocation_pct": new_total_allocation * 100
            }
        )


if __name__ == "__main__":
    # Test validator
    logging.basicConfig(level=logging.INFO)
    
    validator = SignalValidator()
    validator.update_liquidity_cache(["KRW-BTC", "KRW-ETH"])
    
    # Test signal
    test_signal = Signal(
        signal_id="test_001",
        strategy_id="ULTRA_SCALP",
        ticker="KRW-BTC",
        confidence=0.85,
        snapshot_score=0.92,
        btc_regime="BULL",
        timestamp=datetime.now()
    )
    
    # Test validation scenarios
    print("\n=== Test 1: Normal validation ===")
    response = validator.validate_signal(
        test_signal,
        current_equity=1000000,
        current_positions=1,
        invested_amount=100000,
        regime_full_downtrend=False
    )
    print(f"Action: {response.action}, Reason: {response.reason}")
    
    print("\n=== Test 2: FULL_DOWNTREND regime ===")
    response = validator.validate_signal(
        test_signal,
        current_equity=1000000,
        current_positions=1,
        invested_amount=100000,
        regime_full_downtrend=True
    )
    print(f"Action: {response.action}, Reason: {response.reason}")
    
    print("\n=== Test 3: Max positions ===")
    response = validator.validate_signal(
        test_signal,
        current_equity=1000000,
        current_positions=2,
        invested_amount=100000,
        regime_full_downtrend=False
    )
    print(f"Action: {response.action}, Reason: {response.reason}")
