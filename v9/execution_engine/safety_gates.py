#!/usr/bin/env python3
"""
Safety Gates for Execution Engine
Double-lock system:
1. Environment variable ENABLE_REAL_TRADING=true
2. File /enable_live.flag must exist
3. First live phase exposure capped at 100,000 KRW
4. Daily equity drop > 2% triggers automatic halt
"""

import logging
import os
from typing import Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SafetyStatus:
    """Current safety gate status"""
    real_trading_enabled: bool
    reason: str
    exposure_limit_krw: float
    daily_drawdown_limit_pct: float
    circuit_breaker_active: bool


class SafetyGates:
    """Enforces safety checks before real trading"""
    
    def __init__(self):
        # Safety limits
        self.FIRST_PHASE_EXPOSURE_LIMIT = 100000  # KRW
        self.DAILY_DRAWDOWN_LIMIT_PCT = 2.0
        
        # Circuit breaker state
        self.circuit_breaker_active = False
        self.circuit_breaker_reason = None
        self.circuit_breaker_time = None
        
        # Daily tracking
        self.daily_start_equity = None
        self.daily_start_date = None
    
    def check_env_variable(self) -> Tuple[bool, str]:
        """Check if ENABLE_REAL_TRADING environment variable is set"""
        enabled = os.getenv("ENABLE_REAL_TRADING", "false").lower() == "true"
        
        if enabled:
            return True, "Environment variable ENABLE_REAL_TRADING=true"
        else:
            return False, "Environment variable ENABLE_REAL_TRADING not set or false"
    
    def check_flag_file(self, flag_path: str = "/enable_live.flag") -> Tuple[bool, str]:
        """Check if live trading flag file exists"""
        if os.path.exists(flag_path):
            return True, f"Flag file exists: {flag_path}"
        else:
            return False, f"Flag file not found: {flag_path}"
    
    def check_exposure_limit(self, current_invested: float) -> Tuple[bool, str]:
        """Check if current investment is within first phase limit"""
        if current_invested <= self.FIRST_PHASE_EXPOSURE_LIMIT:
            return True, f"Exposure OK: {current_invested:,.0f} / {self.FIRST_PHASE_EXPOSURE_LIMIT:,.0f} KRW"
        else:
            return False, f"Exposure limit exceeded: {current_invested:,.0f} > {self.FIRST_PHASE_EXPOSURE_LIMIT:,.0f} KRW"
    
    def check_daily_drawdown(self, current_equity: float) -> Tuple[bool, str]:
        """Check if daily drawdown exceeds limit"""
        # Initialize daily tracking if needed
        today = datetime.now().date()
        if self.daily_start_date != today:
            self.daily_start_equity = current_equity
            self.daily_start_date = today
            logger.info(f"📊 Daily tracking reset: Starting equity {current_equity:,.0f} KRW")
        
        # Calculate drawdown
        if self.daily_start_equity and self.daily_start_equity > 0:
            drawdown_pct = ((current_equity - self.daily_start_equity) / self.daily_start_equity) * 100
            
            if drawdown_pct <= -self.DAILY_DRAWDOWN_LIMIT_PCT:
                return False, f"Daily drawdown limit breached: {drawdown_pct:.2f}% (limit: {self.DAILY_DRAWDOWN_LIMIT_PCT}%)"
            else:
                return True, f"Daily drawdown OK: {drawdown_pct:+.2f}%"
        
        return True, "Daily tracking not yet initialized"
    
    def check_circuit_breaker(self) -> Tuple[bool, str]:
        """Check if circuit breaker is active"""
        if self.circuit_breaker_active:
            elapsed = (datetime.now() - self.circuit_breaker_time).total_seconds() / 60
            return False, f"Circuit breaker ACTIVE: {self.circuit_breaker_reason} (elapsed: {elapsed:.0f} min)"
        
        return True, "Circuit breaker not active"
    
    def trigger_circuit_breaker(self, reason: str):
        """Activate circuit breaker"""
        self.circuit_breaker_active = True
        self.circuit_breaker_reason = reason
        self.circuit_breaker_time = datetime.now()
        
        logger.error(f"🚨 CIRCUIT BREAKER ACTIVATED: {reason}")
    
    def reset_circuit_breaker(self):
        """Manually reset circuit breaker"""
        if self.circuit_breaker_active:
            logger.warning(f"🔓 Circuit breaker reset manually")
        
        self.circuit_breaker_active = False
        self.circuit_breaker_reason = None
        self.circuit_breaker_time = None
    
    def is_real_trading_allowed(
        self,
        current_equity: float,
        current_invested: float,
        flag_path: str = "/enable_live.flag"
    ) -> SafetyStatus:
        """
        Check all safety gates
        
        Returns SafetyStatus with enabled flag and reason
        """
        checks = []
        
        # 1. Environment variable
        env_ok, env_msg = self.check_env_variable()
        checks.append(("ENV", env_ok, env_msg))
        
        # 2. Flag file
        flag_ok, flag_msg = self.check_flag_file(flag_path)
        checks.append(("FLAG", flag_ok, flag_msg))
        
        # 3. Circuit breaker
        cb_ok, cb_msg = self.check_circuit_breaker()
        checks.append(("CIRCUIT_BREAKER", cb_ok, cb_msg))
        
        # 4. Exposure limit
        exposure_ok, exposure_msg = self.check_exposure_limit(current_invested)
        checks.append(("EXPOSURE", exposure_ok, exposure_msg))
        
        # 5. Daily drawdown
        dd_ok, dd_msg = self.check_daily_drawdown(current_equity)
        checks.append(("DRAWDOWN", dd_ok, dd_msg))
        
        # If daily drawdown breached, trigger circuit breaker
        if not dd_ok and not self.circuit_breaker_active:
            self.trigger_circuit_breaker(dd_msg)
        
        # Log all checks
        for check_name, check_ok, check_msg in checks:
            status_emoji = "✅" if check_ok else "❌"
            logger.info(f"{status_emoji} Safety Gate [{check_name}]: {check_msg}")
        
        # Determine overall status
        all_ok = all(ok for _, ok, _ in checks)
        
        if all_ok:
            return SafetyStatus(
                real_trading_enabled=True,
                reason="All safety gates passed",
                exposure_limit_krw=self.FIRST_PHASE_EXPOSURE_LIMIT,
                daily_drawdown_limit_pct=self.DAILY_DRAWDOWN_LIMIT_PCT,
                circuit_breaker_active=False
            )
        else:
            failed_checks = [name for name, ok, _ in checks if not ok]
            return SafetyStatus(
                real_trading_enabled=False,
                reason=f"Failed checks: {', '.join(failed_checks)}",
                exposure_limit_krw=self.FIRST_PHASE_EXPOSURE_LIMIT,
                daily_drawdown_limit_pct=self.DAILY_DRAWDOWN_LIMIT_PCT,
                circuit_breaker_active=self.circuit_breaker_active
            )


if __name__ == "__main__":
    # Test safety gates
    logging.basicConfig(level=logging.INFO)
    
    gates = SafetyGates()
    
    print("\n=== Test 1: Check without env/flag ===")
    status = gates.is_real_trading_allowed(
        current_equity=1000000,
        current_invested=50000
    )
    print(f"Enabled: {status.real_trading_enabled}")
    print(f"Reason: {status.reason}")
    
    print("\n=== Test 2: Simulate environment variable ===")
    os.environ["ENABLE_REAL_TRADING"] = "true"
    status = gates.is_real_trading_allowed(
        current_equity=1000000,
        current_invested=50000
    )
    print(f"Enabled: {status.real_trading_enabled}")
    print(f"Reason: {status.reason}")
    
    print("\n=== Test 3: Exposure limit breach ===")
    status = gates.is_real_trading_allowed(
        current_equity=1000000,
        current_invested=150000
    )
    print(f"Enabled: {status.real_trading_enabled}")
    print(f"Reason: {status.reason}")
    
    print("\n=== Test 4: Daily drawdown breach ===")
    gates.daily_start_equity = 1000000
    gates.daily_start_date = datetime.now().date()
    status = gates.is_real_trading_allowed(
        current_equity=970000,  # -3% loss
        current_invested=30000
    )
    print(f"Enabled: {status.real_trading_enabled}")
    print(f"Reason: {status.reason}")
    print(f"Circuit Breaker: {status.circuit_breaker_active}")
