#!/usr/bin/env python3
"""
Recovery Engine for Execution Engine
Handles portfolio recovery when positions drop to -20%:
- No hard -2% stop-loss
- Sell 10-50% of least-negative holdings
- Re-allocate only under valid regime
- Log all recovery actions
"""

import logging
import pyupbit
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RecoveryAction:
    """Represents a recovery action taken"""
    timestamp: datetime
    trigger_ticker: str
    trigger_loss_pct: float
    action: str  # "PARTIAL_SELL", "REALLOC", "HOLD"
    details: Dict
    result: str


class RecoveryEngine:
    """Manages portfolio recovery from deep losses"""
    
    def __init__(self, executor, validator):
        self.executor = executor  # TradeExecutor instance
        self.validator = validator  # SignalValidator instance
        self.recovery_log: List[RecoveryAction] = []
        self.recovery_active = False
        
        # Recovery thresholds
        self.CRITICAL_LOSS_PCT = -20.0  # Trigger recovery mode
        self.PARTIAL_SELL_MIN_PCT = 10.0  # Minimum % to sell
        self.PARTIAL_SELL_MAX_PCT = 50.0  # Maximum % to sell
        
    def check_recovery_triggers(self, positions: Dict) -> List[str]:
        """
        Check if any position has dropped to -20% or worse
        
        Returns list of tickers in critical loss
        """
        critical_positions = []
        
        for ticker, position in positions.items():
            current_price = pyupbit.get_current_price(ticker)
            if current_price is None:
                continue
            
            profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            
            if profit_pct <= self.CRITICAL_LOSS_PCT:
                critical_positions.append(ticker)
                logger.warning(f"⚠️ CRITICAL LOSS: {ticker} at {profit_pct:.2f}%")
        
        return critical_positions
    
    def get_least_negative_positions(self, positions: Dict, exclude: List[str]) -> List[Tuple[str, float]]:
        """
        Get positions sorted by loss % (least negative first)
        Excludes specified tickers
        
        Returns [(ticker, profit_pct), ...]
        """
        position_losses = []
        
        for ticker, position in positions.items():
            if ticker in exclude:
                continue
            
            current_price = pyupbit.get_current_price(ticker)
            if current_price is None:
                continue
            
            profit_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            position_losses.append((ticker, profit_pct))
        
        # Sort by profit_pct descending (least negative first)
        position_losses.sort(key=lambda x: x[1], reverse=True)
        
        return position_losses
    
    def execute_recovery(
        self,
        critical_tickers: List[str],
        positions: Dict,
        regime_full_downtrend: bool
    ) -> List[RecoveryAction]:
        """
        Execute recovery strategy
        
        Strategy:
        1. Identify least-negative positions (excluding critical ones)
        2. Sell 10-50% of those positions to raise capital
        3. If regime is valid, consider re-allocation
        4. Log all actions
        
        Returns list of RecoveryActions taken
        """
        actions = []
        
        if not critical_tickers:
            return actions
        
        # Activate recovery mode
        self.recovery_active = True
        logger.warning(f"🚨 RECOVERY MODE ACTIVATED - {len(critical_tickers)} position(s) in critical loss")
        
        for trigger_ticker in critical_tickers:
            trigger_position = positions.get(trigger_ticker)
            if not trigger_position:
                continue
            
            current_price = pyupbit.get_current_price(trigger_ticker)
            if current_price is None:
                continue
            
            trigger_loss_pct = ((current_price - trigger_position.entry_price) / trigger_position.entry_price) * 100
            
            # Get least-negative positions (exclude critical ones)
            least_negative = self.get_least_negative_positions(positions, critical_tickers)
            
            if not least_negative:
                action = RecoveryAction(
                    timestamp=datetime.now(),
                    trigger_ticker=trigger_ticker,
                    trigger_loss_pct=trigger_loss_pct,
                    action="HOLD",
                    details={"reason": "No other positions to liquidate"},
                    result="Recovery deferred - holding all positions"
                )
                actions.append(action)
                self.recovery_log.append(action)
                logger.info(f"📊 Recovery action: HOLD - no liquidation candidates")
                continue
            
            # Determine how much to sell
            # Sell from least-negative positions
            total_raised = 0
            sell_actions = []
            
            for sell_ticker, profit_pct in least_negative[:2]:  # Max 2 positions
                # Determine sell %
                if profit_pct > 0:
                    # Profitable position - sell 10%
                    sell_pct = self.PARTIAL_SELL_MIN_PCT
                elif profit_pct > -5:
                    # Small loss - sell 20%
                    sell_pct = 20.0
                elif profit_pct > -10:
                    # Medium loss - sell 30%
                    sell_pct = 30.0
                else:
                    # Large loss (but less than -20%) - sell 50%
                    sell_pct = self.PARTIAL_SELL_MAX_PCT
                
                # Execute partial sell
                success, msg = self.executor.execute_exit(
                    ticker=sell_ticker,
                    exit_reason=f"RECOVERY_{trigger_ticker}",
                    exit_pct=sell_pct
                )
                
                if success:
                    sell_position = positions[sell_ticker]
                    raised_krw = sell_position.invested_krw * (sell_pct / 100.0)
                    total_raised += raised_krw
                    
                    sell_actions.append({
                        "ticker": sell_ticker,
                        "profit_pct": profit_pct,
                        "sell_pct": sell_pct,
                        "raised_krw": raised_krw,
                        "result": msg
                    })
                    
                    logger.info(f"💰 Recovery liquidation: {sell_ticker} {sell_pct:.0f}% → {raised_krw:,.0f} KRW")
            
            # Record recovery action
            action = RecoveryAction(
                timestamp=datetime.now(),
                trigger_ticker=trigger_ticker,
                trigger_loss_pct=trigger_loss_pct,
                action="PARTIAL_SELL",
                details={
                    "liquidations": sell_actions,
                    "total_raised_krw": total_raised
                },
                result=f"Raised {total_raised:,.0f} KRW from {len(sell_actions)} partial liquidation(s)"
            )
            actions.append(action)
            self.recovery_log.append(action)
            
            # Re-allocation decision
            if regime_full_downtrend:
                logger.warning(f"⛔ No re-allocation: FULL_DOWNTREND regime active")
                realloc_action = RecoveryAction(
                    timestamp=datetime.now(),
                    trigger_ticker=trigger_ticker,
                    trigger_loss_pct=trigger_loss_pct,
                    action="HOLD",
                    details={"reason": "FULL_DOWNTREND regime - new entries blocked"},
                    result="Capital held in cash"
                )
                actions.append(realloc_action)
                self.recovery_log.append(realloc_action)
            else:
                logger.info(f"✅ Recovery capital available for re-allocation under valid regime")
                # Re-allocation would be handled by normal signal flow
                # This engine just raises the capital
        
        return actions
    
    def get_recovery_status(self) -> Dict:
        """Get current recovery mode status"""
        return {
            "recovery_active": self.recovery_active,
            "recovery_log": [
                {
                    "timestamp": action.timestamp.isoformat(),
                    "trigger_ticker": action.trigger_ticker,
                    "trigger_loss_pct": action.trigger_loss_pct,
                    "action": action.action,
                    "result": action.result
                }
                for action in self.recovery_log[-10:]  # Last 10 actions
            ]
        }
    
    def reset_recovery_mode(self):
        """Exit recovery mode"""
        if self.recovery_active:
            self.recovery_active = False
            logger.info(f"✅ Recovery mode deactivated")


if __name__ == "__main__":
    # Test recovery engine
    logging.basicConfig(level=logging.INFO)
    
    # Mock objects for testing
    class MockExecutor:
        def execute_exit(self, ticker, exit_reason, exit_pct):
            logger.info(f"Mock exit: {ticker} {exit_pct}% for {exit_reason}")
            return True, f"Mock sell executed: {ticker}"
    
    class MockValidator:
        pass
    
    class MockPosition:
        def __init__(self, ticker, entry_price, invested):
            self.ticker = ticker
            self.entry_price = entry_price
            self.invested_krw = invested
    
    # Create engine
    executor = MockExecutor()
    validator = MockValidator()
    recovery = RecoveryEngine(executor, validator)
    
    # Test scenario: One position at -21%, two others at -5% and +2%
    import pyupbit
    pyupbit.get_current_price = lambda t: {
        "KRW-DOGE": 79.0,  # -21% from entry
        "KRW-XRP": 95.0,   # -5% from entry
        "KRW-ADA": 102.0   # +2% from entry
    }.get(t, 100.0)
    
    positions = {
        "KRW-DOGE": MockPosition("KRW-DOGE", 100.0, 100000),
        "KRW-XRP": MockPosition("KRW-XRP", 100.0, 100000),
        "KRW-ADA": MockPosition("KRW-ADA", 100.0, 100000)
    }
    
    print("\n=== Recovery Test ===")
    critical = recovery.check_recovery_triggers(positions)
    print(f"Critical positions: {critical}")
    
    if critical:
        actions = recovery.execute_recovery(critical, positions, regime_full_downtrend=False)
        print(f"\nRecovery actions taken: {len(actions)}")
        for action in actions:
            print(f"- {action.action}: {action.result}")
    
    print("\n=== Recovery Status ===")
    status = recovery.get_recovery_status()
    print(f"Active: {status['recovery_active']}")
    print(f"Actions logged: {len(status['recovery_log'])}")
