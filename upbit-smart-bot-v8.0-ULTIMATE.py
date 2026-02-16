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
from flask import Flask, render_template, jsonify, request, make_response
from flask_cors import CORS
import traceback

# ═══════════════════════════════════════════════════════
# ⚙️ 전체 설정
# ═══════════════════════════════════════════════════════

# 급등/급락 감지
SURGE_CONFIG = {
    # 급등
    'surge_threshold_1m': 1.5,
    'surge_threshold_3m': 2.5,
    
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
    
    # 익절/손절
    'take_profit_targets': [1.5, 2.5, 4.0],
    'stop_loss': -2.0,
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
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'dip_hunter': {
        'name': '급락 저점 → 원가 복귀',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'box_trader': {
        'name': '박스권 매매',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'trend_follower': {
        'name': '추세 추종',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    },
    'volume_hunter': {
        'name': '수급 기반',
        'enabled': True,
        'weight': 1.0,
        'performance': {'trades': 0, 'wins': 0, 'total_profit': 0}
    }
}

# ═══════════════════════════════════════════════════════
# 🎮 봇 상태 관리
# ═══════════════════════════════════════════════════════
bot_state = {
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
    'strategy_performance': STRATEGIES.copy(),
    'current_patterns': {},
    
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
    
    'last_update': None,
    'start_time': None,
}

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

# ═══════════════════════════════════════════════════════
# 🚀 급등 감지
# ═══════════════════════════════════════════════════════
def detect_surge_signal(ticker):
    """급등 신호 감지"""
    try:
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
        if df_1m is None or len(df_1m) < 10:
            return None
        
        price_before = df_1m['close'].iloc[-2]
        price_now = df_1m['close'].iloc[-1]
        change_1m = ((price_now - price_before) / price_before) * 100
        vol_spike = calculate_volume_spike(df_1m)
        
        if change_1m >= SURGE_CONFIG['surge_threshold_1m'] and vol_spike >= SURGE_CONFIG['volume_spike_ratio']:
            return {
                'type': 'SURGE',
                'ticker': ticker,
                'current_price': price_now,
                'change_pct': change_1m,
                'vol_spike': vol_spike,
                'signals': [f'급등 +{change_1m:.2f}%', f'거래량 {vol_spike:.1f}배'],
                'score': 5
            }
        
        return None
    except:
        return None

# ═══════════════════════════════════════════════════════
# 📉 급락 감지
# ═══════════════════════════════════════════════════════
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

def analyze_all_patterns(ticker):
    """모든 패턴 종합 분석"""
    patterns = {}
    
    # 급등/급락 우선
    surge = detect_surge_signal(ticker)
    if surge:
        patterns['surge'] = surge
    
    dip = detect_dip_signal(ticker)
    if dip:
        patterns['dip'] = dip
    
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
        elif 'box' in patterns and strategy_id == 'box_trader':
            score += patterns['box']['confidence'] * 5 * 0.5
        elif 'trend' in patterns and strategy_id == 'trend_follower':
            score += patterns['trend']['confidence'] * 5 * 0.5
        elif 'volume' in patterns and strategy_id == 'volume_hunter':
            score += patterns['volume']['confidence'] * 5 * 0.5
        
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
def check_recovery_mode_activation():
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

def find_recovery_opportunity(tickers):
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
# 💰 거래 실행
# ═══════════════════════════════════════════════════════
def execute_trade(ticker, strategy_id, patterns):
    """거래 실행"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            invest_amount = bot_state['recovery_seed']
        else:
            invest_amount = min(bot_state['simulation_krw'] * 0.15, 150000)
        
        if invest_amount < 5000:
            return None
        
        buy_amount = invest_amount / current_price
        
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
            'entry_time': datetime.now(),
            'strategy': strategy_id,
            'patterns': patterns,
            'peak_price': current_price,
            'type': 'RECOVERY' if bot_state['recovery_mode_active'] else patterns.get('type', 'NORMAL')
        }
        
        # 급락 매수인 경우 원가 저장
        if 'dip' in patterns:
            holding_info['price_before_dip'] = patterns['dip'].get('price_before_dip', current_price)
        
        bot_state['simulation_holdings'][ticker] = holding_info
        
        log(f"💰 {'[복구]' if bot_state['recovery_mode_active'] else ''} 매수: {ticker} | {current_price:,.0f}원 | {STRATEGIES[strategy_id]['name']}", "SUCCESS")
        
        # 거래 내역 추가
        bot_state['recent_trades'].append({
            'ticker': ticker,
            'type': 'BUY',
            'amount': buy_amount,
            'price': current_price,
            'strategy': STRATEGIES[strategy_id]['name'],
            'timestamp': datetime.now().isoformat()
        })
        
        return True
    except Exception as e:
        log(f"거래 오류: {e}", "ERROR")
        return None

def check_exit(ticker, holding):
    """청산 조건 체크"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return False, None
        
        entry_price = holding['avg_price']
        profit_rate = (current_price - entry_price) / entry_price * 100
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
            
            hold_time = (datetime.now() - holding['entry_time']).total_seconds() / 60
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
            
            hold_time = (datetime.now() - holding['entry_time']).total_seconds() / 60
            if hold_time >= SURGE_CONFIG['dip_max_hold_time']:
                return True, "급락 최대시간"
        
        # 일반
        else:
            if profit_rate >= 3.0 or profit_rate <= SURGE_CONFIG['stop_loss']:
                return True, f"{'익절' if profit_rate > 0 else '손절'}"
        
        return False, None
    except:
        return False, None

def execute_exit(ticker, holding, reason):
    """청산 실행"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        amount = holding['amount']
        entry_price = holding['avg_price']
        strategy_id = holding.get('strategy')
        invested = holding['invested']
        
        sell_krw = amount * current_price
        profit_krw = sell_krw - invested
        profit_rate = (current_price - entry_price) / entry_price * 100
        
        # 복구 모드
        if bot_state['recovery_mode_active']:
            bot_state['recovery_seed'] += sell_krw
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
            bot_state['simulation_krw'] += sell_krw
            log(f"💸 매도: {ticker} | {profit_rate:+.2f}% | {reason}", "SUCCESS" if profit_rate > 0 else "WARNING")
            
            # 거래 내역 추가
            bot_state['recent_trades'].append({
                'ticker': ticker,
                'type': 'SELL',
                'amount': holding['amount'],
                'price': current_price,
                'profit_rate': profit_rate,
                'timestamp': datetime.now().isoformat()
            })
        
        del bot_state['simulation_holdings'][ticker]
        
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
CORS(app)

@app.route('/')
def index():
    response = make_response(render_template('dashboard-ultimate-v2.html'))
    # 캐시 방지
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/status')
def api_status():
    try:
        # 봇이 실행 중이 아니면 초기 상태 반환
        if not bot_state['running']:
            return jsonify({
                'running': False,
                'current_krw': bot_state.get('simulation_seed', 1000000),
                'total_profit': 0,
                'profit_rate': 0,
                'win_rate': 0,
                'strategies': bot_state['strategy_performance'],
                'recent_surges': [],
                'recent_trades': []
            })
        
        # 봇 실행 중일 때만 실제 계산
        current_krw = bot_state['simulation_krw'] + bot_state.get('recovery_seed', 0)
        
        # 보유 코인 가치 계산 (실제 가격 조회)
        holdings_value = 0
        if bot_state['simulation_holdings']:
            for ticker, h in bot_state['simulation_holdings'].items():
                try:
                    current_price = pyupbit.get_current_price(ticker)
                    if current_price:
                        holdings_value += h['amount'] * current_price
                    else:
                        holdings_value += h['amount'] * h['avg_price']
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
        
        return jsonify({
            'running': True,
            'current_krw': current_krw,
            'total_profit': profit,
            'profit_rate': profit_rate,
            'win_rate': win_rate,
            'strategies': bot_state['strategy_performance'],
            'recent_surges': [],
            'recent_trades': recent_trades
        })
    except Exception as e:
        log(f"API 상태 조회 오류: {e}", "ERROR")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    try:
        if bot_state['running']:
            return jsonify({'success': False, 'message': '이미 실행 중'})
        
        data = request.json or {}
        mode = data.get('mode', 'practice')
        seed = data.get('seed', 1000000)
        txid = data.get('txid', '')
        
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
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'❌ 잔고 조회 실패: {str(e)}\n\nAPI 키를 확인하세요.'
                })
        
        # 완전 초기화
        bot_state['mode'] = mode
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
        
        bot_state['running'] = True
        bot_state['start_time'] = datetime.now()
        
        thread = threading.Thread(target=bot_main_loop, daemon=True)
        thread.start()
        bot_state['thread'] = thread
        
        mode_text = "💎 실전 모드" if mode == 'live' else "연습 모드"
        log(f"봇 시작! {mode_text}, 시드: {seed:,}원", "SUCCESS")
        
        return jsonify({'success': True, 'message': f'✅ 봇 시작! ({mode_text})'})
    except Exception as e:
        log(f"시작 오류: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    try:
        bot_state['running'] = False
        # 스레드가 종료될 때까지 대기 (최대 5초)
        if 'thread' in bot_state and bot_state['thread'] and bot_state['thread'].is_alive():
            bot_state['thread'].join(timeout=5)
        log("봇이 정지되었습니다", "INFO")
        return jsonify({'success': True, 'message': '봇 중지'})
    except Exception as e:
        log(f"정지 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

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
def bot_main_loop():
    """메인 루프 (완전체)"""
    log_separator()
    log("🚀 AI 트레이딩 봇 v8.0 ULTIMATE 시작!", "SUCCESS")
    log_separator()
    
    bot_state['start_time'] = datetime.now()
    
    popular_tickers = [
        'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
        'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK',
        'KRW-ATOM', 'KRW-ETC', 'KRW-NEAR', 'KRW-HBAR', 'KRW-APT'
    ]
    
    while bot_state['running']:
        try:
            # 1. 복구 모드 체크
            if not bot_state['recovery_mode_active']:
                check_recovery_mode_activation()
            
            # 2. 보유 포지션 관리
            for ticker, holding in list(bot_state['simulation_holdings'].items()):
                should_exit, reason = check_exit(ticker, holding)
                if should_exit:
                    execute_exit(ticker, holding, reason)
            
            # 3. 신규 진입
            max_positions = 1 if bot_state['recovery_mode_active'] else 3
            
            if len(bot_state['simulation_holdings']) < max_positions:
                # 복구 모드
                if bot_state['recovery_mode_active']:
                    # 쿨다운
                    if bot_state['last_loss_time']:
                        cooldown = (datetime.now() - bot_state['last_loss_time']).total_seconds()
                        if cooldown < 120:
                            time.sleep(5)
                            continue
                    
                    opportunities = find_recovery_opportunity(popular_tickers[:10])
                    if opportunities:
                        best = opportunities[0]
                        execute_trade(best['ticker'], 'surge_hunter', {'recovery': best})
                
                # 일반 모드
                else:
                    import random
                    scan_tickers = random.sample(popular_tickers, min(5, len(popular_tickers)))
                    
                    for ticker in scan_tickers:
                        try:
                            patterns = analyze_all_patterns(ticker)
                            
                            if patterns:
                                bot_state['current_patterns'][ticker] = patterns
                                best_strategy, score = select_best_strategy(ticker, patterns)
                                
                                if best_strategy and score > 0.5:
                                    execute_trade(ticker, best_strategy, patterns)
                                    time.sleep(2)
                                    break
                        except:
                            continue
            
            bot_state['last_update'] = datetime.now()
            time.sleep(15 if bot_state['recovery_mode_active'] else 20)
            
        except Exception as e:
            log(f"메인 루프 오류: {e}", "ERROR")
            time.sleep(10)
    
    log("🛑 봇 중지", "WARNING")

if __name__ == "__main__":
    log_separator()
    log("🚀 업비트 AI 트레이딩 봇 v8.0 ULTIMATE", "SUCCESS")
    log("💎 급등/급락 + AI학습 + 손실복구 = 완전체!", "INFO")
    log_separator()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
