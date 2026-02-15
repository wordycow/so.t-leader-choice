#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 업비트 스마트 스캘핑 봇 v4.0 - 5단계 매수 + 3단계 매도 + SOL 수익 전환
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 핵심 전략:
- 24시간 지속 운영 (NOW 상태와 무관)
- 5단계 분할 매수: 6천→1만→1만→1만→10만 (총 136,000원)
- 3단계 익절 매도: 가장 높은 가격에서 가장 큰 금액 우선 매도
- 수익금 자동 SOL(솔라나) 전환
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
# 💰 5단계 매수 + 3단계 매도 설정
# ═══════════════════════════════════════════════════════
BUY_STAGES = {
    1: {
        'amount': 6000,       # 1단계: 6천원
        'rsi_range': (28, 30),
        'drop_percent': 0,    # 첫 매수
        'description': '1차 테스트 매수 (6천원)'
    },
    2: {
        'amount': 10000,      # 2단계: 1만원
        'rsi_range': (26, 28),
        'drop_percent': 3,    # 3% 하락
        'description': '2차 추가 매수 (1만원)'
    },
    3: {
        'amount': 10000,      # 3단계: 1만원
        'rsi_range': (24, 26),
        'drop_percent': 5,    # 5% 하락
        'description': '3차 추가 매수 (1만원)'
    },
    4: {
        'amount': 10000,      # 4단계: 1만원
        'rsi_range': (22, 24),
        'drop_percent': 7,    # 7% 하락
        'description': '4차 추가 매수 (1만원)'
    },
    5: {
        'amount': 100000,     # 5단계: 10만원 🔥
        'rsi_range': (0, 22),
        'drop_percent': 10,   # 10% 하락
        'description': '최종 승부수 (10만원)'
    }
}

# 3단계 익절 매도 설정 (비율)
SELL_STAGES = {
    1: {
        'ratio': 0.50,        # 50% 매도 (가장 큰 금액)
        'profit_target': 2.5, # +2.5% 이상
        'description': '1차 익절 (50%, 가장 높은 가격)'
    },
    2: {
        'ratio': 0.30,        # 30% 매도
        'profit_target': 2.0, # +2.0% 이상
        'description': '2차 익절 (30%)'
    },
    3: {
        'ratio': 0.20,        # 20% 매도 (잔량 전부)
        'profit_target': 1.5, # +1.5% 이상
        'description': '3차 익절 (20%, 잔량)'
    }
}

# 코인별 매수/매도 이력 저장
coin_trading_history = {}

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

def fetch_delisting_coins():
    """상장폐지 코인 목록 표시"""
    log_separator()
    log("🚫 제외 대상 필터링 설정:", "INFO")
    log(f"\n📋 상장폐지 코인 ({len(DELISTED_COINS)}개):", "WARNING")
    for coin in sorted(DELISTED_COINS):
        log(f"   ❌ {coin}", "WARNING")
    
    log(f"\n🚫 제외 마켓:", "WARNING")
    for market in sorted(EXCLUDED_MARKETS):
        log(f"   ❌ {market}-* (예: {market}-BTC, {market}-ETH 등)", "WARNING")

def is_valid_market(ticker):
    """유효한 시장인지 검증"""
    for market in EXCLUDED_MARKETS:
        if ticker.startswith(f'{market}-'):
            log(f"⚠️  [{ticker}] {market} 마켓은 제외됩니다", "WARNING")
            return False
    
    if ticker in DELISTED_COINS:
        log(f"❌ [{ticker}] 상장폐지 예정 코인입니다 - 거래 중단", "ERROR")
        return False
    
    return True

# ═══════════════════════════════════════════════════════
# 🔑 API 키 로드 함수
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
        
        print(f"2️⃣ {Colors.CYAN}api_keys.json{Colors.END} 파일 생성:\n")
        print("   다음 내용을 복사해서 api_keys.json 파일을 만드세요:")
        print(f"\n{Colors.YELLOW}───────────────────────────────────────{Colors.END}")
        print(json.dumps({
            "access_key": "여기에_실제_Access_Key_붙여넣기",
            "secret_key": "여기에_실제_Secret_Key_붙여넣기"
        }, indent=2, ensure_ascii=False))
        print(f"{Colors.YELLOW}───────────────────────────────────────{Colors.END}\n")
        
        print(f"3️⃣ 저장 후 다시 실행: {Colors.GREEN}python3 {sys.argv[0]}{Colors.END}\n")
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
        log(f"💡 {config_file} 파일을 확인하고 올바른 API 키를 입력하세요", "WARNING")
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

def check_volume_increase(df):
    """거래량 증가 확인"""
    avg_volume = df['volume'].tail(20).mean()
    current_volume = df['volume'].iloc[-1]
    
    # 현재 거래량이 평균의 150% 이상
    if current_volume >= avg_volume * 1.5:
        return True
    return False

# ═══════════════════════════════════════════════════════
# 💼 포트폴리오 분석
# ═══════════════════════════════════════════════════════
def analyze_portfolio(upbit):
    """현재 보유 중인 코인 분석"""
    log_separator()
    log("💼 포트폴리오 분석 시작...", "INFO")
    
    try:
        balances = upbit.get_balances()
    except Exception as e:
        log(f"❌ 잔고 조회 실패: {e}", "ERROR")
        return 0, []
    
    if not isinstance(balances, list):
        log(f"⚠️  잘못된 API 응답 형식: {type(balances)}", "WARNING")
        log(f"   응답 내용: {balances}", "WARNING")
        return 0, []
    
    krw_balance = 0
    holdings = []
    
    for balance in balances:
        if not isinstance(balance, dict):
            log(f"⚠️  잘못된 잔고 데이터: {balance}", "WARNING")
            continue
        
        try:
            currency = balance.get('currency', 'UNKNOWN')
            amount = float(balance.get('balance', 0))
            locked = float(balance.get('locked', 0))
            avg_buy_price = float(balance.get('avg_buy_price', 0))
        except (ValueError, TypeError) as e:
            log(f"⚠️  잔고 데이터 파싱 실패: {e}", "WARNING")
            continue
        
        if currency == 'KRW':
            krw_balance = amount
            log(f"💰 보유 원화: {krw_balance:,.0f} KRW", "INFO")
            continue
        
        if amount > 0:
            ticker = f"KRW-{currency}"
            
            if not is_valid_market(ticker):
                log(f"⏩️  [{ticker}] 모니터링 제외 - 건너뜀", "WARNING")
                continue
            
            try:
                current_price = pyupbit.get_current_price(ticker)
            except Exception as e:
                log(f"⚠️  [{ticker}] 가격 조회 실패: {e}", "WARNING")
                log(f"   코인이 상장폐지되었거나 거래 중단되었을 수 있습니다", "WARNING")
                DELISTED_COINS.add(ticker)
                log(f"   ➕ [{ticker}]를 상장폐지 목록에 추가했습니다", "INFO")
                continue
            
            if current_price and current_price > 0:
                invested = avg_buy_price * amount
                current_value = current_price * amount
                profit = current_value - invested
                profit_rate = (profit / invested) * 100
                
                holdings.append({
                    'ticker': ticker,
                    'currency': currency,
                    'amount': amount,
                    'locked': locked,
                    'avg_buy_price': avg_buy_price,
                    'current_price': current_price,
                    'invested': invested,
                    'current_value': current_value,
                    'profit': profit,
                    'profit_rate': profit_rate
                })
                
                log(f"\n📊 보유 코인: {currency}", "INFO", Colors.BOLD)
                log(f"   • 티커: {ticker}", "INFO")
                log(f"   • 보유 수량: {amount:.8f} {currency}", "INFO")
                log(f"   • 평균 매수가: {avg_buy_price:,.0f} KRW", "INFO")
                log(f"   • 현재 가격: {current_price:,.0f} KRW", "INFO")
                log(f"   • 투자 금액: {invested:,.0f} KRW", "INFO")
                log(f"   • 평가 금액: {current_value:,.0f} KRW", "INFO")
                
                if profit >= 0:
                    log(f"   • 수익: +{profit:,.0f} KRW ({profit_rate:+.2f}%)", "SUCCESS")
                else:
                    log(f"   • 손실: {profit:,.0f} KRW ({profit_rate:.2f}%)", "WARNING")
    
    return krw_balance, holdings

# ═══════════════════════════════════════════════════════
# 💰 5단계 매수 로직
# ═══════════════════════════════════════════════════════
def get_buy_stage(ticker, current_price, avg_buy_price, rsi):
    """
    현재 상황에 맞는 매수 단계 반환
    
    Returns:
        stage (int): 1~5 단계, None이면 매수 불가
        reason (str): 판단 이유
    """
    # 이력 조회
    history = coin_trading_history.get(ticker, {
        'buy_stages_completed': [],
        'first_buy_price': None,
        'last_buy_time': None,
        'sell_stages_completed': [],
        'total_profit': 0
    })
    
    # 이미 구매한 단계들
    bought_stages = history.get('buy_stages_completed', [])
    first_price = history.get('first_buy_price')
    last_buy_time = history.get('last_buy_time')
    
    # 첫 매수인 경우
    if not bought_stages:
        # RSI가 30 이하일 때만 1단계 매수
        if rsi <= 30:
            return 1, f"1단계 매수 조건 충족 (RSI: {rsi:.1f})"
        else:
            return None, f"RSI({rsi:.1f})가 높아 매수 대기 (30 이하 필요)"
    
    # 다음 단계 계산
    next_stage = max(bought_stages) + 1
    
    if next_stage > 5:
        return None, "5단계 모두 완료 - 추가 매수 불가"
    
    # 마지막 매수 후 최소 10분 경과 확인
    if last_buy_time:
        time_diff = datetime.now() - last_buy_time
        if time_diff < timedelta(minutes=10):
            remaining = 10 - (time_diff.seconds // 60)
            return None, f"매수 대기 시간 ({remaining}분 남음)"
    
    # 하락 퍼센트 확인
    stage_info = BUY_STAGES[next_stage]
    required_drop = stage_info['drop_percent']
    current_drop = ((first_price - current_price) / first_price) * 100
    
    if current_drop < required_drop:
        return None, f"하락률 부족 ({current_drop:.1f}% < {required_drop}%)"
    
    # RSI 범위 확인
    rsi_min, rsi_max = stage_info['rsi_range']
    if not (rsi_min <= rsi < rsi_max):
        return None, f"RSI 범위 불일치 ({rsi:.1f}, 필요: {rsi_min}~{rsi_max})"
    
    return next_stage, f"{next_stage}단계 조건 충족 ({stage_info['description']})"

# ═══════════════════════════════════════════════════════
# 📈 3단계 익절 매도 로직
# ═══════════════════════════════════════════════════════
def get_sell_stage(ticker, profit_rate):
    """
    현재 수익률에 맞는 매도 단계 반환
    
    Returns:
        stage (int): 1~3 단계, None이면 매도 불가
        ratio (float): 매도 비율
        reason (str): 판단 이유
    """
    # 이력 조회
    history = coin_trading_history.get(ticker, {
        'buy_stages_completed': [],
        'sell_stages_completed': [],
        'total_profit': 0
    })
    
    sold_stages = history.get('sell_stages_completed', [])
    
    # 다음 매도 단계
    next_stage = len(sold_stages) + 1
    
    if next_stage > 3:
        return None, 0, "3단계 익절 모두 완료"
    
    stage_info = SELL_STAGES[next_stage]
    target_profit = stage_info['profit_target']
    
    if profit_rate >= target_profit:
        return next_stage, stage_info['ratio'], f"{next_stage}차 익절 조건 충족 (수익률: {profit_rate:.2f}% >= {target_profit}%)"
    else:
        return None, 0, f"익절 목표 미달 (현재: {profit_rate:.2f}% < 목표: {target_profit}%)"

# ═══════════════════════════════════════════════════════
# 🎯 전략 수립
# ═══════════════════════════════════════════════════════
def create_strategy(upbit, holding):
    """
    5단계 매수 + 3단계 매도 전략
    """
    ticker = holding['ticker']
    
    if not is_valid_market(ticker):
        log(f"⚠️  [{ticker}] 유효하지 않은 시장 - 전략 분석 건너뜀", "WARNING")
        return None
    
    log_separator()
    log(f"🎯 [{ticker}] 전략 분석 중...", "STRATEGY")
    
    # 1. 캔들 데이터 가져오기
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=100)
    if df is None or len(df) < 20:
        log(f"⚠️  데이터 부족으로 분석 불가", "WARNING")
        return None
    
    current_price = holding['current_price']
    avg_buy_price = holding['avg_buy_price']
    profit_rate = holding['profit_rate']
    
    # 2. 기술적 지표 계산
    rsi = calculate_rsi(df)
    bb = calculate_bollinger_bands(df)
    has_volume = check_volume_increase(df)
    
    log(f"\n📈 기술적 지표:", "INFO")
    log(f"   • RSI(14): {rsi:.2f}", "INFO")
    log(f"   • 볼린저 상단: {bb['upper']:,.0f} KRW", "INFO")
    log(f"   • 볼린저 중단: {bb['middle']:,.0f} KRW", "INFO")
    log(f"   • 볼린저 하단: {bb['lower']:,.0f} KRW", "INFO")
    log(f"   • 거래량 증가: {'✅' if has_volume else '❌'}", "INFO")
    
    # 3. 전략 판단
    strategy = {
        'ticker': ticker,
        'action': 'HOLD',
        'reason': [],
        'buy_stage': None,
        'buy_amount': 0,
        'sell_stage': None,
        'sell_ratio': 0
    }
    
    log(f"\n🧠 전략 판단:", "STRATEGY")
    
    # === 매도 신호 분석 (우선) ===
    sell_stage, sell_ratio, sell_reason = get_sell_stage(ticker, profit_rate)
    
    if sell_stage:
        strategy['action'] = 'SELL'
        strategy['sell_stage'] = sell_stage
        strategy['sell_ratio'] = sell_ratio
        strategy['reason'].append(("SELL", sell_reason))
        log(f"   🔴 {sell_reason}", "REASON")
        log(f"\n✅ 최종 판단: {Colors.RED}매도 신호{Colors.END} ({sell_stage}차 익절, {sell_ratio*100:.0f}% 매도)", "STRATEGY")
        return strategy
    else:
        log(f"   ⚪ {sell_reason}", "INFO")
    
    # 손절 조건 (극단적 손실)
    if profit_rate <= -15.0:
        strategy['action'] = 'SELL'
        strategy['sell_stage'] = 0  # 긴급 손절
        strategy['sell_ratio'] = 1.0  # 전량 매도
        strategy['reason'].append(("SELL", f"긴급 손절 (손실: {profit_rate:.2f}% <= -15.0%)"))
        log(f"   🔴 긴급 손절 필요", "ERROR")
        log(f"\n✅ 최종 판단: {Colors.RED}긴급 손절{Colors.END} (전량 매도)", "STRATEGY")
        return strategy
    
    # === 매수 신호 분석 ===
    buy_stage, buy_reason = get_buy_stage(ticker, current_price, avg_buy_price, rsi)
    
    if buy_stage:
        strategy['action'] = 'BUY'
        strategy['buy_stage'] = buy_stage
        strategy['buy_amount'] = BUY_STAGES[buy_stage]['amount']
        strategy['reason'].append(("BUY", buy_reason))
        log(f"   🟢 {buy_reason}", "REASON")
        log(f"\n✅ 최종 판단: {Colors.GREEN}매수 신호{Colors.END} ({buy_stage}단계, {strategy['buy_amount']:,}원)", "STRATEGY")
    else:
        log(f"   ⚪ {buy_reason}", "INFO")
        log(f"\n✅ 최종 판단: {Colors.CYAN}관망{Colors.END}", "STRATEGY")
    
    return strategy

# ═══════════════════════════════════════════════════════
# 💱 주문 실행
# ═══════════════════════════════════════════════════════
def execute_order(upbit, strategy, holding, krw_balance):
    """전략에 따른 실제 주문 실행"""
    ticker = strategy['ticker']
    action = strategy['action']
    
    if action == 'HOLD':
        log(f"⏸️  [{ticker}] 관망 - 주문 없음", "INFO")
        return
    
    log_separator()
    log(f"💱 [{ticker}] 주문 실행 시작...", "INFO")
    
    try:
        if action == 'BUY':
            # 5단계 분할 매수
            stage = strategy.get('buy_stage')
            buy_amount = strategy.get('buy_amount', 0)
            
            if buy_amount < 5000:
                log(f"⚠️  매수 금액 부족 (최소 5,000원 필요, 현재: {buy_amount:,.0f}원)", "WARNING")
                return
            
            if krw_balance < buy_amount:
                log(f"⚠️  원화 잔고 부족 (필요: {buy_amount:,}원, 보유: {krw_balance:,.0f}원)", "WARNING")
                return
            
            log(f"🔵 매수 주문:", "INFO")
            log(f"   • 단계: {stage}단계 / 5단계", "INFO")
            log(f"   • 금액: {buy_amount:,} KRW", "INFO")
            log(f"   • 설명: {BUY_STAGES[stage]['description']}", "INFO")
            log(f"   • 이유:", "INFO")
            for action_type, reason in strategy['reason']:
                if action_type == 'BUY':
                    log(f"     - {reason}", "INFO")
            
            # 실제 주문 (주석 해제하여 사용)
            # order = upbit.buy_market_order(ticker, buy_amount)
            # log(f"✅ 매수 완료: {order}", "SUCCESS")
            
            # 이력 업데이트 (시뮬레이션용)
            history = coin_trading_history.get(ticker, {
                'buy_stages_completed': [],
                'first_buy_price': None,
                'last_buy_time': None,
                'sell_stages_completed': [],
                'total_profit': 0
            })
            
            if stage not in history['buy_stages_completed']:
                history['buy_stages_completed'].append(stage)
            
            if not history['first_buy_price']:
                history['first_buy_price'] = holding['current_price']
            
            history['last_buy_time'] = datetime.now()
            coin_trading_history[ticker] = history
            
            log(f"⚠️  [시뮬레이션 모드] 실제 주문은 위 주석을 해제하세요", "WARNING")
            log(f"   💡 실전 모드: upbit.buy_market_order('{ticker}', {buy_amount}) 주석 해제", "INFO")
            
        elif action == 'SELL':
            # 3단계 분할 익절 매도
            stage = strategy.get('sell_stage', 0)
            ratio = strategy.get('sell_ratio', 1.0)
            sell_amount = holding['amount'] * ratio
            
            log(f"🔴 매도 주문:", "INFO")
            if stage > 0:
                log(f"   • 단계: {stage}차 익절 / 3단계", "INFO")
                log(f"   • 비율: {ratio*100:.0f}% 매도", "INFO")
            else:
                log(f"   • 긴급 손절 (전량)", "INFO")
            log(f"   • 수량: {sell_amount:.8f} {holding['currency']}", "INFO")
            log(f"   • 예상 금액: {sell_amount * holding['current_price']:,.0f} KRW", "INFO")
            log(f"   • 이유:", "INFO")
            for action_type, reason in strategy['reason']:
                if action_type == 'SELL':
                    log(f"     - {reason}", "INFO")
            
            # 실제 주문 (주석 해제하여 사용)
            # order = upbit.sell_market_order(ticker, sell_amount)
            # log(f"✅ 매도 완료: {order}", "SUCCESS")
            
            # 수익 계산 및 이력 업데이트
            profit = (holding['current_price'] - holding['avg_buy_price']) * sell_amount
            
            history = coin_trading_history.get(ticker, {
                'buy_stages_completed': [],
                'sell_stages_completed': [],
                'total_profit': 0
            })
            
            if stage > 0 and stage not in history['sell_stages_completed']:
                history['sell_stages_completed'].append(stage)
            
            history['total_profit'] += profit
            coin_trading_history[ticker] = history
            
            log(f"   💰 이번 매도 수익: {profit:,.0f} KRW", "SUCCESS" if profit > 0 else "WARNING")
            log(f"   💰 누적 수익: {history['total_profit']:,.0f} KRW", "SUCCESS")
            
            # 3단계 익절 모두 완료 시 SOL 전환
            if stage == 3:
                log(f"\n🎉 [{ticker}] 3단계 익절 완료!", "SUCCESS")
                log(f"   💰 총 수익: {history['total_profit']:,.0f} KRW", "SUCCESS")
                
                if history['total_profit'] > 5000:  # 최소 5천원 이상 수익
                    log(f"   🔄 수익금을 SOL(솔라나)로 전환 예정", "INFO")
                    # convert_profit_to_sol(upbit, history['total_profit'])
                    log(f"   ⚠️  [시뮬레이션 모드] SOL 전환 기능 준비 중", "WARNING")
                
                # 이력 초기화
                del coin_trading_history[ticker]
                log(f"   🔄 [{ticker}] 거래 이력 초기화", "INFO")
            
            log(f"⚠️  [시뮬레이션 모드] 실제 주문은 위 주석을 해제하세요", "WARNING")
            log(f"   💡 실전 모드: upbit.sell_market_order('{ticker}', {sell_amount:.8f}) 주석 해제", "INFO")
    
    except Exception as e:
        log(f"❌ 주문 실패: {e}", "ERROR")

def convert_profit_to_sol(upbit, profit_krw):
    """수익금을 SOL(솔라나)로 전환"""
    sol_ticker = "KRW-SOL"
    
    if profit_krw < 5000:
        log(f"⚠️  SOL 전환 금액 부족 (최소 5,000원, 현재: {profit_krw:,.0f}원)", "WARNING")
        return
    
    log_separator()
    log(f"🔄 수익금 SOL 전환 시작", "INFO")
    log(f"   💰 전환 금액: {profit_krw:,.0f} KRW → SOL", "INFO")
    
    try:
        # SOL 매수 (주석 해제하여 사용)
        # order = upbit.buy_market_order(sol_ticker, profit_krw)
        # log(f"✅ SOL 매수 완료: {order}", "SUCCESS")
        
        log(f"⚠️  [시뮬레이션 모드] SOL 전환 시뮬레이션", "WARNING")
        log(f"   💡 실전 모드: upbit.buy_market_order('{sol_ticker}', {profit_krw}) 주석 해제", "INFO")
        
    except Exception as e:
        log(f"❌ SOL 전환 실패: {e}", "ERROR")

# ═══════════════════════════════════════════════════════
# 🚀 메인 루프
# ═══════════════════════════════════════════════════════
def main():
    """메인 실행 함수"""
    
    # 헤더 출력
    log_separator()
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("  🤖 업비트 스마트 스캘핑 봇 v4.0")
    print("  💰 5단계 매수: 6천→1만→1만→1만→10만")
    print("  📈 3단계 익절: 50%→30%→20% (가장 높은 가격 우선)")
    print("  🔄 수익 → SOL 자동 전환")
    print("  ⏰ 24시간 지속 운영")
    print(f"{Colors.END}")
    log_separator()
    
    # 설정 로드
    load_delisted_coins_config()
    fetch_delisting_coins()
    log_separator()
    
    # API 키 로드
    access_key, secret_key = load_api_keys()
    
    # 업비트 객체 생성
    try:
        upbit = pyupbit.Upbit(access_key, secret_key)
        log("✅ 업비트 연결 성공", "SUCCESS")
    except Exception as e:
        log(f"❌ 업비트 연결 실패: {e}", "ERROR")
        sys.exit(1)
    
    log(f"\n🔄 자동 거래 시작... (10초마다 체크)", "INFO")
    log(f"💡 종료: Ctrl + C\n", "INFO")
    log(f"📋 전략 요약:", "INFO")
    log(f"   • 매수: 5단계 (6천→1만→1만→1만→10만원)", "INFO")
    log(f"   • 매도: 3단계 익절 (50%→30%→20%)", "INFO")
    log(f"   • 수익 전환: SOL(솔라나) 자동 매수", "INFO")
    log(f"   • NOW 상태: 참고용 (봇은 독립 운영)", "INFO")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            log_separator()
            log(f"🔄 [{iteration}회차] 분석 시작...", "INFO", Colors.BOLD)
            
            # 1. 포트폴리오 분석
            krw_balance, holdings = analyze_portfolio(upbit)
            
            # 2. 보유 코인이 없으면 대기
            if not holdings:
                log("\n⏸️  보유 코인 없음 - 대기 중...", "INFO")
                log("💡 수동으로 코인을 매수한 후 봇이 자동으로 관리합니다", "INFO")
                time.sleep(10)
                continue
            
            # 3. 각 코인별 전략 수립 및 실행
            for holding in holdings:
                strategy = create_strategy(upbit, holding)
                
                if strategy:
                    execute_order(upbit, strategy, holding, krw_balance)
            
            # 4. 다음 체크까지 대기
            log(f"\n⏰ 다음 체크: 10초 후...", "INFO")
            time.sleep(10)
            
    except KeyboardInterrupt:
        log_separator()
        log("🛑 사용자에 의해 봇 종료", "WARNING")
        log("👋 안전하게 종료되었습니다", "INFO")
        
        # 거래 이력 요약
        if coin_trading_history:
            log("\n📊 거래 이력 요약:", "INFO")
            for ticker, history in coin_trading_history.items():
                log(f"\n[{ticker}]", "INFO")
                log(f"  • 매수 단계: {len(history.get('buy_stages_completed', []))}/5", "INFO")
                log(f"  • 매도 단계: {len(history.get('sell_stages_completed', []))}/3", "INFO")
                log(f"  • 누적 수익: {history.get('total_profit', 0):,.0f} KRW", "INFO")
        
        sys.exit(0)
    except Exception as e:
        log(f"❌ 예상치 못한 오류: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        sys.exit(1)

# ═══════════════════════════════════════════════════════
# 실행
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
