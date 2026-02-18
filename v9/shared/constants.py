#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v9 Constants - Shared configuration across Signal and Execution engines
"""

# === API Configuration ===
UPBIT_API_BASE = "https://api.upbit.com/v1"
SNAPSHOT_INTERVAL_SECONDS = 300  # 5 minutes

# === Market Filters ===
MARKET_PREFIX = "KRW"  # Only KRW market
EXCLUDE_MARKETS = ["BTC", "USDT"]  # No BTC/USDT pairs
MIN_LIQUIDITY_PERCENTILE = 5  # Exclude bottom 5%

# === TOP 20 Candidate Selection ===
TOP_N_CANDIDATES = 20
SCORE_WEIGHTS = {
    'delta_money': 0.5,
    'price_change': 0.3,
    'delta_volume': 0.2
}

# === BTC Regime Detection ===
BTC_TICKER = "KRW-BTC"
BTC_1H_SMA_SHORT = 20
BTC_1H_SMA_LONG = 50
BTC_4H_SMA_SHORT = 20
BTC_4H_SMA_LONG = 50
STABLECOIN_SPIKE_THRESHOLD = 0.02  # 2%
DOMINANCE_SPIKE_THRESHOLD = 0.01   # 1%

# === Ultra Scalp Strategy ===
ULTRA_SCALP = {
    'id': 'ULTRA_SCALP_V2_1',
    'timeframe': '1m',
    'bb_period': 20,
    'bb_std': 2,
    'rsi_period': 14,
    'rsi_threshold': 20,
    'consecutive_red_candles': 3,
    'volume_spike_multiplier': 2.0,
    'capital_per_trade_pct': 10,
    'max_concurrent_positions': 2,
    'max_total_allocation_pct': 20,
    'partial_exit_3': 0.30,  # Sell 30% at +3%
    'partial_exit_5': 0.40,  # Sell 40% at +5%
    'partial_exit_7': 0.30,  # Remaining 30% at +7%
    'trailing_stop_5': 0.015,  # 1.5% trailing after +5%
    'trailing_stop_7': 0.018,  # 1.8% trailing after +7%
    'time_stop_seconds': 360,  # 6 minutes
    'time_stop_min_profit': 0.01  # Exit if < +1% after 6 min
}

# === Deep Hunter Strategy ===
DEEP_HUNTER = {
    'id': 'DEEP_HUNTER_V1',
    'timeframe': '1H',
    'rsi_period': 14,
    'rsi_threshold': 15,
    'bb_period': 20,
    'bb_std': 2,
    'initial_capital_pct': 5,
    'max_total_allocation_pct': 15,
    'averaging_enabled': True,
    'no_hard_stop_loss': True
}

# === Recovery Engine ===
RECOVERY = {
    'trigger_loss_pct': -20.0,  # Activate when any position -20%
    'realloc_sell_pct_range': (0.10, 0.50),  # Sell 10-50% of least negative
    'min_signal_confidence': 0.8
}

# === BTC Stacking ===
BTC_STACKING = {
    'profit_threshold_krw': 10000,  # Convert to BTC when profit >= 10k KRW
    'btc_ticker': 'KRW-BTC'
}

# === Safety Gates ===
SAFETY = {
    'env_var': 'ENABLE_REAL_TRADING',
    'flag_file': '/home/user/webapp/enable_live.flag',
    'max_exposure_krw': 100000,  # First live phase limit
    'daily_drawdown_limit_pct': -2.0,  # Auto-halt at -2% daily
    'emergency_stop_endpoint': '/api/emergency_stop'
}

# === WebSocket ===
WEBSOCKET = {
    'signal_to_execution_url': 'ws://localhost:8765',  # Adjust for actual deployment
    'heartbeat_interval': 30,
    'reconnect_delay': 5,
    'max_reconnect_attempts': 10
}

# === Logging ===
LOG_DIR = '/home/user/webapp/logs'
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# === Signal Types ===
class SignalType:
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    REGIME_CHANGE = "REGIME_CHANGE"

# === Regime States ===
class RegimeState:
    NORMAL = "NORMAL"
    FULL_DOWNTREND = "FULL_DOWNTREND"

# === Exit Reasons ===
class ExitReason:
    PARTIAL_3 = "PARTIAL_3"
    PARTIAL_5 = "PARTIAL_5"
    TRAIL_7 = "TRAIL_7"
    TIME_STOP = "TIME_STOP"
    RECOVERY_REBALANCE = "RECOVERY_REBALANCE"
    MANUAL = "MANUAL"
    REGIME_INVALID = "REGIME_INVALID"

# === Signal Status ===
class SignalStatus:
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
