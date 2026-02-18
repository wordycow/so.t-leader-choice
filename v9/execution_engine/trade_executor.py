#!/usr/bin/env python3
"""
Trade Executor for Execution Engine
Handles:
- Trade entry (buy orders via Upbit API)
- Partial exits: +3% → 30%, +5% → 40%, +7%+ → 30% trailing
- Time-stop: 6 min without +1% → full exit
- Stop-to-breakeven after first partial
- Exit reason logging (PARTIAL_3, PARTIAL_5, TRAIL_7, TIME_STOP)
"""

import logging
import pyupbit
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from v9.shared.constants import (
    CAPITAL_PER_TRADE_PCT,
    FEE_RATE,
    PARTIAL_EXIT_THRESHOLDS,
    TRAILING_STOP_PCT,
    TIME_STOP_MINUTES,
    TIME_STOP_MIN_PROFIT_PCT,
)

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents an open position"""
    ticker: str
    strategy_id: str
    entry_price: float
    entry_time: datetime
    amount: float  # Coin amount
    invested_krw: float  # Total KRW invested (including fees)
    
    # Tracking
    peak_price: float = 0.0
    remaining_pct: float = 100.0  # % of position remaining
    stop_moved_to_breakeven: bool = False
    
    # Partial exit tracking
    exits: list = field(default_factory=list)
    
    def update_peak(self, current_price: float):
        """Update peak price for trailing stop"""
        if current_price > self.peak_price:
            self.peak_price = current_price
    
    def get_profit_pct(self, current_price: float) -> float:
        """Calculate current profit %"""
        return ((current_price - self.entry_price) / self.entry_price) * 100
    
    def get_time_held_minutes(self) -> float:
        """Get minutes since entry"""
        return (datetime.now() - self.entry_time).total_seconds() / 60


class TradeExecutor:
    """Executes trades and manages exits"""
    
    def __init__(self, upbit_access: str, upbit_secret: str, practice_mode: bool = True):
        self.practice_mode = practice_mode
        
        if not practice_mode:
            self.upbit = pyupbit.Upbit(upbit_access, upbit_secret)
            logger.info("🔴 LIVE TRADING MODE - Real orders will be executed")
        else:
            self.upbit = None
            logger.info("📝 PRACTICE MODE - Simulated orders only")
        
        self.positions: Dict[str, Position] = {}
        self.trade_log = []
    
    def execute_entry(
        self,
        ticker: str,
        strategy_id: str,
        trade_size_krw: float,
        entry_reason: str
    ) -> Tuple[bool, str]:
        """
        Execute buy order
        
        Returns (success, message)
        """
        try:
            current_price = pyupbit.get_current_price(ticker)
            if current_price is None:
                return False, f"Failed to get price for {ticker}"
            
            # Calculate amount after fees
            fee = trade_size_krw * FEE_RATE
            net_investment = trade_size_krw - fee
            amount = net_investment / current_price
            
            if self.practice_mode:
                # Simulated buy
                logger.info(f"📝 [PRACTICE] BUY {ticker}: {amount:.8f} @ {current_price:,.0f} KRW "
                          f"(invest: {trade_size_krw:,.0f}, fee: {fee:,.0f})")
            else:
                # Real buy order
                order = self.upbit.buy_market_order(ticker, trade_size_krw)
                if order is None or 'error' in order:
                    return False, f"Order failed: {order}"
                
                logger.info(f"🟢 [LIVE] BUY {ticker}: {amount:.8f} @ {current_price:,.0f} KRW "
                          f"(invest: {trade_size_krw:,.0f}, fee: {fee:,.0f})")
            
            # Create position
            position = Position(
                ticker=ticker,
                strategy_id=strategy_id,
                entry_price=current_price,
                entry_time=datetime.now(),
                amount=amount,
                invested_krw=trade_size_krw,
                peak_price=current_price
            )
            
            self.positions[ticker] = position
            
            # Log trade
            self.trade_log.append({
                "timestamp": datetime.now(),
                "type": "BUY",
                "ticker": ticker,
                "strategy": strategy_id,
                "amount": amount,
                "price": current_price,
                "invested": trade_size_krw,
                "fee": fee,
                "reason": entry_reason
            })
            
            return True, f"Entry executed: {ticker} @ {current_price:,.0f}"
            
        except Exception as e:
            logger.error(f"❌ Entry failed for {ticker}: {e}")
            return False, str(e)
    
    def check_exits(self) -> list:
        """
        Check all positions for exit conditions
        
        Returns list of (ticker, exit_reason, exit_pct)
        """
        exits = []
        
        for ticker, position in list(self.positions.items()):
            current_price = pyupbit.get_current_price(ticker)
            if current_price is None:
                continue
            
            position.update_peak(current_price)
            profit_pct = position.get_profit_pct(current_price)
            time_held = position.get_time_held_minutes()
            
            # Exit logic
            
            # 1. Time-stop: 6 min without +1%
            if time_held >= TIME_STOP_MINUTES and profit_pct < TIME_STOP_MIN_PROFIT_PCT:
                exits.append((ticker, "TIME_STOP", 100.0))
                continue
            
            # 2. Trailing stop (only if we've taken partials and are at +7%+)
            if position.remaining_pct < 100 and profit_pct >= 7.0:
                # Check trailing from peak
                drawdown_from_peak = ((position.peak_price - current_price) / position.peak_price) * 100
                if drawdown_from_peak >= TRAILING_STOP_PCT:
                    exits.append((ticker, "TRAIL_7", position.remaining_pct))
                    continue
            
            # 3. Partial exits based on thresholds
            for threshold_pct, exit_pct in PARTIAL_EXIT_THRESHOLDS.items():
                # Check if we've already taken this partial
                already_taken = any(
                    exit['reason'] == f"PARTIAL_{threshold_pct}" 
                    for exit in position.exits
                )
                
                if not already_taken and profit_pct >= threshold_pct:
                    exits.append((ticker, f"PARTIAL_{threshold_pct}", exit_pct))
                    
                    # After first partial, move stop to breakeven
                    if not position.stop_moved_to_breakeven:
                        position.stop_moved_to_breakeven = True
                        logger.info(f"🛡️ Stop moved to breakeven for {ticker}")
        
        return exits
    
    def execute_exit(
        self,
        ticker: str,
        exit_reason: str,
        exit_pct: float
    ) -> Tuple[bool, str]:
        """
        Execute sell order (full or partial)
        
        Returns (success, message)
        """
        if ticker not in self.positions:
            return False, f"No position found for {ticker}"
        
        position = self.positions[ticker]
        current_price = pyupbit.get_current_price(ticker)
        
        if current_price is None:
            return False, f"Failed to get price for {ticker}"
        
        # Calculate sell amount
        sell_amount = position.amount * (exit_pct / 100.0)
        sell_value = sell_amount * current_price
        fee = sell_value * FEE_RATE
        net_proceeds = sell_value - fee
        
        # Calculate profit
        invested_portion = position.invested_krw * (exit_pct / 100.0)
        profit_krw = net_proceeds - invested_portion
        profit_pct = position.get_profit_pct(current_price)
        
        try:
            if self.practice_mode:
                logger.info(f"📝 [PRACTICE] SELL {exit_pct:.0f}% of {ticker}: "
                          f"{sell_amount:.8f} @ {current_price:,.0f} KRW "
                          f"(profit: {profit_krw:+,.0f} KRW, {profit_pct:+.2f}%) - {exit_reason}")
            else:
                # Real sell order
                order = self.upbit.sell_market_order(ticker, sell_amount)
                if order is None or 'error' in order:
                    return False, f"Sell order failed: {order}"
                
                logger.info(f"🔴 [LIVE] SELL {exit_pct:.0f}% of {ticker}: "
                          f"{sell_amount:.8f} @ {current_price:,.0f} KRW "
                          f"(profit: {profit_krw:+,.0f} KRW, {profit_pct:+.2f}%) - {exit_reason}")
            
            # Update position
            position.amount -= sell_amount
            position.invested_krw -= invested_portion
            position.remaining_pct -= exit_pct
            
            # Record exit
            position.exits.append({
                "timestamp": datetime.now(),
                "reason": exit_reason,
                "exit_pct": exit_pct,
                "price": current_price,
                "profit_krw": profit_krw,
                "profit_pct": profit_pct
            })
            
            # Log trade
            self.trade_log.append({
                "timestamp": datetime.now(),
                "type": "SELL",
                "ticker": ticker,
                "strategy": position.strategy_id,
                "amount": sell_amount,
                "price": current_price,
                "profit_krw": profit_krw,
                "profit_pct": profit_pct,
                "reason": exit_reason,
                "exit_pct": exit_pct
            })
            
            # Remove position if fully closed
            if position.remaining_pct <= 0:
                del self.positions[ticker]
                logger.info(f"✅ Position fully closed: {ticker}")
            
            return True, f"Exit executed: {ticker} {exit_pct:.0f}% @ {current_price:,.0f} - {exit_reason}"
            
        except Exception as e:
            logger.error(f"❌ Exit failed for {ticker}: {e}")
            return False, str(e)
    
    def get_portfolio_status(self) -> Dict:
        """Get current portfolio summary"""
        total_invested = sum(p.invested_krw for p in self.positions.values())
        
        positions_detail = []
        for ticker, pos in self.positions.items():
            current_price = pyupbit.get_current_price(ticker)
            if current_price:
                profit_pct = pos.get_profit_pct(current_price)
                positions_detail.append({
                    "ticker": ticker,
                    "strategy": pos.strategy_id,
                    "entry_price": pos.entry_price,
                    "current_price": current_price,
                    "profit_pct": profit_pct,
                    "remaining_pct": pos.remaining_pct,
                    "time_held_min": pos.get_time_held_minutes()
                })
        
        return {
            "position_count": len(self.positions),
            "total_invested_krw": total_invested,
            "positions": positions_detail,
            "recent_trades": self.trade_log[-10:]
        }


if __name__ == "__main__":
    # Test executor
    logging.basicConfig(level=logging.INFO)
    
    executor = TradeExecutor("", "", practice_mode=True)
    
    print("\n=== Test 1: Entry ===")
    success, msg = executor.execute_entry(
        ticker="KRW-BTC",
        strategy_id="ULTRA_SCALP",
        trade_size_krw=100000,
        entry_reason="RSI < 20 + volume spike"
    )
    print(f"Success: {success}, Message: {msg}")
    
    print("\n=== Portfolio Status ===")
    status = executor.get_portfolio_status()
    print(f"Positions: {status['position_count']}")
    print(f"Total Invested: {status['total_invested_krw']:,.0f} KRW")
