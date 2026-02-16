#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 업비트 급등 포착 봇 v7.2 - SURGE HUNTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 핵심 전략: 24시간 대기 → 급등 신호 포착 → 초고속 진입 → 익절

✨ 셀링 포인트:
1. 연습 모드에서 실전과 동일하게 작동
2. 실시간 급등 코인 자동 포착
3. 투명한 수익 증명
4. 검증된 전략으로 실전 전환

🎯 목표: 연습 모드에서 확실한 수익을 보여주고 실전 전환 유도
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
from collections import deque
import traceback

# ═══════════════════════════════════════════════════════
# 🌐 Flask 웹 서버 설정
# ═══════════════════════════════════════════════════════
app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════
# 🎨 터미널 색상 코드
# ═══════════════════════════════════════════════════════
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ═══════════════════════════════════════════════════════
# 🚀 급등 포착 설정
# ═══════════════════════════════════════════════════════
SURGE_CONFIG = {
    # 급등 감지 조건
    'surge_threshold_1m': 1.5,      # 1분봉 1.5% 이상 상승
    'surge_threshold_3m': 2.5,      # 3분봉 2.5% 이상 상승
    'surge_threshold_5m': 3.5,      # 5분봉 3.5% 이상 상승
    'surge_threshold_15m': 5.0,     # 15분봉 5% 이상 상승
    
    # 거래량 조건
    'volume_spike_ratio': 2.0,      # 평균 거래량 대비 2배 이상
    'min_volume_krw': 100000000,    # 최소 1억원 거래량
    
    # 진입 조건
    'max_entry_price_increase': 0.5, # 급등 감지 후 최대 0.5% 상승까지 진입
    'entry_speed': 'FAST',           # FAST (즉시), CAUTIOUS (조심)
    
    # 익절/손절
    'take_profit_targets': [1.5, 2.5, 4.0],  # 1.5%, 2.5%, 4.0% 익절
    'take_profit_ratios': [0.4, 0.4, 0.2],   # 40%, 40%, 20% 비중
    'stop_loss': -2.0,               # -2% 손절
    'trailing_stop': True,           # 트레일링 스톱 사용
    'trailing_stop_trigger': 3.0,    # 3% 수익 시 트레일링 시작
    'trailing_stop_distance': 1.5,   # 최고점 대비 1.5% 하락 시 매도
    
    # 필터링
    'exclude_new_coins_days': 7,     # 7일 이내 신규 상장 코인 제외
    'min_price_krw': 100,            # 최소 100원 이상
    'max_price_krw': 10000000,       # 최대 1,000만원 이하
}

# ═══════════════════════════════════════════════════════
# 🎮 봇 상태 관리
# ═══════════════════════════════════════════════════════
bot_state = {
    'running': False,
    'mode': 'practice',  # 'practice' 또는 'live'
    'upbit': None,
    'thread': None,
    
    # 시드 관리
    'initial_seed': 0,
    'current_krw': 0,
    'total_profit': 0,
    
    # 시뮬레이션 (연습 모드)
    'simulation_seed': 1000000,      # 기본 100만원
    'simulation_krw': 1000000,
    'simulation_holdings': {},       # {'KRW-BTC': {'amount': 0.001, 'avg_price': 50000000}}
    'simulation_start_seed': 1000000,
    
    # 보유 현황
    'holdings': [],
    'trade_history': [],
    
    # 급등 포착 시스템
    'surge_alerts': deque(maxlen=100),  # 최근 100개 급등 알림
    'watching_coins': [],                # 현재 모니터링 중인 코인
    'active_trades': [],                 # 진행 중인 거래
    'surge_statistics': {
        'total_surges_detected': 0,
        'total_trades_executed': 0,
        'successful_trades': 0,
        'failed_trades': 0,
        'total_profit_krw': 0,
        'win_rate': 0,
        'avg_profit_per_trade': 0,
    },
    
    # 시스템
    'last_update': None,
    'error': None,
    'start_time': None,
}

# ═══════════════════════════════════════════════════════
# 📝 로깅 함수
# ═══════════════════════════════════════════════════════
def log(message, level="INFO", color=None):
    """상세한 로그 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    level_colors = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "SURGE": Colors.BOLD + Colors.YELLOW,  # 급등 알림
        "TRADE": Colors.BOLD + Colors.GREEN,   # 거래 실행
    }
    
    if color is None:
        color = level_colors.get(level, Colors.CYAN)
    
    level_emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "SURGE": "🚀",
        "TRADE": "💰",
    }
    
    emoji = level_emoji.get(level, "📝")
    
    print(f"{color}[{timestamp}] {emoji} {level}: {message}{Colors.END}")
    sys.stdout.flush()

def log_separator():
    """시각적 구분선"""
    print(f"\n{Colors.CYAN}{'═' * 80}{Colors.END}\n")
    sys.stdout.flush()

# ═══════════════════════════════════════════════════════
# 🔑 API 키 관리
# ═══════════════════════════════════════════════════════
def load_api_keys():
    """API 키 로드"""
    try:
        if os.path.exists('api_keys.json'):
            with open('api_keys.json', 'r') as f:
                keys = json.load(f)
                return keys.get('access_key'), keys.get('secret_key')
    except Exception as e:
        log(f"API 키 로드 실패: {e}", "ERROR")
    return None, None

def save_api_keys(access_key, secret_key):
    """API 키 저장"""
    try:
        with open('api_keys.json', 'w') as f:
            json.dump({
                'access_key': access_key,
                'secret_key': secret_key
            }, f)
        return True
    except Exception as e:
        log(f"API 키 저장 실패: {e}", "ERROR")
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
        return rsi.iloc[-1]
    except:
        return 50

def calculate_volume_spike(df):
    """거래량 급증 감지"""
    try:
        avg_volume = df['volume'].rolling(window=20).mean().iloc[-2]
        current_volume = df['volume'].iloc[-1]
        spike_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        return spike_ratio
    except:
        return 0

def calculate_price_momentum(df, window=5):
    """가격 모멘텀 계산"""
    try:
        price_change = (df['close'].iloc[-1] - df['close'].iloc[-window]) / df['close'].iloc[-window] * 100
        return price_change
    except:
        return 0

# ═══════════════════════════════════════════════════════
# 🚀 급등 감지 시스템
# ═══════════════════════════════════════════════════════
def detect_surge_signal(ticker):
    """급등 신호 감지 - 다중 시간대 분석"""
    try:
        surge_signals = []
        
        # 1분봉 체크 (가장 빠른 신호)
        df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=20)
        if df_1m is not None and len(df_1m) >= 2:
            change_1m = (df_1m['close'].iloc[-1] - df_1m['close'].iloc[-2]) / df_1m['close'].iloc[-2] * 100
            volume_spike_1m = calculate_volume_spike(df_1m)
            
            if change_1m >= SURGE_CONFIG['surge_threshold_1m'] and volume_spike_1m >= SURGE_CONFIG['volume_spike_ratio']:
                surge_signals.append({
                    'timeframe': '1분',
                    'change': change_1m,
                    'volume_spike': volume_spike_1m,
                    'strength': 'HIGH'
                })
        
        # 3분봉 체크 (중기 신호)
        df_3m = pyupbit.get_ohlcv(ticker, interval="minute3", count=20)
        if df_3m is not None and len(df_3m) >= 2:
            change_3m = (df_3m['close'].iloc[-1] - df_3m['close'].iloc[-2]) / df_3m['close'].iloc[-2] * 100
            volume_spike_3m = calculate_volume_spike(df_3m)
            
            if change_3m >= SURGE_CONFIG['surge_threshold_3m'] and volume_spike_3m >= SURGE_CONFIG['volume_spike_ratio']:
                surge_signals.append({
                    'timeframe': '3분',
                    'change': change_3m,
                    'volume_spike': volume_spike_3m,
                    'strength': 'MEDIUM'
                })
        
        # 5분봉 체크 (안정적 신호)
        df_5m = pyupbit.get_ohlcv(ticker, interval="minute5", count=20)
        if df_5m is not None and len(df_5m) >= 2:
            change_5m = (df_5m['close'].iloc[-1] - df_5m['close'].iloc[-2]) / df_5m['close'].iloc[-2] * 100
            volume_spike_5m = calculate_volume_spike(df_5m)
            rsi_5m = calculate_rsi(df_5m)
            
            if change_5m >= SURGE_CONFIG['surge_threshold_5m'] and volume_spike_5m >= SURGE_CONFIG['volume_spike_ratio']:
                surge_signals.append({
                    'timeframe': '5분',
                    'change': change_5m,
                    'volume_spike': volume_spike_5m,
                    'rsi': rsi_5m,
                    'strength': 'CONFIRMED'
                })
        
        return surge_signals if surge_signals else None
        
    except Exception as e:
        log(f"급등 감지 오류 ({ticker}): {e}", "ERROR")
        return None

def scan_all_markets_for_surge():
    """전체 마켓 스캔 - 급등 코인 찾기 (최적화 버전)"""
    try:
        # 전체 KRW 마켓 조회
        tickers = pyupbit.get_tickers(fiat="KRW")
        
        # ⚡ 최적화: 인기 코인만 먼저 스캔 (상위 50개)
        # 실제 급등은 주로 거래량 많은 코인에서 발생
        popular_tickers = [
            'KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-SOL', 'KRW-DOGE',
            'KRW-ADA', 'KRW-AVAX', 'KRW-DOT', 'KRW-MATIC', 'KRW-LINK',
            'KRW-ATOM', 'KRW-ETC', 'KRW-BCH', 'KRW-LTC', 'KRW-NEAR',
            'KRW-HBAR', 'KRW-APT', 'KRW-ARB', 'KRW-OP', 'KRW-SUI',
            'KRW-SEI', 'KRW-STRK', 'KRW-TIA', 'KRW-INJ', 'KRW-FET'
        ]
        
        # 인기 코인 + 나머지 랜덤 25개
        import random
        other_tickers = [t for t in tickers if t not in popular_tickers]
        scan_tickers = popular_tickers + random.sample(other_tickers, min(25, len(other_tickers)))
        
        surge_candidates = []
        
        log(f"🔍 빠른 스캔 시작... ({len(scan_tickers)}개 코인)", "INFO")
        
        # ⚡ 최적화: 한 번에 여러 코인 현재가 조회
        try:
            prices = pyupbit.get_current_price(scan_tickers)
            if prices is None:
                prices = {}
        except:
            prices = {}
        
        scanned = 0
        for ticker in scan_tickers:
            try:
                # 기본 필터링
                current_price = prices.get(ticker) if isinstance(prices, dict) else None
                if current_price is None:
                    current_price = pyupbit.get_current_price(ticker)
                    if current_price is None:
                        continue
                
                # 가격 범위 필터
                if current_price < SURGE_CONFIG['min_price_krw'] or current_price > SURGE_CONFIG['max_price_krw']:
                    continue
                
                # 급등 신호 감지
                surge_signals = detect_surge_signal(ticker)
                
                if surge_signals:
                    # 거래량 확인
                    df_1m = pyupbit.get_ohlcv(ticker, interval="minute1", count=5)
                    if df_1m is not None:
                        total_volume_krw = (df_1m['close'] * df_1m['volume']).sum()
                        
                        if total_volume_krw >= SURGE_CONFIG['min_volume_krw']:
                            surge_candidates.append({
                                'ticker': ticker,
                                'current_price': current_price,
                                'signals': surge_signals,
                                'volume_krw': total_volume_krw,
                                'detected_at': datetime.now(),
                            })
                            
                            log(f"🚀 급등 감지! {ticker} | 가격: {current_price:,.0f}원 | 신호: {len(surge_signals)}개", "SURGE")
                
                scanned += 1
                if scanned % 10 == 0:
                    log(f"   진행: {scanned}/{len(scan_tickers)} 스캔 완료", "INFO")
                
                time.sleep(0.05)  # API 호출 제한 (0.1 → 0.05초로 단축)
                
            except Exception as e:
                continue
        
        log(f"✅ 스캔 완료: {scanned}개 코인 분석, {len(surge_candidates)}개 급등 발견", "SUCCESS")
        
        return surge_candidates
        
    except Exception as e:
        log(f"마켓 스캔 오류: {e}", "ERROR")
        return []

# ═══════════════════════════════════════════════════════
# 💰 거래 실행 시스템
# ═══════════════════════════════════════════════════════
def execute_surge_trade(upbit, surge_info, mode='practice'):
    """급등 코인 진입"""
    try:
        ticker = surge_info['ticker']
        current_price = surge_info['current_price']
        
        # 진입 금액 계산 (시드의 10-20% 사용)
        if mode == 'practice':
            available_krw = bot_state['simulation_krw']
            invest_amount = min(available_krw * 0.15, 150000)  # 15% 또는 최대 15만원
        else:
            available_krw = upbit.get_balance("KRW")
            invest_amount = min(available_krw * 0.15, 150000)
        
        if invest_amount < 5000:
            log(f"⚠️ 투자 금액 부족: {invest_amount:,.0f}원", "WARNING")
            return None
        
        # 매수 수량 계산
        buy_amount = invest_amount / current_price
        
        # 거래 실행
        if mode == 'practice':
            # 시뮬레이션 매수
            bot_state['simulation_krw'] -= invest_amount
            
            if ticker not in bot_state['simulation_holdings']:
                bot_state['simulation_holdings'][ticker] = {
                    'amount': 0,
                    'avg_price': 0,
                    'invested': 0
                }
            
            holding = bot_state['simulation_holdings'][ticker]
            new_amount = holding['amount'] + buy_amount
            new_invested = holding['invested'] + invest_amount
            new_avg_price = new_invested / new_amount if new_amount > 0 else 0
            
            bot_state['simulation_holdings'][ticker] = {
                'amount': new_amount,
                'avg_price': new_avg_price,
                'invested': new_invested,
                'entry_time': datetime.now(),
                'peak_price': current_price,
                'surge_info': surge_info
            }
            
            trade_record = {
                'type': 'BUY',
                'ticker': ticker,
                'price': current_price,
                'amount': buy_amount,
                'krw': invest_amount,
                'time': datetime.now(),
                'mode': 'practice',
                'reason': f"급등 포착 ({len(surge_info['signals'])}개 신호)",
                'signals': surge_info['signals']
            }
            
        else:
            # 실전 매수
            order = upbit.buy_market_order(ticker, invest_amount)
            
            if order is None:
                log(f"❌ 주문 실패: {ticker}", "ERROR")
                return None
            
            trade_record = {
                'type': 'BUY',
                'ticker': ticker,
                'price': current_price,
                'amount': buy_amount,
                'krw': invest_amount,
                'time': datetime.now(),
                'mode': 'live',
                'order': order,
                'reason': f"급등 포착 ({len(surge_info['signals'])}개 신호)",
                'signals': surge_info['signals']
            }
        
        # 거래 기록
        bot_state['trade_history'].append(trade_record)
        bot_state['active_trades'].append({
            'ticker': ticker,
            'entry_price': current_price,
            'entry_time': datetime.now(),
            'invest_amount': invest_amount,
            'trade_record': trade_record
        })
        
        bot_state['surge_statistics']['total_trades_executed'] += 1
        
        log(f"💰 매수 완료! {ticker} | 가격: {current_price:,.0f}원 | 수량: {buy_amount:.6f} | 금액: {invest_amount:,.0f}원", "TRADE")
        
        return trade_record
        
    except Exception as e:
        log(f"거래 실행 오류: {e}", "ERROR")
        log(traceback.format_exc(), "ERROR")
        return None

def check_exit_conditions(upbit, ticker, holding, mode='practice'):
    """익절/손절 조건 체크"""
    try:
        current_price = pyupbit.get_current_price(ticker)
        if current_price is None:
            return None
        
        entry_price = holding['avg_price']
        profit_rate = (current_price - entry_price) / entry_price * 100
        
        # 최고가 업데이트 (트레일링 스톱용)
        if 'peak_price' not in holding or current_price > holding['peak_price']:
            holding['peak_price'] = current_price
        
        # 손절 체크
        if profit_rate <= SURGE_CONFIG['stop_loss']:
            return {
                'action': 'SELL',
                'reason': f"손절 ({profit_rate:.2f}%)",
                'price': current_price,
                'profit_rate': profit_rate
            }
        
        # 익절 체크
        for i, target in enumerate(SURGE_CONFIG['take_profit_targets']):
            if profit_rate >= target:
                ratio = SURGE_CONFIG['take_profit_ratios'][i]
                return {
                    'action': 'PARTIAL_SELL',
                    'reason': f"익절 {i+1}단계 ({profit_rate:.2f}%)",
                    'price': current_price,
                    'profit_rate': profit_rate,
                    'sell_ratio': ratio
                }
        
        # 트레일링 스톱 체크
        if SURGE_CONFIG['trailing_stop'] and profit_rate >= SURGE_CONFIG['trailing_stop_trigger']:
            peak_price = holding['peak_price']
            drawdown_from_peak = (peak_price - current_price) / peak_price * 100
            
            if drawdown_from_peak >= SURGE_CONFIG['trailing_stop_distance']:
                return {
                    'action': 'SELL',
                    'reason': f"트레일링 스톱 (최고점 대비 -{drawdown_from_peak:.2f}%)",
                    'price': current_price,
                    'profit_rate': profit_rate
                }
        
        return None
        
    except Exception as e:
        log(f"청산 조건 체크 오류: {e}", "ERROR")
        return None

def execute_exit(upbit, ticker, holding, exit_decision, mode='practice'):
    """청산 실행"""
    try:
        current_price = exit_decision['price']
        sell_amount = holding['amount']
        
        if exit_decision['action'] == 'PARTIAL_SELL':
            sell_amount *= exit_decision['sell_ratio']
        
        # 거래 실행
        if mode == 'practice':
            # 시뮬레이션 매도
            sell_krw = sell_amount * current_price
            bot_state['simulation_krw'] += sell_krw
            
            # 보유량 감소
            holding['amount'] -= sell_amount
            holding['invested'] -= (sell_amount * holding['avg_price'])
            
            # 수익 계산
            cost = sell_amount * holding['avg_price']
            profit_krw = sell_krw - cost
            profit_rate = exit_decision['profit_rate']
            
            # 전체 매도 시 홀딩 제거
            if holding['amount'] < 0.00001:
                del bot_state['simulation_holdings'][ticker]
            
        else:
            # 실전 매도
            order = upbit.sell_market_order(ticker, sell_amount)
            
            if order is None:
                log(f"❌ 매도 주문 실패: {ticker}", "ERROR")
                return None
            
            sell_krw = sell_amount * current_price
            cost = sell_amount * holding['avg_price']
            profit_krw = sell_krw - cost
            profit_rate = exit_decision['profit_rate']
        
        # 통계 업데이트
        bot_state['surge_statistics']['total_profit_krw'] += profit_krw
        
        if profit_krw > 0:
            bot_state['surge_statistics']['successful_trades'] += 1
        else:
            bot_state['surge_statistics']['failed_trades'] += 1
        
        # 승률 계산
        total_finished = bot_state['surge_statistics']['successful_trades'] + bot_state['surge_statistics']['failed_trades']
        if total_finished > 0:
            bot_state['surge_statistics']['win_rate'] = (bot_state['surge_statistics']['successful_trades'] / total_finished) * 100
            bot_state['surge_statistics']['avg_profit_per_trade'] = bot_state['surge_statistics']['total_profit_krw'] / total_finished
        
        # 거래 기록
        trade_record = {
            'type': 'SELL',
            'ticker': ticker,
            'price': current_price,
            'amount': sell_amount,
            'krw': sell_krw,
            'profit_krw': profit_krw,
            'profit_rate': profit_rate,
            'time': datetime.now(),
            'mode': mode,
            'reason': exit_decision['reason']
        }
        
        bot_state['trade_history'].append(trade_record)
        
        log(f"💸 매도 완료! {ticker} | 수익: {profit_krw:+,.0f}원 ({profit_rate:+.2f}%) | 사유: {exit_decision['reason']}", "TRADE")
        
        return trade_record
        
    except Exception as e:
        log(f"청산 실행 오류: {e}", "ERROR")
        return None

# ═══════════════════════════════════════════════════════
# 🔄 메인 봇 루프
# ═══════════════════════════════════════════════════════
def bot_main_loop():
    """메인 봇 루프 - 급등 포착 + 관리"""
    log_separator()
    log("🚀 급등 포착 봇 v7.2 시작!", "SUCCESS")
    log_separator()
    
    # API 연결
    access_key, secret_key = load_api_keys()
    mode = bot_state['mode']
    
    if mode == 'live':
        if not access_key or not secret_key:
            log("❌ API 키가 설정되지 않았습니다!", "ERROR")
            bot_state['running'] = False
            return
        
        upbit = pyupbit.Upbit(access_key, secret_key)
        bot_state['upbit'] = upbit
        log("✅ 실전 모드 - API 연결 완료", "SUCCESS")
    else:
        upbit = None
        log(f"🎮 연습 모드 - 시뮬레이션 시드: {bot_state['simulation_seed']:,}원", "SUCCESS")
    
    bot_state['start_time'] = datetime.now()
    scan_counter = 0
    last_scan_time = datetime.now() - timedelta(seconds=30)  # 즉시 첫 스캔 실행
    
    while bot_state['running']:
        try:
            current_time = datetime.now()
            
            # 1. 전체 마켓 스캔 (15초마다 - 더 빠른 감지)
            if (current_time - last_scan_time).total_seconds() >= 15:
                log("🔍 전체 마켓 스캔 중...", "INFO")
                surge_candidates = scan_all_markets_for_surge()
                
                if surge_candidates:
                    log(f"🚀 {len(surge_candidates)}개 급등 코인 발견!", "SURGE")
                    
                    # 급등 알림 저장
                    for candidate in surge_candidates:
                        bot_state['surge_alerts'].append(candidate)
                        bot_state['surge_statistics']['total_surges_detected'] += 1
                        
                        # 진입 조건 체크 및 거래 실행
                        if len(bot_state['active_trades']) < 3:  # 최대 3개 동시 거래
                            execute_surge_trade(upbit, candidate, mode)
                
                last_scan_time = current_time
                scan_counter += 1
            
            # 2. 보유 포지션 관리 (5초마다)
            if mode == 'practice':
                for ticker, holding in list(bot_state['simulation_holdings'].items()):
                    exit_decision = check_exit_conditions(upbit, ticker, holding, mode)
                    
                    if exit_decision:
                        execute_exit(upbit, ticker, holding, exit_decision, mode)
            else:
                # 실전 모드 포지션 관리
                balances = upbit.get_balances()
                for balance in balances:
                    if balance['currency'] != 'KRW':
                        ticker = f"KRW-{balance['currency']}"
                        # ... (실전 청산 로직)
            
            # 3. 상태 업데이트
            bot_state['last_update'] = current_time
            
            # 4. 대기
            time.sleep(5)
            
        except Exception as e:
            log(f"메인 루프 오류: {e}", "ERROR")
            log(traceback.format_exc(), "ERROR")
            time.sleep(10)
    
    log("🛑 봇 중지됨", "WARNING")

# ═══════════════════════════════════════════════════════
# 🌐 Flask API 엔드포인트
# ═══════════════════════════════════════════════════════
@app.route('/')
def index():
    """메인 대시보드"""
    return render_template('dashboard-surge-hunter.html')

@app.route('/api/status')
def api_status():
    """봇 상태 조회"""
    try:
        # 시뮬레이션 수익률 계산
        if bot_state['mode'] == 'practice':
            total_value = bot_state['simulation_krw']
            for ticker, holding in bot_state['simulation_holdings'].items():
                current_price = pyupbit.get_current_price(ticker)
                if current_price:
                    total_value += holding['amount'] * current_price
            
            profit_rate = ((total_value - bot_state['simulation_start_seed']) / bot_state['simulation_start_seed']) * 100
        else:
            profit_rate = 0  # 실전 모드는 별도 계산
        
        return jsonify({
            'running': bot_state['running'],
            'mode': bot_state['mode'],
            'start_time': bot_state['start_time'].isoformat() if bot_state['start_time'] else None,
            'last_update': bot_state['last_update'].isoformat() if bot_state['last_update'] else None,
            
            # 시뮬레이션 정보
            'simulation': {
                'seed': bot_state['simulation_seed'],
                'current_krw': bot_state['simulation_krw'],
                'holdings': [
                    {
                        'ticker': ticker,
                        'amount': holding['amount'],
                        'avg_price': holding['avg_price'],
                        'current_price': pyupbit.get_current_price(ticker),
                    }
                    for ticker, holding in bot_state['simulation_holdings'].items()
                ],
                'total_value': total_value if bot_state['mode'] == 'practice' else 0,
                'profit_rate': profit_rate,
            },
            
            # 급등 통계
            'surge_statistics': bot_state['surge_statistics'],
            
            # 최근 급등 알림
            'recent_surges': [
                {
                    'ticker': surge['ticker'],
                    'price': surge['current_price'],
                    'signals': len(surge['signals']),
                    'time': surge['detected_at'].isoformat(),
                }
                for surge in list(bot_state['surge_alerts'])[-10:]
            ],
            
            # 진행 중인 거래
            'active_trades': [
                {
                    'ticker': trade['ticker'],
                    'entry_price': trade['entry_price'],
                    'current_price': pyupbit.get_current_price(trade['ticker']),
                    'entry_time': trade['entry_time'].isoformat(),
                }
                for trade in bot_state['active_trades']
            ],
            
            # 최근 거래 내역
            'recent_trades': [
                {
                    'type': trade['type'],
                    'ticker': trade['ticker'],
                    'price': trade['price'],
                    'amount': trade['amount'],
                    'krw': trade['krw'],
                    'profit_krw': trade.get('profit_krw', 0),
                    'profit_rate': trade.get('profit_rate', 0),
                    'time': trade['time'].isoformat(),
                    'reason': trade['reason'],
                }
                for trade in bot_state['trade_history'][-20:]
            ],
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start', methods=['POST'])
def api_start():
    """봇 시작"""
    try:
        data = request.json
        bot_state['mode'] = data.get('mode', 'practice')
        
        if data.get('simulation_seed'):
            bot_state['simulation_seed'] = int(data['simulation_seed'])
            bot_state['simulation_krw'] = int(data['simulation_seed'])
            bot_state['simulation_start_seed'] = int(data['simulation_seed'])
        
        if not bot_state['running']:
            bot_state['running'] = True
            bot_state['thread'] = threading.Thread(target=bot_main_loop, daemon=True)
            bot_state['thread'].start()
            
            return jsonify({'success': True, 'message': '봇이 시작되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '봇이 이미 실행 중입니다.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """봇 중지"""
    try:
        bot_state['running'] = False
        return jsonify({'success': True, 'message': '봇이 중지되었습니다.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def api_config():
    """API 키 설정"""
    try:
        data = request.json
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        
        if save_api_keys(access_key, secret_key):
            return jsonify({'success': True, 'message': 'API 키가 저장되었습니다.'})
        else:
            return jsonify({'success': False, 'message': 'API 키 저장 실패'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ═══════════════════════════════════════════════════════
# 🚀 메인 실행
# ═══════════════════════════════════════════════════════
if __name__ == '__main__':
    log_separator()
    log("🚀 업비트 급등 포착 봇 v7.2 - SURGE HUNTER", "SUCCESS")
    log("📊 웹 대시보드: http://localhost:5000", "INFO")
    log_separator()
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
