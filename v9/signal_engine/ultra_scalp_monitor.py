#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Signal Engine - Ultra Scalp Monitor
Monitors 1-minute candles for Ultra Scalp entry conditions
"""

import time
import pyupbit
import pandas as pd
import logging
from typing import List, Optional, Dict
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.constants import ULTRA_SCALP, RegimeState
from shared.signal_schema import SignalPayload, CandidateSnapshot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/signal_engine/ultra_scalp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UltraScalpMonitor')


class UltraScalpMonitor:
    """
    Monitors TOP 20 candidates for Ultra Scalp entry signals
    
    Entry Conditions:
    - 1m close below lower Bollinger (20, 2)
    - RSI(14) < 20
    - 3 consecutive red candles
    - Volume spike > 2x avg
    - FULL_DOWNTREND = False
    """
    
    def __init__(self, top_20_candidates: List[CandidateSnapshot], current_regime: str):
        self.top_20_candidates = top_20_candidates
        self.current_regime = current_regime
        self.last_signals: Dict[str, int] = {}  # ticker -> timestamp (cooldown)
        self.cooldown_seconds = 300  # 5 min cooldown per ticker
        
        logger.info("UltraScalpMonitor initialized")
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands (20, 2)"""
        df['sma'] = df['close'].rolling(window=ULTRA_SCALP['bb_period']).mean()
        df['std'] = df['close'].rolling(window=ULTRA_SCALP['bb_period']).std()
        df['bb_upper'] = df['sma'] + (ULTRA_SCALP['bb_std'] * df['std'])
        df['bb_lower'] = df['sma'] - (ULTRA_SCALP['bb_std'] * df['std'])
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def check_consecutive_red_candles(self, df: pd.DataFrame, count: int = 3) -> bool:
        """Check if last N candles are red (close < open)"""
        if len(df) < count:
            return False
        
        last_n = df.tail(count)
        return all(last_n['close'] < last_n['open'])
    
    def check_volume_spike(self, df: pd.DataFrame) -> bool:
        """Check if current volume > 2x average"""
        if len(df) < 20:
            return False
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].iloc[-20:-1].mean()
        
        if avg_volume == 0:
            return False
        
        spike_ratio = current_volume / avg_volume
        return spike_ratio >= ULTRA_SCALP['volume_spike_multiplier']
    
    def check_entry_conditions(self, ticker: str) -> Optional[SignalPayload]:
        """
        Check if ticker meets Ultra Scalp entry conditions
        Returns SignalPayload if conditions met, None otherwise
        """
        try:
            # Check cooldown
            now = int(datetime.now().timestamp())
            if ticker in self.last_signals:
                if (now - self.last_signals[ticker]) < self.cooldown_seconds:
                    return None
            
            # Fetch 1-minute candles
            df = pyupbit.get_ohlcv(ticker, interval="minute1", count=50)
            if df is None or df.empty or len(df) < ULTRA_SCALP['bb_period']:
                return None
            
            # Calculate indicators
            df = self.calculate_bollinger_bands(df)
            df = self.calculate_rsi(df, period=ULTRA_SCALP['rsi_period'])
            
            # Get latest values
            latest = df.iloc[-1]
            close = latest['close']
            bb_lower = latest['bb_lower']
            rsi = latest['rsi']
            
            # Check conditions
            if pd.isna(bb_lower) or pd.isna(rsi):
                return None
            
            # 1. Close below lower Bollinger
            below_bb = close < bb_lower
            
            # 2. RSI < 20
            rsi_oversold = rsi < ULTRA_SCALP['rsi_threshold']
            
            # 3. 3 consecutive red candles
            red_candles = self.check_consecutive_red_candles(df, ULTRA_SCALP['consecutive_red_candles'])
            
            # 4. Volume spike
            volume_spike = self.check_volume_spike(df)
            
            # All conditions must be true
            if below_bb and rsi_oversold and red_candles and volume_spike:
                logger.info(
                    f"✅ Ultra Scalp signal: {ticker} "
                    f"(RSI={rsi:.1f}, BB_lower={bb_lower:.0f}, Close={close:.0f})"
                )
                
                # Get snapshot score from TOP 20
                snapshot_score = 0.0
                for candidate in self.top_20_candidates:
                    if candidate.ticker == ticker:
                        snapshot_score = candidate.score
                        break
                
                # Create signal
                signal = SignalPayload.create_entry_signal(
                    strategy_id=ULTRA_SCALP['id'],
                    ticker=ticker,
                    confidence=0.85,  # Base confidence
                    snapshot_score=snapshot_score,
                    btc_regime=self.current_regime,
                    indicators={
                        'rsi_14': float(rsi),
                        'bb_lower': float(bb_lower),
                        'close': float(close),
                        'volume_spike_ratio': float(latest['volume'] / df['volume'].iloc[-20:-1].mean())
                    }
                )
                
                # Update cooldown
                self.last_signals[ticker] = now
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking {ticker}: {e}")
            return None
    
    def scan_all_candidates(self) -> List[SignalPayload]:
        """
        Scan all TOP 20 candidates for entry signals
        """
        # Check regime
        if self.current_regime == RegimeState.FULL_DOWNTREND:
            logger.warning("FULL_DOWNTREND active - Ultra Scalp disabled")
            return []
        
        signals = []
        
        logger.info(f"Scanning {len(self.top_20_candidates)} candidates for Ultra Scalp...")
        
        for candidate in self.top_20_candidates:
            signal = self.check_entry_conditions(candidate.ticker)
            if signal:
                signals.append(signal)
        
        if signals:
            logger.info(f"Generated {len(signals)} Ultra Scalp signals")
        else:
            logger.debug("No Ultra Scalp signals this cycle")
        
        return signals
    
    def update_state(self, top_20: List[CandidateSnapshot], regime: str):
        """Update monitoring state"""
        self.top_20_candidates = top_20
        self.current_regime = regime
    
    def run(self, interval_seconds: int = 60):
        """
        Main loop: scan every minute
        """
        logger.info(f"Starting UltraScalpMonitor loop (interval: {interval_seconds}s)")
        
        while True:
            try:
                signals = self.scan_all_candidates()
                
                # In production, emit signals via WebSocket here
                for signal in signals:
                    logger.info(f"Signal: {signal.ticker} @ {signal.indicators['close']:.0f}")
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("UltraScalpMonitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(60)


if __name__ == '__main__':
    # Test mode - requires TOP 20 from snapshot_scorer
    from snapshot_scorer import SnapshotScorer
    
    scorer = SnapshotScorer()
    scorer.update_top_20()  # Get initial TOP 20
    
    monitor = UltraScalpMonitor(
        top_20_candidates=scorer.top_20_candidates,
        current_regime=RegimeState.NORMAL
    )
    monitor.run()
