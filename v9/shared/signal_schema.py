#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Signal Schema - Structured data models for Signal ↔ Execution communication
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional, List
from datetime import datetime
import uuid

@dataclass
class SignalPayload:
    """Signal sent from Signal Engine to Execution Engine"""
    signal_type: str  # ENTRY, EXIT, REGIME_CHANGE
    strategy_id: str
    ticker: str
    confidence: float
    snapshot_score: float
    btc_regime: str  # NORMAL, FULL_DOWNTREND
    indicators: Dict[str, float]
    timestamp: int
    signal_id: str
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def create_entry_signal(
        cls,
        strategy_id: str,
        ticker: str,
        confidence: float,
        snapshot_score: float,
        btc_regime: str,
        indicators: Dict[str, float]
    ) -> 'SignalPayload':
        return cls(
            signal_type="ENTRY",
            strategy_id=strategy_id,
            ticker=ticker,
            confidence=confidence,
            snapshot_score=snapshot_score,
            btc_regime=btc_regime,
            indicators=indicators,
            timestamp=int(datetime.now().timestamp()),
            signal_id=str(uuid.uuid4())
        )
    
    @classmethod
    def create_exit_signal(
        cls,
        strategy_id: str,
        ticker: str,
        reason: str,
        btc_regime: str
    ) -> 'SignalPayload':
        return cls(
            signal_type="EXIT",
            strategy_id=strategy_id,
            ticker=ticker,
            confidence=1.0,
            snapshot_score=0.0,
            btc_regime=btc_regime,
            indicators={'exit_reason': reason},
            timestamp=int(datetime.now().timestamp()),
            signal_id=str(uuid.uuid4())
        )
    
    @classmethod
    def create_regime_change_signal(
        cls,
        old_regime: str,
        new_regime: str
    ) -> 'SignalPayload':
        return cls(
            signal_type="REGIME_CHANGE",
            strategy_id="REGIME_DETECTOR",
            ticker="KRW-BTC",
            confidence=1.0,
            snapshot_score=0.0,
            btc_regime=new_regime,
            indicators={'old_regime': old_regime, 'new_regime': new_regime},
            timestamp=int(datetime.now().timestamp()),
            signal_id=str(uuid.uuid4())
        )


@dataclass
class ExecutionResponse:
    """Response from Execution Engine back to Signal Engine (optional logging)"""
    signal_id: str
    status: str  # ACCEPTED, REJECTED
    reject_reason: Optional[str] = None
    order_id: Optional[str] = None
    executed_amount: Optional[float] = None
    executed_price: Optional[float] = None
    timestamp: int = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = int(datetime.now().timestamp())
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CandidateSnapshot:
    """TOP 20 candidate data"""
    ticker: str
    rank: int
    score: float
    delta_money: float
    delta_volume: float
    price_change_pct: float
    current_price: float
    timestamp: int
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StrategyConfig:
    """Structured strategy configuration"""
    id: str
    display_name: str
    stop_loss_pct: float
    take_profit_pct: float
    trailing_stop_pct: float
    entry_indicators: List[str]
    exit_logic: str
    time_stop: int  # seconds
    capital_rule: Dict[str, float]
    source: str  # manual, youtube, backtest
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StrategyConfig':
        return cls(**data)


@dataclass
class PositionState:
    """Current position state in Execution Engine"""
    ticker: str
    strategy_id: str
    entry_price: float
    entry_time: int
    amount: float
    invested_krw: float
    current_pnl_pct: float
    peak_price: float
    partial_exits_done: List[str]  # ["PARTIAL_3", "PARTIAL_5"]
    time_elapsed_seconds: int
    
    def to_dict(self) -> dict:
        return asdict(self)


# === Validation Functions ===
def validate_signal_payload(data: dict) -> bool:
    """Validate incoming signal payload structure"""
    required_fields = [
        'signal_type', 'strategy_id', 'ticker', 'confidence',
        'snapshot_score', 'btc_regime', 'indicators', 'timestamp', 'signal_id'
    ]
    return all(field in data for field in required_fields)


def validate_execution_response(data: dict) -> bool:
    """Validate execution response structure"""
    required_fields = ['signal_id', 'status', 'timestamp']
    return all(field in data for field in required_fields)
