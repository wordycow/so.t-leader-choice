#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Signal Engine - Deep Hunter Monitor
Monitors 1-hour candles for extreme oversold conditions with staged entry
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

from shared.constants import DEEP_HUNTER, RegimeState
from shared.signal_schema import SignalPayload, CandidateSnapshot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/signal_engine/deep_hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DeepHunterMonitor')


class DeepHunterMonitor:
    """
    Monitors TOP 20 candidates for Deep Hunter entry signals
    
    Entry Conditions:
    - 1H extreme oversold (RSI < 15)
    - Lower Bollinger break (1H)
    - NOT during BTC full collapse
    - Staged entry approach
    """
    
    def __init__(self, top_20_candidates: List[CandidateSnapshot], current_regime: str):
        self.top_20_candidates = top_20_candidates
        self.current_regime = current_regime
        self.active_hunts: Dict[str, Dict] = {}  # ticker -> hunt state
        self.cooldown_seconds = 3600  # 1 hour cooldown
        
        logger.info("DeepHunterMonitor initialized")
    
    def calculate_bollinger_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands (20, 2) on 1H"""
        df['sma'] = df['close'].rolling(window=DEEP_HUNTER['bb_period']).mean()
        df['std'] = df['close'].rolling(window=DEEP_HUNTER['bb_period']).std()
        df['bb_upper'] = df['sma'] + (DEEP_HUNTER['bb_std'] * df['std'])
        df['bb_lower'] = df['sma'] - (DEEP_HUNTER['bb_std'] * df['std'])
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate RSI"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        return df
    
    def detect_drop_slowdown(self, df: pd.DataFrame) -> bool:
        """
        Detect if price drop is slowing down
        Compare last 3 candles: if volatility decreasing, slowdown detected
        """
        if len(df) < 5:
            return False
        
        last_3 = df.tail(3)
        volatility = (last_3['high'] - last_3['low']).values
        
        # Decreasing volatility = slowdown
        return volatility[2] < volatility[1] < volatility[0]
    
    def is_btc_full_collapse(self) -> bool:
        """
        Check if BTC is in full collapse (extreme drop)
        Returns True if BTC dropped >5% in last 4 hours
        """
        try:
            df = pyupbit.get_ohlcv("KRW-BTC", interval="minute240", count=2)
            if df is None or df.empty or len(df) < 2:
                return False
            
            start_price = df['close'].iloc[0]
            current_price = df['close'].iloc[-1]
            
            drop_pct = ((current_price - start_price) / start_price) * 100
            
            is_collapse = drop_pct < -5.0
            
            if is_collapse:
                logger.warning(f"BTC full collapse detected: {drop_pct:.2f}%")
            
            return is_collapse
            
        except Exception as e:
            logger.error(f"Error checking BTC collapse: {e}")
            return False
    
    def check_initial_entry(self, ticker: str) -> Optional[SignalPayload]:
        """
        Check if ticker meets Deep Hunter initial entry (Stage 1: 5%)
        """
        try:
            # Fetch 1-hour candles
            df = pyupbit.get_ohlcv(ticker, interval="minute60", count=50)
            if df is None or df.empty or len(df) < DEEP_HUNTER['bb_period']:
                return None
            
            # Calculate indicators
            df = self.calculate_bollinger_bands(df)
            df = self.calculate_rsi(df, period=DEEP_HUNTER['rsi_period'])
            
            # Get latest values
            latest = df.iloc[-1]
            close = latest['close']
            bb_lower = latest['bb_lower']
            rsi = latest['rsi']
            
            if pd.isna(bb_lower) or pd.isna(rsi):
                return None
            
            # Check conditions
            # 1. RSI < 15 (extreme oversold)
            extreme_oversold = rsi < DEEP_HUNTER['rsi_threshold']
            
            # 2. Close below lower Bollinger
            below_bb = close < bb_lower
            
            # 3. NOT during BTC full collapse
            not_btc_collapse = not self.is_btc_full_collapse()
            
            if extreme_oversold and below_bb and not_btc_collapse:
                logger.info(
                    f"✅ Deep Hunter Stage 1 signal: {ticker} "
                    f"(RSI={rsi:.1f}, BB_lower={bb_lower:.0f}, Close={close:.0f})"
                )
                
                # Get snapshot score
                snapshot_score = 0.0
                for candidate in self.top_20_candidates:
                    if candidate.ticker == ticker:
                        snapshot_score = candidate.score
                        break
                
                # Create signal
                signal = SignalPayload.create_entry_signal(
                    strategy_id=DEEP_HUNTER['id'],
                    ticker=ticker,
                    confidence=0.75,  # Initial stage, lower confidence
                    snapshot_score=snapshot_score,
                    btc_regime=self.current_regime,
                    indicators={
                        'rsi_14': float(rsi),
                        'bb_lower': float(bb_lower),
                        'close': float(close),
                        'stage': 1,
                        'allocation_pct': DEEP_HUNTER['initial_capital_pct']
                    }
                )
                
                # Track hunt
                self.active_hunts[ticker] = {
                    'entry_price': close,
                    'entry_time': int(datetime.now().timestamp()),
                    'stage': 1
                }
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking {ticker}: {e}")
            return None
    
    def check_averaging_opportunity(self, ticker: str) -> Optional[SignalPayload]:
        """
        Check if existing hunt can be averaged down (Stages 2-3)
        """
        if ticker not in self.active_hunts:
            return None
        
        hunt = self.active_hunts[ticker]
        
        if hunt['stage'] >= 3:  # Max 3 stages
            return None
        
        try:
            # Fetch current data
            df = pyupbit.get_ohlcv(ticker, interval="minute60", count=5)
            if df is None or df.empty:
                return None
            
            current_price = df['close'].iloc[-1]
            entry_price = hunt['entry_price']
            
            # Price dropped further (e.g., -5% more)
            drop_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Check if drop slowdown detected
            slowdown = self.detect_drop_slowdown(df)
            
            if drop_pct < -5.0 and slowdown:
                logger.info(
                    f"✅ Deep Hunter Stage {hunt['stage']+1} averaging: {ticker} "
                    f"(Drop={drop_pct:.2f}%, Slowdown detected)"
                )
                
                # Create averaging signal
                signal = SignalPayload.create_entry_signal(
                    strategy_id=DEEP_HUNTER['id'],
                    ticker=ticker,
                    confidence=0.80 + (hunt['stage'] * 0.05),  # Increase confidence per stage
                    snapshot_score=0.0,
                    btc_regime=self.current_regime,
                    indicators={
                        'stage': hunt['stage'] + 1,
                        'drop_from_entry': drop_pct,
                        'allocation_pct': DEEP_HUNTER['initial_capital_pct']
                    }
                )
                
                # Update hunt stage
                hunt['stage'] += 1
                
                return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking averaging for {ticker}: {e}")
            return None
    
    def scan_all_candidates(self) -> List[SignalPayload]:
        """
        Scan all TOP 20 candidates for Deep Hunter signals
        """
        # Check regime
        if self.current_regime == RegimeState.FULL_DOWNTREND:
            logger.warning("FULL_DOWNTREND active - Deep Hunter disabled")
            return []
        
        signals = []
        
        logger.info(f"Scanning {len(self.top_20_candidates)} candidates for Deep Hunter...")
        
        # Check for new initial entries
        for candidate in self.top_20_candidates:
            if candidate.ticker not in self.active_hunts:
                signal = self.check_initial_entry(candidate.ticker)
                if signal:
                    signals.append(signal)
        
        # Check for averaging opportunities on active hunts
        for ticker in list(self.active_hunts.keys()):
            signal = self.check_averaging_opportunity(ticker)
            if signal:
                signals.append(signal)
        
        if signals:
            logger.info(f"Generated {len(signals)} Deep Hunter signals")
        
        return signals
    
    def update_state(self, top_20: List[CandidateSnapshot], regime: str):
        """Update monitoring state"""
        self.top_20_candidates = top_20
        self.current_regime = regime
    
    def run(self, interval_seconds: int = 3600):
        """
        Main loop: scan every hour (1H strategy)
        """
        logger.info(f"Starting DeepHunterMonitor loop (interval: {interval_seconds}s)")
        
        while True:
            try:
                signals = self.scan_all_candidates()
                
                # In production, emit signals via WebSocket here
                for signal in signals:
                    logger.info(
                        f"Signal: {signal.ticker} Stage {signal.indicators.get('stage', 1)}"
                    )
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("DeepHunterMonitor stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(300)


if __name__ == '__main__':
    # Test mode
    from snapshot_scorer import SnapshotScorer
    
    scorer = SnapshotScorer()
    scorer.update_top_20()
    
    monitor = DeepHunterMonitor(
        top_20_candidates=scorer.top_20_candidates,
        current_regime=RegimeState.NORMAL
    )
    monitor.run()
