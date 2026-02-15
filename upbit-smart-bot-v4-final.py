#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 업비트 스마트 봇 v4.0 - 완벽한 순간 포착 + 수익 SOL 전환
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 핵심 전략:
- 24시간 완벽한 순간 대기 (NOW 무관)
- 5단계 물타기: 6천→1만→1만→1만→10만
- 3분할 익절: 최고점에서 최대금액 먼저 매도
- 수익 전액 → SOL 자동 매수
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
# 💰 매수/매도 설정
# ═══════════════════════════════════════════════════════
MARTINGALE_STAGES = {
    1: {'amount': 6000,   'rsi_range': (28, 30), 'drop_percent': 0,  'description': '1차 테스트 매수'},
    2: {'amount': 10000,  'rsi_range': (26, 28), 'drop_percent': 3,  'description': '2차 추가 매수'},
    3: {'amount': 10000,  'rsi_range': (24, 26), 'drop_percent': 5,  'description': '3차 추가 매수'},
    4: {'amount': 10000,  'rsi_range': (22, 24), 'drop_percent': 7,  'description': '4차 추가 매수'},
    5: {'amount': 100000, 'rsi_range': (0, 22),  'drop_percent': 10, 'description': '최종 승부수'}
}

# 매도 3분할 설정 (최고점부터 큰 금액 먼저)
SELL_STAGES = [
    {'ratio': 0.50, 'target_profit': 0.03, 'description': '1차 익절 (50%, +3%)'},
    {'ratio': 0.30, 'target_profit': 0.05, 'description': '2차 익절 (30%, +5%)'},
    {'ratio': 0.20, 'target_profit': 0.07, 'description': '3차 익절 (20%, +7%)'}
]

# 완벽한 순간 조건 (up-coin.html NOW 조건과 동일)
PERFECT_CONDITIONS = {
    'rsi_max': 25,              # RSI 25 이하
    'bb_lower_margin': 0.02,    # 볼린저 하단 -2%
    'volume_min_ratio': 1.5,    # 거래량 평균 대비 150%
    'position_max': 0.5,        # 30일 범위의 50% 이하
    'pump_min_days': 5,         # 펌프 최소 5일 경과
    'pump_max_days': 30,        # 펌프 최대 30일 이내
    'stop_gap_min': 0.005,      # 손절가 거리 0.5% 이상
}

# 솔라나 자동 매수
SOL_TICKER = "KRW-SOL"
SOL_AUTO_BUY = True  # True면 수익 전액 SOL 매수

# 코인별 거래 이력
coin_history = {}

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
        "STRATEGY": Colors.BLUE,
        "REASON": Colors.HEADER,
        "PROFIT": Colors.GREEN,
    }
    
    color = color or level_colors.get(level, Colors.END)
    prefix = f"{color}[{level}]{Colors.END}"
    
    log_msg = f"{timestamp} {prefix} {message}"
    print(log_msg)
    
    clean_msg = f"{timestamp} [{level}] {message}\n"
    with open("bot.log", "a", encoding="utf-8") as f:
        f.write(clean_msg)

def log_separator():
    """구분선 출력"""
    print(f"\n{Colors.BOLD}{'═' * 80}{Colors.END}\n")

# ═══════════════════════════════════════════════════════
# 🚫 상장폐지 코인 목록 관리
# ═══════════════════════════════════════════════════════
DELISTED_COINS = set()
EXCLUDED_MARKETS = set()

def load_delisted_coins_config():
    """delisted_coins.json 파일에서 설정 로드"""
    global DELISTED_COINS, EXCLUDED_MARKETS
    
    config_file = "delisted_coins.json"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            DELISTED_COINS = set(config.get("delisted_coins", []))
            EXCLUDED_MARKETS = set(config.get("excluded_markets", []))
            
            log("📋 상장폐지 코인 설정 로드 완료", "SUCCESS")
            log(f"   제외 코인: {len(DELISTED_COINS)}개", "INFO")
            log(f"   제외 마켓: {', '.join(EXCLUDED_MARKETS)}", "INFO")
        else:
            DELISTED_COINS = set([
                'KRW-AXS', 'KRW-WAXP', 'KRW-STEEM', 'KRW-SBD',
                'KRW-SC', 'KRW-POWR', 'KRW-STORJ', 'KRW-RFR'
            ])
            EXCLUDED_MARKETS = set(['USDT', 'BTC'])
            log(f"⚠️  {config_file} 파일이 없어 기본 설정 사용", "WARNING")
        
        return DELISTED_COINS, EXCLUDED_MARKETS
        
    except Exception as e:
        log(f"❌ 설정 로드 실패: {e}", "ERROR")
        DELISTED_COINS = set([
            'KRW-AXS', 'KRW-WAXP', 'KRW-STEEM', 'KRW-SBD',
            'KRW-SC', 'KRW-POWR', 'KRW-STORJ', 'KRW-RFR'
        ])
        EXCLUDED_MARKETS = set(['USDT', 'BTC'])
        return DELISTED_COINS, EXCLUDED_MARKETS

def is_valid_market(ticker):
    """유효한 시장인지 검증"""
    for market in EXCLUDED_MARKETS:
        if ticker.startswith(f'{market}-'):
            return False
    
    if ticker in DELISTED_COINS:
        return False
    
    return True

# ═══════════════════════════════════════════════════════
# 🔑 API 키 로드
# ═══════════════════════════════════════════════════════
def load_api_keys():
    """api_keys.json 파일에서 API 키 로드"""
    config_file = "api_keys.json"
    
    if not os.path.exists(config_file):
        log("❌ API 키 설정 파일이 없습니다!", "ERROR")
        print(f"\n{Colors.BOLD}📋 API 키 설정 방법:{Colors.END}\n")
        print("1️⃣ 업비트 API 키 발급:")
        print("   https://upbit.com → 로그인 → 프로필 → Open API 관리")
        print("   권한: ✅ 자산조회, ✅ 주문조회, ✅ 주문하기")
        print("   권한: ❌ 출금하기 (절대 체크 금지!)\n")
        
        print(f"2️⃣ {Colors.CYAN}api_keys.json{Colors.END} 파일 생성")
        sys.exit(1)
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            keys = json.load(f)
        
        access_key = keys.get("access_key")
        secret_key = keys.get("secret_key")
        
        if not access_key or not secret_key:
            raise ValueError("API 키가 비어있습니다")
        
        if "여기에" in access_key or "여기에" in secret_key:
            raise ValueError("API 키를 실제 값으로 변경해주세요")
        
        log(f"✅ API 키 로드 성공: {access_key[:8]}****", "SUCCESS")
        return access_key, secret_key
        
    except Exception as e:
        log(f"❌ API 키 로드 실패: {e}", "ERROR")
        sys.exit(1)

# ═══════════════════════════════════════════════════════
# 📊 기술적 지표 계산
# ═══════════════════════════════════════════════════════
def calculate_rsi(df, period=14):
    """RSI 계산"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_bollinger_bands(df, period=20, std=2):
    """볼린저 밴드 계산"""
    sma = df['close'].rolling(window=period).mean()
    std_dev = df['close'].rolling(window=period).std()
    
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    
    return {
        'upper': upper.iloc[-1],
        'middle': sma.iloc[-1],
        'lower': lower.iloc[-1]
    }

def check_price_bounce(df):
    """가격 반등 확인 (최근 3캔들)"""
    recent_3 = df['close'].tail(3).tolist()
    if len(recent_3) < 3:
        return False
    
    # 최근 2캔들이 상승 중이면 반등
    if recent_3[-1] > recent_3[-2] and recent_3[-2] > recent_3[-3]:
        return True
    return False

def check_volume_increase(df, min_ratio=1.5):
    """거래량 증가 확인"""
    avg_volume = df['volume'].tail(20).mean()
    current_volume = df['volume'].iloc[-1]
    
    if current_volume >= avg_volume * min_ratio:
        return True
    return False

def calculate_position_in_30d(df):
    """30일 범위에서 현재 가격 위치 (0~1)"""
    recent_30 = df['close'].tail(30)
    if len(recent_30) < 2:
        return 0.5
    
    high = recent_30.max()
    low = recent_30.min()
    current = df['close'].iloc[-1]
    
    if high == low:
        return 0.5
    
    position = (current - low) / (high - low)
    return position

# ═══════════════════════════════════════════════════════
# 🎯 완벽한 순간 판정 (up-coin.html NOW 조건과 동일)
# ═══════════════════════════════════════════════════════
def is_perfect_moment(ticker, upbit):
    """
    완벽한 순간인지 판정
    
    조건 (up-coin.html NOW와 동일):
    1. RSI < 25
    2. 볼린저 하단 -2% 이하
    3. 가격 반등 확인
    4. 거래량 150% 이상
    5. 포지션 50% 이하 (바닥권)
    6. 손절가 거리 충분
    """
    try:
        # 데이터 가져오기
        df = pyupbit.get_ohlcv(ticker, interval="minute5", count=100)
        if df is None or len(df) < 30:
            return False, "데이터 부족"
        
        current_price = pyupbit.get_current_price(ticker)
        if not current_price or current_price <= 0:
            return False, "가격 조회 실패"
        
        # 1. RSI 체크
        rsi = calculate_rsi(df)
        if rsi >= PERFECT_CONDITIONS['rsi_max']:
            return False, f"RSI({rsi:.1f}) 아직 높음 (< {PERFECT_CONDITIONS['rsi_max']} 필요)"
        
        # 2. 볼린저 하단 체크
        bb = calculate_bollinger_bands(df)
        bb_threshold = bb['lower'] * (1 - PERFECT_CONDITIONS['bb_lower_margin'])
        if current_price > bb_threshold:
            return False, f"볼린저 하단 미달 (현재: {current_price:,.0f}, 기준: {bb_threshold:,.0f})"
        
        # 3. 가격 반등 체크
        if not check_price_bounce(df):
            return False, "반등 미확인 (아직 하락 중)"
        
        # 4. 거래량 체크
        if not check_volume_increase(df, PERFECT_CONDITIONS['volume_min_ratio']):
            return False, f"거래량 부족 (< {PERFECT_CONDITIONS['volume_min_ratio']}배)"
        
        # 5. 포지션 체크
        position = calculate_position_in_30d(df)
        if position > PERFECT_CONDITIONS['position_max']:
            return False, f"포지션 높음 ({position*100:.1f}% > {PERFECT_CONDITIONS['position_max']*100:.0f}%)"
        
        # 6. 손절가 거리 체크
        stop_price = current_price * 0.97  # 간단히 -3%로 설정
        gap = (current_price - stop_price) / current_price
        if gap < PERFECT_CONDITIONS['stop_gap_min']:
            return False, f"손절가 너무 가까움 ({gap*100:.2f}%)"
        
        # 모든 조건 충족!
        reason = f"완벽한 순간! RSI:{rsi:.1f}, BB하단:{bb['lower']:,.0f}, 포지션:{position*100:.0f}%"
        return True, reason
        
    except Exception as e:
        return False, f"분석 오류: {e}"

# ═══════════════════════════════════════════════════════
# 💼 포트폴리오 관리
# ═══════════════════════════════════════════════════════
def get_coin_history(ticker):
    """코인별 거래 이력 조회"""
    if ticker not in coin_history:
        coin_history[ticker] = {
            'buy_stages': [],           # 매수한 단계들
            'buy_prices': [],           # 각 단계 매수가
            'buy_amounts': [],          # 각 단계 매수 수량
            'first_buy_price': None,    # 첫 매수가
            'last_buy_time': None,      # 마지막 매수 시간
            'avg_buy_price': 0,         # 평균 매수가
            'total_invested': 0,        # 총 투자금
            'total_amount': 0,          # 총 보유 수량
            'sell_stages_done': [],     # 완료된 매도 단계
            'total_profit': 0,          # 총 수익
        }
    return coin_history[ticker]

def update_buy_history(ticker, stage, price, amount, invested):
    """매수 이력 업데이트"""
    history = get_coin_history(ticker)
    
    if stage not in history['buy_stages']:
        history['buy_stages'].append(stage)
    
    history['buy_prices'].append(price)
    history['buy_amounts'].append(amount)
    history['last_buy_time'] = datetime.now()
    
    if not history['first_buy_price']:
        history['first_buy_price'] = price
    
    # 평균 매수가 재계산
    history['total_invested'] += invested
    history['total_amount'] += amount
    history['avg_buy_price'] = history['total_invested'] / history['total_amount'] if history['total_amount'] > 0 else 0
    
    log(f"📝 [{ticker}] 매수 이력 업데이트: {stage}단계, 평단가: {history['avg_buy_price']:,.0f}원", "INFO")

def update_sell_history(ticker, stage, profit):
    """매도 이력 업데이트"""
    history = get_coin_history(ticker)
    
    if stage not in history['sell_stages_done']:
        history['sell_stages_done'].append(stage)
    
    history['total_profit'] += profit
    
    log(f"📝 [{ticker}] 매도 이력 업데이트: {stage}단계, 누적 수익: {history['total_profit']:,.0f}원", "PROFIT")

def clear_coin_history(ticker):
    """코인 이력 초기화 (전량 매도 시)"""
    if ticker in coin_history:
        del coin_history[ticker]
    log(f"🔄 [{ticker}] 이력 초기화 완료", "INFO")

# ═══════════════════════════════════════════════════════
# 💱 매수/매도 실행
# ═══════════════════════════════════════════════════════
def execute_buy(upbit, ticker):
    """
    매수 실행 (5단계 물타기)
    """
    try:
        history = get_coin_history(ticker)
        bought_stages = history['buy_stages']
        
        # 다음 단계 결정
        if not bought_stages:
            next_stage = 1
        else:
            next_stage = max(bought_stages) + 1
        
        if next_stage > 5:
            log(f"⚠️  [{ticker}] 5단계 모두 완료 - 추가 매수 불가", "WARNING")
            return False
        
        # 마지막 매수 후 10분 경과 확인
        if history['last_buy_time']:
            time_diff = datetime.now() - history['last_buy_time']
            if time_diff < timedelta(minutes=10):
                remaining = 10 - (time_diff.seconds // 60)
                log(f"⏳ [{ticker}] 매수 대기 시간 ({remaining}분 남음)", "WARNING")
                return False
        
        stage_info = MARTINGALE_STAGES[next_stage]
        buy_amount_krw = stage_info['amount']
        
        # 현재가 확인
        current_price = pyupbit.get_current_price(ticker)
        if not current_price or current_price <= 0:
            log(f"❌ [{ticker}] 가격 조회 실패", "ERROR")
            return False
        
        # 하락률 확인 (2단계부터)
        if next_stage > 1 and history['first_buy_price']:
            current_drop = ((history['first_buy_price'] - current_price) / history['first_buy_price']) * 100
            required_drop = stage_info['drop_percent']
            
            if current_drop < required_drop:
                log(f"⏳ [{ticker}] 하락률 부족 ({current_drop:.1f}% < {required_drop}%)", "WARNING")
                return False
        
        log_separator()
        log(f"🔵 [{ticker}] {next_stage}단계 매수 준비", "INFO")
        log(f"   • 금액: {buy_amount_krw:,}원", "INFO")
        log(f"   • 현재가: {current_price:,.0f}원", "INFO")
        log(f"   • 설명: {stage_info['description']}", "INFO")
        
        # 실제 주문 (주석 해제하여 사용)
        # order = upbit.buy_market_order(ticker, buy_amount_krw)
        # if order:
        #     # 주문 정보에서 실제 매수 수량 추출
        #     executed_volume = float(order.get('executed_volume', 0))
        #     update_buy_history(ticker, next_stage, current_price, executed_volume, buy_amount_krw)
        #     log(f"✅ [{ticker}] {next_stage}단계 매수 완료: {executed_volume:.8f}개", "SUCCESS")
        #     return True
        
        # 시뮬레이션
        simulated_amount = buy_amount_krw / current_price
        update_buy_history(ticker, next_stage, current_price, simulated_amount, buy_amount_krw)
        log(f"⚠️  [시뮬레이션] {next_stage}단계 매수: {simulated_amount:.8f}개", "WARNING")
        
        return True
        
    except Exception as e:
        log(f"❌ [{ticker}] 매수 실패: {e}", "ERROR")
        return False

def execute_sell(upbit, ticker, current_price):
    """
    매도 실행 (3분할 익절, 최고점부터 큰 금액)
    """
    try:
        history = get_coin_history(ticker)
        
        if history['total_amount'] <= 0:
            return False
        
        avg_price = history['avg_buy_price']
        if avg_price <= 0:
            return False
        
        # 현재 수익률
        profit_rate = (current_price - avg_price) / avg_price
        
        # 다음 매도 단계 찾기
        next_sell_stage = None
        for i, stage_info in enumerate(SELL_STAGES, 1):
            if i not in history['sell_stages_done']:
                if profit_rate >= stage_info['target_profit']:
                    next_sell_stage = i
                    break
        
        if not next_sell_stage:
            return False
        
        stage_info = SELL_STAGES[next_sell_stage - 1]
        sell_ratio = stage_info['ratio']
        sell_amount = history['total_amount'] * sell_ratio
        
        log_separator()
        log(f"🔴 [{ticker}] {next_sell_stage}단계 익절 준비", "SUCCESS")
        log(f"   • 목표 수익률: +{stage_info['target_profit']*100:.1f}%", "SUCCESS")
        log(f"   • 현재 수익률: +{profit_rate*100:.2f}%", "SUCCESS")
        log(f"   • 매도 비율: {sell_ratio*100:.0f}%", "INFO")
        log(f"   • 매도 수량: {sell_amount:.8f}개", "INFO")
        log(f"   • 예상 금액: {sell_amount * current_price:,.0f}원", "INFO")
        
        # 실제 주문 (주석 해제하여 사용)
        # order = upbit.sell_market_order(ticker, sell_amount)
        # if order:
        #     executed_volume = float(order.get('executed_volume', 0))
        #     sell_value = executed_volume * current_price
        #     invested = history['total_invested'] * sell_ratio
        #     profit = sell_value - invested
        #     
        #     update_sell_history(ticker, next_sell_stage, profit)
        #     history['total_amount'] -= executed_volume
        #     history['total_invested'] -= invested
        #     
        #     log(f"✅ [{ticker}] {next_sell_stage}단계 익절 완료: +{profit:,.0f}원", "PROFIT")
        #     
        #     # 3단계 완료 시
        #     if len(history['sell_stages_done']) >= 3:
        #         total_profit = history['total_profit']
        #         log(f"🎉 [{ticker}] 전체 익절 완료! 총 수익: +{total_profit:,.0f}원", "PROFIT")
        #         
        #         # SOL 자동 매수
        #         if SOL_AUTO_BUY and total_profit > 5000:
        #             buy_sol_with_profit(upbit, total_profit)
        #         
        #         clear_coin_history(ticker)
        #     
        #     return True
        
        # 시뮬레이션
        sell_value = sell_amount * current_price
        invested = history['total_invested'] * sell_ratio
        profit = sell_value - invested
        
        update_sell_history(ticker, next_sell_stage, profit)
        history['total_amount'] -= sell_amount
        history['total_invested'] -= invested
        
        log(f"⚠️  [시뮬레이션] {next_sell_stage}단계 익절: +{profit:,.0f}원", "PROFIT")
        
        # 3단계 완료 확인
        if len(history['sell_stages_done']) >= 3:
            total_profit = history['total_profit']
            log(f"🎉 [{ticker}] 전체 익절 완료! 총 수익: +{total_profit:,.0f}원", "PROFIT")
            
            # SOL 시뮬레이션
            if SOL_AUTO_BUY and total_profit > 5000:
                log(f"⚠️  [시뮬레이션] SOL 매수: {total_profit:,.0f}원", "PROFIT")
            
            clear_coin_history(ticker)
        
        return True
        
    except Exception as e:
        log(f"❌ [{ticker}] 매도 실패: {e}", "ERROR")
        return False

def buy_sol_with_profit(upbit, profit_krw):
    """수익금으로 SOL 매수"""
    try:
        log_separator()
        log(f"💰 수익금 {profit_krw:,.0f}원으로 {SOL_TICKER} 매수 시도", "PROFIT")
        
        # 실제 주문 (주석 해제하여 사용)
        # order = upbit.buy_market_order(SOL_TICKER, profit_krw)
        # if order:
        #     log(f"✅ {SOL_TICKER} 매수 완료!", "SUCCESS")
        #     return True
        
        # 시뮬레이션
        sol_price = pyupbit.get_current_price(SOL_TICKER)
        if sol_price and sol_price > 0:
            sol_amount = profit_krw / sol_price
            log(f"⚠️  [시뮬레이션] {SOL_TICKER} 매수: {sol_amount:.8f}개 ({profit_krw:,.0f}원)", "PROFIT")
        
        return True
        
    except Exception as e:
        log(f"❌ {SOL_TICKER} 매수 실패: {e}", "ERROR")
        return False

# ═══════════════════════════════════════════════════════
# 📊 모니터링 & 실행
# ═══════════════════════════════════════════════════════
def get_monitoring_tickers(upbit):
    """
    모니터링할 티커 목록 가져오기
    - 보유 중인 코인
    - 업비트 전체 KRW 마켓 (완벽한 순간 찾기)
    """
    tickers = set()
    
    # 1. 보유 중인 코인
    try:
        balances = upbit.get_balances()
        if isinstance(balances, list):
            for balance in balances:
                if isinstance(balance, dict):
                    currency = balance.get('currency', '')
                    amount = float(balance.get('balance', 0))
                    
                    if currency != 'KRW' and amount > 0:
                        ticker = f"KRW-{currency}"
                        if is_valid_market(ticker):
                            tickers.add(ticker)
    except Exception as e:
        log(f"⚠️  잔고 조회 실패: {e}", "WARNING")
    
    # 2. 전체 KRW 마켓 (완벽한 순간 찾기용)
    try:
        all_tickers = pyupbit.get_tickers(fiat="KRW")
        if all_tickers:
            for ticker in all_tickers:
                if is_valid_market(ticker):
                    tickers.add(ticker)
    except Exception as e:
        log(f"⚠️  티커 목록 조회 실패: {e}", "WARNING")
    
    return list(tickers)

def monitor_and_trade(upbit):
    """메인 모니터링 및 트레이딩 로직"""
    
    log_separator()
    log("🔍 시장 스캔 시작...", "INFO", Colors.BOLD)
    
    tickers = get_monitoring_tickers(upbit)
    log(f"📊 모니터링 대상: {len(tickers)}개 코인", "INFO")
    
    perfect_moments = []
    holding_coins = []
    
    for ticker in tickers:
        try:
            # 보유 여부 확인
            history = get_coin_history(ticker)
            is_holding = (history['total_amount'] > 0)
            
            if is_holding:
                holding_coins.append(ticker)
                
                # 매도 체크
                current_price = pyupbit.get_current_price(ticker)
                if current_price and current_price > 0:
                    execute_sell(upbit, ticker, current_price)
            else:
                # 완벽한 순간 체크
                is_perfect, reason = is_perfect_moment(ticker, upbit)
                
                if is_perfect:
                    perfect_moments.append((ticker, reason))
                    log(f"🔥 [{ticker}] 완벽한 순간 포착! {reason}", "STRATEGY")
                    
                    # 매수 실행
                    execute_buy(upbit, ticker)
        
        except Exception as e:
            continue
    
    # 요약
    log_separator()
    log(f"📈 스캔 완료: 완벽한 순간 {len(perfect_moments)}개, 보유 코인 {len(holding_coins)}개", "INFO")
    
    if perfect_moments:
        log("🔥 완벽한 순간 포착 목록:", "STRATEGY")
        for ticker, reason in perfect_moments:
            log(f"   • {ticker}: {reason}", "STRATEGY")
    
    if holding_coins:
        log("💼 보유 코인 목록:", "INFO")
        for ticker in holding_coins:
            history = get_coin_history(ticker)
            log(f"   • {ticker}: {history['total_amount']:.8f}개 (평단: {history['avg_buy_price']:,.0f}원)", "INFO")

# ═══════════════════════════════════════════════════════
# 🚀 메인 루프
# ═══════════════════════════════════════════════════════
def main():
    """메인 실행 함수"""
    
    # 헤더
    log_separator()
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("  🤖 업비트 스마트 봇 v4.0 FINAL")
    print("  🎯 완벽한 순간 포착 + 수익 SOL 전환")
    print("  💰 매수 5회: 6천→1만→1만→1만→10만")
    print("  🎁 매도 3회: 최고점부터 큰 금액 먼저")
    print(f"{Colors.END}")
    log_separator()
    
    # 설정 로드
    load_delisted_coins_config()
    log_separator()
    
    # API 키
    access_key, secret_key = load_api_keys()
    
    # 업비트 연결
    try:
        upbit = pyupbit.Upbit(access_key, secret_key)
        log("✅ 업비트 연결 성공", "SUCCESS")
    except Exception as e:
        log(f"❌ 업비트 연결 실패: {e}", "ERROR")
        sys.exit(1)
    
    log(f"\n🔄 24시간 모니터링 시작... (5초마다 체크)", "INFO")
    log(f"💡 종료: Ctrl + C\n", "INFO")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            log(f"🔄 [{iteration}회차] 모니터링...", "INFO")
            
            monitor_and_trade(upbit)
            
            log(f"\n⏰ 다음 체크: 5초 후...", "INFO")
            time.sleep(5)
            
    except KeyboardInterrupt:
        log_separator()
        log("🛑 사용자에 의해 봇 종료", "WARNING")
        log("👋 안전하게 종료되었습니다", "INFO")
        sys.exit(0)
    except Exception as e:
        log(f"❌ 예상치 못한 오류: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
