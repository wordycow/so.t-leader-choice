#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Signal Engine - Snapshot Scorer
Fetches all tickers every 5 minutes, calculates delta scores, maintains TOP 20
"""

import time
import pyupbit
import logging
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.constants import (
    MARKET_PREFIX, TOP_N_CANDIDATES, SCORE_WEIGHTS,
    SNAPSHOT_INTERVAL_SECONDS, EXCLUDE_MARKETS, MIN_LIQUIDITY_PERCENTILE
)
from shared.signal_schema import CandidateSnapshot

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/signal_engine/snapshot_scorer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SnapshotScorer')


class SnapshotScorer:
    """
    Fetches market snapshot every 5 minutes
    Calculates delta scores
    Maintains TOP 20 candidates
    """
    
    def __init__(self):
        self.previous_snapshot: Optional[Dict] = None
        self.current_snapshot: Optional[Dict] = None
        self.top_20_candidates: List[CandidateSnapshot] = []
        self.last_update_time: int = 0
        
        logger.info("SnapshotScorer initialized")
    
    def fetch_full_snapshot(self) -> Dict[str, Dict]:
        """
        Fetch all KRW market tickers in single API call
        Returns: {ticker: {price, volume, acc_trade_price, ...}}
        """
        try:
            tickers = pyupbit.get_tickers(fiat=MARKET_PREFIX)
            
            # Filter out excluded markets
            filtered_tickers = [
                t for t in tickers
                if not any(excluded in t for excluded in EXCLUDE_MARKETS)
            ]
            
            # Fetch current data for all tickers (single API call)
            snapshot = {}
            for ticker in filtered_tickers:
                try:
                    current = pyupbit.get_current_price(ticker)
                    if current is None:
                        continue
                    
                    # Get recent OHLCV for volume/acc_trade_price
                    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1)
                    if df is None or df.empty:
                        continue
                    
                    snapshot[ticker] = {
                        'trade_price': current,
                        'acc_trade_price': df['value'].iloc[-1] if 'value' in df.columns else 0,
                        'acc_trade_volume': df['volume'].iloc[-1],
                        'timestamp': int(datetime.now().timestamp())
                    }
                except Exception as e:
                    logger.warning(f"Error fetching {ticker}: {e}")
                    continue
            
            logger.info(f"Fetched snapshot: {len(snapshot)} tickers")
            return snapshot
            
        except Exception as e:
            logger.error(f"Failed to fetch snapshot: {e}")
            return {}
    
    def calculate_scores(self) -> List[CandidateSnapshot]:
        """
        Calculate delta scores between current and previous snapshots
        Returns sorted list of candidates
        """
        if self.previous_snapshot is None or self.current_snapshot is None:
            logger.warning("Cannot calculate scores without previous snapshot")
            return []
        
        candidates = []
        
        for ticker in self.current_snapshot.keys():
            if ticker not in self.previous_snapshot:
                continue  # New ticker, skip for now
            
            curr = self.current_snapshot[ticker]
            prev = self.previous_snapshot[ticker]
            
            # Calculate deltas
            delta_money = curr['acc_trade_price'] - prev['acc_trade_price']
            delta_volume = curr['acc_trade_volume'] - prev['acc_trade_volume']
            price_change_pct = (
                (curr['trade_price'] - prev['trade_price']) / prev['trade_price']
                if prev['trade_price'] > 0 else 0
            )
            
            # Rank-based scoring (normalized)
            candidates.append({
                'ticker': ticker,
                'delta_money': delta_money,
                'delta_volume': delta_volume,
                'price_change_pct': price_change_pct,
                'current_price': curr['trade_price']
            })
        
        # Rank by delta_money and delta_volume
        candidates.sort(key=lambda x: x['delta_money'], reverse=True)
        for i, c in enumerate(candidates):
            c['money_rank'] = i + 1
        
        candidates.sort(key=lambda x: x['delta_volume'], reverse=True)
        for i, c in enumerate(candidates):
            c['volume_rank'] = i + 1
        
        # Calculate final score
        n = len(candidates)
        for c in candidates:
            money_score = 1 - (c['money_rank'] / n)
            volume_score = 1 - (c['volume_rank'] / n)
            price_score = c['price_change_pct']
            
            c['score'] = (
                SCORE_WEIGHTS['delta_money'] * money_score +
                SCORE_WEIGHTS['delta_volume'] * volume_score +
                SCORE_WEIGHTS['price_change'] * price_score
            )
        
        # Sort by final score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Convert to CandidateSnapshot objects
        result = []
        for rank, c in enumerate(candidates[:TOP_N_CANDIDATES], 1):
            result.append(CandidateSnapshot(
                ticker=c['ticker'],
                rank=rank,
                score=c['score'],
                delta_money=c['delta_money'],
                delta_volume=c['delta_volume'],
                price_change_pct=c['price_change_pct'],
                current_price=c['current_price'],
                timestamp=int(datetime.now().timestamp())
            ))
        
        return result
    
    def update_top_20(self) -> List[CandidateSnapshot]:
        """
        Main update cycle: fetch snapshot → calculate scores → update TOP 20
        """
        logger.info("=== Starting snapshot update cycle ===")
        
        # Fetch new snapshot
        new_snapshot = self.fetch_full_snapshot()
        
        if not new_snapshot:
            logger.error("Empty snapshot, skipping update")
            return self.top_20_candidates
        
        # Move current to previous
        self.previous_snapshot = self.current_snapshot
        self.current_snapshot = new_snapshot
        
        # Calculate scores (needs both snapshots)
        if self.previous_snapshot is not None:
            new_top_20 = self.calculate_scores()
            
            # Log rotation
            if self.top_20_candidates:
                old_tickers = set(c.ticker for c in self.top_20_candidates)
                new_tickers = set(c.ticker for c in new_top_20)
                dropped = old_tickers - new_tickers
                added = new_tickers - old_tickers
                
                if dropped or added:
                    logger.info(f"TOP 20 rotation: Dropped {dropped}, Added {added}")
            
            self.top_20_candidates = new_top_20
            self.last_update_time = int(datetime.now().timestamp())
            
            # Log TOP 20
            logger.info("=== TOP 20 Candidates ===")
            for c in self.top_20_candidates[:5]:  # Log top 5
                logger.info(
                    f"#{c.rank} {c.ticker}: score={c.score:.4f} "
                    f"Δmoney={c.delta_money/1e6:.1f}M Δvol={c.delta_volume/1e6:.1f}M"
                )
        else:
            logger.info("First snapshot collected, waiting for next cycle")
        
        return self.top_20_candidates
    
    def run(self):
        """
        Main loop: update every SNAPSHOT_INTERVAL_SECONDS
        """
        logger.info(f"Starting SnapshotScorer loop (interval: {SNAPSHOT_INTERVAL_SECONDS}s)")
        
        while True:
            try:
                self.update_top_20()
                
                logger.info(f"Sleeping {SNAPSHOT_INTERVAL_SECONDS} seconds until next update...")
                time.sleep(SNAPSHOT_INTERVAL_SECONDS)
                
            except KeyboardInterrupt:
                logger.info("SnapshotScorer stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(60)  # Wait 1 min on error


if __name__ == '__main__':
    scorer = SnapshotScorer()
    scorer.run()
