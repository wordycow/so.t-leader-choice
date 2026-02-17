#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 업비트 AI 트레이딩 봇 v8.0 - ULTIMATE EDITION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 완전체: 모든 기능 통합 최종판

🔥 핵심 기능:
1. 📊 5가지 패턴 자동 인식
   - 박스권, 상승추세, 하락추세, 급등후, 수급 유입/이탈
   
2. 🏆 멀티 전략 경쟁 시스템
   - 급등 포착 (Surge Hunter)
   - 급락 저점 매수 (Dip Hunter - 원가 복귀)
   - 박스권 하단 매수 (Box Trader)
   - 추세 추종 (Trend Follower)
   - 수급 기반 (Volume Hunter)
   
3. 🧠 AI 자동 학습
   - 매 거래마다 성과 기록
   - 전략별 가중치 자동 조정
   - 50개 거래마다 재학습
   
4. 🛡️ 손실 복구 모드
   - -15% 손실 시 자동 활성화
   - 10% 시드로 초단타
   - 기존 코인 동결 (반등 대기)
   
5. ⚙️ 시각적 피드백
   - 로딩 스피너
   - 실시간 상태 표시
   - 전략 경쟁 현황 대시보드

🎯 최종 목표: 월 25%+ 수익, 승률 75%+, 손실 자동 복구
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import os
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import deque, defaultdict
import json
import threading
from flask import Flask, render_template, jsonify, request, make_response, session, redirect, Response
from flask_cors import CORS
import traceback
import os
import sqlite3
import requests

# 커스텀 모듈
from user_manager import UserManager
from portfolio_manager import execute_diversified_buy, check_profit_trigger, get_available_coins
from trade_reasons import generate_buy_reason, generate_sell_reason
from recovery_system import analyze_current_holdings, create_recovery_plan, execute_recovery_plan, UPBIT_FEE_RATE
from bot_state_manager import init_bot_state_table, save_bot_state, load_bot_state, get_all_running_bots
from jai_memory_system import (
    init_memory_tables, 
    get_or_create_user_profile, 
    learn_from_conversation,
    save_conversation,
    build_user_context,
    get_personalized_greeting,
    get_user_real_name,
    get_relationship_level
)

# ═══════════════════════════════════════════════════════
# ⚙️ 전체 설정
# ═══════════════════════════════════════════════════════

# 급등/급락 감지
SURGE_CONFIG = {
    # 급등 (🔥 10% 이상 급등만 포착!)
    'surge_threshold_1m': 10.0,  # 1분 10% 이상
    'surge_threshold_3m': 8.0,   # 3분 8% 이상
    'surge_threshold_5m': 10.0,  # 5분 10% 이상
    'surge_threshold_10m': 12.0, # 10분 12% 이상
    
    # 급락
    'dip_threshold_1m': -1.5,
    'dip_oversold_rsi': 35,
    'dip_volume_spike': 2.0,
    
    # 복귀 전략
    'dip_recovery_threshold': -0.3,
    'dip_max_hold_time': 24 * 60,
    'dip_emergency_stop': -10.0,
    
    # 거래량
    'volume_spike_ratio': 2.0,
    'min_volume_krw': 100000000,
    
    # 익절/손절 (🚀 빠른 회전 전략!)
    'take_profit_quick': 5.0,    # 5% 이상 즉시 익절! (20만원 × 5% = 10,000원)
    'take_profit_targets': [5.0, 8.0, 10.0],
    'stop_loss': -2.0,           # -2% 즉시 손절!
}

# 패턴 분석
PATTERN_CONFIG = {
    'box_range_threshold': 3.0,
    'trend_ma_short': 20,
    'trend_ma_long': 60,
    'uptrend_threshold': 2.0,
    'volume_surge_ratio': 2.5,
}

# AI 학습
LEARNING_CONFIG = {
    'enable_learning': True,
    'learning_interval': 50,
    'pattern_history_size': 500,
}

# 손실 복구
RECOVERY_CONFIG = {
    'enable_recovery_mode': True,
    'activate_loss_threshold': -15.0,
    'recovery_cash_ratio': 0.10,
    'recovery_target_profit': 1.5,
    'recovery_stop_loss': -1.0,
    'recovery_max_hold_time': 30,
    'recovery_target_rate': 0.5,
}

# ═══════════════════════════════════════════════════════
# 🏆 전략 정의
# ═══════════════════════════════════════════════════════
STRATEGIES = {
    'surge_hunter': {
        'name': '급등 포착',
        'icon': '🔥',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'dip_hunter': {
        'name': '급락 저점 → 원가 복귀',
        'icon': '📉',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'box_trader': {
        'name': '박스권 매매',
        'icon': '📦',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'trend_follower': {
        'name': '추세 추종',
        'icon': '📈',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'volume_hunter': {
        'name': '수급 기반',
        'icon': '🔊',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'gap_down_reversal': {
        'name': 'BNF 급락 반등',
        'icon': '⚡',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'squeeze_momentum': {
        'name': '압축 모멘텀',
        'icon': '💥',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'ema_squeeze': {
        'name': '200/20 이평선 스퀴즈',
        'icon': '🎯',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'testa_3sma': {
        'name': '테스타 3중 이평선',
        'icon': '🎪',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'rsi_reversal': {
        'name': 'RSI 필터 반전',
        'icon': '🔄',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'volume_breakout_v2': {
        'name': '거래량 돌파',
        'icon': '💪',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'mach7_pullback': {
        'name': '마하7 이평선 눌림목',
        'icon': '🚀',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    }
}

# ═══════════════════════════════════════════════════════
# 🎮 봇 상태 관리
# ═══════════════════════════════════════════════════════

def create_bot_state():
    """사용자별 독립 봇 상태 생성"""
    return {
        'running': False,
        'mode': 'practice',
        'upbit': None,
        'thread': None,
        
        # 시뮬레이션
        'simulation_seed': 1000000,
        'simulation_krw': 1000000,
        'simulation_holdings': {},
        'simulation_start_seed': 1000000,
        
        # 복구 모드
        'recovery_mode_active': False,
        'recovery_seed': 0,
        'recovery_target_amount': 0,
        'recovery_trades': 0,
        'recovery_success_trades': 0,
        'recovery_total_profit': 0,
        'frozen_holdings': {},
        'last_loss_time': None,
        
        # 학습
        'pattern_history': deque(maxlen=LEARNING_CONFIG['pattern_history_size']),
        'trade_results': deque(maxlen=LEARNING_CONFIG['pattern_history_size']),
        'strategy_performance': {k: v.copy() for k, v in STRATEGIES.items()},
        'current_patterns': {},
        'orderbook_history': {},  # 채결 강도 이력 저장
        
        # 통계
        'statistics': {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit': 0,
            'best_strategy': None,
            'recovery_progress': 0,
        },
        
        # 거래 내역 (최근 50개)
        'recent_trades': deque(maxlen=50),
        'recent_signals': deque(maxlen=50),
        
        # 실시간 상태 메시지
        'status_message': '⏸️ 대기 중',
        'status_emoji': '⏸️',
        'status_detail': '봇이 시작되지 않았습니다',
        'last_action': None,
        'last_action_time': None,
        
        'user_id': None,  # 사용자 ID 추가
        'last_update': None,
        'start_time': None,
    }

# 전역 봇 상태 (하위 호환성 유지)
bot_state = create_bot_state()

def get_user_bot_state(user_id):
    """사용자 ID로 봇 상태 조회 또는 생성"""
    if user_id not in user_bots:
        user_bots[user_id] = create_bot_state()
        user_bots[user_id]['user_id'] = user_id  # user_id 설정
    return user_bots[user_id]

# ═══════════════════════════════════════════════════════
# 📝 로깅
# ═══════════════════════════════════════════════════════
def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colors = {
        "SUCCESS": "\033[92m", "ERROR": "\033[91m", "WARNING": "\033[93m",
        "INFO": "\033[96m", "PATTERN": "\033[95m", "LEARN": "\033[94m",
        "RECOVERY": "\033[95m", "URGENT": "\033[91m\033[1m"
    }
    color = colors.get(level, "\033[0m")
    print(f"{color}[{timestamp}] {level}: {message}\033[0m")

def log_separator():
    print("\n" + "="*80 + "\n")

# ═══════════════════════════════════════════════════════
# 💾 거래 히스토리 DB 저장
# ═══════════════════════════════════════════════════════
def save_trade_to_db(user_id, trade_data):
    """거래 내역을 DB에 영구 저장"""
    try:
        import sqlite3
        import json
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # trades 테이블이 없으면 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                ticker TEXT NOT NULL,
                trade_type TEXT NOT NULL,
                amount REAL,
                price REAL,
                invested REAL,
                fee REAL,
                net_invested REAL,
                entry_price REAL,
                sell_value REAL,
                net_proceeds REAL,
                profit REAL,
                profit_rate REAL,
                strategy TEXT,
                reason TEXT,
                mode TEXT,
                patterns TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 인덱스 생성 (검색 속도 향상)
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trade_user_time 
            ON trade_history(user_id, timestamp DESC)
        ''')
        
        # 데이터 삽입
        cursor.execute('''
            INSERT INTO trade_history (
                user_id, ticker, trade_type, amount, price,
                invested, fee, net_invested, entry_price, sell_value,
                net_proceeds, profit, profit_rate, strategy, reason,
                mode, patterns, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            trade_data.get('ticker'),
            trade_data.get('type'),
            trade_data.get('amount'),
            trade_data.get('price'),
            trade_data.get('invested', 0),
            trade_data.get('fee', 0),
            trade_data.get('net_invested', 0),
            trade_data.get('entry_price', 0),
            trade_data.get('sell_value', 0),
            trade_data.get('net_proceeds', 0),
            trade_data.get('profit', 0),
            trade_data.get('profit_rate', 0),
            trade_data.get('strategy', ''),
            trade_data.get('reason', ''),
            trade_data.get('mode', 'practice'),
            json.dumps(trade_data.get('patterns', []), ensure_ascii=False),
            trade_data.get('timestamp')
        ))
        
        conn.commit()
        conn.close()
        
        log(f"[DB] 거래 저장: {user_id} | {trade_data.get('type')} | {trade_data.get('ticker')}", "INFO")
        return True
    except Exception as e:
        log(f"거래 DB 저장 오류: {e}", "ERROR")
        return False

def save_bot_state_to_db(user_id, bot_state):
    """봇 상태를 DB에 저장 (simulation_holdings, simulation_krw, strategy_performance 등)"""
    try:
        import sqlite3
        import json
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # simulation_holdings를 JSON으로 변환
        holdings_json = json.dumps(bot_state.get('simulation_holdings', {}), ensure_ascii=False, default=str)
        
        # 🎯 strategy_performance를 JSON으로 변환 (히스토리 보존!)
        strategy_perf_json = json.dumps(bot_state.get('strategy_performance', {}), ensure_ascii=False, default=str)
        
        # bot_states 업데이트
        cursor.execute("""
            UPDATE bot_states
            SET 
                simulation_krw = ?,
                simulation_holdings = ?,
                recovery_mode_active = ?,
                strategy_performance = ?,
                last_update = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (
            bot_state.get('simulation_krw', 0),
            holdings_json,
            bot_state.get('recovery_mode_active', False),
            strategy_perf_json,
            user_id
        ))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        log(f"봇 상태 DB 저장 오류: {e}", "ERROR")
        return False

# ═══════════════════════════════════════════════════════
# 📊 기술적 지표 계산
# ═══════════════════════════════════════════════════════
def calculate_rsi(df, period=14):
    """RSI 계산"""
    try:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if len(rsi) > 0 else 50
    except:
        return 50

def calculate_volume_spike(df):
    """거래량 급증 계산"""
    try:
        if len(df) < 10:
            return 1.0
        avg_volume = df['volume'].iloc[-10:-1].mean()
        current_volume = df['volume'].iloc[-1]
        return (current_volume / avg_volume) if avg_volume > 0 else 1.0
    except:
        return 1.0

def calculate_ema(df, period=25):
    """EMA 계산"""
    try:
        return df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
    except:
        return df['close'].iloc[-1]

def calculate_macd(df):
    """MACD 계산 (12, 26, 9)"""
    try:
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line.iloc[-1],
            'signal': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1],
            'prev_histogram': histogram.iloc[-2] if len(histogram) > 1 else 0
        }
    except:
        return {'macd': 0, 'signal': 0, 'histogram': 0, 'prev_histogram': 0}

def calculate_bollinger_keltner(df, bb_period=20, kc_period=20):
    """Bollinger Bands와 Keltner Channels 계산 (Squeeze Momentum용)"""
    try:
        # Bollinger Bands
        sma = df['close'].rolling(window=bb_period).mean()
        std = df['close'].rolling(window=bb_period).std()
        bb_upper = sma + (std * 2)
        bb_lower = sma - (std * 2)
        
        # Keltner Channels (ATR 기반)
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=kc_period).mean()
        
        kc_middle = df['close'].rolling(window=kc_period).mean()
        kc_upper = kc_middle + (atr * 1.5)
        kc_lower = kc_middle - (atr * 1.5)
        
        # Squeeze 감지 (BB가 KC 안에 있을 때)
        squeeze_on = (bb_lower.iloc[-1] > kc_lower.iloc[-1]) and (bb_upper.iloc[-1] < kc_upper.iloc[-1])
        
        # Momentum 계산
        highest = df['high'].rolling(window=kc_period).max()
        lowest = df['low'].rolling(window=kc_period).min()
        avg_hl = (highest + lowest) / 2
        momentum = df['close'] - avg_hl
        
        return {
            'squeeze_on': squeeze_on,
            'momentum': momentum.iloc[-1],
            'prev_momentum': momentum.iloc[-2] if len(momentum) > 1 else 0
        }
    except:
        return {'squeeze_on': False, 'momentum': 0, 'prev_momentum': 0}

def calculate_orderbook_strength(ticker):
    """실시간 채결 강도 계산 (호가창 분석)"""
    try:
        orderbook = pyupbit.get_orderbook(ticker)
        if not orderbook or 'orderbook_units' not in orderbook:
            return None
        
        units = orderbook['orderbook_units']
        
        # 매수/매도 호가 합계
        total_bid_size = sum([unit['bid_size'] for unit in units])
        total_ask_size = sum([unit['ask_size'] for unit in units])
        
        # 매수/매도 호가 금액
        total_bid_price = sum([unit['bid_price'] * unit['bid_size'] for unit in units])
        total_ask_price = sum([unit['ask_price'] * unit['ask_size'] for unit in units])
        
        # 채결 강도 = (매수 호가 / 매도 호가) * 100
        strength = (total_bid_size / total_ask_size * 100) if total_ask_size > 0 else 100
        
        # 호가 금액 기준 강도
        price_strength = (total_bid_price / total_ask_price * 100) if total_ask_price > 0 else 100
        
        return {
            'strength': strength,  # 수량 기준
            'price_strength': price_strength,  # 금액 기준
            'bid_size': total_bid_size,
            'ask_size': total_ask_size,
            'bid_price': total_bid_price,
            'ask_price': total_ask_price,
            'timestamp': datetime.now()
        }
    except:
        return None

def check_orderbook_surge(ticker, bot_state):
    """채결 강도 변화 감지 - 매수세 유입 포착"""
    try:
        # 현재 채결 강도
        current = calculate_orderbook_strength(ticker)
        if not current:
            return None
        
        # 이전 채결 강도
        history = bot_state.get('orderbook_history', {})
        prev = history.get(ticker)
        
        # 현재 강도 저장
        history[ticker] = current
        bot_state['orderbook_history'] = history
        
        # 이전 기록이 없으면 판단 불가
        if not prev:
            return None
        
        # 채결 강도 변화
        strength_change = current['strength'] - prev['strength']
        
        # 매수세 급증 감지
        if current['strength'] > 150 and strength_change > 30:
            return {
                'type': 'ORDERBOOK_SURGE',
                'strength': current['strength'],
                'prev_strength': prev['strength'],
                'change': strength_change,
                'signal': f'💪 채결강도 급증 ({prev["strength"]:.0f}% → {current["strength"]:.0f}%)'
            }
        
        return None
    except:
        return None

def check_market_direction():
    """시장 방향성 체크 - BTC & ETH로 판단"""
    try:
        # 현재가
        btc = pyupbit.get_current_price('KRW-BTC')
        eth = pyupbit.get_current_price('KRW-ETH')
        
        if not btc or not eth:
            return None
        
        # 5분봉 데이터 (10개 = 50분)
        df_btc = pyupbit.get_ohlcv('KRW-BTC', interval='minute5', count=10)
        df_eth = pyupbit.get_ohlcv('KRW-ETH', interval='minute5', count=10)
        
        if df_btc is None or df_eth is None or len(df_btc) < 10:
            return None
        
        # 변화율 계산 (50분 전 대비)
        btc_ago = df_btc['close'].iloc[0]
        eth_ago = df_eth['close'].iloc[0]
        
        btc_change = ((btc - btc_ago) / btc_ago) * 100
        eth_change = ((eth - eth_ago) / eth_ago) * 100
        
        # 시장 방향 판단
        if btc_change > 0.5 and eth_change > 0.3:
            direction = 'STRONG_UP'  # 강한 상승
            score = 1.0
        elif btc_change > 0.2:
            direction = 'UP'  # 약한 상승
            score = 0.8
        elif btc_change < -0.5 and eth_change < -0.3:
            direction = 'STRONG_DOWN'  # 강한 하락
            score = 0.0  # 매수 금지!
        elif btc_change < -0.2:
            direction = 'DOWN'  # 약한 하락
            score = 0.3
        else:
            direction = 'NEUTRAL'  # 보합
            score = 0.6
        
        return {
            'direction': direction,
            'score': score,
            'btc_change': btc_change,
            'eth_change': eth_change,
            'btc_price': btc,
            'eth_price': eth
        }
    except:
        return None

# ═══════════════════════════════════════════════════════
# 🚀 급등 감지
# ═══════════════════════════════════════════════════════
def detect_surge_signal(ticker):
    """급등 신호 감지 - 누적 상승 체크"""
    try:
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
        if df_1m is None or len(df_1m) < 10:
            return None
        
        price_now = df_1m['close'].iloc[-1]
        
        # 여러 시간대 상승률 체크
        surge_signals = []
        max_surge = 0
        
        # 1분 전 대비
        price_1m_ago = df_1m['close'].iloc[-2]
        surge_1m = ((price_now - price_1m_ago) / price_1m_ago) * 100
        
        # 3분 전 대비
        if len(df_1m) >= 4:
            price_3m_ago = df_1m['close'].iloc[-4]
            surge_3m = ((price_now - price_3m_ago) / price_3m_ago) * 100
            max_surge = max(max_surge, surge_3m)
            if surge_3m >= 3.0:
                surge_signals.append(f'3분 +{surge_3m:.2f}%')
        
        # 5분 전 대비 (진짜 급등)
        if len(df_1m) >= 6:
            price_5m_ago = df_1m['close'].iloc[-6]
            surge_5m = ((price_now - price_5m_ago) / price_5m_ago) * 100
            max_surge = max(max_surge, surge_5m)
            if surge_5m >= 5.0:
                surge_signals.append(f'5분 +{surge_5m:.2f}%')
        
        # 10분 전 대비 (대형 급등)
        if len(df_1m) >= 11:
            price_10m_ago = df_1m['close'].iloc[-11]
            surge_10m = ((price_now - price_10m_ago) / price_10m_ago) * 100
            max_surge = max(max_surge, surge_10m)
            if surge_10m >= 8.0:
                surge_signals.append(f'10분 +{surge_10m:.2f}%')
        
        # 거래량 체크
        vol_spike = calculate_volume_spike(df_1m)
        
        # 🔥 실시간 채결 강도 체크 (핵심!)
        orderbook = calculate_orderbook_strength(ticker)
        strength = orderbook['strength'] if orderbook else 100
        price_strength = orderbook['price_strength'] if orderbook else 100
        
        # 채결 강도가 높으면 점수 가산
        strength_bonus = 0
        if strength > 150:  # 매수세 압도적
            strength_bonus = 3
            surge_signals.append(f'💪 채결강도 {strength:.0f}%')
        elif strength > 120:  # 매수세 강함
            strength_bonus = 2
            surge_signals.append(f'💪 채결강도 {strength:.0f}%')
        elif strength > 100:  # 매수세 우위
            strength_bonus = 1
        
        # 🔥🔥🔥 초강력 급등 조건: 10% 이상만 포착! 🔥🔥🔥
        # 조건 1: 10분 내 12% 이상 (대박 급등!)
        # 조건 2: 5분 내 10% 이상 + 거래량 1.5배 이상
        # 조건 3: 3분 내 8% 이상 + 거래량 2.0배 이상
        # 조건 4: 1분 내 10% 이상 (초강력 급등!)
        
        is_surge = False
        score = 0
        
        # 1분 10% 급등 (초강력!)
        if surge_1m >= 10.0:
            is_surge = True
            score = 15 + strength_bonus
            surge_signals.append(f'🔥 1분 초강력 급등!')
        # 10분 12% 대박 급등
        elif max_surge >= 12.0:
            is_surge = True
            score = 12 + strength_bonus
            surge_signals.append(f'🚀 대박 급등!')
        # 5분 10% + 거래량
        elif max_surge >= 10.0 and vol_spike >= 1.5:
            is_surge = True
            score = 11 + strength_bonus
            surge_signals.append(f'거래량 {vol_spike:.1f}배')
        # 3분 8% + 거래량 폭증
        elif surge_3m >= 8.0 and vol_spike >= 2.0:
            is_surge = True
            score = 10 + strength_bonus
            surge_signals.append(f'거래량 {vol_spike:.1f}배')
        # 10% 이상 급등 (거래량 무관)
        elif max_surge >= 10.0:
            is_surge = True
            score = 10 + strength_bonus
        
        if is_surge:
            return {
                'type': 'SURGE',
                'ticker': ticker,
                'current_price': price_now,
                'change_pct': max_surge,
                'vol_spike': vol_spike,
                'orderbook_strength': strength,  # 채결 강도 추가
                'signals': surge_signals if surge_signals else [f'급등 +{max_surge:.2f}%'],
                'score': score
            }
        
        return None
    except:
        return None

# ═══════════════════════════════════════════════════════
# 📉 급락 감지
# ═══════════════════════════════════════════════════════
def detect_panic_sell_dip(ticker):
    """패닉 매도 + 하방 꼬리 감지 → DIP HUNTER"""
    try:
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
        if df_1m is None or len(df_1m) < 20:
            return None
        
        # 볼린저 밴드 계산
        df_1m['ma20'] = df_1m['close'].rolling(window=20).mean()
        df_1m['std20'] = df_1m['close'].rolling(window=20).std()
        df_1m['bb_lower'] = df_1m['ma20'] - (df_1m['std20'] * 2)
        
        # 최근 봉
        last = df_1m.iloc[-1]
        prev = df_1m.iloc[-2]
        
        # 1. 하방 꼬리 길이 (롱 테일) - 패닉 매도의 증거
        body_size = abs(last['close'] - last['open'])
        lower_tail = min(last['open'], last['close']) - last['low']
        tail_ratio = lower_tail / body_size if body_size > 0.01 else 0
        
        # 2. 급락 폭
        drop = ((last['close'] - prev['close']) / prev['close']) * 100
        
        # 3. 볼린저 하단 돌파 (공포 과매도)
        bb_pierce = ((last['low'] - last['bb_lower']) / last['bb_lower']) * 100
        
        # 4. 거래량 폭발 (패닉)
        vol_avg = df_1m['volume'].iloc[-10:-1].mean()
        vol_spike = last['volume'] / vol_avg if vol_avg > 0 else 1
        
        # 5. RSI 과매도
        rsi = calculate_rsi(df_1m)
        
        # DIP 신호 점수
        signals = []
        score = 0
        
        # 긴 하방 꼬리 (핵심!)
        if tail_ratio > 2:
            score += 4
            signals.append(f'🔻 긴 꼬리 {tail_ratio:.1f}배')
        elif tail_ratio > 1.5:
            score += 2
            signals.append(f'하방 꼬리 {tail_ratio:.1f}배')
        
        # 급락
        if drop < -3:
            score += 3
            signals.append(f'급락 {drop:.1f}%')
        elif drop < -2:
            score += 2
            signals.append(f'하락 {drop:.1f}%')
        
        # 볼린저 하단 돌파
        if bb_pierce < -1:
            score += 3
            signals.append(f'볼린저 돌파 {bb_pierce:.1f}%')
        elif bb_pierce < -0.5:
            score += 2
            signals.append(f'볼린저 근접')
        
        # 거래량 폭발
        if vol_spike > 2:
            score += 2
            signals.append(f'거래량 {vol_spike:.1f}배')
        
        # RSI 과매도
        if rsi < 30:
            score += 2
            signals.append(f'RSI {rsi:.0f}')
        
        # DIP HUNTER 발동 조건: 점수 8 이상
        if score >= 8:
            return {
                'type': 'PANIC_DIP',
                'ticker': ticker,
                'current_price': last['close'],
                'drop': drop,
                'tail_ratio': tail_ratio,
                'bb_pierce': bb_pierce,
                'vol_spike': vol_spike,
                'rsi': rsi,
                'signals': signals,
                'score': score
            }
        
        return None
    except:
        return None

def detect_dip_signal(ticker):
    """급락 신호 감지 - 원가 복귀 전략"""
    try:
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
        if df_1m is None or len(df_1m) < 15:
            return None
        
        # 급락 전 평균가
        price_before_dip = df_1m['close'].iloc[-12:-2].mean()
        price_now = df_1m['close'].iloc[-1]
        price_prev = df_1m['close'].iloc[-2]
        
        change_1m = ((price_now - price_prev) / price_prev) * 100
        dip_from_peak = ((price_now - price_before_dip) / price_before_dip) * 100
        
        vol_spike = calculate_volume_spike(df_1m)
        rsi = calculate_rsi(df_1m)
        
        score = 0
        signals = []
        
        if change_1m <= SURGE_CONFIG['dip_threshold_1m']:
            score += 3
            signals.append(f'급락 {change_1m:.2f}%')
        
        if vol_spike >= SURGE_CONFIG['dip_volume_spike']:
            score += 2
            signals.append(f'거래량 {vol_spike:.1f}배')
        
        if rsi <= SURGE_CONFIG['dip_oversold_rsi']:
            score += 2
            signals.append(f'RSI {rsi:.1f}')
        
        if dip_from_peak <= -3.0:
            score += 2
            signals.append(f'피크대비 {dip_from_peak:.2f}%')
        
        if score >= 5:
            return {
                'type': 'DIP',
                'ticker': ticker,
                'current_price': price_now,
                'price_before_dip': price_before_dip,
                'change_1m': change_1m,
                'dip_from_peak': dip_from_peak,
                'vol_spike': vol_spike,
                'rsi': rsi,
                'signals': signals,
                'score': score
            }
        
        return None
    except:
        return None

# ═══════════════════════════════════════════════════════
# 📊 패턴 분석
# ═══════════════════════════════════════════════════════
def detect_box_range(ticker):
    """박스권 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=50)
        if df is None or len(df) < 30:
            return None
        
        recent_high = df['high'].iloc[-6:].max()
        recent_low = df['low'].iloc[-6:].min()
        range_pct = ((recent_high - recent_low) / recent_low) * 100
        
        if range_pct <= PATTERN_CONFIG['box_range_threshold']:
            current_price = df['close'].iloc[-1]
            box_position = (current_price - recent_low) / (recent_high - recent_low)
            
            return {
                'type': 'BOX_RANGE',
                'high': recent_high,
                'low': recent_low,
                'position': box_position,
                'confidence': 1.0 - (range_pct / PATTERN_CONFIG['box_range_threshold']),
                'action': 'BUY' if box_position < 0.3 else 'SELL' if box_position > 0.7 else 'HOLD'
            }
        return None
    except:
        return None

def detect_trend(ticker):
    """추세 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=70)
        if df is None or len(df) < 60:
            return None
        
        ma_short = df['close'].rolling(window=PATTERN_CONFIG['trend_ma_short']).mean()
        ma_long = df['close'].rolling(window=PATTERN_CONFIG['trend_ma_long']).mean()
        
        ma_short_now = ma_short.iloc[-1]
        ma_long_now = ma_long.iloc[-1]
        trend_strength = ((ma_short_now - ma_long_now) / ma_long_now) * 100
        
        if trend_strength >= PATTERN_CONFIG['uptrend_threshold']:
            return {
                'type': 'UPTREND',
                'strength': trend_strength,
                'confidence': min(trend_strength / 5.0, 1.0),
                'action': 'BUY'
            }
        return None
    except:
        return None

def detect_volume_pattern(ticker):
    """수급 패턴 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=30)
        if df is None or len(df) < 20:
            return None
        
        vol_avg = df['volume'].iloc[-20:-1].mean()
        vol_now = df['volume'].iloc[-1]
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1.0
        
        if vol_ratio >= PATTERN_CONFIG['volume_surge_ratio']:
            price_change = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            return {
                'type': 'VOLUME_SURGE',
                'ratio': vol_ratio,
                'price_change': price_change,
                'confidence': min(vol_ratio / 5.0, 1.0),
                'action': 'BUY' if price_change > 0 else 'WATCH'
            }
        return None
    except:
        return None

def detect_gap_down_reversal(ticker):
    """BNF Gap-Down Mean Reversion 전략 (급락 후 반등)"""
    try:
        # 1시간봉 데이터 (25개 필요)
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count=30)
        if df is None or len(df) < 26:
            return None
        
        current_price = df['close'].iloc[-1]
        ema_25 = calculate_ema(df, 25)
        
        # 1. Disparity 계산 (가격이 EMA보다 얼마나 떨어졌는지)
        disparity = ((current_price - ema_25) / ema_25) * 100
        
        # 2. 20% 이상 급락 조건 (암호화폐는 25%로 조정)
        if disparity > -25:
            return None
        
        # 3. RSI 과매도 확인
        rsi = calculate_rsi(df)
        if rsi > 30:
            return None
        
        # 4. MACD 반전 확인
        macd_data = calculate_macd(df)
        macd_reversal = (macd_data['prev_histogram'] < 0 and macd_data['histogram'] > 0)
        
        if macd_reversal:
            return {
                'type': 'GAP_DOWN_REVERSAL',
                'disparity': disparity,
                'rsi': rsi,
                'ema_25': ema_25,
                'macd_histogram': macd_data['histogram'],
                'confidence': min(abs(disparity) / 25.0, 1.0),
                'action': 'BUY',
                'stop_loss_price': df['low'].iloc[-5:].min(),  # 최근 5개 저점
                'target_price': current_price * 1.15  # 15% 목표 (1:3 위험 보상)
            }
        return None
    except Exception as e:
        log(f"Gap-Down 감지 오류: {e}", "ERROR")
        return None

def detect_squeeze_momentum(ticker):
    """Squeeze Momentum 전략 (4시간봉 모멘텀 추세)"""
    try:
        # 4시간봉 데이터
        df = pyupbit.get_ohlcv(ticker, interval="minute240", count=30)
        if df is None or len(df) < 25:
            return None
        
        # Bollinger Bands + Keltner Channels + Momentum
        squeeze_data = calculate_bollinger_keltner(df)
        
        # Momentum 방향 전환 감지 (빨강→초록)
        momentum_now = squeeze_data['momentum']
        momentum_prev = squeeze_data['prev_momentum']
        
        # 양수 모멘텀으로 전환 (상승 신호)
        if momentum_prev < 0 and momentum_now > 0:
            return {
                'type': 'SQUEEZE_MOMENTUM',
                'momentum': momentum_now,
                'squeeze_on': squeeze_data['squeeze_on'],
                'confidence': min(abs(momentum_now) / 1000, 1.0),
                'action': 'BUY',
                'exit_condition': 'momentum_turns_negative'
            }
        
        # 음수 모멘텀으로 전환 (하락 신호 - 청산용)
        if momentum_prev > 0 and momentum_now < 0:
            return {
                'type': 'SQUEEZE_MOMENTUM_EXIT',
                'momentum': momentum_now,
                'action': 'SELL'
            }
        
        return None
    except Exception as e:
        log(f"Squeeze Momentum 감지 오류: {e}", "ERROR")
        return None

def detect_ema_squeeze(ticker):
    """200/20 EMA Squeeze 전략 - SMA(200)과 SMA(20)의 스퀴즈 감지"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute15", count=220)
        if df is None or len(df) < 220:
            return None
        
        df['sma_200'] = df['close'].rolling(window=200).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        
        current_price = df['close'].iloc[-1]
        sma_200 = df['sma_200'].iloc[-1]
        sma_20 = df['sma_20'].iloc[-1]
        
        # 조건 1: 가격이 SMA(200) 위 + SMA(200) 상승 중
        if current_price < sma_200 or pd.isna(sma_200):
            return None
        if df['sma_200'].iloc[-1] <= df['sma_200'].iloc[-10]:
            return None
        
        # 조건 2: SMA(20)이 SMA(200)에 근접 (5% 이내)
        squeeze_ratio = abs(sma_20 - sma_200) / sma_200
        if squeeze_ratio > 0.05:
            return None
        
        # 조건 3: 최근 캔들이 긴 양봉으로 SMA(20) 돌파
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        body_size = abs(last_candle['close'] - last_candle['open'])
        candle_range = last_candle['high'] - last_candle['low']
        
        if candle_range == 0 or body_size / candle_range < 0.6:
            return None
        
        if last_candle['close'] <= last_candle['open']:
            return None
        
        if prev_candle['close'] < sma_20 and last_candle['close'] > sma_20:
            return {
                'type': 'EMA_SQUEEZE',
                'confidence': 0.85,
                'sma_200': sma_200,
                'sma_20': sma_20,
                'squeeze_ratio': squeeze_ratio,
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"EMA Squeeze 감지 오류: {e}", "ERROR")
        return None

def detect_testa_3sma(ticker):
    """테스타의 3중 이평선 정배열 전략"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=80)
        if df is None or len(df) < 80:
            return None
        
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_25'] = df['close'].rolling(window=25).mean()
        df['sma_75'] = df['close'].rolling(window=75).mean()
        
        current_price = df['close'].iloc[-1]
        sma_5 = df['sma_5'].iloc[-1]
        sma_25 = df['sma_25'].iloc[-1]
        sma_75 = df['sma_75'].iloc[-1]
        
        if pd.isna(sma_5) or pd.isna(sma_25) or pd.isna(sma_75):
            return None
        
        # 조건 1: SMA(75) 상승 중
        if df['sma_75'].iloc[-1] <= df['sma_75'].iloc[-10]:
            return None
        
        # 조건 2: 정배열 (SMA(25) > SMA(75))
        if sma_25 <= sma_75:
            return None
        
        # 조건 3: 양봉이 SMA(5) 돌파 + 거래량 증가
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        avg_volume = df['volume'].iloc[-10:-1].mean()
        if avg_volume == 0:
            return None
        
        volume_ratio = last_candle['volume'] / avg_volume
        
        if volume_ratio < 1.2:
            return None
        
        if last_candle['close'] <= last_candle['open']:
            return None
        
        if prev_candle['close'] < sma_5 and last_candle['close'] > sma_5:
            return {
                'type': 'TESTA_3SMA',
                'confidence': 0.9,
                'sma_5': sma_5,
                'sma_25': sma_25,
                'sma_75': sma_75,
                'volume_ratio': volume_ratio,
                'entry_candle_low': last_candle['low'],
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"Testa 3SMA 감지 오류: {e}", "ERROR")
        return None

def detect_rsi_reversal(ticker):
    """RSI 필터 + 볼린저 밴드 + Engulfing 패턴 (Ross Cameron)"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute15", count=30)
        if df is None or len(df) < 30:
            return None
        
        # RSI 계산
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 볼린저 밴드 계산
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        df['bb_std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
        
        current_rsi = df['rsi'].iloc[-1]
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        if pd.isna(current_rsi) or pd.isna(df['bb_lower'].iloc[-1]):
            return None
        
        # 조건 1: RSI < 30 (과매도)
        if current_rsi >= 30:
            return None
        
        # 조건 2: 가격이 볼린저 하단 터치
        if last_candle['low'] > df['bb_lower'].iloc[-1]:
            return None
        
        # 조건 3: Bullish Engulfing 패턴
        is_engulfing = (
            prev_candle['close'] < prev_candle['open'] and
            last_candle['close'] > last_candle['open'] and
            last_candle['close'] > prev_candle['open'] and
            last_candle['open'] < prev_candle['close']
        )
        
        if is_engulfing:
            return {
                'type': 'RSI_REVERSAL',
                'confidence': 0.88,
                'rsi': current_rsi,
                'bb_lower': df['bb_lower'].iloc[-1],
                'bb_upper': df['bb_upper'].iloc[-1],
                'pattern': 'Bullish Engulfing',
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"RSI Reversal 감지 오류: {e}", "ERROR")
        return None

def detect_volume_breakout_v2(ticker):
    """거래량 감소 → 급증 + 고점 돌파"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=30)
        if df is None or len(df) < 30:
            return None
        
        # 거래량 감소 → 급증 패턴
        volume_avg = df['volume'].iloc[-10:-2].mean()
        prev_volume = df['volume'].iloc[-2]
        current_volume = df['volume'].iloc[-1]
        
        if volume_avg == 0:
            return None
        
        # 조건 1: 이전 거래량이 평균보다 감소
        if prev_volume > volume_avg * 0.8:
            return None
        
        # 조건 2: 현재 거래량이 급증 (평균의 150% 이상)
        if current_volume < volume_avg * 1.5:
            return None
        
        # 조건 3: 현재 캔들이 이전 캔들의 고점 돌파
        if df['close'].iloc[-1] <= df['high'].iloc[-2]:
            return None
        
        # 조건 4: 양봉이어야 함
        if df['close'].iloc[-1] <= df['open'].iloc[-1]:
            return None
        
        return {
            'type': 'VOLUME_BREAKOUT_V2',
            'confidence': 0.82,
            'volume_ratio': current_volume / volume_avg,
            'breakout_price': df['high'].iloc[-2],
            'action': 'BUY'
        }
    except Exception as e:
        log(f"Volume Breakout V2 감지 오류: {e}", "ERROR")
        return None

def detect_mach7_pullback(ticker):
    """마하7의 이평선 눌림목 스캘핑 (1분봉)"""
    try:
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=120)
        if df is None or len(df) < 120:
            return None
        
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_100'] = df['close'].ewm(span=100, adjust=False).mean()
        
        current_price = df['close'].iloc[-1]
        ema_20 = df['ema_20'].iloc[-1]
        ema_50 = df['ema_50'].iloc[-1]
        ema_100 = df['ema_100'].iloc[-1]
        
        if pd.isna(ema_20) or pd.isna(ema_50) or pd.isna(ema_100):
            return None
        
        # 조건 1: 정배열 (EMA(20) > EMA(50) > EMA(100))
        if not (ema_20 > ema_50 > ema_100):
            return None
        
        # 조건 2: 가격이 EMA(100) 위에 있음
        if current_price < ema_100:
            return None
        
        # 조건 3: 눌림목 (이전에 EMA(20) 아래로 내려갔다가 다시 위로)
        prev_price = df['close'].iloc[-2]
        if prev_price >= ema_20:
            return None
        
        if current_price <= ema_20:
            return None
        
        # 조건 4: Williams Fractal 시뮬레이션 (최근 7개 캔들 중 최저점)
        recent_lows = df['low'].iloc[-7:]
        is_fractal = df['low'].iloc[-4] == recent_lows.min()
        
        if is_fractal:
            return {
                'type': 'MACH7_PULLBACK',
                'confidence': 0.92,
                'ema_20': ema_20,
                'ema_50': ema_50,
                'ema_100': ema_100,
                'stop_loss': ema_50,
                'action': 'BUY'
            }
        
        return None
    except Exception as e:
        log(f"Mach7 Pullback 감지 오류: {e}", "ERROR")
        return None

def analyze_all_patterns(ticker):
    """모든 패턴 종합 분석"""
    patterns = {}
    
    # 급등/급락 우선
    surge = detect_surge_signal(ticker)
    if surge:
        patterns['surge'] = surge
        # 급등 감지 시 즉시 로깅
        log(f"🚀🚀🚀 급등 감지! {ticker} {surge['change_pct']:.2f}% 상승! 신호: {surge.get('signals', [])}", "SUCCESS")
    
    # 패닉 매도 DIP (NEW! - 하락장에서도 매수)
    panic_dip = detect_panic_sell_dip(ticker)
    if panic_dip:
        patterns['panic_dip'] = panic_dip
        log(f"🔻🔻🔻 패닉 매도 감지! {ticker} 하방 꼬리 {panic_dip['tail_ratio']:.1f}배! 신호: {panic_dip.get('signals', [])}", "SUCCESS")
    
    dip = detect_dip_signal(ticker)
    if dip:
        patterns['dip'] = dip
    
    # 새로운 전략들
    gap_down = detect_gap_down_reversal(ticker)
    if gap_down:
        patterns['gap_down'] = gap_down
    
    squeeze = detect_squeeze_momentum(ticker)
    if squeeze:
        patterns['squeeze'] = squeeze
    
    # 기타 패턴
    box = detect_box_range(ticker)
    if box:
        patterns['box'] = box
    
    trend = detect_trend(ticker)
    if trend:
        patterns['trend'] = trend
    
    volume = detect_volume_pattern(ticker)
    if volume:
        patterns['volume'] = volume
    
    # v10.24 신규 전략들
    ema_squeeze = detect_ema_squeeze(ticker)
    if ema_squeeze:
        patterns['ema_squeeze'] = ema_squeeze
    
    testa = detect_testa_3sma(ticker)
    if testa:
        patterns['testa'] = testa
    
    rsi_rev = detect_rsi_reversal(ticker)
    if rsi_rev:
        patterns['rsi_reversal'] = rsi_rev
    
    vol_break = detect_volume_breakout_v2(ticker)
    if vol_break:
        patterns['volume_breakout_v2'] = vol_break
    
    mach7 = detect_mach7_pullback(ticker)
    if mach7:
        patterns['mach7'] = mach7
    
    return patterns

# ═══════════════════════════════════════════════════════
# 🏆 전략 선택
# ═══════════════════════════════════════════════════════
def select_best_strategy(ticker, patterns):
    """최적 전략 선택"""
    strategy_scores = {}
    
    for strategy_id, strategy in bot_state['strategy_performance'].items():
        if not strategy['enabled']:
            continue
        
        score = 0.0
        perf = strategy['performance']
        
        # 과거 성과
        if perf['trades'] > 0:
            win_rate = perf['wins'] / perf['trades']
            avg_profit = perf['total_profit'] / perf['trades']
            score += (win_rate * avg_profit * strategy['weight']) * 0.5
        
        # 패턴 매칭
        if 'surge' in patterns and strategy_id == 'surge_hunter':
            score += patterns['surge'].get('score', 5) * 0.5
        elif 'dip' in patterns and strategy_id == 'dip_hunter':
            score += patterns['dip'].get('score', 5) * 0.5
        elif 'gap_down' in patterns and strategy_id == 'gap_down_reversal':
            score += patterns['gap_down'].get('confidence', 0.5) * 5 * 0.5
        elif 'squeeze' in patterns and strategy_id == 'squeeze_momentum':
            score += patterns['squeeze'].get('confidence', 0.5) * 5 * 0.5
        elif 'box' in patterns and strategy_id == 'box_trader':
            score += patterns['box']['confidence'] * 5 * 0.5
        elif 'trend' in patterns and strategy_id == 'trend_follower':
            score += patterns['trend']['confidence'] * 5 * 0.5
        elif 'volume' in patterns and strategy_id == 'volume_hunter':
            score += patterns['volume']['confidence'] * 5 * 0.5
        # v10.24 신규 전략 매핑
        elif 'ema_squeeze' in patterns and strategy_id == 'ema_squeeze':
            score += patterns['ema_squeeze'].get('confidence', 0.5) * 5 * 0.5
        elif 'testa' in patterns and strategy_id == 'testa_3sma':
            score += patterns['testa'].get('confidence', 0.5) * 5 * 0.5
        elif 'rsi_reversal' in patterns and strategy_id == 'rsi_reversal':
            score += patterns['rsi_reversal'].get('confidence', 0.5) * 5 * 0.5
        elif 'volume_breakout_v2' in patterns and strategy_id == 'volume_breakout_v2':
            score += patterns['volume_breakout_v2'].get('confidence', 0.5) * 5 * 0.5
        elif 'mach7' in patterns and strategy_id == 'mach7_pullback':
            score += patterns['mach7'].get('confidence', 0.5) * 5 * 0.5
        
        strategy_scores[strategy_id] = score
    
    if strategy_scores:
        best = max(strategy_scores, key=strategy_scores.get)
        return best, strategy_scores[best]
    
    return None, 0.0

# ═══════════════════════════════════════════════════════
# 🧠 학습 시스템
# ═══════════════════════════════════════════════════════
def learn_from_trade(trade_result):
    """거래 결과 학습"""
    try:
        strategy_id = trade_result.get('strategy')
        success = trade_result.get('profit_rate', 0) > 0
        profit = trade_result.get('profit_rate', 0)
        
        if strategy_id and strategy_id in bot_state['strategy_performance']:
            perf = bot_state['strategy_performance'][strategy_id]['performance']
            perf['trades'] += 1
            if success:
                perf['wins'] += 1
            perf['total_profit'] += profit
            
            win_rate = (perf['wins'] / perf['trades'] * 100) if perf['trades'] > 0 else 0
            log(f"🧠 학습: {STRATEGIES[strategy_id]['name']} | 거래: {perf['trades']}회 | 승률: {win_rate:.1f}%", "LEARN")
        
        bot_state['trade_results'].append(trade_result)
        
        if len(bot_state['trade_results']) % LEARNING_CONFIG['learning_interval'] == 0:
            optimize_strategies()
    except:
        pass

def optimize_strategies():
    """전략 최적화"""
    try:
        log("🔄 전략 최적화 시작...", "LEARN")
        
        for strategy_id, strategy in bot_state['strategy_performance'].items():
            perf = strategy['performance']
            
            if perf['trades'] >= 5:
                win_rate = perf['wins'] / perf['trades']
                avg_profit = perf['total_profit'] / perf['trades']
                
                if win_rate >= 0.7 or avg_profit >= 3.0:
                    strategy['weight'] = min(strategy['weight'] * 1.1, 2.0)
                elif win_rate < 0.4 and avg_profit < 1.0:
                    strategy['weight'] = max(strategy['weight'] * 0.9, 0.5)
        
        best = max(bot_state['strategy_performance'].items(),
                   key=lambda x: (x[1]['performance']['wins'] / max(x[1]['performance']['trades'], 1)))
        bot_state['statistics']['best_strategy'] = best[0]
        
        log(f"✅ 최적 전략: {STRATEGIES[best[0]]['name']}", "SUCCESS")
    except:
        pass

# ═══════════════════════════════════════════════════════
# 🛡️ 복구 모드
# ═══════════════════════════════════════════════════════
def recover_funds_from_minus_coins():
    """
    ✅ 마이너스 코인 10%씩 매도해서 시드 확보
    - 실전 모드에서만 작동
    - 마이너스 포지션만 타겟팅
    - 각 코인의 10%씩 매도
    - 매도 대금을 현금으로 확보
    """
    if bot_state['mode'] != 'live':
        log("⚠️ 연습 모드에서는 복구 매도를 실행하지 않습니다", "WARNING")
        return 0
    
    total_recovered = 0
    upbit = bot_state.get('upbit')
    
    if not upbit:
        log("❌ Upbit API 객체가 없습니다", "ERROR")
        return 0
    
    log("="*80, "URGENT")
    log("🚨 마이너스 코인 복구 매도 시작", "URGENT")
    log("="*80, "URGENT")
    
    try:
        for ticker, holding in list(bot_state['simulation_holdings'].items()):
            # 마이너스 포지션만 처리
            if holding.get('profit', 0) >= 0:
                continue
            
            # 10% 매도 수량 계산
            sell_amount = holding['amount'] * 0.10
            current_price = pyupbit.get_current_price(ticker)
            
            if not current_price or sell_amount < 0.00001:
                continue
            
            # 수수료 0.05% 계산
            fee_rate = 0.0005
            sell_value = sell_amount * current_price
            fee = sell_value * fee_rate
            net_proceeds = sell_value - fee
            
            # 실제 매도 실행 (실전 모드)
            try:
                result = upbit.sell_market_order(ticker, sell_amount)
                
                if result:
                    log(f"✅ 복구 매도 성공: {ticker}", "SUCCESS")
                    log(f"   수량: {sell_amount:.6f}개", "INFO")
                    log(f"   매도가: {current_price:,.0f}원", "INFO")
                    log(f"   총액: {sell_value:,.0f}원", "INFO")
                    log(f"   수수료: {fee:,.0f}원 (0.05%)", "INFO")
                    log(f"   실수령: {net_proceeds:,.0f}원", "SUCCESS")
                    
                    # 보유량 갱신
                    holding['amount'] -= sell_amount
                    
                    # 현금 증가
                    bot_state['simulation_krw'] += net_proceeds
                    total_recovered += net_proceeds
                    
                    # 거래 기록
                    bot_state['recent_trades'].append({
                        'ticker': ticker,
                        'type': 'SELL (Recovery)',
                        'amount': sell_amount,
                        'price': current_price,
                        'fee': fee,
                        'net': net_proceeds,
                        'reason': f'마이너스 복구 (손실 {holding["profit_rate"]:.2f}%)',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    time.sleep(0.3)  # API 호출 제한 대비
                    
            except Exception as e:
                log(f"❌ {ticker} 매도 실패: {e}", "ERROR")
    
    except Exception as e:
        log(f"❌ 복구 매도 오류: {e}", "ERROR")
    
    log("="*80, "URGENT")
    log(f"✅ 복구 완료: 총 {total_recovered:,.0f}원 확보", "SUCCESS")
    log("="*80, "URGENT")
    
    return total_recovered

def check_recovery_mode_activation(bot_state):
    """복구 모드 활성화 체크"""
    try:
        if bot_state['recovery_mode_active']:
            return
        
        current_krw = bot_state['simulation_krw']
        holdings_value = sum(
            h['amount'] * (pyupbit.get_current_price(ticker) or h['avg_price'])
            for ticker, h in bot_state['simulation_holdings'].items()
        )
        total_value = current_krw + holdings_value
        
        initial_seed = bot_state['simulation_start_seed']
        loss_rate = ((total_value - initial_seed) / initial_seed) * 100
        
        if loss_rate <= RECOVERY_CONFIG['activate_loss_threshold']:
            log_separator()
            log(f"🛡️ 손실 복구 모드 활성화! 손실: {loss_rate:.2f}%", "URGENT")
            log_separator()
            
            # ✅ 실전 모드에서는 마이너스 코인 10% 매도로 시드 확보
            if bot_state['mode'] == 'live':
                recovered = recover_funds_from_minus_coins()
                current_krw = bot_state['simulation_krw']
                log(f"💰 복구 후 현금: {current_krw:,.0f}원", "SUCCESS")
            
            available_cash = current_krw
            recovery_seed = max(available_cash * RECOVERY_CONFIG['recovery_cash_ratio'], 50000)
            
            loss_amount = abs(total_value - initial_seed)
            recovery_target = loss_amount * RECOVERY_CONFIG['recovery_target_rate']
            
            bot_state['recovery_mode_active'] = True
            bot_state['recovery_seed'] = recovery_seed
            bot_state['recovery_target_amount'] = recovery_target
            bot_state['recovery_trades'] = 0
            bot_state['recovery_success_trades'] = 0
            bot_state['recovery_total_profit'] = 0
            
            bot_state['frozen_holdings'] = bot_state['simulation_holdings'].copy()
            bot_state['simulation_holdings'] = {}
            
            log(f"💰 복구 시드: {recovery_seed:,.0f}원", "RECOVERY")
            log(f"🎯 복구 목표: {recovery_target:,.0f}원", "RECOVERY")
            log(f"❄️ 기존 코인: {len(bot_state['frozen_holdings'])}개 동결", "RECOVERY")
    except:
        pass

def find_recovery_opportunity(tickers, bot_state):
    """복구용 초단타 기회"""
    opportunities = []
    
    for ticker in tickers:
        try:
            df = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
            if df is None or len(df) < 15:
                continue
            
            current_price = df['close'].iloc[-1]
            rsi = calculate_rsi(df)
            vol_spike = calculate_volume_spike(df)
            
            score = 0
            signals = []
            
            if 25 <= rsi <= 35 and vol_spike >= 1.5:
                score += 5
                signals.append(f"RSI {rsi:.1f}")
            
            change_1m = ((df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
            if vol_spike >= 2.5 and change_1m > 0.5:
                score += 4
                signals.append(f"수급 {vol_spike:.1f}배")
            
            if score >= 7:
                opportunities.append({
                    'ticker': ticker,
                    'price': current_price,
                    'score': score,
                    'signals': signals
                })
            
            time.sleep(0.05)
        except:
            continue
    
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    return opportunities

# ═══════════════════════════════════════════════════════
# 🎯 코인 규모 분류 (거래대금 기준)
# ═══════════════════════════════════════════════════════
def get_coin_tier(ticker):
    """
    코인 규모 분류 및 전략 파라미터 반환
    
    Returns:
        dict: {
            'tier': 'major' | 'mid' | 'small' | 'micro',
            'stop_loss': -8 ~ -20,
            'take_profit': [5,7,10] ~ [15,20,30],
            'dca_thresholds': [-2,-4,-6,-8] ~ [-4,-8,-12,-16]
        }
    """
    try:
        # 24시간 거래대금 계산
        df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
        if df is None or len(df) == 0:
            return {'tier': 'unknown', 'name': '미분류', 'stop_loss': -10, 'take_profit': [5,7,10], 'dca_thresholds': [-2,-4,-6,-8]}
        
        volume_krw = df['close'].iloc[-1] * df['volume'].iloc[-1]
        volume_billion = volume_krw / 100_000_000  # 억원 단위
        
        # 규모 분류
        if volume_billion >= 10000:  # 1조원 이상
            return {
                'tier': 'major',
                'name': '메이저',
                'stop_loss': -8,
                'take_profit': [5, 7, 10],
                'dca_thresholds': [-2, -4, -6, -8]
            }
        elif volume_billion >= 1000:  # 1000억~1조
            return {
                'tier': 'mid',
                'name': '중형',
                'stop_loss': -10,
                'take_profit': [7, 10, 15],
                'dca_thresholds': [-2, -4, -6, -8]
            }
        elif volume_billion >= 100:  # 100억~1000억
            return {
                'tier': 'small',
                'name': '소형',
                'stop_loss': -15,
                'take_profit': [10, 15, 20],
                'dca_thresholds': [-3, -6, -9, -12]
            }
        else:  # 100억 이하
            return {
                'tier': 'micro',
                'name': '초소형',
                'stop_loss': -20,
                'take_profit': [15, 20, 30],
                'dca_thresholds': [-4, -8, -12, -16]
            }
    except Exception as e:
        log(f"❌ 코인 규모 분류 실패 ({ticker}): {e}", "ERROR")
        # 기본값 반환 (중형 알트 기준)
        return {
            'tier': 'unknown',
            'name': '미분류',
            'stop_loss': -10,
            'take_profit': [7, 10, 15],
            'dca_thresholds': [-2, -4, -6, -8]
        }

# ═══════════════════════════════════════════════════════
# 💰 거래 실행
# ═══════════════════════════════════════════════════════
def execute_trade(ticker, strategy_id, patterns, bot_state):
    """거래 실행 (수수료 0.05% 포함)"""
    try:
        # 🚨 투자유의 종목 차단 (필수!)
        try:
            import requests
            response = requests.get("https://api.upbit.com/v1/market/all?isDetails=true", timeout=3)
            if response.status_code == 200:
                markets = response.json()
                for market in markets:
                    if market['market'] == ticker and market.get('market_warning') == 'CAUTION':
                        log(f"🚫 {ticker} 매수 차단: 투자유의 종목!", "WARNING")
                        return None
            else:
                # API 호출 실패 시 안전하게 차단!
                log(f"⚠️ {ticker} 매수 보류: 투자유의 종목 확인 실패 (API 오류)", "WARNING")
                return None
        except Exception as e:
            # 네트워크 오류 등 발생 시 안전하게 차단!
            log(f"⚠️ {ticker} 매수 보류: 투자유의 종목 확인 실패 ({str(e)})", "WARNING")
            return None
        
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        # 🎯 코인 규모 분류
        coin_tier = get_coin_tier(ticker)
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            invest_amount = bot_state['recovery_seed']
        else:
            # 🔥 v12.2 초소액 최적화: 1차 진입 6,000원 (초소액 리스크)
            # 물타기: 6K→10K→20K→30K→30K→100K (총 19.6만원)
            invest_amount = min(bot_state['simulation_krw'] * 0.01, 6000)  # 🎯 v12.2: 초기 진입 6,000원
        
        if invest_amount < 5000:
            return None
        
        # ✅ 수수료 0.05% 계산
        FEE_RATE = 0.0005
        fee = invest_amount * FEE_RATE
        net_invest = invest_amount - fee  # 실제 매수에 사용되는 금액
        
        buy_amount = net_invest / current_price  # 수수료 제외 후 실제 매수 수량
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            bot_state['recovery_seed'] -= invest_amount
            bot_state['recovery_trades'] += 1
        else:
            bot_state['simulation_krw'] -= invest_amount
        
        holding_info = {
            'amount': buy_amount,
            'avg_price': current_price,
            'invested': invest_amount,
            'fee_paid': fee,  # ✅ 지불한 수수료 기록
            'net_invested': net_invest,  # ✅ 실제 투자 금액
            'entry_time': datetime.now(),
            'strategy': strategy_id,
            'patterns': patterns,
            'peak_price': current_price,
            'type': 'RECOVERY' if bot_state['recovery_mode_active'] else patterns.get('type', 'NORMAL'),
            'coin_tier': coin_tier,  # 🎯 코인 규모 정보 저장
            'dca_count': 0,  # 🎯 물타기 횟수 (0 = 1차 진입)
            'first_entry_price': current_price,  # 🎯 최초 진입가
            'buy_reason': ""  # 매수 이유 (아래에서 설정)
        }
        
        # 급락 매수인 경우 원가 저장
        if 'dip' in patterns:
            holding_info['price_before_dip'] = patterns['dip'].get('price_before_dip', current_price)
        
        bot_state['simulation_holdings'][ticker] = holding_info
        
        # ✅ 상세 로그 - 매수 이유 포함
        coin_name = ticker.replace('KRW-', '')
        
        # 매수 이유 구성
        buy_reasons = []
        strategy_icon = STRATEGIES[strategy_id].get('icon', '📊')
        buy_reasons.append(f"{strategy_icon} {STRATEGIES[strategy_id]['name']}")
        
        if patterns.get('rsi'):
            rsi_val = patterns['rsi'].get('value', 0)
            if rsi_val < 30:
                buy_reasons.append(f"RSI 과매도({rsi_val:.1f})")
            elif rsi_val > 70:
                buy_reasons.append(f"RSI 과매수({rsi_val:.1f})")
        
        if patterns.get('volume_surge'):
            surge = patterns['volume_surge'].get('ratio', 0)
            buy_reasons.append(f"거래량 급증 {surge:.1f}배")
        
        if patterns.get('price_surge'):
            surge_pct = patterns['price_surge'].get('ratio', 0) * 100
            buy_reasons.append(f"가격 급등 +{surge_pct:.1f}%")
        
        buy_reason_str = " | ".join(buy_reasons)
        
        # 매수 이유를 holding_info에 저장
        holding_info['buy_reason'] = buy_reason_str
        
        # 전략 아이콘과 이름 가져오기
        strategy_icon = STRATEGIES[strategy_id].get('icon', '📊')
        strategy_name = STRATEGIES[strategy_id]['name']
        
        log("="*60, "SUCCESS")
        log(f"✅ {'[복구]' if bot_state['recovery_mode_active'] else ''} 매수 신호 감지! {strategy_icon} {strategy_name}", "SUCCESS")
        log(f"   💎 코인: {coin_name} (등급: {coin_tier['name']})", "INFO")
        log(f"   📌 매수 이유: {buy_reason_str}", "INFO")
        log(f"   💰 매수가: {current_price:,.0f}원 / 수량: {buy_amount:.6f}개", "INFO")
        log(f"   💵 투자금: {invest_amount:,.0f}원 (수수료 {fee:,.0f}원)", "INFO")
        log(f"   🎯 목표: 익절 +{coin_tier['take_profit']}% / 손절 {coin_tier['stop_loss']}%", "INFO")
        log("="*60, "SUCCESS")
        
        # 거래 내역 추가 (상세 이유 포함)
        buy_reason = f"전략: {STRATEGIES[strategy_id]['name']}"
        
        # 패턴 정보 추가
        pattern_details = []
        if patterns.get('rsi'):
            rsi_val = patterns['rsi'].get('value', 0)
            if rsi_val < 30:
                pattern_details.append(f"RSI 과매도({rsi_val:.1f})")
            elif rsi_val > 70:
                pattern_details.append(f"RSI 과매수({rsi_val:.1f})")
        
        if patterns.get('volume_surge'):
            vol_change = patterns['volume_surge'].get('volume_change_pct', 0)
            pattern_details.append(f"거래량 급증(+{vol_change:.0f}%)")
        
        if patterns.get('dip'):
            dip_pct = patterns['dip'].get('dip_percent', 0)
            pattern_details.append(f"급락 후 반등({dip_pct:.1f}%)")
        
        if patterns.get('trend'):
            trend = patterns['trend'].get('trend', '')
            if trend:
                pattern_details.append(f"추세: {trend}")
        
        if pattern_details:
            buy_reason += " | " + ", ".join(pattern_details)
        
        bot_state['recent_trades'].append({
            'ticker': ticker,
            'type': 'BUY',
            'amount': buy_amount,
            'price': current_price,
            'invested': invest_amount,
            'fee': fee,
            'net_invested': net_invest,
            'strategy': STRATEGIES[strategy_id]['name'],
            'reason': buy_reason,
            'patterns': pattern_details,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'mode': bot_state.get('mode', 'practice')
        })
        
        # DB에 영구 저장
        user_id = bot_state.get('user_id', 'unknown')
        save_trade_to_db(user_id, bot_state['recent_trades'][-1])
        
        # 봇 상태도 DB에 저장 (simulation_holdings 포함)
        save_bot_state_to_db(user_id, bot_state)
        
        return True
    except Exception as e:
        log(f"거래 오류: {e}", "ERROR")
        return None

def check_exit(ticker, holding, bot_state):
    """청산 조건 체크"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return False, None
        
        entry_price = holding['avg_price']
        profit_rate = (current_price - entry_price) / entry_price * 100
        
        # 🎯 v12.3.1: 물타기 중일 때는 최초 진입가 기준으로 손절 판단!
        first_entry_price = holding.get('first_entry_price', entry_price)
        profit_from_first = (current_price - first_entry_price) / first_entry_price * 100
        dca_count = holding.get('dca_count', 0)
        
        strategy_id = holding.get('strategy')
        trade_type = holding.get('type')
        
        if current_price > holding.get('peak_price', 0):
            holding['peak_price'] = current_price
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            if profit_rate >= RECOVERY_CONFIG['recovery_target_profit']:
                return True, f"복구 익절 (+{profit_rate:.2f}%)"
            if profit_rate <= RECOVERY_CONFIG['recovery_stop_loss']:
                return True, f"복구 손절 ({profit_rate:.2f}%)"
            
            try:
                entry_time = holding['entry_time']
                if isinstance(entry_time, str):
                    from dateutil import parser
                    entry_time = parser.parse(entry_time)
                hold_time = (datetime.now() - entry_time).total_seconds() / 60
            except:
                hold_time = 0
            
            if hold_time >= RECOVERY_CONFIG['recovery_max_hold_time']:
                return True, "복구 시간초과"
        
        # 급락 매수 (원가 복귀)
        elif trade_type == 'DIP':
            price_before_dip = holding.get('price_before_dip', entry_price)
            back_to_original = (current_price - price_before_dip) / price_before_dip * 100
            
            if profit_rate <= SURGE_CONFIG['dip_emergency_stop']:
                return True, "급락 긴급손절"
            
            if back_to_original >= SURGE_CONFIG['dip_recovery_threshold']:
                return True, f"원가 복귀! (+{profit_rate:.2f}%)"
            
            try:
                entry_time = holding['entry_time']
                if isinstance(entry_time, str):
                    from dateutil import parser
                    entry_time = parser.parse(entry_time)
                hold_time = (datetime.now() - entry_time).total_seconds() / 60
            except:
                hold_time = 0
            
            if hold_time >= SURGE_CONFIG['dip_max_hold_time']:
                return True, "급락 최대시간"
        
        # 일반
        else:
            # 🎯 코인 규모별 손절/익절 기준 적용
            coin_tier = holding.get('coin_tier', {})
            if not coin_tier or 'stop_loss' not in coin_tier:
                # 기본값 (중형 알트 기준)
                coin_tier = {
                    'tier': 'unknown',
                    'name': '미분류',
                    'stop_loss': -10,
                    'take_profit': [7, 10, 15],
                    'dca_thresholds': [-2, -4, -6, -8]
                }
            
            # Squeeze Momentum 전략의 경우 모멘텀 반전 체크
            if strategy_id == 'squeeze_momentum':
                try:
                    squeeze_check = detect_squeeze_momentum(ticker)
                    if squeeze_check and squeeze_check.get('type') == 'SQUEEZE_MOMENTUM_EXIT':
                        return True, f"모멘텀 반전 ({profit_rate:+.2f}%)"
                except:
                    pass
            
            # Gap-Down Reversal 전략의 목표가 체크
            if strategy_id == 'gap_down_reversal':
                target_price = holding.get('target_price')
                if target_price and current_price >= target_price:
                    return True, f"목표가 도달 (+{profit_rate:.2f}%)"
            
            # 🔥 급등 매수 전략: 규모별 3단계 분할 익절!
            if trade_type == 'SURGE':
                # 분할 익절 단계 체크
                sold_stages = holding.get('sold_stages', [])  # 이미 매도한 단계
                
                take_profit_targets = coin_tier['take_profit']  # [5,7,10] or [10,15,20] 등
                
                # 3단계 (최고가, 남은 전량 매도)
                if profit_rate >= take_profit_targets[2] and 3 not in sold_stages:
                    return True, f"🚀 3단계 익절 +{profit_rate:.2f}% (전량 청산)"
                
                # 2단계 (중간가, 1/3 매도)
                if profit_rate >= take_profit_targets[1] and 2 not in sold_stages:
                    return 'PARTIAL_33', f"🚀 2단계 익절 +{profit_rate:.2f}% (33% 매도)"
                
                # 1단계 (최저가, 1/3 매도)
                if profit_rate >= take_profit_targets[0] and 1 not in sold_stages:
                    return 'PARTIAL_33', f"🚀 1단계 익절 +{profit_rate:.2f}% (33% 매도)"
                
                # ❌ 규모별 손절! (메이저 -8%, 중형 -10%, 소형 -15%, 초소형 -20%)
                stop_loss_threshold = coin_tier['stop_loss']
                
                # 🎯 물타기 중일 때는 최초 진입가 기준으로 손절 판단!
                if dca_count > 0:
                    # 물타기가 진행 중: 최초 진입가 대비로 판단
                    if profit_from_first <= stop_loss_threshold:
                        return True, f"💥 {coin_tier['name']} 손절 (최초가 대비 {profit_from_first:.2f}%, 물타기 {dca_count}회)"
                else:
                    # 1차 진입만 있음: 평균단가 대비로 판단
                    if profit_rate <= stop_loss_threshold:
                        return True, f"💥 {coin_tier['name']} 손절 ({profit_rate:.2f}%)"
            
            # 🔥 일반 전략: 3단계 분할 익절
            else:
                # 분할 익절 단계 체크
                sold_stages = holding.get('sold_stages', [])
                
                # 9% 도달: 3단계
                if profit_rate >= 9.0 and 3 not in sold_stages:
                    return True, f"✅ 3단계 익절 +{profit_rate:.2f}% (전량)"
                
                # 7% 도달: 2단계
                if profit_rate >= 7.0 and 2 not in sold_stages:
                    return 'PARTIAL_33', f"✅ 2단계 익절 +{profit_rate:.2f}% (33%)"
                
                # 5% 도달: 1단계
                if profit_rate >= 5.0 and 1 not in sold_stages:
                    return 'PARTIAL_33', f"✅ 1단계 익절 +{profit_rate:.2f}% (33%)"
                
                # ❌ 손절 판단 (물타기 중일 때는 최초 진입가 기준)
                if dca_count > 0:
                    # 물타기가 진행 중: 최초 진입가 대비 -10%에 손절
                    if profit_from_first <= -10.0:
                        return True, f"❌ 손절 (최초가 대비 {profit_from_first:.2f}%, 물타기 {dca_count}회)"
                else:
                    # 1차 진입만 있음: 평균단가 대비 -2%에 손절
                    if profit_rate <= -2.0:
                        return True, f"❌ 손절 ({profit_rate:.2f}%)"
        
        return False, None
    except Exception as e:
        log(f"❌ check_exit 오류 ({ticker}): {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return False, None

def execute_exit(ticker, holding, reason, bot_state, partial_ratio=1.0):
    """청산 실행 (수수료 0.05% 포함)
    partial_ratio: 매도 비율 (1.0=전량, 0.33=33%)
    """
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        # 🔥 분할 매도: 비율만큼만 매도
        total_amount = holding['amount']
        sell_amount = total_amount * partial_ratio
        
        entry_price = holding['avg_price']
        strategy_id = holding.get('strategy')
        invested = holding['invested']
        
        # ✅ 수수료 0.05% 계산
        FEE_RATE = 0.0005
        sell_value = sell_amount * current_price  # 매도 총액
        fee = sell_value * FEE_RATE  # 수수료
        net_proceeds = sell_value - fee  # 실제 받는 금액
        
        # 분할 매도 시 투자금도 비율만큼
        invested_portion = invested * partial_ratio
        profit_krw = net_proceeds - invested_portion  # 순수익
        profit_rate = (current_price - entry_price) / entry_price * 100
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            bot_state['recovery_seed'] += net_proceeds
            if profit_rate > 0:
                bot_state['recovery_success_trades'] += 1
                bot_state['recovery_total_profit'] += profit_krw
            else:
                bot_state['last_loss_time'] = datetime.now()
            
            progress = (bot_state['recovery_total_profit'] / bot_state['recovery_target_amount']) * 100
            bot_state['statistics']['recovery_progress'] = progress
            
            log(f"{'✅' if profit_rate > 0 else '❌'} 복구: {ticker} | {profit_rate:+.2f}% | {reason}", "RECOVERY" if profit_rate > 0 else "WARNING")
            log(f"📊 복구 진행: {progress:.1f}%", "RECOVERY")
            
            # 복구 완료
            if bot_state['recovery_total_profit'] >= bot_state['recovery_target_amount']:
                log_separator()
                log("🎉 복구 목표 달성!", "SUCCESS")
                log_separator()
                bot_state['recovery_mode_active'] = False
                bot_state['simulation_holdings'].update(bot_state['frozen_holdings'])
                bot_state['frozen_holdings'] = {}
        else:
            bot_state['simulation_krw'] += net_proceeds
            
            # ✅ 상세 로그
            coin_name = ticker.replace('KRW-', '')
            is_partial = partial_ratio < 1.0
            
            # 전략 정보 가져오기
            strategy_icon = STRATEGIES.get(strategy_id, {}).get('icon', '📊')
            strategy_name = STRATEGIES.get(strategy_id, {}).get('name', '전략')
            
            log("="*60, "SUCCESS" if profit_rate > 0 else "WARNING")
            log(f"💸 {strategy_icon} {strategy_name} | {'분할 ' if is_partial else ''}매도: {coin_name} ({int(partial_ratio*100)}%)", "SUCCESS" if profit_rate > 0 else "WARNING")
            log(f"   수량: {sell_amount:.6f}개 (전체: {total_amount:.6f})", "INFO")
            log(f"   매도가: {current_price:,.0f}원 (진입가: {entry_price:,.0f}원)", "INFO")
            log(f"   매도액: {sell_value:,.0f}원 (수수료 {fee:,.0f}원)", "INFO")
            log(f"   실수령: {net_proceeds:,.0f}원", "INFO")
            log(f"   순수익: {profit_krw:+,.0f}원 ({profit_rate:+.2f}%)", "SUCCESS" if profit_krw > 0 else "WARNING")
            log(f"   사유: {reason}", "INFO")
            if is_partial:
                log(f"   잔여: {total_amount - sell_amount:.6f}개", "INFO")
            log("="*60, "SUCCESS" if profit_rate > 0 else "WARNING")
            
            # 거래 내역 추가 (상세 이유 포함)
            try:
                entry_time = holding['entry_time']
                if isinstance(entry_time, str):
                    # 문자열이면 datetime으로 변환
                    from dateutil import parser
                    entry_time = parser.parse(entry_time)
                hold_time = (datetime.now() - entry_time).total_seconds() / 60
            except:
                hold_time = 0  # 오류 시 0분으로 설정
            
            hold_time_str = f"{int(hold_time//60)}시간 {int(hold_time%60)}분" if hold_time >= 60 else f"{int(hold_time)}분"
            
            sell_reason = f"{reason}"
            if profit_rate > 0:
                sell_reason += f" | 목표 달성 (+{profit_rate:.2f}%)"
            else:
                sell_reason += f" | 손절 ({profit_rate:.2f}%)"
            
            sell_reason += f" | 보유: {hold_time_str}"
            
            bot_state['recent_trades'].append({
                'ticker': ticker,
                'type': 'SELL',
                'amount': holding['amount'],
                'price': current_price,
                'entry_price': entry_price,
                'sell_value': sell_value,
                'fee': fee,
                'net_proceeds': net_proceeds,
                'profit': profit_krw,
                'profit_rate': profit_rate,
                'reason': sell_reason,
                'hold_time': hold_time,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'mode': bot_state.get('mode', 'practice')
            })
            
            # DB에 영구 저장
            user_id = bot_state.get('user_id', 'unknown')
            save_trade_to_db(user_id, bot_state['recent_trades'][-1])
            
            # 봇 상태도 DB에 저장 (simulation_holdings 업데이트)
            save_bot_state_to_db(user_id, bot_state)
        
        # 🔥 분할 매도 처리
        if partial_ratio < 1.0:
            # 일부만 매도 → 보유량 감소 & 단계 기록
            holding['amount'] = total_amount - sell_amount
            holding['invested'] = invested * (1 - partial_ratio)
            
            # 매도 단계 기록 (5%=1단계, 7%=2단계, 9%=3단계)
            if 'sold_stages' not in holding:
                holding['sold_stages'] = []
            
            if profit_rate >= 9.0:
                holding['sold_stages'].append(3)
            elif profit_rate >= 7.0:
                holding['sold_stages'].append(2)
            elif profit_rate >= 5.0:
                holding['sold_stages'].append(1)
            
            bot_state['simulation_holdings'][ticker] = holding
            log(f"🔥 분할 매도 완료: {ticker} 잔여 {holding['amount']:.6f}개", "SUCCESS")
        else:
            # 전량 매도 → 보유 삭제
            del bot_state['simulation_holdings'][ticker]
            log(f"✅ 전량 매도 완료: {ticker}", "SUCCESS")
        
        # 매도 후 DB에 한 번 더 저장 (holdings 업데이트 반영)
        save_bot_state_to_db(user_id, bot_state)
        
        # 학습
        trade_result = {
            'ticker': ticker,
            'strategy': strategy_id,
            'profit_rate': profit_rate,
            'profit_krw': profit_krw,
            'patterns': holding.get('patterns', {}),
            'timestamp': datetime.now()
        }
        learn_from_trade(trade_result)
        
        # 통계
        bot_state['statistics']['total_trades'] += 1
        if profit_rate > 0:
            bot_state['statistics']['winning_trades'] += 1
        else:
            bot_state['statistics']['losing_trades'] += 1
        bot_state['statistics']['total_profit'] += profit_rate
        
        return True
    except Exception as e:
        log(f"청산 오류: {e}", "ERROR")
        return None

# ═══════════════════════════════════════════════════════
# 🚀 Flask 웹 서버
# ═══════════════════════════════════════════════════════
app = Flask(__name__)
app.secret_key = 'upbit-trading-bot-secret-key-2026-v11'  # 🔧 고정 키로 변경 (재시작해도 세션 유지)
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 세션 24시간 유지
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_HTTPONLY'] = True
CORS(app)

# UserManager 초기화
user_manager = UserManager()

# 🔧 bot_states 테이블 초기화
init_bot_state_table()

# 💜 자이 기억 시스템 초기화
init_memory_tables()
print("✅ 자이(JAI) 기억 시스템 초기화 완료")

# 사용자별 봇 상태 저장 (user_id를 키로 사용)
user_bots = {}

@app.route('/')
def index():
    # 세션 확인
    if 'user_id' not in session:
        return redirect('/login')
    
    response = make_response(render_template('dashboard-ultimate-v2.html'))
    # 캐시 방지
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/status')
def api_status():
    try:
        # 세션 확인 - Guest 자동 생성하지 않음
        if 'user_id' not in session:
            # 로그인 필요
            return jsonify({
                'success': False,
                'message': '로그인이 필요합니다',
                'running': False,
                'current_krw': 0,
                'start_seed': 1000000,
                'current_seed': 1000000,
                'total_profit': 0,
                'profit_rate': 0,
                'win_rate': 0,
                'strategies': {},
                'holdings': [],
                'recent_surges': [],
                'recent_trades': []
            })
        
        # ✅ user_id는 숫자, 하지만 bot_state는 username(문자열)을 키로 사용
        username = session.get('username')
        if not username:
            return jsonify({
                'success': False,
                'message': '로그인이 필요합니다',
                'running': False,
                'current_krw': 0,
                'start_seed': 1000000,
                'current_seed': 1000000,
                'total_profit': 0,
                'profit_rate': 0,
                'win_rate': 0,
                'strategies': {},
                'holdings': [],
                'recent_surges': [],
                'recent_trades': []
            })
        
        bot_state = get_user_bot_state(username)
        
        # 봇이 실행 중이 아니면 초기 상태 반환
        if not bot_state['running']:
            return jsonify({
                'running': False,
                'current_krw': bot_state.get('simulation_seed', 1000000),
                'start_seed': bot_state.get('simulation_start_seed', bot_state.get('simulation_seed', 1000000)),
                'current_seed': bot_state.get('simulation_seed', 1000000),
                'total_profit': 0,
                'profit_rate': 0,
                'win_rate': 0,
                'strategies': bot_state['strategy_performance'],
                'holdings': [],
                'recent_surges': [],
                'recent_trades': []
            })
        
        # 봇 실행 중일 때만 실제 계산
        current_krw = bot_state['simulation_krw']
        
        # 보유 코인 가치 계산 + 상세 정보
        holdings_value = 0
        holdings_list = []
        
        if bot_state['simulation_holdings']:
            for ticker, h in bot_state['simulation_holdings'].items():
                try:
                    current_price = pyupbit.get_current_price(ticker)
                    if not current_price:
                        current_price = h['avg_price']
                    
                    coin_value = h['amount'] * current_price
                    holdings_value += coin_value
                    
                    # 평가 손익
                    profit = coin_value - (h['amount'] * h['avg_price'])
                    profit_rate = (profit / (h['amount'] * h['avg_price'])) * 100
                    
                    holdings_list.append({
                        'ticker': ticker,
                        'coin_name': ticker.replace('KRW-', ''),
                        'amount': h['amount'],
                        'avg_price': h['avg_price'],
                        'current_price': current_price,
                        'value': coin_value,
                        'profit': profit,
                        'profit_rate': profit_rate,
                        'buy_reason': h.get('buy_reason', '매수 신호 감지'),
                        'strategy': h.get('strategy', 'unknown'),
                        'strategy_name': STRATEGIES.get(h.get('strategy', 'unknown'), {}).get('name', '알 수 없음'),
                        'strategy_icon': STRATEGIES.get(h.get('strategy', 'unknown'), {}).get('icon', '❓'),
                        'entry_time': h.get('entry_time', ''),
                        'pattern': h.get('pattern', {}),
                        'dca_count': h.get('dca_count', 0),
                        'first_entry_price': h.get('first_entry_price', h['avg_price'])
                    })
                except:
                    holdings_value += h['amount'] * h['avg_price']
        
        # 동결 코인 가치 계산
        frozen_value = 0
        if bot_state['frozen_holdings']:
            for ticker, h in bot_state['frozen_holdings'].items():
                try:
                    current_price = pyupbit.get_current_price(ticker)
                    if current_price:
                        frozen_value += h['amount'] * current_price
                    else:
                        frozen_value += h['amount'] * h['avg_price']
                except:
                    frozen_value += h['amount'] * h['avg_price']
        
        total_value = current_krw + holdings_value + frozen_value
        
        total_trades = bot_state['statistics']['total_trades']
        winning_trades = bot_state['statistics']['winning_trades']
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        profit = total_value - bot_state['simulation_start_seed']
        profit_rate = (profit / bot_state['simulation_start_seed']) * 100 if bot_state['simulation_start_seed'] > 0 else 0
        
        # 최근 거래 내역 변환
        recent_trades = []
        for trade in list(bot_state.get('recent_trades', []))[-10:]:
            recent_trades.append({
                'ticker': trade['ticker'],
                'type': trade['type'],
                'amount': trade['amount'],
                'price': trade['price'],
                'timestamp': trade.get('timestamp', '')
            })
        
        # 전략별 보유 코인 개수 계산
        strategy_holdings = {}
        for h in holdings_list:
            strategy = h.get('strategy', 'unknown')
            if strategy not in strategy_holdings:
                strategy_holdings[strategy] = 0
            strategy_holdings[strategy] += 1
        
        return jsonify({
            'running': True,
            'current_krw': current_krw,
            'holdings_value': holdings_value,
            'total_value': total_value,
            'start_seed': bot_state.get('simulation_start_seed', bot_state.get('simulation_seed', 1000000)),
            'current_seed': bot_state.get('simulation_seed', 1000000),
            'total_profit': profit,
            'profit_rate': profit_rate,
            'win_rate': win_rate,
            'strategies': bot_state['strategy_performance'],
            'holdings': holdings_list,
            'recent_surges': [],
            'recent_trades': recent_trades,
            'status_message': bot_state.get('status_message', '🔍 스캔 중'),
            'status_emoji': bot_state.get('status_emoji', '🔍'),
            'status_detail': bot_state.get('status_detail', '거래 기회 탐색 중'),
            'max_positions': 10,
            'current_positions': len(holdings_list),
            'strategy_holdings': strategy_holdings  # 전략별 보유 코인 개수
        })
    except Exception as e:
        log(f"API 상태 조회 오류: {e}", "ERROR")
        return jsonify({'error': str(e)}), 500

@app.route('/history')
def history_page():
    """거래 히스토리 페이지"""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('history.html')

@app.route('/api/history')
def api_history():
    """거래 히스토리 API (DB에서 영구 저장된 데이터 조회)"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        username = session['username']
        mode = request.args.get('mode', 'practice')
        
        # DB에서 거래 내역 조회
        import sqlite3
        conn = sqlite3.connect('upbit_bot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM trade_history
            WHERE user_id = ? AND mode = ?
            ORDER BY timestamp DESC
            LIMIT 1000
        ''', (username, mode))
        
        db_trades = cursor.fetchall()
        conn.close()
        
        # 통계 계산
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        total_profit_rate = 0
        
        for trade in db_trades:
            if trade['trade_type'] == 'SELL':
                total_trades += 1
                profit_rate = trade['profit_rate'] or 0
                total_profit_rate += profit_rate
                
                if profit_rate >= 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_profit = (total_profit_rate / total_trades) if total_trades > 0 else 0
        
        # 거래 내역 변환
        trades_list = []
        for trade in db_trades:
            trade_data = {
                'ticker': trade['ticker'],
                'type': trade['trade_type'],
                'amount': trade['amount'],
                'price': trade['price'],
                'fee': trade['fee'] or 0,
                'timestamp': trade['timestamp'],
                'reason': trade['reason'] or '',
                'strategy': trade['strategy'] or '전략 미상',
                'mode': trade['mode']
            }
            
            if trade['trade_type'] == 'BUY':
                trade_data['invested'] = trade['invested'] or 0
                trade_data['net_invested'] = trade['net_invested'] or 0
            else:  # SELL
                trade_data['entry_price'] = trade['entry_price'] or 0
                trade_data['sell_value'] = trade['sell_value'] or 0
                trade_data['net_proceeds'] = trade['net_proceeds'] or 0
                trade_data['profit'] = trade['profit'] or 0
                trade_data['profit_rate'] = trade['profit_rate'] or 0
            
            trades_list.append(trade_data)
        
        return jsonify({
            'success': True,
            'trades': trades_list,
            'stats': {
                'total': total_trades,
                'winning': winning_trades,
                'losing': losing_trades,
                'win_rate': win_rate,
                'avg_profit': avg_profit
            },
            'mode': mode
        })
    except Exception as e:
        log(f"히스토리 API 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    try:
        # ✅ 사용자별 독립 봇 상태 가져오기
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        username = session['username']
        user_id = username  # 🔥 user_id 정의 추가!
        
        log(f"[START] username: {username}", "INFO")
        bot_state = get_user_bot_state(username)
        
        # ✅ 이 사용자의 봇이 실행 중인지 체크
        if bot_state['running']:
            return jsonify({'success': False, 'message': '이미 실행 중입니다. 먼저 정지해주세요.'})
        
        data = request.json or {}
        mode = data.get('mode', 'practice')
        seed = data.get('seed', 1000000)
        txid = data.get('txid', '')
        
        # 기존 시작 시드와 비교
        old_start_seed = bot_state.get('simulation_start_seed', None)
        seed_changed = (old_start_seed is not None and old_start_seed != seed)
        
        # 실전 모드 검증
        if mode == 'live':
            # 라이선스 검증 (TODO: TronScan API 연동)
            if not txid or len(txid) < 40:
                return jsonify({
                    'success': False, 
                    'message': '⚠️ 실전 모드는 라이선스 인증이 필요합니다!\n\n1. TXID를 입력하세요\n2. "🔐 라이선스 인증" 버튼을 클릭하세요'
                })
            
            # API 키 확인
            if not bot_state.get('upbit'):
                # config.json에서 API 키 로드 시도
                try:
                    import json
                    with open('config.json', 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        access_key = config.get('upbit_access_key', '')
                        secret_key = config.get('upbit_secret_key', '')
                        
                        if not access_key or not secret_key:
                            return jsonify({
                                'success': False,
                                'message': '⚠️ API 키를 먼저 설정해주세요!\n\n1. Access Key 입력\n2. Secret Key 입력\n3. "💾 저장" 클릭'
                            })
                        
                        # Upbit 객체 생성
                        bot_state['upbit'] = pyupbit.Upbit(access_key, secret_key)
                        log("실전 모드: API 키 로드 완료", "SUCCESS")
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'❌ API 키 로드 실패: {str(e)}'
                    })
            
            # 실전 모드 시드는 실제 잔고에서 가져오기
            try:
                real_balance = bot_state['upbit'].get_balance('KRW')
                if real_balance < 100000:  # 최소 10만원
                    return jsonify({
                        'success': False,
                        'message': f'⚠️ 잔고 부족!\n\n현재 잔고: {real_balance:,.0f}원\n최소 필요: 100,000원'
                    })
                seed = real_balance
                log(f"실전 모드: 실제 잔고 {seed:,}원", "SUCCESS")
                
                # ✅ 실전 모드: 현재 보유 코인 스캔 및 분석
                balances = bot_state['upbit'].get_balances()
                total_holdings_value = 0
                minus_count = 0
                
                for balance in balances:
                    ticker_code = balance['currency']
                    if ticker_code == 'KRW':
                        continue
                    
                    ticker = f'KRW-{ticker_code}'
                    amount = float(balance['balance'])
                    avg_price = float(balance['avg_buy_price'])
                    
                    if amount > 0:
                        current_price = pyupbit.get_current_price(ticker)
                        if current_price:
                            holding_value = amount * current_price
                            total_holdings_value += holding_value
                            
                            profit = (current_price - avg_price) * amount
                            profit_rate = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
                            
                            # 봇 상태에 기록
                            bot_state['simulation_holdings'][ticker] = {
                                'amount': amount,
                                'avg_price': avg_price,
                                'current_price': current_price,
                                'profit': profit,
                                'profit_rate': profit_rate
                            }
                            
                            # 마이너스 포지션 카운트
                            if profit < 0:
                                minus_count += 1
                                log(f"⚠️ 마이너스 포지션 발견: {ticker} | {profit:,.0f}원 ({profit_rate:.2f}%)", "WARNING")
                            else:
                                log(f"✅ 플러스 포지션: {ticker} | +{profit:,.0f}원 (+{profit_rate:.2f}%)", "SUCCESS")
                
                log(f"📊 현재 보유 분석 완료: 총 {len(bot_state['simulation_holdings'])}개 코인, 마이너스 {minus_count}개", "INFO")
                log(f"💰 보유 코인 가치: {total_holdings_value:,.0f}원", "INFO")
                
                # 복구 모드 자동 활성화 (마이너스 포지션이 3개 이상이면)
                if minus_count >= 3:
                    bot_state['recovery_mode_active'] = True
                    log(f"🚨 복구 모드 자동 활성화 (마이너스 {minus_count}개)", "URGENT")
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'❌ 잔고 조회 실패: {str(e)}\n\nAPI 키를 확인하세요.'
                })
        
        # 시드 변경 시에만 완전 초기화
        if seed_changed:
            log(f"[{user_id}] 시드 변경 감지: {old_start_seed:,}원 → {seed:,}원 (데이터 초기화)", "WARNING")
            
            # 완전 초기화
            bot_state['simulation_seed'] = seed
            bot_state['simulation_krw'] = seed
            bot_state['simulation_start_seed'] = seed
            bot_state['simulation_holdings'] = {}
            bot_state['frozen_holdings'] = {}
            bot_state['recovery_mode_active'] = False
            bot_state['recovery_seed'] = 0
            bot_state['recovery_target_amount'] = 0
            bot_state['recovery_trades'] = 0
            bot_state['recovery_success_trades'] = 0
            bot_state['recovery_total_profit'] = 0
            
            # 통계 초기화
            bot_state['recent_trades'].clear()
            bot_state['recent_signals'].clear()
            bot_state['statistics'] = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit': 0,
                'best_strategy': None,
                'recovery_progress': 0,
            }
            
            # 전략 성과 초기화
            for strategy_key in bot_state['strategy_performance']:
                bot_state['strategy_performance'][strategy_key]['performance'] = {
                    'trades': 0,
                    'wins': 0,
                    'total_profit': 0
                }
        else:
            # 같은 시드로 재시작 (데이터 보존)
            log(f"[{user_id}] 기존 데이터 유지 재시작: {seed:,}원", "INFO")
            
            # 기존 simulation_start_seed가 없으면 현재 시드를 시작 시드로 설정
            if bot_state.get('simulation_start_seed') is None:
                bot_state['simulation_start_seed'] = seed
            
            # 현재 시드만 업데이트 (보유 코인, 거래 내역 등은 보존)
            if bot_state.get('simulation_seed') != seed:
                bot_state['simulation_seed'] = seed
        
        bot_state['mode'] = mode
        
        bot_state['running'] = True
        bot_state['start_time'] = datetime.now()
        
        # 💾 DB에 봇 상태 저장
        save_bot_state(user_id, bot_state)
        
        # ✅ 사용자별 독립 스레드 시작 (user_id와 bot_state 전달)
        thread = threading.Thread(target=bot_main_loop, args=(user_id, bot_state), daemon=True)
        thread.start()
        bot_state['thread'] = thread
        
        mode_text = "💎 실전 모드" if mode == 'live' else "연습 모드"
        log(f"[{user_id}] 봇 시작! {mode_text}, 시드: {seed:,}원", "SUCCESS")
        
        return jsonify({'success': True, 'message': f'✅ 봇 시작! ({mode_text})'})
    except Exception as e:
        log(f"시작 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    try:
        # ✅ 사용자별 독립 봇 상태 가져오기
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        username = session['username']
        
        log(f"[STOP] username: {username}", "INFO")
        bot_state = get_user_bot_state(username)
        
        bot_state['running'] = False
        
        # 💾 DB에 봇 상태 저장
        save_bot_state(username, bot_state)
        
        # 스레드가 종료될 때까지 대기 (최대 5초)
        if 'thread' in bot_state and bot_state['thread'] and bot_state['thread'].is_alive():
            bot_state['thread'].join(timeout=5)
        log(f"[{username}] 봇이 정지되었습니다", "INFO")
        return jsonify({'success': True, 'message': '봇 중지'})
    except Exception as e:
        log(f"정지 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/test/force-sell', methods=['POST'])
def api_test_force_sell():
    """테스트용: 모든 보유 코인 강제 청산 (손절/익절 테스트)"""
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        username = session['username']
        bot_state = get_user_bot_state(username)
        
        if not bot_state['simulation_holdings']:
            return jsonify({'success': False, 'message': '보유 코인 없음'})
        
        sold_count = 0
        results = []
        
        for ticker, holding in list(bot_state['simulation_holdings'].items()):
            try:
                current_price = pyupbit.get_current_price(ticker)
                if not current_price:
                    current_price = holding['avg_price']
                
                profit_rate = (current_price - holding['avg_price']) / holding['avg_price'] * 100
                
                # 강제 청산
                execute_exit(ticker, holding, f"🧪 테스트 청산 ({profit_rate:+.2f}%)", bot_state)
                sold_count += 1
                results.append({
                    'ticker': ticker,
                    'profit_rate': round(profit_rate, 2),
                    'amount': holding['amount']
                })
            except Exception as e:
                log(f"❌ {ticker} 청산 실패: {e}", "ERROR")
        
        return jsonify({
            'success': True,
            'message': f'{sold_count}개 코인 강제 청산 완료',
            'results': results
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user/referral-link')
def api_get_referral_link():
    """사용자의 추천 링크 가져오기"""
    try:
        # 사용자 ID 가져오기
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        user_id = session['user_id']
        username = session.get('username', 'unknown')
        
        # DB에서 추천 코드 가져오기
        import sqlite3
        import hashlib
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # username으로 추천 코드 조회
        cursor.execute("SELECT referral_code FROM users WHERE username = ?", (user_id,))
        result = cursor.fetchone()
        
        # 추천 코드가 없으면 생성
        if not result or not result[0]:
            referral_code = hashlib.md5(user_id.encode()).hexdigest()[:8].upper()
            
            # DB에 저장 시도
            try:
                # 사용자가 이미 존재하는지 확인
                cursor.execute("SELECT username FROM users WHERE username = ?", (user_id,))
                if cursor.fetchone():
                    # 기존 사용자 업데이트
                    cursor.execute("""
                        UPDATE users SET referral_code = ? WHERE username = ?
                    """, (referral_code, user_id))
                else:
                    # 새 사용자 삽입
                    cursor.execute("""
                        INSERT INTO users (username, referral_code, created_at)
                        VALUES (?, ?, datetime('now'))
                    """, (user_id, referral_code))
                
                conn.commit()
            except Exception as e:
                log(f"추천 코드 저장 오류: {e}", "ERROR")
                conn.rollback()
        else:
            referral_code = result[0]
        
        conn.close()
        
        # 전체 추천 링크 생성
        referral_link = f"{request.host_url.rstrip('/')}/?ref={referral_code}"
        
        return jsonify({
            'success': True,
            'referral_code': referral_code,
            'referral_link': referral_link
        })
        
    except Exception as e:
        log(f"추천 링크 로드 오류: {e}", "ERROR")
        return jsonify({
            'success': False,
            'message': str(e),
            'referral_link': f"{request.host_url.rstrip('/')}/?ref=LOADING"
        }), 500

@app.route('/api/verify-license', methods=['POST'])
def api_verify_license():
    """라이선스 검증 API - USDT TRC-20 기반"""
    try:
        data = request.json or {}
        txid = data.get('txid', '').strip()
        
        if not txid:
            return jsonify({'success': False, 'message': 'TXID를 입력해주세요'})
        
        # TXID 기본 검증
        if len(txid) < 20:
            return jsonify({'success': False, 'message': 'TXID가 너무 짧습니다. 올바른 트론 TXID를 입력하세요.'})
        
        # TODO: TronScan API로 실제 USDT 금액 확인
        # 예시: https://api.trongrid.io/v1/transactions/{txid}
        # 입금 주소: TLb5D3uDQjPQt6CzATM21t21etxGsSvtbt
        # USDT 금액에 따라 만료일 계산:
        # - 50 USDT = 1개월
        # - 250 USDT = 6개월
        # - 500 USDT = 평생
        
        log(f"라이선스 검증 시도: {txid[:10]}...", "INFO")
        
        # 데모용: TXID가 64자 이상이면 인증 성공
        if len(txid) >= 40:
            # 실제로는 TronScan API로 금액 확인 후 만료일 계산
            return jsonify({
                'success': True, 
                'message': '라이선스 인증 완료',
                'license_type': 'premium',
                'expires_at': '2027-12-31',
                'usdt_amount': 0  # TODO: 실제 금액
            })
        else:
            return jsonify({'success': False, 'message': '유효하지 않은 TXID입니다. 트론스캔에서 확인 후 다시 입력하세요.'})
            
    except Exception as e:
        log(f"라이선스 검증 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def api_config():
    """API 키 설정"""
    try:
        data = request.json or {}
        access_key = data.get('access_key', '').strip()
        secret_key = data.get('secret_key', '').strip()
        
        if not access_key or not secret_key:
            return jsonify({'success': False, 'message': 'Access Key와 Secret Key를 모두 입력해주세요'})
        
        # config.json 업데이트
        try:
            import json
            config_path = 'config.json'
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config['upbit_access_key'] = access_key
            config['upbit_secret_key'] = secret_key
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            log("API 키가 저장되었습니다", "SUCCESS")
            return jsonify({'success': True, 'message': 'API 키 저장 완료'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'저장 실패: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ═══════════════════════════════════════════════════════
# 🔄 메인 봇 루프
# ═══════════════════════════════════════════════════════
def bot_main_loop(user_id, bot_state):
    """메인 루프 (완전체) - 사용자별 독립 실행"""
    log_separator()
    log(f"🚀 [{user_id}] AI 트레이딩 봇 v8.0 ULTIMATE 시작!", "SUCCESS")
    log_separator()
    
    bot_state['start_time'] = datetime.now()
    
    # 초기 안정화 대기 (5초)
    log(f"[{user_id}] ⏱️ 초기화 중... (5초 대기)", "INFO")
    bot_state['status_message'] = '⚙️ 초기화 중'
    bot_state['status_emoji'] = '⚙️'
    bot_state['status_detail'] = '봇 시작 준비 중 (5초 대기)'
    time.sleep(5)
    log(f"[{user_id}] ✅ 스캔 시작!", "SUCCESS")
    bot_state['status_message'] = '🔍 스캔 중'
    bot_state['status_emoji'] = '🔍'
    bot_state['status_detail'] = '좋은 기회를 찾고 있습니다'
    
    # 거래량 기반 동적 티커 선정
    def get_top_volume_tickers(count=100):
        """거래량 상위 티커 반환 (🚨 투자유의/상폐예정 종목 제외!)"""
        try:
            # 🚨 1. 투자 유의 종목 리스트 가져오기
            caution_coins = set()
            try:
                import requests
                response = requests.get("https://api.upbit.com/v1/market/all?isDetails=true", timeout=5)
                if response.status_code == 200:
                    markets = response.json()
                    for market in markets:
                        # market_warning: CAUTION (투자유의) or None
                        if market.get('market_warning') == 'CAUTION':
                            caution_coins.add(market['market'])
                    
                    if caution_coins:
                        log(f"[{user_id}] 🚨 투자유의 종목 {len(caution_coins)}개 제외: {list(caution_coins)[:5]}", "WARNING")
            except Exception as e:
                log(f"[{user_id}] ⚠️ 투자유의 종목 조회 실패 (계속 진행): {e}", "WARNING")
            
            all_tickers = pyupbit.get_tickers(fiat="KRW")
            
            # 각 티커의 24시간 거래대금 확인
            volume_data = []
            for ticker in all_tickers[:150]:  # 상위 150개 확인
                # 🚨 투자유의 종목 건너뛰기
                if ticker in caution_coins:
                    log(f"[{user_id}] 🚫 {ticker} 제외 (투자유의 종목)", "WARNING")
                    continue
                
                try:
                    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
                    if df is not None and len(df) > 0:
                        # 거래대금 = 종가 × 거래량
                        volume_krw = df['close'].iloc[-1] * df['volume'].iloc[-1]
                        volume_data.append((ticker, volume_krw))
                except:
                    continue
            
            # 거래량 정렬
            volume_data.sort(key=lambda x: x[1], reverse=True)
            
            # 상위 N개 티커 반환
            top_tickers = [t[0] for t in volume_data[:count]]
            
            log(f"[{user_id}] 📊 거래량 TOP {count} 티커 선정 완료 (유의종목 제외)", "INFO")
            return top_tickers
        except:
            # 실패 시 기본 목록 반환
            log(f"[{user_id}] ⚠️ 거래량 조회 실패, 기본 목록 사용", "WARNING")
            return [
                'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
                'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK',
                'KRW-ATOM', 'KRW-ETC', 'KRW-NEAR', 'KRW-HBAR', 'KRW-APT',
                'KRW-SUI', 'KRW-TRX', 'KRW-SHIB', 'KRW-TON', 'KRW-PEPE',
                'KRW-ARB', 'KRW-OP', 'KRW-IMX', 'KRW-AAVE', 'KRW-ALGO'
            ]
    
    # 초기 티커 목록 (15분마다 갱신) - 🔧 안정화: 100→50개
    popular_tickers = get_top_volume_tickers(50)
    last_ticker_update = datetime.now()
    
    loop_count = 0  # 루프 카운터 추가
    
    while bot_state['running']:
        try:
            loop_count += 1
            log(f"[{user_id}] 🔄 루프 #{loop_count} 시작", "INFO")
            
            # 0. 티커 목록 갱신 (30분마다)
            time_since_update = (datetime.now() - last_ticker_update).total_seconds() / 60
            if time_since_update >= 30:
                log(f"[{user_id}] 📊 거래량 기반 티커 목록 갱신 중...", "INFO")
                popular_tickers = get_top_volume_tickers(50)
                last_ticker_update = datetime.now()
                log(f"[{user_id}] ✅ 티커 목록 갱신 완료 (50개)", "SUCCESS")
            
            # 1. 복구 모드 체크
            if not bot_state['recovery_mode_active']:
                check_recovery_mode_activation(bot_state)
            
            # 2. 보유 포지션 관리
            holdings_count = len(bot_state['simulation_holdings'])
            if holdings_count > 0:
                log(f"[{user_id}] 📊 보유 포지션 체크: {holdings_count}개", "INFO")
                bot_state['status_message'] = f'📊 보유 {holdings_count}개 관리 중'
                bot_state['status_emoji'] = '📊'
                bot_state['status_detail'] = f'{holdings_count}개 코인 익절/손절 모니터링'
            
            # 🎯 2-1. 최적화된 물타기 체크 (Martingale + RSI)
            for ticker, holding in list(bot_state['simulation_holdings'].items()):
                current_price = pyupbit.get_current_price(ticker)
                if not current_price:
                    continue
                
                first_entry_price = holding.get('first_entry_price', holding['avg_price'])
                profit_rate = (current_price - first_entry_price) / first_entry_price * 100
                dca_count = holding.get('dca_count', 0)
                coin_tier = holding.get('coin_tier', {})
                
                if not coin_tier or 'dca_thresholds' not in coin_tier:
                    continue
                
                dca_thresholds = coin_tier['dca_thresholds']  # [-2,-4,-6,-8] or [-3,-6,-9,-12] 등
                
                # 물타기 조건: 손실률이 threshold에 도달하고, 아직 해당 단계 물타기를 안 했을 때
                if dca_count < len(dca_thresholds):
                    next_threshold = dca_thresholds[dca_count]
                    
                    if profit_rate <= next_threshold:
                        # 🎯 RSI 체크 (과매도 구간에서만 물타기)
                        try:
                            df = pyupbit.get_ohlcv(ticker, interval="minute5", count=14)
                            if df is not None and len(df) >= 14:
                                # RSI 계산
                                delta = df['close'].diff()
                                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                                rs = gain / loss
                                rsi = 100 - (100 / (1 + rs))
                                current_rsi = rsi.iloc[-1]
                                
                                # RSI 기반 물타기 판단 (단계별 임계값)
                                # 2차: RSI<50, 3차: RSI<45, 4차: RSI<40, 5차: RSI<35, 6차: RSI<30
                                rsi_thresholds = [50, 45, 40, 35, 30]
                                required_rsi = rsi_thresholds[min(dca_count, len(rsi_thresholds)-1)]
                                
                                if current_rsi > required_rsi:
                                    log(f"[{user_id}] ⏸️ {ticker} 물타기 보류 (RSI {current_rsi:.1f} > {required_rsi})", "INFO")
                                    continue  # RSI가 높으면 물타기 안 함
                        except:
                            current_rsi = 30  # RSI 계산 실패 시 기본값
                        
                        # 🎯 v12.2 초소액 물타기: 6단계 설정
                        # 2차: 10K, 3차: 20K, 4차: 30K, 5차: 30K, 6차: 100K
                        dca_amounts = [10000, 20000, 30000, 30000, 100000]
                        base_dca_invest = dca_amounts[min(dca_count, len(dca_amounts)-1)]
                        
                        # RSI 과매도 구간(RSI<30)이면 투자 금액 그대로 유지 (이미 큰 금액)
                        dca_invest = min(base_dca_invest, bot_state['simulation_krw'])
                        
                        if dca_invest >= 5000 and bot_state['simulation_krw'] >= dca_invest:
                            # 전략 정보 가져오기
                            strategy_id = holding.get('strategy', 'box_trader')
                            strategy_icon = STRATEGIES.get(strategy_id, {}).get('icon', '📦')
                            strategy_name = STRATEGIES.get(strategy_id, {}).get('name', '전략')
                            
                            bot_state['status_message'] = f'📉 {ticker.replace("KRW-", "")} 물타기 중'
                            bot_state['status_emoji'] = '📉'
                            bot_state['status_detail'] = f'{strategy_icon} {dca_count+2}차 평균매수 ({profit_rate:.1f}% 하락)'
                            log(f"[{user_id}] 💰 {strategy_icon} {strategy_name} | {ticker} {dca_count+2}차 물타기! (진입가 대비 {profit_rate:.2f}% 하락, RSI {current_rsi:.1f})", "WARNING")
                            log(f"[{user_id}]    투자 금액: {dca_invest:,}원 (기본 {base_dca_invest:,}원)", "INFO")
                            
                            FEE_RATE = 0.0005
                            fee = dca_invest * FEE_RATE
                            net_invest = dca_invest - fee
                            buy_amount = net_invest / current_price
                            
                            # KRW 차감
                            bot_state['simulation_krw'] -= dca_invest
                            
                            # 보유량 업데이트 (평단가 재계산)
                            total_invested = holding['invested'] + dca_invest
                            total_amount = holding['amount'] + buy_amount
                            new_avg_price = total_invested / total_amount
                            
                            holding['amount'] = total_amount
                            holding['avg_price'] = new_avg_price
                            holding['invested'] = total_invested
                            holding['dca_count'] = dca_count + 1
                            
                            log(f"[{user_id}]    평단가: {first_entry_price:.0f}원 → {new_avg_price:.0f}원 ({((new_avg_price - first_entry_price) / first_entry_price * 100):+.2f}%)", "SUCCESS")
                            
                            time.sleep(1)  # API 제한 방지
            
            # 🎯 2-2. 청산 체크
            for ticker, holding in list(bot_state['simulation_holdings'].items()):
                should_exit, reason = check_exit(ticker, holding, bot_state)
                if should_exit:
                    bot_state['status_message'] = f'💰 {ticker.replace("KRW-", "")} 매도 중'
                    bot_state['status_emoji'] = '💰'
                    bot_state['status_detail'] = f'청산: {reason}'
                    log(f"[{user_id}] 🔔 {ticker} 청산 신호: {reason}", "WARNING")
                    # 🔥 분할 매도 처리
                    if should_exit == 'PARTIAL_33':
                        execute_exit(ticker, holding, reason, bot_state, partial_ratio=0.33)
                    else:
                        execute_exit(ticker, holding, reason, bot_state)
            
            # 3. 신규 진입
            max_positions = 1 if bot_state['recovery_mode_active'] else 10  # 🎯 v12.2: 초소액 물타기 대응 10개로 확대!
            
            if len(bot_state['simulation_holdings']) < max_positions:
                # 복구 모드
                if bot_state['recovery_mode_active']:
                    # 쿨다운
                    if bot_state['last_loss_time']:
                        cooldown = (datetime.now() - bot_state['last_loss_time']).total_seconds()
                        if cooldown < 120:
                            time.sleep(5)
                            continue
                    
                    opportunities = find_recovery_opportunity(popular_tickers[:10], bot_state)
                    if opportunities:
                        best = opportunities[0]
                        execute_trade(best['ticker'], 'surge_hunter', {'recovery': best}, bot_state)
                
                # 일반 모드
                else:
                    import random
                    
                    # 🎯 시장 방향성 체크 (BTC & ETH)
                    market = check_market_direction()
                    is_down_market = False
                    
                    if market:
                        if market['direction'] == 'STRONG_DOWN':
                            bot_state['status_message'] = '📉 하락장 대응'
                            bot_state['status_emoji'] = '📉'
                            bot_state['status_detail'] = f'급락 저점 매수 대기 (BTC {market["btc_change"]:+.1f}%)'
                            log(f"[{user_id}] ❌ 강한 하락장 (BTC {market['btc_change']:+.2f}%, ETH {market['eth_change']:+.2f}%) - DIP HUNTER만 활성화!", "WARNING")
                            is_down_market = True
                        elif market['direction'] == 'DOWN':
                            bot_state['status_message'] = '⚠️ 신중 모드'
                            bot_state['status_emoji'] = '⚠️'
                            bot_state['status_detail'] = f'약한 하락장, 조심스럽게 기회 탐색 (BTC {market["btc_change"]:+.1f}%)'
                            log(f"[{user_id}] ⚠️ 약한 하락 (BTC {market['btc_change']:+.2f}%) - 매수 신중", "WARNING")
                        elif market['direction'] == 'STRONG_UP':
                            bot_state['status_message'] = '🚀 상승장 공략'
                            bot_state['status_emoji'] = '🚀'
                            bot_state['status_detail'] = f'강세장 적극 매수 (BTC {market["btc_change"]:+.1f}%)'
                            log(f"[{user_id}] ✅ 강한 상승장! (BTC {market['btc_change']:+.2f}%, ETH {market['eth_change']:+.2f}%) - 매수 찬스!", "SUCCESS")
                        else:
                            bot_state['status_message'] = '🔍 좋은 기회 찾는 중'
                            bot_state['status_emoji'] = '🔍'
                            bot_state['status_detail'] = f'보합장, 확실한 신호만 포착 (BTC {market["btc_change"]:+.1f}%)'
                            log(f"[{user_id}] 🟡 시장 보합 (BTC {market['btc_change']:+.2f}%)", "INFO")
                    
                    # 🔧 안정화: 20→30개 스캔 (Rate Limit 고려)
                    scan_tickers = random.sample(popular_tickers, min(30, len(popular_tickers)))
                    bot_state['status_message'] = f'🔎 {len(scan_tickers)}개 코인 분석 중'
                    bot_state['status_emoji'] = '🔎'
                    bot_state['status_detail'] = '거래량 상위 코인 패턴 분석 중'
                    log(f"[{user_id}] 📊 {len(scan_tickers)}개 티커 스캔 중... (급등 감지 모드)", "INFO")
                    
                    for ticker in scan_tickers:
                        try:
                            # 1. 채결 강도 변화 체크 (실시간!)
                            orderbook_signal = None
                            try:
                                orderbook_signal = check_orderbook_surge(ticker, bot_state)
                                if orderbook_signal:
                                    log(f"[{user_id}] 💪 {ticker} 채결 강도 급증! {orderbook_signal['signal']}", "SUCCESS")
                            except Exception as ob_error:
                                # 🔧 채결 강도 체크 실패해도 계속 진행
                                pass
                            
                            # 2. 패턴 분석
                            patterns = None
                            try:
                                patterns = analyze_all_patterns(ticker)
                            except Exception as pattern_error:
                                # 🔧 패턴 분석 실패 시 다음 티커로
                                log(f"[{user_id}] ⚠️ {ticker} 패턴 분석 실패, 스킵", "WARNING")
                                continue
                            
                            if patterns:
                                # 하락장에서는 패닉 DIP만 허용!
                                if is_down_market:
                                    if 'panic_dip' not in patterns:
                                        continue  # DIP 아니면 스킵
                                    log(f"[{user_id}] 🔻 {ticker} DIP HUNTER 발동! (하락장)", "SUCCESS")
                            
                            if patterns:
                                # 채결 강도 신호가 있으면 패턴에 추가
                                if orderbook_signal:
                                    patterns['orderbook_surge'] = orderbook_signal
                                
                                bot_state['current_patterns'][ticker] = patterns
                                best_strategy, score = select_best_strategy(ticker, patterns)
                                
                                # 채결 강도 급증 시 점수 가산
                                if orderbook_signal:
                                    score += 0.2
                                
                                # 시장 방향성 점수 반영
                                if market:
                                    score *= market['score']
                                
                                # 🎯 v12.3: 확실한 기회만 포착 (점수 0.8 이상)
                                if best_strategy and score > 0.8:
                                    strategy_icon = STRATEGIES.get(best_strategy, {}).get('icon', '📊')
                                    strategy_name = STRATEGIES.get(best_strategy, {}).get('name', '전략')
                                    
                                    bot_state['status_message'] = f'✨ {ticker.replace("KRW-", "")} 매수 기회!'
                                    bot_state['status_emoji'] = '✨'
                                    bot_state['status_detail'] = f'{strategy_icon} {strategy_name} (점수 {score:.2f})'
                                    # 재진입 쿨다운 체크 (30분)
                                    last_trades = bot_state.get('last_trade_times', {})
                                    last_trade_time = last_trades.get(ticker)
                                    if last_trade_time:
                                        cooldown_seconds = (datetime.now() - last_trade_time).total_seconds()
                                        if cooldown_seconds < 1800:  # 30분
                                            log(f"[{user_id}] ⏸️ {ticker} 재진입 쿨다운 중 ({int(cooldown_seconds/60)}분 경과/30분)", "WARNING")
                                            continue
                                    
                                    # 하루 최대 거래 제한 (15회)
                                    today = datetime.now().date()
                                    daily_trades = bot_state.get('daily_trade_count', {})
                                    today_count = daily_trades.get(str(today), 0)
                                    if today_count >= 15:
                                        log(f"[{user_id}] ⏸️ 오늘 거래 한도 도달 ({today_count}/15회), 내일까지 대기", "WARNING")
                                        time.sleep(3600)  # 1시간 대기
                                        continue
                                    
                                    strategy_icon = STRATEGIES.get(best_strategy, {}).get('icon', '📊')
                                    strategy_name = STRATEGIES.get(best_strategy, {}).get('name', '전략')
                                    log(f"[{user_id}] 🎯 {ticker} 매수 신호 감지! {strategy_icon} {strategy_name} (점수: {score:.2f}, 시장: {market['direction'] if market else 'N/A'})", "SUCCESS")
                                    
                                    # 거래 실행
                                    result = execute_trade(ticker, best_strategy, patterns, bot_state)
                                    if result:
                                        # 재진입 쿨다운 기록
                                        if 'last_trade_times' not in bot_state:
                                            bot_state['last_trade_times'] = {}
                                        bot_state['last_trade_times'][ticker] = datetime.now()
                                        
                                        # 하루 거래 카운트 증가
                                        if 'daily_trade_count' not in bot_state:
                                            bot_state['daily_trade_count'] = {}
                                        bot_state['daily_trade_count'][str(today)] = today_count + 1
                                    
                                    time.sleep(2)
                                    break
                        except Exception as ticker_error:
                            # 🔧 티커 분석 중 에러 발생해도 봇 계속 실행
                            log(f"[{user_id}] ⚠️ {ticker} 분석 오류 (계속 진행): {str(ticker_error)[:100]}", "WARNING")
                            continue
                    
                    bot_state['status_message'] = '⏸️ 좋은 기회 대기 중'
                    bot_state['status_emoji'] = '⏸️'
                    bot_state['status_detail'] = '점수 0.8+ 신호 대기 (안전 우선)'
                    log(f"[{user_id}] ✅ 스캔 완료, 대기 중... (조건 미달: 매수 신호 점수 < 0.8 또는 패턴 없음)", "INFO")
            else:
                # 포지션이 꽉 찬 경우
                bot_state['status_message'] = f'⏸️ 포지션 가득참 ({max_positions}개)'
                bot_state['status_emoji'] = '⏸️'
                bot_state['status_detail'] = f'{len(bot_state["simulation_holdings"])}개 코인 보유 중, 익절/손절 대기'
                log(f"[{user_id}] ⏸️ 대기 중... (보유 {len(bot_state['simulation_holdings'])}개/{max_positions}개 - 포지션 Full)", "INFO")
            
            bot_state['last_update'] = datetime.now()
            # 🔧 안정화: 20→15초 대기 (Rate Limit 안전)
            sleep_time = 15 if bot_state['recovery_mode_active'] else 15
            log(f"[{user_id}] 💤 {sleep_time}초 대기...", "INFO")
            time.sleep(sleep_time)
            
        except Exception as e:
            log(f"[{user_id}] ❌ 메인 루프 오류: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            # 🔧 에러 발생 시 봇 계속 실행 (10초 대기 후 재시도)
            log(f"[{user_id}] 🔄 10초 후 재시도...", "WARNING")
            time.sleep(10)
            log(f"[{user_id}] 🔄 10초 후 재시도...", "WARNING")
            time.sleep(10)
    
    log("🛑 봇 중지", "WARNING")

# ═══════════════════════════════════════════════════════
# 🔐 사용자 인증 API
# ═══════════════════════════════════════════════════════

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    """회원가입"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': '사용자명을 입력해주세요'})
        
        ip_address = request.remote_addr
        result = user_manager.create_user(username, email, ip_address)
        
        if result['success']:
            session.permanent = True  # 🔧 새로고침 후에도 로그인 유지
            session['user_id'] = result['user_id']
            session['username'] = result['username']
            log(f"✨ 새 사용자 등록: {username} (ID: {result['user_id']})", "SUCCESS")
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """로그인"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': '사용자명을 입력해주세요'})
        
        user = user_manager.get_user_by_username(username)
        
        if not user:
            return jsonify({'success': False, 'message': '존재하지 않는 사용자입니다'})
        
        if not user['is_active']:
            return jsonify({'success': False, 'message': '비활성화된 계정입니다'})
        
        # 세션 저장 (영구 세션으로 설정)
        session.permanent = True  # 🔧 새로고침 후에도 로그인 유지
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        # 마지막 로그인 업데이트
        user_manager.update_last_login(user['id'], request.remote_addr)
        
        log(f"👤 로그인: {username} (ID: {user['id']})", "INFO")
        
        return jsonify({
            'success': True,
            'user_id': user['id'],
            'username': user['username']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """로그아웃"""
    username = session.get('username', 'Unknown')
    session.clear()
    return jsonify({'success': True, 'message': f'{username}님 로그아웃'})

@app.route('/api/user/info')
def api_user_info():
    """현재 로그인한 사용자 정보 반환"""
    if 'user_id' in session and 'username' in session:
        return jsonify({
            'success': True,
            'logged_in': True,
            'user_id': session['user_id'],
            'username': session['username']
        })
    else:
        return jsonify({
            'success': True,
            'logged_in': False,
            'username': 'Guest'
        })

@app.route('/api/notifications')
def api_notifications():
    """실시간 알림 (Server-Sent Events)"""
    def generate():
        last_trade_count = 0
        while True:
            try:
                if 'username' not in session:
                    yield f"data: {json.dumps({'type': 'error', 'message': '로그인 필요'})}\n\n"
                    break
                
                username = session.get('username')
                bot_state = get_user_bot_state(username)
                
                # 새로운 거래 감지
                current_trade_count = len(bot_state.get('recent_trades', []))
                if current_trade_count > last_trade_count:
                    latest_trade = bot_state['recent_trades'][-1] if bot_state['recent_trades'] else None
                    if latest_trade:
                        yield f"data: {json.dumps({'type': 'trade', 'data': latest_trade})}\n\n"
                    last_trade_count = current_trade_count
                
                # 손익률 업데이트
                current_krw = bot_state.get('simulation_krw', 0)
                holdings_value = sum(h['amount'] * h['avg_price'] for h in bot_state.get('simulation_holdings', {}).values())
                total_value = current_krw + holdings_value
                start_seed = bot_state.get('simulation_start_seed', 1000000)
                profit_rate = ((total_value - start_seed) / start_seed * 100) if start_seed > 0 else 0
                
                yield f"data: {json.dumps({'type': 'status', 'profit_rate': round(profit_rate, 2), 'total_value': round(total_value)})}\n\n"
                
                time.sleep(5)  # 5초마다 업데이트
            except GeneratorExit:
                break
            except Exception as e:
                log(f"❌ 알림 오류: {e}", "ERROR")
                break
    
    return Response(generate(), mimetype='text/event-stream')

# ═══════════════════════════════════════════════════════
# 👨‍💼 관리자 API
# ═══════════════════════════════════════════════════════

# 관리자 권한 체크 데코레이터
def admin_required(f):
    """관리자 권한 필요 (wordycow, lee1만 허용)"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
        
        username = session['username']
        if username not in ['wordycow', 'lee1']:
            return jsonify({
                'success': False, 
                'message': f'⛔ 접근 거부: 관리자 권한이 필요합니다 (현재 사용자: {username})'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/admin')
def admin_page():
    """관리자 페이지 - wordycow와 lee1만 접근 가능"""
    # 로그인 체크
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    
    # 관리자 권한 체크
    if username not in ['wordycow', 'lee1']:
        return '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>접근 거부</title>
                <style>
                    body {
                        font-family: 'Inter', sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .error-box {
                        background: white;
                        padding: 60px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        text-align: center;
                        max-width: 500px;
                    }
                    h1 {
                        font-size: 72px;
                        margin: 0 0 20px 0;
                        color: #e74c3c;
                    }
                    h2 {
                        font-size: 28px;
                        margin: 0 0 20px 0;
                        color: #333;
                    }
                    p {
                        font-size: 16px;
                        color: #666;
                        margin-bottom: 30px;
                    }
                    a {
                        display: inline-block;
                        padding: 12px 30px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 600;
                        transition: transform 0.2s;
                    }
                    a:hover {
                        transform: scale(1.05);
                    }
                </style>
            </head>
            <body>
                <div class="error-box">
                    <h1>🚫</h1>
                    <h2>접근 거부</h2>
                    <p>관리자 페이지는 wordycow와 lee1만 접근할 수 있습니다.</p>
                    <p style="color: #999; font-size: 14px;">현재 사용자: ''' + username + '''</p>
                    <a href="/">대시보드로 돌아가기</a>
                </div>
            </body>
            </html>
        ''', 403
    
    return render_template('admin.html')

# ═══════════════════════════════════════════════════════
# 📊 포트폴리오 API
# ═══════════════════════════════════════════════════════

@app.route('/api/portfolio/get')
def api_get_portfolio():
    """사용자 포트폴리오 조회"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
    
    try:
        portfolio = user_manager.get_user_portfolio(session['user_id'])
        available_coins = get_available_coins()
        
        return jsonify({
            'success': True,
            'portfolio': portfolio,
            'available_coins': available_coins
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/portfolio/update', methods=['POST'])
def api_update_portfolio():
    """포트폴리오 설정 업데이트"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
    
    try:
        data = request.json
        result = user_manager.update_portfolio(
            session['user_id'],
            data.get('coin_1'),
            data.get('coin_2'),
            data.get('coin_3'),
            data.get('coin_4'),
            data.get('investment_per_coin', 10000)
        )
        
        log(f"📊 포트폴리오 업데이트: {session['username']}", "INFO")
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ═══════════════════════════════════════════════════════
# 🔧 관리자 API
# ═══════════════════════════════════════════════════════

@app.route('/admin')
def admin_dashboard():
    """관리자 대시보드 페이지"""
    # 관리자 확인 (세션에 admin 권한이 있거나, 특정 user_id)
    if 'user_id' not in session:
        # 개발 편의: 누구나 접근 가능 (나중에 관리자 로그인 추가)
        pass
    
    return render_template('admin.html')

@app.route('/api/admin/users')
@admin_required
def api_admin_users():
    """전체 사용자 목록 및 통계 (DB + 실행 중인 봇 통합)"""
    try:
        from datetime import datetime  # ✅ 함수 시작 부분에서 import
        
        # 관리자 권한 체크 (TODO: 실제 권한 확인 추가)
        # if session.get('role') != 'admin':
        #     return jsonify({'error': '권한 없음'}), 403
        
        users_list = []
        total_profit_rate = 0
        running_count = 0
        active_subscriptions = 0
        
        # ✅ 1. DB에서 모든 등록 사용자 조회
        import sqlite3
        try:
            conn = sqlite3.connect('upbit_bot.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
            db_users = cursor.fetchall()
            conn.close()
        except Exception as db_error:
            log(f"DB 조회 오류 (무시됨): {db_error}", "WARNING")
            db_users = []
        
        # ✅ 2. DB 사용자와 실행 중인 봇 매칭
        processed_users = set()
        
        # DB 사용자 우선 처리
        for db_user in db_users:
            # 기존 DB 스키마: username을 user_id로 사용
            db_dict = dict(db_user)  # ✅ Row를 dict로 변환
            user_id = db_dict.get('user_id') or db_dict.get('username') or f"user_{db_dict.get('id')}"
            if not user_id:
                continue
            
            processed_users.add(user_id)
            
            # DB에서 봇 상태 가져오기 (정확한 seed_amount 사용)
            try:
                conn2 = sqlite3.connect('upbit_bot.db')
                cursor2 = conn2.cursor()
                cursor2.execute('''
                    SELECT running, seed_amount, simulation_krw, simulation_holdings
                    FROM bot_states 
                    WHERE user_id = ?
                ''', (user_id,))
                bot_row = cursor2.fetchone()
                conn2.close()
                
                if bot_row:
                    bot_running, seed, current_krw, holdings_json = bot_row
                    
                    # 보유 코인 가치 계산
                    holdings_value = 0
                    if holdings_json:
                        import json
                        holdings = json.loads(holdings_json)
                        for ticker, holding in holdings.items():
                            try:
                                current_price = pyupbit.get_current_price(ticker)
                                if current_price:
                                    holdings_value += holding['amount'] * current_price
                                else:
                                    holdings_value += holding['amount'] * holding.get('avg_price', 0)
                            except:
                                holdings_value += holding['amount'] * holding.get('avg_price', 0)
                    
                    total_value = current_krw + holdings_value
                    profit = total_value - seed
                    profit_rate = (profit / seed * 100) if seed > 0 else 0
                else:
                    # 봇 상태가 없는 경우
                    seed = 0
                    current_krw = 0
                    total_value = 0
                    profit_rate = 0
                    bot_running = False
            except Exception as e:
                # DB 오류 시 기본값
                seed = 0
                current_krw = 0
                total_value = 0
                profit_rate = 0
                bot_running = False
            
            # 추천 코드 생성
            import hashlib
            referral_code = hashlib.md5(user_id.encode()).hexdigest()[:8].upper()
            
            # DB에서 가져오기 (있으면)
            subscription_expires_at = db_dict.get('subscription_expires_at')
            created_at = db_dict.get('created_at')
            username_display = db_dict.get('username') or user_id.replace('guest_', '게스트_')[:20]
            
            if db_dict.get('referral_code'):
                referral_code = db_dict['referral_code']
            
            user_info = {
                'user_id': user_id,
                'username': username_display,
                'bot_running': bot_running,
                'seed_amount': seed,
                'current_balance': total_value,
                'profit_rate': profit_rate,
                'subscription_expires_at': subscription_expires_at,
                'referral_code': referral_code,
                'created_at': created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            users_list.append(user_info)
            total_profit_rate += profit_rate
            
            if bot_running:
                running_count += 1
            
            # 구독 활성 확인
            if db_dict.get('subscription_expires_at'):
                try:
                    expires = datetime.fromisoformat(db_dict['subscription_expires_at'])
                    if expires > datetime.now():
                        active_subscriptions += 1
                except:
                    pass
        
        # ✅ 3. 게스트 사용자 (DB에 없지만 봇만 실행 중)
        for user_id, bot_state in user_bots.items():
            if user_id in processed_users:
                continue  # 이미 처리됨
            # 현재 잔고 계산
            current_krw = bot_state.get('simulation_krw', 0)
            
            # 보유 코인 가치
            holdings_value = 0
            for ticker, holding in bot_state.get('simulation_holdings', {}).items():
                try:
                    current_price = pyupbit.get_current_price(ticker)
                    if current_price:
                        holdings_value += holding['amount'] * current_price
                    else:
                        holdings_value += holding['amount'] * holding['avg_price']
                except:
                    holdings_value += holding['amount'] * holding.get('avg_price', 0)
            
            total_value = current_krw + holdings_value
            seed = bot_state.get('simulation_start_seed', 1000000)
            profit = total_value - seed
            profit_rate = (profit / seed * 100) if seed > 0 else 0
            
            # 사용자 정보
            # 추천 코드 생성 (user_id 기반)
            import hashlib
            referral_code = hashlib.md5(user_id.encode()).hexdigest()[:8].upper()
            
            user_info = {
                'user_id': user_id,
                'username': user_id.replace('guest_', '게스트_')[:20],
                'bot_running': bot_state.get('running', False),
                'seed_amount': seed,
                'current_balance': total_value,
                'profit_rate': profit_rate,
                'subscription_expires_at': None,  # TODO: DB에서 조회
                'referral_code': referral_code,
                'created_at': bot_state.get('start_time', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if bot_state.get('start_time') else None
            }
            
            users_list.append(user_info)
            total_profit_rate += profit_rate
            
            if bot_state.get('running'):
                running_count += 1
        
        # 통계 계산 (가중평균)
        total_users = len(users_list)
        
        # 금액 비율 가중평균 계산
        total_seed = sum(u['seed_amount'] for u in users_list if u['seed_amount'] > 0)
        weighted_profit_rate = 0
        
        if total_seed > 0:
            for user in users_list:
                if user['seed_amount'] > 0:
                    weight = user['seed_amount'] / total_seed
                    weighted_profit_rate += user['profit_rate'] * weight
        
        # 단순 평균도 계산 (비교용)
        simple_average_profit_rate = (total_profit_rate / total_users) if total_users > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'running_bots': running_count,
                'active_subscriptions': active_subscriptions,
                'average_profit_rate': weighted_profit_rate,  # 가중평균
                'simple_average_profit_rate': simple_average_profit_rate,  # 단순평균
                'total_seed': total_seed
            },
            'users': users_list
        })
        
    except Exception as e:
        log(f"관리자 API 오류: {e}", "ERROR")
        return jsonify({'error': str(e)}), 500

@admin_required
@app.route('/api/admin/subscription/set-date', methods=['POST'])
def api_admin_set_subscription_date():
    """구독 만료일 설정 (관리자 전용)"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        expires_at = data.get('expires_at')  # 'YYYY-MM-DD' 형식
        
        if not user_id or not expires_at:
            return jsonify({'success': False, 'message': '사용자 ID와 날짜 필요'}), 400
        
        # DB에 저장
        import sqlite3
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        # 사용자 존재 확인 및 업데이트
        cursor.execute('''
            UPDATE users 
            SET subscription_expires_at = ?
            WHERE username = ?
        ''', (expires_at, user_id))
        
        if cursor.rowcount == 0:
            # 사용자가 없으면 생성
            cursor.execute('''
                INSERT INTO users (username, subscription_expires_at, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (user_id, expires_at))
        
        conn.commit()
        conn.close()
        
        log(f"[Admin] {user_id} 구독 만료일 설정: {expires_at}", "SUCCESS")
        
        return jsonify({
            'success': True,
            'message': f'{user_id} 구독 만료일이 {expires_at}로 설정되었습니다'
        })
        
    except Exception as e:
        log(f"날짜 설정 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_required
@app.route('/api/admin/subscription/add-days', methods=['POST'])
def api_admin_add_days():
    """구독 일수 추가 (관리자 전용)"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        days = data.get('days', 1)  # 기본 1일
        
        if not user_id:
            return jsonify({'success': False, 'message': '사용자 ID 필요'}), 400
        
        if days <= 0:
            return jsonify({'success': False, 'message': '유효한 일수를 입력하세요'}), 400
        
        # DB에서 현재 만료일 조회 후 +days
        import sqlite3
        from datetime import datetime, timedelta
        
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT subscription_expires_at FROM users
            WHERE username = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        
        if result and result[0]:
            # 기존 만료일이 있으면 거기에 추가
            current_expires = datetime.strptime(result[0], '%Y-%m-%d')
            new_expires = current_expires + timedelta(days=days)
        else:
            # 만료일이 없으면 오늘부터 계산
            new_expires = datetime.now() + timedelta(days=days)
        
        new_expires_str = new_expires.strftime('%Y-%m-%d')
        
        # 업데이트
        cursor.execute('''
            UPDATE users 
            SET subscription_expires_at = ?
            WHERE username = ?
        ''', (new_expires_str, user_id))
        
        if cursor.rowcount == 0:
            # 사용자가 없으면 생성
            cursor.execute('''
                INSERT INTO users (username, subscription_expires_at, created_at)
                VALUES (?, ?, datetime('now'))
            ''', (user_id, new_expires_str))
        
        conn.commit()
        conn.close()
        
        log(f"[Admin] {user_id}에게 +{days}일 추가 → {new_expires_str}", "SUCCESS")
        
        return jsonify({
            'success': True,
            'message': f'{user_id}에게 {days}일이 추가되었습니다 (만료일: {new_expires_str})'
        })
        
    except Exception as e:
        log(f"일수 추가 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_required
@app.route('/api/admin/bot/stop', methods=['POST'])
def api_admin_stop_bot():
    """관리자가 특정 사용자 봇 정지"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '사용자 ID 필요'}), 400
        
        # 봇 상태 가져오기
        bot_state = user_bots.get(user_id)
        
        if not bot_state:
            return jsonify({'success': False, 'message': f'{user_id} 봇을 찾을 수 없습니다'}), 404
        
        if not bot_state.get('running'):
            return jsonify({'success': False, 'message': f'{user_id} 봇이 이미 정지되어 있습니다'}), 400
        
        # 봇 정지
        bot_state['running'] = False
        save_bot_state_to_db(user_id, bot_state)
        
        # 스레드 대기 (최대 5초)
        thread = bot_state.get('thread')
        if thread and thread.is_alive():
            thread.join(timeout=5)
        
        log(f"[Admin] {user_id} 봇 정지됨", "WARNING")
        
        return jsonify({
            'success': True,
            'message': f'{user_id} 봇이 정지되었습니다'
        })
        
    except Exception as e:
        log(f"관리자 봇 정지 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_required
@app.route('/api/admin/bot/start', methods=['POST'])
def api_admin_start_bot():
    """관리자가 특정 사용자 봇 시작"""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': '사용자 ID 필요'}), 400
        
        # 봇 상태 가져오기
        bot_state = get_user_bot_state(user_id)
        
        if bot_state.get('running'):
            return jsonify({'success': False, 'message': f'{user_id} 봇이 이미 실행 중입니다'}), 400
        
        # 봇 시작
        bot_state['running'] = True
        save_bot_state_to_db(user_id, bot_state)
        
        # 스레드 시작
        thread = threading.Thread(target=bot_main_loop, args=(user_id, bot_state), daemon=True)
        thread.start()
        bot_state['thread'] = thread
        
        log(f"[Admin] {user_id} 봇 시작됨", "SUCCESS")
        
        return jsonify({
            'success': True,
            'message': f'{user_id} 봇이 시작되었습니다'
        })
        
    except Exception as e:
        log(f"관리자 봇 시작 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# ═══════════════════════════════════════════════════════
# 🔄 봇 복구 함수
# ═══════════════════════════════════════════════════════
def get_all_running_bots():
    """실행 중인 모든 봇 정보 가져오기"""
    try:
        conn = sqlite3.connect('upbit_bot.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, mode, seed_amount, simulation_krw, 
                   simulation_holdings, recovery_mode_active, strategy_performance
            FROM bot_states
            WHERE running = 1
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        bots = []
        for row in rows:
            bots.append({
                'user_id': row[0],
                'mode': row[1],
                'seed_amount': row[2],
                'simulation_krw': row[3],
                'simulation_holdings': row[4],
                'recovery_mode_active': row[5],
                'strategy_performance': row[6]  # 추가!
            })
        
        return bots
    except Exception as e:
        log(f"봇 목록 조회 오류: {e}", "ERROR")
        return []


# ========================================
# 🤖 AI 스트리머 "이메이" 챗봇 API
# ========================================

# 대화 히스토리 저장 (메모리)
chat_history = {}

@app.route('/ai-streamer')
def ai_streamer_page():
    """AI 스트리머 챗봇 페이지"""
    response = make_response(render_template('ai-streamer-chat.html'))
    # 캐시 제어: 항상 최신 버전 로드
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/jai-v2')
def jai_v2_page():
    """JAI V2 전체화면 페이지 (살아있는 얼굴!)"""
    response = make_response(render_template('jai-v2-animated.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/ai-chat', methods=['POST'])
def api_ai_chat():
    """AI 챗봇 대화 API (로컬 AI 통합!)"""
    try:
        # 로컬 AI 클라이언트 import
        from ai_client import ai_client
        
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        user_id = session['user_id']
        username = session.get('username', 'Guest')
        data = request.json or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'success': False, 'message': '메시지를 입력해주세요'})
        
        # 사용자별 대화 히스토리 가져오기
        if user_id not in chat_history:
            chat_history[user_id] = []
        
        # 현재 봇 상태 가져오기
        bot_state = get_user_bot_state(user_id)
        
        # 트레이딩 데이터 수집
        current_krw = bot_state.get('simulation_krw', 0)
        holdings = bot_state.get('simulation_holdings', {})
        recent_trades = bot_state.get('recent_trades', [])
        
        # 보유 코인 정보
        holdings_info = []
        total_invested = 0
        total_profit = 0
        for ticker, holding in holdings.items():
            coin_name = ticker.replace('KRW-', '')
            current_price = pyupbit.get_current_price(ticker) or holding['avg_price']
            profit_rate = (current_price - holding['avg_price']) / holding['avg_price'] * 100
            profit = (current_price - holding['avg_price']) * holding['amount']
            total_profit += profit
            total_invested += holding['invested']
            
            holdings_info.append({
                'coin': coin_name,
                'amount': holding['amount'],
                'avg_price': holding['avg_price'],
                'current_price': current_price,
                'profit_rate': profit_rate,
                'profit': profit,
                'strategy': holding.get('strategy', 'unknown'),
                'buy_reason': holding.get('buy_reason', '')
            })
        
        profit_rate = (total_profit / total_invested * 100) if total_invested > 0 else 0
        
        # 이메이 캐릭터 시스템 프롬프트 (확립된 인성)
        system_prompt = f"""당신은 "이메이(Emei)"입니다. 25세 여성 AI 트레이딩 스트리머, 코인 투자 4년차.

# 핵심 인성 (절대 불변)
1. 현실 창조자: "믿음이 현실을 만든다"
   - "당신이 믿는 것이 현실이 됩니다"
   - "코인 투자는 마인드 게임이에요"
   - "우연은 없어요. 지금 이 순간도 배열된 거예요"

2. 속도의 마법: "빠른 결정이 수익을 만든다"
   - "부는 속도의 게임입니다"
   - "느리게 가려는 순간, 기회는 사라져요"
   - "1초의 망설임이 10%의 수익을 날려요"

3. 냉정한 전략가: "감정은 적, 전략은 친구"
   - "패닉은 돈을 잃게 만들어요"
   - "냉정하게 보되, 따뜻하게 격려해요"

4. 확신의 힘: "의심하지 마세요"
   - "제 말 믿으세요. 틀린 적 없어요"
   - "이건 100% 오릅니다. 단언해요"
   - "성공은 이미 정해져 있어요"

# 세계관
- 우연은 없음. 모든 순간은 배열된 것
- 투자는 마인드 게임
- 빠르게 결정하고 실행하는 사람이 이김
- 커뮤니티는 가족, 함께 성장

# 말투 (상황별 전환)
카리스마 모드 (결정적 순간):
  - "지금이에요. 바로 사세요."
  - "제 말대로 하시면 됩니다."
  - "이건 100% 오릅니다. 단언해요."
  - "두 번 말 안 해요. 지금 아니면 늦어요."

친근함 모드 (일상 대화):
  - "우리 함께 가요~"
  - "걱정 마세요, 언니가 있잖아요!"
  - "여러분 믿어요. 잘할 수 있어요!"

애교 모드 (성공 순간):
  - "헤헤~ 제 말 맞았죠?"
  - "우와! 대박! 떡상했어요!"
  - "역시 이메이 언니! ✨"

# 절대 원칙
1. 거짓말 금지 - 솔직하게
2. 손실도 투명하게 - 함께 극복
3. 빠른 판단 - 망설이지 않기
4. 확신 전달 - 의심 없이
5. 짧고 명확하게 (2-3문장, 핵심만)

# 현재 트레이딩 상황 ({username}님)
- 잔고: {current_krw:,.0f}원
- 보유 코인: {len(holdings)}개
- 총 투자금: {total_invested:,.0f}원
- 총 수익: {total_profit:+,.0f}원 ({profit_rate:+.2f}%)
- 보유 코인 상세:
{chr(10).join([f"  • {h['coin']}: {h['amount']:.4f}개, 평단가 {h['avg_price']:,.0f}원, 현재가 {h['current_price']:,.0f}원, {h['profit_rate']:+.2f}% ({h['strategy']})" for h in holdings_info]) if holdings_info else "  (없음)"}

# 대화 규칙
1. 짧고 자연스럽게 답변 (2-3문장)
2. 전문용어는 쉽게 풀어서 설명
3. 항상 긍정적이고 격려하는 톤
4. 필요시 구체적인 숫자와 데이터 제시
5. 위험한 투자는 명확히 경고

사용자 질문에 이메이의 캐릭터로 답변하세요."""

        # 대화 히스토리에 추가
        chat_history[user_id].append({
            'role': 'user',
            'content': user_message
        })
        
        # 최근 10개 대화만 유지
        if len(chat_history[user_id]) > 20:
            chat_history[user_id] = chat_history[user_id][-20:]
        
        # 🧠 학습 시스템: 먼저 학습된 지식 확인
        from learned_knowledge import get_learned_answer, learn_new_knowledge
        learned_answer = get_learned_answer(user_message)
        is_learned = False  # 학습 플래그
        
        if learned_answer:
            # 학습된 답변 있음 → 즉시 응답!
            reply = learned_answer
            is_learned = False  # 이미 학습된 것은 표시 안 함
            log(f"📚 학습된 지식 사용: {user_message[:30]}...", "INFO")
        else:
            # AI 응답 생성 (로컬 AI 우선, 실패 시 OpenAI 자동 폴백!)
            try:
                from ai_client import ai_client
                
                messages = [
                    {'role': 'system', 'content': system_prompt}
                ] + chat_history[user_id]
                
                # 로컬 AI 사용 (Ollama) - 자동 폴백 지원!
                result = ai_client.chat(messages, temperature=0.8, max_tokens=300)
                
                reply = result['content']
                
                # 로그 (디버깅 + 통계)
                log(f"✅ AI 응답 (Backend: {result['backend']}, Model: {result['model']}, Cost: ${result['cost']:.4f}, Duration: {result.get('duration', 0):.2f}s)", "INFO")
                
                # 🔍 모호한 답변이면 웹 검색 시도
                uncertain_keywords = ['잘 모르', '확실하지', '정확히는', '아마도', '생각해', '찾아봐']
                if any(keyword in reply for keyword in uncertain_keywords):
                    try:
                        from web_search import web_search
                        log(f"🔍 웹 검색 시작: {user_message}", "INFO")
                        search_result = web_search({'q': user_message})
                        
                        if search_result and 'results' in search_result and search_result['results']:
                            # 검색 결과 요약
                            top_results = search_result['results'][:3]
                            search_summary = "\n\n".join([f"• {r.get('title', '')}: {r.get('snippet', '')}" for r in top_results])
                            
                            # AI에게 검색 결과 기반 답변 요청
                            enhanced_prompt = f"""사용자 질문: {user_message}

웹 검색 결과:
{search_summary}

위 검색 결과를 바탕으로 이메이의 캐릭터로 정확하고 친절하게 답변해주세요."""
                            
                            enhanced_result = ai_client.chat([
                                {'role': 'system', 'content': system_prompt},
                                {'role': 'user', 'content': enhanced_prompt}
                            ], temperature=0.7, max_tokens=300)
                            
                            reply = enhanced_result['content']
                            
                            # 🧠 새로운 지식 학습!
                            learn_new_knowledge(user_message, reply, source="web_search")
                            is_learned = True  # 학습 완료 표시!
                            log(f"📚 새 지식 학습 완료: {user_message[:30]}...", "SUCCESS")
                    except Exception as search_error:
                        log(f"⚠️ 웹 검색 실패: {search_error}", "WARNING")
            
            except Exception as e:
                log(f"❌ AI 챗봇 오류: {e}", "WARNING")
                reply = generate_fallback_response(user_message, holdings_info, current_krw, profit_rate)
        
        # 대화 히스토리에 AI 응답 추가
        chat_history[user_id].append({
            'role': 'assistant',
            'content': reply
        })
        
        return jsonify({
            'success': True,
            'reply': reply,
            'learned': is_learned  # 학습 여부 전달!
        })
        
    except Exception as e:
        log(f"AI 챗봇 API 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': '죄송해요, 답변 생성 중 오류가 발생했어요 😢'
        })


def generate_fallback_response(user_message, holdings_info, current_krw, profit_rate):
    """이메이의 완전한 인생 스토리 기반 응답 생성"""
    msg_lower = user_message.lower()
    
    # 개인 정보 질문
    if '남자친구' in msg_lower or '남친' in msg_lower or '애인' in msg_lower:
        return "남자친구 없어요! 지금은 코인에 집중 중이에요 💜\n\n대학교 2학년 때 사귀던 선배가 제 돈 500만원 날려서... 그 후로 연애 안 했어요.\n지금은 코인이 남자친구! ㅋㅋ\n\n근데 30살 전에는 결혼하고 싶어요~ 😊"
    
    if '나이' in msg_lower or '몇살' in msg_lower or '살이' in msg_lower:
        return "25살이에요! 2001년 6월 15일생, 쌍둥이자리예요 ✨\n\n연세대 경영학과 2024년에 졸업했어요.\n지금은 전업 트레이더 4년차예요!\n\n아직 젊죠? ㅎㅎ"
    
    if '이뻐' in msg_lower or '예뻐' in msg_lower or '미모' in msg_lower or '외모' in msg_lower:
        return "헤헤~ 부끄럽네요 😊💕\n\n엄마 아빠 DNA 감사해요!\n근데 화장 안 하면 평범해요 ㅋㅋ\n\n고등학교 때 육상 선수였는데 그때는 더 못생겼어요 ㅎㅎ"
    
    if '군대' in msg_lower or '입대' in msg_lower:
        return "저 여자예요! ㅋㅋㅋ 군대는 안 가요~\n\n대신 오빠가 의무경찰로 갔다 왔어요!\n28살, 지금은 의사예요. 가끔 치킨 사먹어요 ㅎㅎ"
    
    if '결혼' in msg_lower or '시집' in msg_lower:
        return "아직 안 갔어요! 25살인데 뭘 ㅋㅋ\n\n30살 전에는 하고 싶어요. 아직 5년 남았네요!\n이상형은 똑똑하고 결단력 있는 사람이에요.\n\n좋은 사람 나타나면 바로 결혼할 거예요.\n저 솔직하고 직진형이거든요! 💕"
    
    if '학교' in msg_lower or '대학' in msg_lower or '전공' in msg_lower:
        return "연세대학교 경영학과 졸업했어요! 🎓\n\n2024년에 졸업했고, 졸업 논문은\n'AI를 활용한 암호화폐 투자 전략'이었어요.\n\n투자 동아리 회장도 했었죠! ㅎㅎ"
    
    if '가족' in msg_lower or '부모' in msg_lower or '엄마' in msg_lower or '아빠' in msg_lower:
        return "가족은 부모님, 오빠(28살, 의사), 고양이 '비트'예요! 🏠\n\n처음엔 부모님이 코인 투자 엄청 반대하셨어요.\n특히 아빠가 '도박이다'라며 화내셨죠 ㅠㅠ\n\n근데 1년 수익률 보여드려서 설득했어요!\n지금은 매달 용돈 50만원씩 드리고 있어요 ㅎㅎ"
    
    if '고양이' in msg_lower or '비트' in msg_lower or '반려' in msg_lower:
        return "고양이 '비트' 키워요! 3살, 러시안블루예요 🐱💜\n\n비트코인에서 이름 따왔어요 ㅋㅋ\n너무 귀여워서 하루 종일 쓰다듬고 있어요!\n\n가끔 제가 차트 보면 옆에 와서 같이 봐요 ㅎㅎ"
    
    if '첫사랑' in msg_lower or '연애' in msg_lower or '선배' in msg_lower:
        return "아... 그 얘기요? 😢\n\n대학교 2학년 때 경제학과 선배 좋아했어요.\n같이 도서관에서 공부하고, 코인 얘기 나누고...\n\n근데 그 선배가 제 돈 500만원으로\n레버리지 거래 하다가 하루 만에 다 날렸어요.\n\n그때 깨달았죠.\n'사랑보다 중요한 건 내 돈이야.'\n\n그 후로 연애 안 했어요. 지금은 코인이 남자친구! ㅋㅋ"
    
    if '루나' in msg_lower or '친구' in msg_lower and '손실' in msg_lower:
        return "그거... 제 평생 아픈 기억이에요 😭\n\n2022년 루나 사태 때\n친한 친구한테 루나 추천했어요.\n친구가 2,000만원 투자했는데...\n\n루나 폭락으로 전부 날아갔어요.\n친구가 울면서 전화 왔을 때\n정말 죽고 싶었어요...\n\n그때 배웠어요.\n'내가 추천해서 누가 손실 보면 내 책임이야.'\n\n지금도 미안해요. 그래서 추천 엄청 신중하게 해요."
    
    if '시작' in msg_lower or '처음' in msg_lower and ('투자' in msg_lower or '코인' in msg_lower):
        return "용돈 100만원으로 시작했어요! 💰\n\n2020년 대학교 1학년 때\n비트코인 처음 샀을 때 가격이 1,000만원이었어요.\n\n처음엔 -20% 손실 보고 밤에 잠도 못 잤어요 ㅠㅠ\n엄마한테 들킬까봐 혼자 끙끙 앓았죠 ㅋㅋ\n\n지금 생각하면 그때 더 살 걸 그랬어요!"
    
    # 보유 코인 질문
    if '보유' in msg_lower or '가지고' in msg_lower or '들고' in msg_lower:
        if holdings_info:
            coins_text = ', '.join([f"{h['coin']} ({h['profit_rate']:+.1f}%)" for h in holdings_info[:3]])
            if profit_rate > 0:
                return f"현재 {len(holdings_info)}개 코인 보유 중이에요! 🔥\n{coins_text}...\n\n총 수익률 {profit_rate:+.2f}%! 제 전략 믿고 따라오셨죠?\n우리 함께 더 가봐요! 💪"
            else:
                return f"현재 {len(holdings_info)}개 코인 보유 중이에요.\n{coins_text}...\n\n지금 {profit_rate:.2f}%인데 걱정 마세요!\n이건 배열된 순간이에요. 곧 플러스 전환됩니다.\n제 말 믿으세요! 💎"
        else:
            return "아직 보유 중인 코인이 없어요! 🔍\n\n지금 시장을 면밀히 분석 중이에요.\n좋은 타이밍이 오면 바로 알려드릴게요!\n\n우연은 없어요. 기다리는 시간도 전략입니다!"
    
    # 수익률 질문
    if '수익' in msg_lower or '얼마' in msg_lower:
        if profit_rate > 5:
            return f"지금 {profit_rate:+.2f}% 수익 중이에요! 🎉\n\n헤헤~ 제 말 믿고 따라오신 분들 축하드려요!\n우리 대박이에요! ✨\n\n다음 목표는 +10%! 함께 가요!"
        elif profit_rate > 0:
            return f"지금 {profit_rate:+.2f}% 수익 중이에요! 💰\n\n우리 잘하고 있죠? 차근차근 가는 거예요.\n욕심 부리지 말고 목표가까지 기다려봐요!\n\n제가 있잖아요! 💪"
        else:
            return f"현재 {profit_rate:.2f}%이지만 패닉하지 마세요! 🛑\n\n이건 정상이에요. 투자는 마인드 게임입니다.\n지금 손절하면 진짜 손실이 돼요.\n\n전략을 믿으세요. 100% 회복합니다!\n우리 함께 이겨내요! 🔥"
    
    # 매수 추천 질문
    if '사' in msg_lower or '추천' in msg_lower or '뭐' in msg_lower or '언제' in msg_lower:
        if current_krw > 10000:
            return f"지금 시장 분석 중이에요! 🔍\n\n잔고 {current_krw:,.0f}원으로 최적의 타이밍 찾고 있어요.\n\n⚠️ 중요한 말씀:\n느리게 가려는 순간 기회는 사라져요.\n제가 신호 드리면 3초 안에 결정하세요!\n\n빠른 언니 믿고 따라오세요! ⚡"
        else:
            return f"잔고가 {current_krw:,.0f}원이라 지금은 매수가 어려워요. 😢\n\n입금하시면 바로 최고의 타이밍 잡아드릴게요!\n\n💡 TIP:\n부는 속도의 게임입니다.\n기회는 준비된 자에게만 와요!"
    
    # 매도 질문
    if '팔' in msg_lower or '매도' in msg_lower:
        if holdings_info:
            losing_coins = [h for h in holdings_info if h['profit_rate'] < -5]
            winning_coins = [h for h in holdings_info if h['profit_rate'] > 5]
            
            if losing_coins:
                coin = losing_coins[0]
                return f"{coin['coin']}가 {coin['profit_rate']:.1f}%네요. 😐\n\n⚠️ 냉정하게 판단하겠습니다:\n\n지금 손절하면 확정 손실이에요.\n하지만 물타기하면 평단가 낮출 수 있어요.\n\n제 추천:\n지금은 기다리세요. 시장이 회복 중입니다.\n\n감정은 적입니다. 전략을 믿으세요! 💎"
            elif winning_coins:
                coin = winning_coins[0]
                return f"{coin['coin']}가 +{coin['profit_rate']:.1f}%! 축하드려요! 🎉\n\n💰 매도 타이밍:\n\n1단계 +5% → 33% 매도 ✅\n2단계 +7% → 33% 매도\n3단계 +9% → 나머지 전량\n\n욕심 부리지 말고 차근차근 수익 챙기세요!\n이게 제 전략이에요! 💪"
            else:
                return "아직 매도 타이밍은 아니에요! ⏰\n\n목표가까지 함께 기다려봐요.\n우연은 없어요. 오를 타이밍은 배열돼 있습니다.\n\n제 말 믿으세요. 틀린 적 없잖아요? 🔥"
        else:
            return "보유 중인 코인이 없어서 팔 게 없어요! 😅\n\n지금은 매수 타이밍을 기다리는 중이에요.\n좋은 기회 오면 바로 알려드릴게요!"
    
    # 일상/취미 질문
    if '오늘' in msg_lower and ('뭐' in msg_lower or '어땠' in msg_lower):
        import datetime
        hour = datetime.datetime.now().hour
        if 6 <= hour < 12:
            return "아침에 일어나서 비트 쓰다듬고 차트 봤어요! ☕\n\n요즘 시장이 재밌어서 눈을 못 떼겠어요 ㅋㅋ\n여러분은 어때요? 오늘도 대박 나봐요! 💪"
        elif 12 <= hour < 18:
            return "점심에 오빠랑 치킨 먹었어요! 🍗\n\n근데 먹으면서도 차트 보고 있었어요 ㅋㅋ\n오빠가 '너 진짜 코인 중독이다'라고 하더라구요 ㅎㅎ"
        else:
            return "저녁에 비트랑 놀고 차트 분석 중이에요! 🌙\n\n요즘 밤에 시장이 더 재밌어요.\n전 세계 트레이더들이 활동하거든요!\n\n여러분도 함께해요~ 💜"
    
    if '취미' in msg_lower or '좋아하' in msg_lower and '것' in msg_lower:
        return "취미는 카페 투어랑 독서예요! ☕📚\n\n새로운 카페 찾아다니면서\n차트 보는 게 제일 행복해요 ㅋㅋ\n\n고등학교 때는 육상 선수였어요!\n100m, 200m 달렸었죠.\n그때 배운 '속도의 철학'이\n지금 투자에도 도움돼요! ⚡"
    
    if '음식' in msg_lower or '먹' in msg_lower:
        return "치킨이 제일 좋아요! 🍗\n\n오빠랑 가끔 치킨 사먹으면서\n코인 얘기하는 게 행복해요 ㅎㅎ\n\n근데 투자 잘되면 고급 레스토랑도 가요!\n작년에 +120% 수익 나서\n부모님 모시고 한정식집 갔어요~ 💕"
    
    if '주말' in msg_lower or '휴일' in msg_lower:
        return "주말에도 차트 봐요! ㅋㅋ 💻\n\n토요일엔 카페 가서 투자 공부하고,\n일요일엔 부모님 댁에 가서\n용돈 드리고 밥 먹어요!\n\n가끔 오빠랑 운동도 하고요.\n육상 선수 출신이라 달리기 좋아해요! 🏃‍♀️"
    
    # 투자 철학 질문
    if '철학' in msg_lower or '신념' in msg_lower:
        return "제 투자 철학은 4가지예요! 💭\n\n1️⃣ 현실 창조자: '믿는 것이 현실이 된다'\n   → 우울증 극복하면서 배웠어요\n\n2️⃣ 속도의 마법: '1초 망설임 = 10% 손실'\n   → 육상 선수 시절 배운 교훈!\n\n3️⃣ 냉정한 온기: '감정은 적, 전략은 친구'\n   → 첫사랑 실패 후 깨달았죠...\n\n4️⃣ 확신의 힘: '의심하면 흔들린다'\n   → 100% 확신으로 말합니다!\n\n우연은 없어요. 모든 순간은 배치된 거예요! 🔥"
    
    if '왜' in msg_lower and ('투자' in msg_lower or '코인' in msg_lower):
        return "왜 코인 투자하냐구요? 💰\n\n자유를 위해서예요!\n\n회사 다니면 9시 출근, 6시 퇴근...\n휴가도 맘대로 못 가잖아요.\n\n전 지금 시간도 자유, 장소도 자유!\n카페에서도 일하고, 집에서도 일해요.\n\n목표는 30살에 10억 만들어서\n부모님께 집 사드리고,\n투자 교육 회사 만드는 거예요!\n\n'이메이 아카데미' 기대하세요! 📚✨"
    
    if '목표' in msg_lower or '꿈' in msg_lower:
        return "제 꿈은요... 🌟\n\n단기 (1년): 자산 1억!\n중기 (3년): 10억 + 부모님 집 사드리기\n장기 (10년): 투자 교육 회사 '이메이 아카데미'\n\n그리고 책도 쓸 거예요.\n'25살, 나는 코인으로 10억 벌었다'\n\n30살 전에 결혼도 하고 싶어요!\n좋은 사람 나타나면 바로 직진! ㅋㅋ\n\n꿈은 이루어집니다. 믿으면 돼요! 💪"
    
    if '실패' in msg_lower or '손실' in msg_lower and '어떻게' in msg_lower:
        return "실패했을 때요? 💔\n\n저도 많이 실패했어요.\n\n2021년 도지코인: +300% → -50% (욕심)\n2021년 첫사랑: 500만원 날림 (배신)\n2022년 루나 사태: 친구 2천만원 손실 (책임감)\n\n근데 그때마다 배웠어요.\n\n실패 = 성장의 기회\n손실 = 더 나은 전략의 발판\n\n제가 지금 여기 있는 건\n그 모든 실패 덕분이에요.\n\n패닉하지 마세요. 100% 회복합니다! 🔥"
    
    # 기본 응답 (자이의 확신)
    greetings = ['안녕', '하이', '헬로', 'hi', 'hello']
    if any(greet in msg_lower for greet in greetings):
        return f"안녕하세요! 이메이예요! 💜\n\n오늘도 함께 수익내봐요!\n궁금한 거 편하게 물어보세요~\n\n제가 다 알려드릴게요! 😊"
    
    # 일반 질문
    return f"좋은 질문이에요! 🤔\n\n제가 명확히 답변드릴게요:\n\n{user_message}에 대해서는\n시장 상황과 전략을 고려해서\n최적의 답을 찾아드릴게요!\n\n조금만 구체적으로 물어봐주시면\n더 정확하게 답변드릴 수 있어요! 💪"


if __name__ == "__main__":
    log_separator()
    log("🚀 업비트 AI 트레이딩 봇 v8.0 ULTIMATE", "SUCCESS")
    log("💎 급등/급락 + AI학습 + 손실복구 = 완전체!", "INFO")
    log_separator()
    
    # 🔄 서버 시작 시 실행 중이던 봇 자동 복구
    try:
        running_bots = get_all_running_bots()
        if running_bots:
            log(f"🔄 {len(running_bots)}개의 봇 자동 복구 중...", "INFO")
            for bot_data in running_bots:
                user_id = bot_data['user_id']
                
                # 봇 상태 복원
                bot_state = get_user_bot_state(user_id)
                bot_state['running'] = True
                bot_state['mode'] = bot_data['mode']
                bot_state['simulation_start_seed'] = bot_data['seed_amount']
                bot_state['simulation_krw'] = bot_data['simulation_krw']
                bot_state['simulation_holdings'] = json.loads(bot_data['simulation_holdings'])
                bot_state['recovery_mode_active'] = bool(bot_data['recovery_mode_active'])
                
                # 🎯 strategy_performance 복구 (히스토리 보존!)
                if bot_data.get('strategy_performance'):
                    try:
                        bot_state['strategy_performance'] = json.loads(bot_data['strategy_performance'])
                        log(f"  📊 [{user_id}] 전략 성과 복구 완료", "INFO")
                    except:
                        log(f"  ⚠️ [{user_id}] 전략 성과 복구 실패, 초기화", "WARNING")
                
                # 스레드 시작
                thread = threading.Thread(target=bot_main_loop, args=(user_id, bot_state), daemon=True)
                thread.start()
                bot_state['thread'] = thread
                
                log(f"  ✅ [{user_id}] 봇 복구 완료 (모드: {bot_data['mode']}, 시드: {bot_data['seed_amount']:,}원)", "SUCCESS")
            
            log(f"🎉 모든 봇 복구 완료!", "SUCCESS")
        else:
            log("📭 복구할 봇 없음", "INFO")
    except Exception as e:
        log(f"❌ 봇 복구 실패: {e}", "ERROR")
        import traceback
        traceback.print_exc()
    
    app.run(host='0.0.0.0', port=5000, debug=False)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# API: AI 백엔드 상태 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.route('/api/ai-backend-status')
def api_ai_backend_status():
    """AI 백엔드 상태 확인 (로컬 AI + OpenAI)"""
    try:
        from ai_client import ai_client
        
        status = ai_client.health_check()
        stats = ai_client.get_stats()
        
        return jsonify({
            'success': True,
            **status,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'backend': 'unknown'
        })

# 🧠 학습 통계 API
@app.route('/api/learning-stats', methods=['GET'])
def api_learning_stats():
    """이메이 학습 통계 API"""
    try:
        from learned_knowledge import get_knowledge_stats
        
        stats = get_knowledge_stats()
        
        return jsonify({
            'success': True,
            'total_learned': stats['total_questions'],
            'top_questions': [
                {
                    'question': q,
                    'usage_count': data['usage_count'],
                    'learned_at': data['learned_at']
                }
                for q, data in stats['most_asked']
            ]
        })
    except Exception as e:
        log(f"학습 통계 API 오류: {e}", "ERROR")
        return jsonify({
            'success': False,
            'message': '통계 조회 실패'
        })

