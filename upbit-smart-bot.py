#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 업비트 스마트 스캘핑 봇 v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 특징:
- 진행 중인 코인(보유 중) 자동 감지 및 전략 수립
- 모든 매매 행동에 상세한 설명 + 타당한 이유 로그
- 로컬 전용 (API 키 파일로 관리)
- Bollinger Bands + RSI + Fibonacci 전략
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import time
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime
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
# 📝 로깅 함수
# ═══════════════════════════════════════════════════════
def log(message, level="INFO", color=None):
    """
    상세한 로그 출력
    Args:
        message: 로그 메시지
        level: 로그 레벨 (INFO, SUCCESS, WARNING, ERROR, STRATEGY)
        color: 색상 (선택)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 레벨별 색상
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
    
    # 파일에도 저장 (색상 코드 제거)
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
    """
    delisted_coins.json 파일에서 상장폐지 코인 목록 로드
    
    이유: 상장폐지 예정 코인은 거래가 위험하므로 모니터링에서 제외
    """
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
            # 기본 설정
            DELISTED_COINS = set([
                'KRW-AXS', 'KRW-WAXP', 'KRW-STEEM', 'KRW-SBD',
                'KRW-SC', 'KRW-POWR', 'KRW-STORJ', 'KRW-RFR'
            ])
            EXCLUDED_MARKETS = set(['USDT', 'BTC'])
            log(f"⚠️  {config_file} 파일이 없어 기본 설정 사용", "WARNING")
        
        return DELISTED_COINS, EXCLUDED_MARKETS
        
    except Exception as e:
        log(f"❌ 설정 로드 실패: {e}", "ERROR")
        # 기본 설정 사용
        DELISTED_COINS = set([
            'KRW-AXS', 'KRW-WAXP', 'KRW-STEEM', 'KRW-SBD',
            'KRW-SC', 'KRW-POWR', 'KRW-STORJ', 'KRW-RFR'
        ])
        EXCLUDED_MARKETS = set(['USDT', 'BTC'])
        return DELISTED_COINS, EXCLUDED_MARKETS

def fetch_delisting_coins():
    """
    상장폐지 코인 목록 표시
    """
    log_separator()
    log("🚫 제외 대상 필터링 설정:", "INFO")
    log(f"\n📋 상장폐지 코인 ({len(DELISTED_COINS)}개):", "WARNING")
    for coin in sorted(DELISTED_COINS):
        log(f"   ❌ {coin}", "WARNING")
    
    log(f"\n🚫 제외 마켓:", "WARNING")
    for market in sorted(EXCLUDED_MARKETS):
        log(f"   ❌ {market}-* (예: {market}-BTC, {market}-ETH 등)", "WARNING")

def is_valid_market(ticker):
    """
    유효한 시장인지 검증
    
    제외 대상:
    - USDT 마켓 (USDT-BTC, USDT-ETH 등)
    - BTC 마켓 (BTC-ETH, BTC-XRP 등)
    - 상장폐지 코인
    
    이유: 
    - USDT/BTC 마켓은 변동성이 다르고 전략이 맞지 않음
    - 상장폐지 코인은 거래 불가 또는 위험
    """
    # 제외 마켓 확인
    for market in EXCLUDED_MARKETS:
        if ticker.startswith(f'{market}-'):
            log(f"⚠️  [{ticker}] {market} 마켓은 제외됩니다", "WARNING")
            return False
    
    # 상장폐지 코인 제외
    if ticker in DELISTED_COINS:
        log(f"❌ [{ticker}] 상장폐지 예정 코인입니다 - 거래 중단", "ERROR")
        return False
    
    return True

# ═══════════════════════════════════════════════════════
# 🔑 API 키 로드 함수
# ═══════════════════════════════════════════════════════
def load_api_keys():
    """
    api_keys.json 파일에서 API 키 로드
    파일이 없으면 생성 가이드 출력 후 종료
    """
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
    """
    RSI (Relative Strength Index) 계산
    
    이유: RSI는 과매수/과매도 상태를 판단하는 지표
          - RSI < 30: 과매도 (매수 신호)
          - RSI > 70: 과매수 (매도 신호)
    """
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_bollinger_bands(df, period=20, std=2):
    """
    볼린저 밴드 계산
    
    이유: 가격의 변동성을 측정하여 매매 타이밍 포착
          - 하단 밴드 근처: 저가 매수 구간
          - 상단 밴드 근처: 고가 매도 구간
    """
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
    """
    피보나치 50% 레벨 계산
    
    이유: 최근 고점/저점의 중간값(50% 되돌림) 계산
          평단가가 이 수준 이하면 매수 유리한 구간
    """
    recent_high = df['high'].tail(20).max()
    recent_low = df['low'].tail(20).min()
    fib_50 = (recent_high + recent_low) / 2
    return fib_50, recent_high, recent_low

# ═══════════════════════════════════════════════════════
# 💼 포트폴리오 분석
# ═══════════════════════════════════════════════════════
def analyze_portfolio(upbit):
    """
    현재 보유 중인 코인 분석
    
    목적: 진행 중인 투자를 파악하고 각 코인별 전략 수립
    """
    log_separator()
    log("💼 포트폴리오 분석 시작...", "INFO")
    
    try:
        balances = upbit.get_balances()
    except Exception as e:
        log(f"❌ 잔고 조회 실패: {e}", "ERROR")
        return 0, []
    
    # 응답이 리스트가 아니면 에러 처리
    if not isinstance(balances, list):
        log(f"⚠️  잘못된 API 응답 형식: {type(balances)}", "WARNING")
        log(f"   응답 내용: {balances}", "WARNING")
        return 0, []
    
    krw_balance = 0
    holdings = []
    
    for balance in balances:
        # dict 타입인지 확인
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
            
            # 시장 유효성 검증 (USDT/BTC 마켓, 상장폐지 코인 제외)
            if not is_valid_market(ticker):
                log(f"⏭️  [{ticker}] 모니터링 제외 - 건너뜀", "WARNING")
                continue
            
            try:
                current_price = pyupbit.get_current_price(ticker)
            except Exception as e:
                log(f"⚠️  [{ticker}] 가격 조회 실패: {e}", "WARNING")
                log(f"   코인이 상장폐지되었거나 거래 중단되었을 수 있습니다", "WARNING")
                # 자동으로 상장폐지 목록에 추가
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
                
                # 상세 로그
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
# 🎯 전략 수립
# ═══════════════════════════════════════════════════════
def create_strategy(upbit, holding):
    """
    보유 코인별 매매 전략 수립
    
    전략 기반:
    1. RSI (과매수/과매도 판단)
    2. 볼린저 밴드 (변동성 기반 가격 위치)
    3. 피보나치 50% (평단가 최적화)
    4. 수익률 (목표 수익 달성 여부)
    """
    ticker = holding['ticker']
    
    # 시장 유효성 재검증
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
    fib_50, recent_high, recent_low = calculate_fibonacci_50(df)
    
    log(f"\n📈 기술적 지표:", "INFO")
    log(f"   • RSI(14): {rsi:.2f}", "INFO")
    log(f"   • 볼린저 상단: {bb['upper']:,.0f} KRW", "INFO")
    log(f"   • 볼린저 중단: {bb['middle']:,.0f} KRW", "INFO")
    log(f"   • 볼린저 하단: {bb['lower']:,.0f} KRW", "INFO")
    log(f"   • 피보나치 50%: {fib_50:,.0f} KRW", "INFO")
    log(f"   • 최근 고점: {recent_high:,.0f} KRW", "INFO")
    log(f"   • 최근 저점: {recent_low:,.0f} KRW", "INFO")
    
    # 3. 전략 판단
    strategy = {
        'ticker': ticker,
        'action': 'HOLD',
        'reason': [],
        'confidence': 0,
        'rsi': rsi,
        'bb': bb,
        'fib_50': fib_50,
        'profit_rate': profit_rate
    }
    
    log(f"\n🧠 전략 판단:", "STRATEGY")
    
    # === 매수 신호 분석 ===
    buy_signals = 0
    
    if rsi < 30:
        buy_signals += 2
        reason = f"RSI({rsi:.1f})가 과매도 구간(30 미만) → 반등 가능성 높음"
        strategy['reason'].append(("BUY", reason))
        log(f"   🟢 {reason}", "REASON")
    elif rsi < 40:
        buy_signals += 1
        reason = f"RSI({rsi:.1f})가 저평가 구간 → 매수 고려"
        strategy['reason'].append(("BUY", reason))
        log(f"   🟡 {reason}", "REASON")
    
    if current_price <= bb['lower'] * 1.01:
        buy_signals += 2
        reason = f"현재가({current_price:,.0f})가 볼린저 하단({bb['lower']:,.0f}) 근처 → 저가 매수 기회"
        strategy['reason'].append(("BUY", reason))
        log(f"   🟢 {reason}", "REASON")
    
    if avg_buy_price <= fib_50:
        buy_signals += 1
        reason = f"평단가({avg_buy_price:,.0f})가 피보나치 50%({fib_50:,.0f}) 이하 → 유리한 평단 구간"
        strategy['reason'].append(("BUY", reason))
        log(f"   🟢 {reason}", "REASON")
    
    # === 매도 신호 분석 ===
    sell_signals = 0
    
    if profit_rate >= 1.5:
        sell_signals += 3
        reason = f"목표 수익률 달성 ({profit_rate:+.2f}% >= 1.5%) → 익절 추천"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    
    if rsi > 70:
        sell_signals += 2
        reason = f"RSI({rsi:.1f})가 과매수 구간(70 초과) → 조정 가능성"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    elif rsi > 60:
        sell_signals += 1
        reason = f"RSI({rsi:.1f})가 고평가 구간 → 분할 매도 고려"
        strategy['reason'].append(("SELL", reason))
        log(f"   🟡 {reason}", "REASON")
    
    if current_price >= bb['upper'] * 0.99:
        sell_signals += 2
        reason = f"현재가({current_price:,.0f})가 볼린저 상단({bb['upper']:,.0f}) 근처 → 고가 매도 기회"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    
    if profit_rate <= -3.0:
        sell_signals += 3
        reason = f"손절 기준 도달 ({profit_rate:.2f}% <= -3.0%) → 손절 추천"
        strategy['reason'].append(("SELL", reason))
        log(f"   🔴 {reason}", "REASON")
    
    # === 최종 결정 ===
    if sell_signals >= 3:
        strategy['action'] = 'SELL'
        strategy['confidence'] = min(sell_signals * 20, 100)
        log(f"\n✅ 최종 판단: {Colors.RED}매도 신호{Colors.END} (확신도: {strategy['confidence']}%)", "STRATEGY")
    elif buy_signals >= 3:
        strategy['action'] = 'BUY'
        strategy['confidence'] = min(buy_signals * 20, 100)
        log(f"\n✅ 최종 판단: {Colors.GREEN}매수 신호{Colors.END} (확신도: {strategy['confidence']}%)", "STRATEGY")
    else:
        strategy['action'] = 'HOLD'
        strategy['confidence'] = 50
        log(f"\n✅ 최종 판단: {Colors.CYAN}관망{Colors.END} (매수 신호: {buy_signals}, 매도 신호: {sell_signals})", "STRATEGY")
    
    return strategy

# ═══════════════════════════════════════════════════════
# 💱 주문 실행
# ═══════════════════════════════════════════════════════
def execute_order(upbit, strategy, holding, krw_balance):
    """
    전략에 따른 실제 주문 실행
    
    매수: 보유 원화의 20%씩 분할 매수
    매도: 보유 수량의 20%씩 분할 매도
    """
    ticker = strategy['ticker']
    action = strategy['action']
    
    if action == 'HOLD':
        log(f"⏸️  [{ticker}] 관망 - 주문 없음", "INFO")
        return
    
    log_separator()
    log(f"💱 [{ticker}] 주문 실행 시작...", "INFO")
    
    try:
        if action == 'BUY':
            # 분할 매수 (보유 원화의 20%)
            buy_amount = krw_balance * 0.2
            
            if buy_amount < 5000:
                log(f"⚠️  매수 금액 부족 (최소 5,000원 필요, 현재: {buy_amount:,.0f}원)", "WARNING")
                return
            
            log(f"🔵 매수 주문:", "INFO")
            log(f"   • 금액: {buy_amount:,.0f} KRW", "INFO")
            log(f"   • 이유:", "INFO")
            for action_type, reason in strategy['reason']:
                if action_type == 'BUY':
                    log(f"     - {reason}", "INFO")
            
            # 실제 주문 (주석 해제하여 사용)
            # order = upbit.buy_market_order(ticker, buy_amount)
            # log(f"✅ 매수 완료: {order}", "SUCCESS")
            
            log(f"⚠️  [시뮬레이션 모드] 실제 주문은 위 주석을 해제하세요", "WARNING")
            
        elif action == 'SELL':
            # 분할 매도 (보유 수량의 20%)
            sell_amount = holding['amount'] * 0.2
            
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
    print("  🤖 업비트 스마트 스캘핑 봇 v2.1")
    print("  🛡️  안전 모드: 상장폐지 코인 자동 차단")
    print("  🚫 제외 마켓: USDT, BTC")
    print(f"{Colors.END}")
    log_separator()
    
    # 상장폐지 코인 목록 로드
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
