#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 업비트 스마트 스캘핑 봇 v3.0 - 보수적 전략 + 마틴게일
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 핵심 전략:
- 대부분의 시간은 관망 (80~90%)
- 안전한 저가 구간에서만 매수
- 5단계 물타기 (1만→1만→1만→1만→10만)
- 마지막 단계가 가장 큰 금액 (최저가에 집중 투자)
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
# 💰 마틴게일 물타기 설정
# ═══════════════════════════════════════════════════════
MARTINGALE_STAGES = {
    1: {
        'amount': 10000,      # 1단계: 1만원
        'rsi_range': (28, 30),
        'drop_percent': 0,    # 첫 매수
        'description': '1차 테스트 매수'
    },
    2: {
        'amount': 10000,      # 2단계: 1만원
        'rsi_range': (26, 28),
        'drop_percent': 3,    # 3% 하락
        'description': '2차 추가 매수'
    },
    3: {
        'amount': 10000,      # 3단계: 1만원
        'rsi_range': (24, 26),
        'drop_percent': 5,    # 5% 하락
        'description': '3차 추가 매수'
    },
    4: {
        'amount': 10000,      # 4단계: 1만원
        'rsi_range': (22, 24),
        'drop_percent': 7,    # 7% 하락
        'description': '4차 추가 매수'
    },
    5: {
        'amount': 100000,     # 5단계: 10만원 🔥
        'rsi_range': (0, 22),
        'drop_percent': 10,   # 10% 하락
        'description': '최종 승부수 (최대 금액)'
    }
}

# 코인별 매수 이력 저장
coin_purchase_history = {}

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

def calculate_fibonacci_50(df):
    """피보나치 50% 레벨 계산"""
    recent_high = df['high'].tail(20).max()
    recent_low = df['low'].tail(20).min()
    fib_50 = (recent_high + recent_low) / 2
    return fib_50, recent_high, recent_low

def check_price_bounce(df):
    """가격 반등 확인 (최근 3캔들)"""
    recent_3 = df['close'].tail(3).tolist()
    if len(recent_3) < 3:
        return False
    
    # 최근 2캔들이 상승 중이면 반등으로 판단
    if recent_3[-1] > recent_3[-2] and recent_3[-2] > recent_3[-3]:
        return True
    return False

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
# 💰 마틴게일 단계 계산
# ═══════════════════════════════════════════════════════
def get_martingale_stage(ticker, current_price, avg_buy_price, rsi):
    """
    현재 상황에 맞는 마틴게일 단계 반환
    
    Returns:
        stage (int): 1~5 단계, None이면 매수 불가
        reason (str): 판단 이유
    """
    # 이력 조회
    history = coin_purchase_history.get(ticker, {
        'stages_bought': [],
        'first_buy_price': None,
        'last_buy_time': None
    })
    
    # 이미 구매한 단계들
    bought_stages = history.get('stages_bought', [])
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
    stage_info = MARTINGALE_STAGES[next_stage]
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
# 🎯 보수적 전략 수립
# ═══════════════════════════════════════════════════════
def create_conservative_strategy(upbit, holding):
    """
    보수적 + 마틴게일 전략
    
    핵심:
    - 대부분 관망
    - 매우 까다로운 매수 조건
    - 5단계 물타기
    """
    ticker = holding['ticker']
    
    if not is_valid_market(ticker):
        log(f"⚠️  [{ticker}] 유효하지 않은 시장 - 전략 분석 건너뜀", "WARNING")
        return None
    
    log_separator()
    log(f"🎯 [{ticker}] 보수적 전략 분석 중...", "STRATEGY")
    
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
    fib_50, recent_high, recent_low = calculate_fibonacci_50(df)
    has_bounce = check_price_bounce(df)
    has_volume = check_volume_increase(df)
    
    log(f"\n📈 기술적 지표:", "INFO")
    log(f"   • RSI(14): {rsi:.2f}", "INFO")
    log(f"   • 볼린저 상단: {bb['upper']:,.0f} KRW", "INFO")
    log(f"   • 볼린저 중단: {bb['middle']:,.0f} KRW", "INFO")
    log(f"   • 볼린저 하단: {bb['lower']:,.0f} KRW", "INFO")
    log(f"   • 피보나치 50%: {fib_50:,.0f} KRW", "INFO")
    log(f"   • 가격 반등: {'✅' if has_bounce else '❌'}", "INFO")
    log(f"   • 거래량 증가: {'✅' if has_volume else '❌'}", "INFO")
    
    # 3. 전략 판단
    strategy = {
        'ticker': ticker,
        'action': 'HOLD',
        'reason': [],
        'confidence': 0,
        'rsi': rsi,
        'bb': bb,
        'fib_50': fib_50,
        'profit_rate': profit_rate,
        'martingale_stage': None,
        'buy_amount': 0
    }
    
    log(f"\n🧠 전략 판단:", "STRATEGY")
    
    # === 매도 신호 분석 (우선) ===
    sell_signals = 0
    
    if profit_rate >= 2.0:
        sell_signals += 3
        reason = f"목표 수익률 달성 ({profit_rate:+.2f}% >= 2.0%) → 익절 추천"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    
    if rsi > 70:
        sell_signals += 2
        reason = f"RSI({rsi:.1f})가 과매수 구간(70 초과) → 조정 가능성"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    
    if current_price >= bb['upper'] * 0.99:
        sell_signals += 2
        reason = f"현재가({current_price:,.0f})가 볼린저 상단({bb['upper']:,.0f}) 근처 → 고가 매도 기회"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    
    if profit_rate <= -15.0:
        sell_signals += 3
        reason = f"큰 손실 발생 ({profit_rate:.2f}% <= -15.0%) → 손절 고려"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    
    # 매도 신호가 3개 이상이면 매도
    if sell_signals >= 3:
        strategy['action'] = 'SELL'
        strategy['confidence'] = min(sell_signals * 25, 100)
        log(f"\n✅ 최종 판단: {Colors.RED}매도 신호{Colors.END} (확신도: {strategy['confidence']}%)", "STRATEGY")
        return strategy
    
    # === 매수 신호 분석 (매우 보수적) ===
    buy_signals = 0
    buy_reasons = []
    
    # 1. RSI 극단적 저평가 (25 이하)
    if rsi < 25:
        buy_signals += 2
        reason = f"RSI({rsi:.1f}) 극단적 과매도 (25 미만) → 강한 반등 가능성"
        buy_reasons.append(reason)
        log(f"   🟢 {reason}", "REASON")
    elif rsi < 30:
        buy_signals += 1
        reason = f"RSI({rsi:.1f}) 과매도 구간 (30 미만)"
        buy_reasons.append(reason)
        log(f"   🟡 {reason}", "REASON")
    else:
        reason = f"RSI({rsi:.1f}) 아직 높음 - 매수 대기"
        log(f"   ⚪ {reason}", "INFO")
    
    # 2. 볼린저 하단 -2% 이하 (극단적 저가)
    bb_threshold = bb['lower'] * 0.98
    if current_price <= bb_threshold:
        buy_signals += 2
        reason = f"현재가({current_price:,.0f}) 볼린저 하단 -2% 이하 ({bb_threshold:,.0f}) → 극단적 저가"
        buy_reasons.append(reason)
        log(f"   🟢 {reason}", "REASON")
    elif current_price <= bb['lower'] * 1.02:
        buy_signals += 1
        reason = f"현재가({current_price:,.0f}) 볼린저 하단 근처"
        buy_reasons.append(reason)
        log(f"   🟡 {reason}", "REASON")
    
    # 3. 가격 반등 확인
    if has_bounce:
        buy_signals += 1
        reason = "최근 3캔들 연속 상승 → 바닥 확인"
        buy_reasons.append(reason)
        log(f"   🟢 {reason}", "REASON")
    else:
        log(f"   ⚪ 아직 하락 중 - 바닥 미확인", "INFO")
    
    # 4. 거래량 증가
    if has_volume:
        buy_signals += 1
        reason = "거래량 평균 대비 150% 이상 → 관심 증가"
        buy_reasons.append(reason)
        log(f"   🟢 {reason}", "REASON")
    
    # 5. 피보나치 50% 이하
    if avg_buy_price <= fib_50:
        buy_signals += 1
        reason = f"평단가({avg_buy_price:,.0f}) ≤ 피보나치 50%({fib_50:,.0f}) → 유리한 구간"
        buy_reasons.append(reason)
        log(f"   🟢 {reason}", "REASON")
    
    log(f"\n📊 매수 신호: {buy_signals}/5", "INFO")
    
    # 마틴게일 단계 확인
    stage, stage_reason = get_martingale_stage(ticker, current_price, avg_buy_price, rsi)
    
    if stage:
        log(f"💰 마틴게일: {stage}단계 - {stage_reason}", "INFO")
        strategy['martingale_stage'] = stage
        strategy['buy_amount'] = MARTINGALE_STAGES[stage]['amount']
        
        # 매수 신호가 4개 이상 + 마틴게일 단계 있음 → 매수
        if buy_signals >= 4:
            strategy['action'] = 'BUY'
            strategy['confidence'] = min(buy_signals * 20, 100)
            strategy['reason'] = [("BUY", r) for r in buy_reasons]
            log(f"\n✅ 최종 판단: {Colors.GREEN}매수 신호{Colors.END} (확신도: {strategy['confidence']}%)", "STRATEGY")
            log(f"   💰 {stage}단계 매수: {strategy['buy_amount']:,}원", "SUCCESS")
        else:
            strategy['action'] = 'HOLD'
            log(f"\n✅ 최종 판단: {Colors.CYAN}관망{Colors.END} (매수 신호 부족: {buy_signals}/5)", "STRATEGY")
            log(f"   💡 조건: 4개 이상 신호 필요", "INFO")
    else:
        log(f"⏸️  마틴게일: {stage_reason}", "WARNING")
        strategy['action'] = 'HOLD'
        log(f"\n✅ 최종 판단: {Colors.CYAN}관망{Colors.END} (마틴게일 조건 불충족)", "STRATEGY")
    
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
            # 마틴게일 단계별 매수
            stage = strategy.get('martingale_stage')
            buy_amount = strategy.get('buy_amount', 0)
            
            if buy_amount < 5000:
                log(f"⚠️  매수 금액 부족 (최소 5,000원 필요, 현재: {buy_amount:,.0f}원)", "WARNING")
                return
            
            if krw_balance < buy_amount:
                log(f"⚠️  원화 잔고 부족 (필요: {buy_amount:,}원, 보유: {krw_balance:,.0f}원)", "WARNING")
                return
            
            log(f"🔵 매수 주문:", "INFO")
            log(f"   • 단계: {stage}단계", "INFO")
            log(f"   • 금액: {buy_amount:,} KRW", "INFO")
            log(f"   • 설명: {MARTINGALE_STAGES[stage]['description']}", "INFO")
            log(f"   • 이유:", "INFO")
            for action_type, reason in strategy['reason']:
                if action_type == 'BUY':
                    log(f"     - {reason}", "INFO")
            
            # 실제 주문 (주석 해제하여 사용)
            # order = upbit.buy_market_order(ticker, buy_amount)
            # log(f"✅ 매수 완료: {order}", "SUCCESS")
            
            # 이력 업데이트 (시뮬레이션용)
            history = coin_purchase_history.get(ticker, {
                'stages_bought': [],
                'first_buy_price': None,
                'last_buy_time': None
            })
            
            if stage not in history['stages_bought']:
                history['stages_bought'].append(stage)
            
            if not history['first_buy_price']:
                history['first_buy_price'] = holding['current_price']
            
            history['last_buy_time'] = datetime.now()
            coin_purchase_history[ticker] = history
            
            log(f"⚠️  [시뮬레이션 모드] 실제 주문은 위 주석을 해제하세요", "WARNING")
            
        elif action == 'SELL':
            # 전량 매도
            sell_amount = holding['amount']
            
            log(f"🔴 매도 주문:", "INFO")
            log(f"   • 수량: {sell_amount:.8f} {holding['currency']}", "INFO")
            log(f"   • 예상 금액: {sell_amount * holding['current_price']:,.0f} KRW", "INFO")
            log(f"   • 이유:", "INFO")
            for action_type, reason in strategy['reason']:
                if action_type == 'SELL':
                    log(f"     - {reason}", "INFO")
            
            # 실제 주문 (주석 해제하여 사용)
            # order = upbit.sell_market_order(ticker, sell_amount)
            # log(f"✅ 매도 완료: {order}", "SUCCESS")
            
            # 이력 초기화 (매도 시)
            if ticker in coin_purchase_history:
                del coin_purchase_history[ticker]
                log(f"🔄 [{ticker}] 마틴게일 이력 초기화", "INFO")
            
            log(f"⚠️  [시뮬레이션 모드] 실제 주문은 위 주석을 해제하세요", "WARNING")
    
    except Exception as e:
        log(f"❌ 주문 실패: {e}", "ERROR")

# ═══════════════════════════════════════════════════════
# 🚀 메인 루프
# ═══════════════════════════════════════════════════════
def main():
    """메인 실행 함수"""
    
    # 헤더 출력
    log_separator()
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("  🤖 업비트 스마트 스캘핑 봇 v3.0")
    print("  🛡️  보수적 전략 + 마틴게일 물타기")
    print("  💰 5단계: 1만→1만→1만→1만→10만")
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
                strategy = create_conservative_strategy(upbit, holding)
                
                if strategy:
                    execute_order(upbit, strategy, holding, krw_balance)
            
            # 4. 다음 체크까지 대기
            log(f"\n⏰ 다음 체크: 10초 후...", "INFO")
            time.sleep(10)
            
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

# ═══════════════════════════════════════════════════════
# 실행
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
