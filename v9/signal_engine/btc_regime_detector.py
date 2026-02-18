#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Signal Engine - BTC Regime Detector
Detects FULL_DOWNTREND condition to disable entry strategies
"""

import time
import pyupbit
import pandas as pd
import logging
from typing import Optional
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.constants import (
    BTC_TICKER, BTC_1H_SMA_SHORT, BTC_1H_SMA_LONG,
    BTC_4H_SMA_SHORT, BTC_4H_SMA_LONG,
    STABLECOIN_SPIKE_THRESHOLD, DOMINANCE_SPIKE_THRESHOLD,
    RegimeState
)
from shared.signal_schema import SignalPayload

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/signal_engine/btc_regime.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('BTCRegimeDetector')


class BTCRegimeDetector:
    """
    Monitors BTC trends and market conditions
    Emits FULL_DOWNTREND flag when:
    - BTC 1H bearish AND
    - BTC 4H bearish AND
    - (Stablecoin spike OR Dominance spike)
    """
    
    def __init__(self):
        self.current_regime: str = RegimeState.NORMAL
        self.last_regime_change: int = 0
        self.btc_1h_trend: str = "UNKNOWN"
        self.btc_4h_trend: str = "UNKNOWN"
        self.stablecoin_spike: bool = False
        self.dominance_spike: bool = False
        
        logger.info("BTCRegimeDetector initialized")
    
    def get_btc_trend(self, interval: str, count: int = 100) -> str:
        """
        Calculate BTC trend using SMA crossover
        Returns: BULLISH, BEARISH, or NEUTRAL
        """
        try:
            df = pyupbit.get_ohlcv(BTC_TICKER, interval=interval, count=count)
            if df is None or df.empty:
                logger.warning(f"Failed to fetch BTC {interval} data")
                return "UNKNOWN"
            
            # Calculate SMAs
            df['sma_short'] = df['close'].rolling(
                window=BTC_1H_SMA_SHORT if '60' in interval else BTC_4H_SMA_SHORT
            ).mean()
            df['sma_long'] = df['close'].rolling(
                window=BTC_1H_SMA_LONG if '60' in interval else BTC_4H_SMA_LONG
            ).mean()
            
            # Latest values
            latest = df.iloc[-1]
            short = latest['sma_short']
            long = latest['sma_long']
            
            if pd.isna(short) or pd.isna(long):
                return "UNKNOWN"
            
            # Trend determination
            if short > long:
                trend = "BULLISH"
            elif short < long:
                trend = "BEARISH"
            else:
                trend = "NEUTRAL"
            
            logger.debug(
                f"BTC {interval} trend: {trend} "
                f"(SMA{BTC_1H_SMA_SHORT if '60' in interval else BTC_4H_SMA_SHORT}={short:.0f}, "
                f"SMA{BTC_1H_SMA_LONG if '60' in interval else BTC_4H_SMA_LONG}={long:.0f})"
            )
            
            return trend
            
        except Exception as e:
            logger.error(f"Error calculating BTC trend {interval}: {e}")
            return "UNKNOWN"
    
    def check_stablecoin_spike(self) -> bool:
        """
        Check if stablecoin supply spiked (simplified version)
        In production, would query on-chain data or APIs
        For now, use BTC volume as proxy
        """
        try:
            # Simplified: Check if BTC 1H volume increased significantly
            df = pyupbit.get_ohlcv(BTC_TICKER, interval="minute60", count=3)
            if df is None or df.empty or len(df) < 2:
                return False
            
            current_volume = df['volume'].iloc[-1]
            previous_volume = df['volume'].iloc[-2]
            
            if previous_volume == 0:
                return False
            
            volume_change = (current_volume - previous_volume) / previous_volume
            
            spike = volume_change > STABLECOIN_SPIKE_THRESHOLD
            
            if spike:
                logger.info(f"Stablecoin spike detected: volume change {volume_change:.2%}")
            
            return spike
            
        except Exception as e:
            logger.error(f"Error checking stablecoin spike: {e}")
            return False
    
    def check_dominance_spike(self) -> bool:
        """
        Check if BTC dominance spiked
        Simplified: Compare BTC vs. altcoin performance
        In production, would use actual dominance data
        """
        try:
            # Simplified: Check if BTC outperformed ETH significantly
            btc_df = pyupbit.get_ohlcv(BTC_TICKER, interval="minute60", count=2)
            eth_df = pyupbit.get_ohlcv("KRW-ETH", interval="minute60", count=2)
            
            if btc_df is None or eth_df is None or btc_df.empty or eth_df.empty:
                return False
            
            btc_change = (btc_df['close'].iloc[-1] - btc_df['close'].iloc[0]) / btc_df['close'].iloc[0]
            eth_change = (eth_df['close'].iloc[-1] - eth_df['close'].iloc[0]) / eth_df['close'].iloc[0]
            
            dominance_change = btc_change - eth_change
            
            spike = dominance_change > DOMINANCE_SPIKE_THRESHOLD
            
            if spike:
                logger.info(
                    f"Dominance spike detected: BTC {btc_change:.2%} vs ETH {eth_change:.2%}"
                )
            
            return spike
            
        except Exception as e:
            logger.error(f"Error checking dominance spike: {e}")
            return False
    
    def detect_regime(self) -> str:
        """
        Main regime detection logic
        Returns: NORMAL or FULL_DOWNTREND
        """
        logger.info("=== BTC Regime Detection ===")
        
        # Get trends
        self.btc_1h_trend = self.get_btc_trend(interval="minute60")
        self.btc_4h_trend = self.get_btc_trend(interval="minute240")
        
        # Check spikes
        self.stablecoin_spike = self.check_stablecoin_spike()
        self.dominance_spike = self.check_dominance_spike()
        
        # Log conditions
        logger.info(f"BTC 1H trend: {self.btc_1h_trend}")
        logger.info(f"BTC 4H trend: {self.btc_4h_trend}")
        logger.info(f"Stablecoin spike: {self.stablecoin_spike}")
        logger.info(f"Dominance spike: {self.dominance_spike}")
        
        # Determine regime
        if (
            self.btc_1h_trend == "BEARISH" and
            self.btc_4h_trend == "BEARISH" and
            (self.stablecoin_spike or self.dominance_spike)
        ):
            new_regime = RegimeState.FULL_DOWNTREND
        else:
            new_regime = RegimeState.NORMAL
        
        # Check for regime change
        if new_regime != self.current_regime:
            logger.warning(
                f"🚨 REGIME CHANGE: {self.current_regime} → {new_regime}"
            )
            
            # Create regime change signal
            signal = SignalPayload.create_regime_change_signal(
                old_regime=self.current_regime,
                new_regime=new_regime
            )
            
            self.current_regime = new_regime
            self.last_regime_change = int(datetime.now().timestamp())
            
            return new_regime, signal
        
        logger.info(f"Current regime: {self.current_regime} (unchanged)")
        return self.current_regime, None
    
    def run(self, interval_seconds: int = 300):
        """
        Main loop: check regime every interval
        """
        logger.info(f"Starting BTCRegimeDetector loop (interval: {interval_seconds}s)")
        
        while True:
            try:
                regime, signal = self.detect_regime()
                
                # In production, emit signal via WebSocket here
                if signal:
                    logger.info(f"Regime change signal: {signal.to_dict()}")
                
                logger.info(f"Sleeping {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("BTCRegimeDetector stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(60)


if __name__ == '__main__':
    detector = BTCRegimeDetector()
    detector.run()
