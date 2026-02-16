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
from flask import Flask, render_template, jsonify, request, make_response, session, redirect
from flask_cors import CORS
import traceback
import os

# 커스텀 모듈
from user_manager import UserManager
from portfolio_manager import execute_diversified_buy, check_profit_trigger, get_available_coins
from trade_reasons import generate_buy_reason, generate_sell_reason
from recovery_system import analyze_current_holdings, create_recovery_plan, execute_recovery_plan, UPBIT_FEE_RATE
from bot_state_manager import init_bot_state_table, save_bot_state, load_bot_state, get_all_running_bots

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

# 전역 봇 상태 (하위 호환성 유지)
bot_state = create_bot_state()

def get_user_bot_state(user_id):
    """사용자 ID로 봇 상태 조회 또는 생성"""
    if user_id not in user_bots:
        user_bots[user_id] = create_bot_state()
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
# 💰 거래 실행
# ═══════════════════════════════════════════════════════
def execute_trade(ticker, strategy_id, patterns, bot_state):
    """거래 실행 (수수료 0.05% 포함)"""
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
            'type': 'RECOVERY' if bot_state['recovery_mode_active'] else patterns.get('type', 'NORMAL')
        }
        
        # 급락 매수인 경우 원가 저장
        if 'dip' in patterns:
            holding_info['price_before_dip'] = patterns['dip'].get('price_before_dip', current_price)
        
        bot_state['simulation_holdings'][ticker] = holding_info
        
        # ✅ 상세 로그
        coin_name = ticker.replace('KRW-', '')
        log("="*60, "SUCCESS")
        log(f"💰 {'[복구]' if bot_state['recovery_mode_active'] else ''} 매수: {coin_name}", "SUCCESS")
        log(f"   수량: {buy_amount:.6f}개", "INFO")
        log(f"   매수가: {current_price:,.0f}원", "INFO")
        log(f"   투자금: {invest_amount:,.0f}원", "INFO")
        log(f"   수수료: {fee:,.0f}원 (0.05%)", "INFO")
        log(f"   실투자: {net_invest:,.0f}원", "INFO")
        log(f"   전략: {STRATEGIES[strategy_id]['name']}", "INFO")
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

def execute_exit(ticker, holding, reason, bot_state):
    """청산 실행 (수수료 0.05% 포함)"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if not current_price:
            return None
        
        amount = holding['amount']
        entry_price = holding['avg_price']
        strategy_id = holding.get('strategy')
        invested = holding['invested']
        
        # ✅ 수수료 0.05% 계산
        FEE_RATE = 0.0005
        sell_value = amount * current_price  # 매도 총액
        fee = sell_value * FEE_RATE  # 수수료
        net_proceeds = sell_value - fee  # 실제 받는 금액
        
        profit_krw = net_proceeds - invested  # 순수익 = 실수령액 - 투자금
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
            log("="*60, "SUCCESS" if profit_rate > 0 else "WARNING")
            log(f"💸 매도: {coin_name}", "SUCCESS" if profit_rate > 0 else "WARNING")
            log(f"   수량: {amount:.6f}개", "INFO")
            log(f"   매도가: {current_price:,.0f}원", "INFO")
            log(f"   매도액: {sell_value:,.0f}원", "INFO")
            log(f"   수수료: {fee:,.0f}원 (0.05%)", "INFO")
            log(f"   실수령: {net_proceeds:,.0f}원", "INFO")
            log(f"   순수익: {profit_krw:+,.0f}원 ({profit_rate:+.2f}%)", "SUCCESS" if profit_krw > 0 else "WARNING")
            log(f"   사유: {reason}", "INFO")
            log("="*60, "SUCCESS" if profit_rate > 0 else "WARNING")
            
            # 거래 내역 추가 (상세 이유 포함)
            hold_time = (datetime.now() - holding['entry_time']).total_seconds() / 60
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
app.secret_key = os.urandom(24)  # 세션 암호화 키
CORS(app)

# UserManager 초기화
user_manager = UserManager()

# 🔧 bot_states 테이블 초기화
init_bot_state_table()

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
        
        user_id = session['user_id']
        
        bot_state = get_user_bot_state(user_id)
        
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
                        'profit_rate': profit_rate
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
            'recent_trades': recent_trades
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
    """거래 히스토리 API (연습/실전 모드 분리)"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        user_id = session['user_id']
        bot_state = get_user_bot_state(user_id)
        
        # 모드 파라미터 가져오기 (기본값: practice)
        mode = request.args.get('mode', 'practice')
        
        # 모든 거래 내역 가져오기
        all_trades = bot_state.get('recent_trades', [])
        
        # 모드별 필터링
        filtered_trades = [t for t in all_trades if t.get('mode', 'practice') == mode]
        
        # 통계 계산
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        total_profit_rate = 0
        
        for trade in filtered_trades:
            if trade['type'] == 'SELL':
                total_trades += 1
                profit_rate = trade.get('profit_rate', 0)
                total_profit_rate += profit_rate
                
                if profit_rate >= 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_profit = (total_profit_rate / total_trades) if total_trades > 0 else 0
        
        # 거래 내역 변환 (최신순)
        trades_list = []
        for trade in reversed(filtered_trades):  # 최신 거래가 먼저 오도록
            trade_data = {
                'ticker': trade['ticker'],
                'type': trade['type'],
                'amount': trade['amount'],
                'price': trade['price'],
                'fee': trade.get('fee', 0),
                'timestamp': trade.get('timestamp', ''),
                'reason': trade.get('reason', ''),
                'strategy': trade.get('strategy', '전략 미상'),
                'mode': trade.get('mode', 'practice')
            }
            
            if trade['type'] == 'BUY':
                trade_data['invested'] = trade.get('invested', 0)
                trade_data['net_invested'] = trade.get('net_invested', 0)
            else:  # SELL
                trade_data['entry_price'] = trade.get('entry_price', 0)
                trade_data['sell_value'] = trade.get('sell_value', 0)
                trade_data['net_proceeds'] = trade.get('net_proceeds', 0)
                trade_data['profit'] = trade.get('profit', 0)
                trade_data['profit_rate'] = trade.get('profit_rate', 0)
            
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
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        user_id = session['user_id']
        
        log(f"[START] user_id: {user_id}", "INFO")
        bot_state = get_user_bot_state(user_id)
        
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
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        user_id = session['user_id']
        
        log(f"[STOP] user_id: {user_id}", "INFO")
        bot_state = get_user_bot_state(user_id)
        
        bot_state['running'] = False
        
        # 💾 DB에 봇 상태 저장
        save_bot_state(user_id, bot_state)
        
        # 스레드가 종료될 때까지 대기 (최대 5초)
        if 'thread' in bot_state and bot_state['thread'] and bot_state['thread'].is_alive():
            bot_state['thread'].join(timeout=5)
        log(f"[{user_id}] 봇이 정지되었습니다", "INFO")
        return jsonify({'success': True, 'message': '봇 중지'})
    except Exception as e:
        log(f"정지 오류: {e}", "ERROR")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/user/referral-link')
def api_get_referral_link():
    """사용자의 추천 링크 가져오기"""
    try:
        # 사용자 ID 가져오기
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '로그인이 필요합니다'})
        
        user_id = session['user_id']
        
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
    time.sleep(5)
    log(f"[{user_id}] ✅ 스캔 시작!", "SUCCESS")
    
    popular_tickers = [
        'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
        'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK',
        'KRW-ATOM', 'KRW-ETC', 'KRW-NEAR', 'KRW-HBAR', 'KRW-APT',
        'KRW-SUI', 'KRW-TRX', 'KRW-SHIB', 'KRW-TON', 'KRW-PEPE',
        'KRW-ARB', 'KRW-OP', 'KRW-IMX', 'KRW-AAVE', 'KRW-ALGO'
    ]
    
    loop_count = 0  # 루프 카운터 추가
    
    while bot_state['running']:
        try:
            loop_count += 1
            log(f"[{user_id}] 🔄 루프 #{loop_count} 시작", "INFO")
            
            # 1. 복구 모드 체크
            if not bot_state['recovery_mode_active']:
                check_recovery_mode_activation(bot_state)
            
            # 2. 보유 포지션 관리
            for ticker, holding in list(bot_state['simulation_holdings'].items()):
                should_exit, reason = check_exit(ticker, holding, bot_state)
                if should_exit:
                    execute_exit(ticker, holding, reason, bot_state)
            
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
                    
                    opportunities = find_recovery_opportunity(popular_tickers[:10], bot_state)
                    if opportunities:
                        best = opportunities[0]
                        execute_trade(best['ticker'], 'surge_hunter', {'recovery': best}, bot_state)
                
                # 일반 모드
                else:
                    import random
                    scan_tickers = random.sample(popular_tickers, min(5, len(popular_tickers)))
                    log(f"[{user_id}] 📊 {len(scan_tickers)}개 티커 스캔 중...", "INFO")
                    
                    for ticker in scan_tickers:
                        try:
                            patterns = analyze_all_patterns(ticker)
                            
                            if patterns:
                                bot_state['current_patterns'][ticker] = patterns
                                best_strategy, score = select_best_strategy(ticker, patterns)
                                
                                if best_strategy and score > 0.3:
                                    log(f"[{user_id}] 🎯 {ticker} 매수 신호 감지 (전략: {best_strategy}, 점수: {score:.2f})", "SUCCESS")
                                    execute_trade(ticker, best_strategy, patterns, bot_state)
                                    time.sleep(2)
                                    break
                        except Exception as ticker_error:
                            log(f"[{user_id}] ⚠️ {ticker} 분석 오류: {ticker_error}", "WARNING")
                            continue
                    
                    log(f"[{user_id}] ✅ 스캔 완료, 대기 중...", "INFO")
            
            bot_state['last_update'] = datetime.now()
            sleep_time = 15 if bot_state['recovery_mode_active'] else 20
            log(f"[{user_id}] 💤 {sleep_time}초 대기...", "INFO")
            time.sleep(sleep_time)
            
        except Exception as e:
            log(f"[{user_id}] ❌ 메인 루프 오류: {e}", "ERROR")
            import traceback
            traceback.print_exc()
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
        
        # 세션 저장
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

# ═══════════════════════════════════════════════════════
# 👨‍💼 관리자 API
# ═══════════════════════════════════════════════════════

@app.route('/admin')
def admin_page():
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
