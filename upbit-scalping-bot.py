#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
업비트 스캘핑 봇 (Bollinger Bands + RSI)
- 100만원 시드
- 5단계 분할 매수/매도
- 24시간 자동 운영
"""

import time
import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime
import os

# python-dotenv로 .env 파일 로드 (선택적)
try:
    from dotenv import load_dotenv
    load_dotenv()  # .env 파일이 있으면 자동 로드
    print("✅ .env 파일 로드 완료")
except ImportError:
    print("⚠️  python-dotenv 미설치 (환경변수에서 직접 로드)")
    print("   설치 권장: pip install python-dotenv")

# =====================================
# 설정
# =====================================

# API 키 설정 (환경변수에서 가져오기)
ACCESS_KEY = os.getenv('UPBIT_ACCESS_KEY')
SECRET_KEY = os.getenv('UPBIT_SECRET_KEY')

# API 키 검증
if not ACCESS_KEY or not SECRET_KEY:
    print("❌ ERROR: API 키가 설정되지 않았습니다!")
    print("   다음 중 하나를 선택하세요:")
    print("   1. .env 파일 생성: cp .env.example .env && nano .env")
    print("   2. 환경변수 설정: export UPBIT_ACCESS_KEY='...'")
    print("   3. 자세한 방법: UPBIT-API-SETUP-GUIDE.md 참고")
    exit(1)

print(f"✅ API 키 로드 성공: {ACCESS_KEY[:8]}****")

# 거래 설정
TICKER = "KRW-BTC"  # 거래할 코인 (비트코인)
TOTAL_SEED = 1_000_000  # 100만원
SPLIT_COUNT = 5  # 5단계 분할
EACH_TRADE_AMOUNT = TOTAL_SEED / SPLIT_COUNT  # 각 단계당 20만원

# 지표 설정
RSI_PERIOD = 14
BB_PERIOD = 20
BB_STD = 2

# 매매 설정
RSI_OVERSOLD = 30  # RSI 과매도 기준
RSI_OVERBOUGHT = 70  # RSI 과매수 기준
TARGET_PROFIT_RATE = 0.015  # 목표 수익률 1.5%
STOP_LOSS_RATE = -0.03  # 손절 -3%

# 체크 간격 (초)
CHECK_INTERVAL = 10

# =====================================
# 지표 계산 함수
# =====================================

def calculate_rsi(df, period=14):
    """RSI 계산"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(df, period=20, std=2):
    """볼린저 밴드 계산"""
    ma = df['close'].rolling(window=period).mean()
    std_dev = df['close'].rolling(window=period).std()
    
    upper = ma + (std_dev * std)
    lower = ma - (std_dev * std)
    
    return upper, ma, lower

def calculate_fibonacci_level(high, low):
    """피보나치 50% 레벨 계산"""
    return low + (high - low) * 0.5

# =====================================
# 매매 함수
# =====================================

def get_balance(upbit, ticker="KRW"):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            return float(b['balance'])
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_current_price(ticker)

def get_avg_buy_price(upbit, ticker):
    """평균 매수가 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker.split('-')[1]:
            return float(b['avg_buy_price'])
    return 0

def get_coin_balance(upbit, ticker):
    """코인 보유량 조회"""
    balances = upbit.get_balances()
    coin_name = ticker.split('-')[1]
    for b in balances:
        if b['currency'] == coin_name:
            return float(b['balance'])
    return 0

# =====================================
# 매매 신호 판단
# =====================================

def check_buy_signal(df, current_price):
    """매수 신호 체크"""
    # 최신 데이터
    rsi = df['rsi'].iloc[-1]
    bb_lower = df['bb_lower'].iloc[-1]
    bb_middle = df['bb_middle'].iloc[-1]
    
    # 최근 고가/저가
    high_24h = df['high'].tail(24).max()
    low_24h = df['low'].tail(24).min()
    fib_50 = calculate_fibonacci_level(high_24h, low_24h)
    
    # 매수 조건
    buy_signal = False
    reason = ""
    
    # 1. RSI 과매도
    if rsi < RSI_OVERSOLD:
        buy_signal = True
        reason += f"RSI과매도({rsi:.1f}) "
    
    # 2. 볼린저 하단 근처
    if current_price <= bb_lower * 1.01:  # 하단의 1% 이내
        buy_signal = True
        reason += f"BB하단근처 "
    
    # 3. 피보나치 50% 이하
    if current_price <= fib_50:
        buy_signal = True
        reason += f"피보나치50%이하 "
    
    return buy_signal, reason

def check_sell_signal(df, current_price, avg_buy_price):
    """매도 신호 체크"""
    if avg_buy_price == 0:
        return False, ""
    
    # 수익률 계산
    profit_rate = (current_price - avg_buy_price) / avg_buy_price
    
    # 최신 데이터
    rsi = df['rsi'].iloc[-1]
    bb_upper = df['bb_upper'].iloc[-1]
    
    sell_signal = False
    reason = ""
    
    # 1. 목표 수익률 도달
    if profit_rate >= TARGET_PROFIT_RATE:
        sell_signal = True
        reason += f"목표수익({profit_rate*100:.2f}%) "
    
    # 2. RSI 과매수
    if rsi > RSI_OVERBOUGHT and profit_rate > 0:
        sell_signal = True
        reason += f"RSI과매수({rsi:.1f}) "
    
    # 3. 볼린저 상단 근처
    if current_price >= bb_upper * 0.99 and profit_rate > 0:
        sell_signal = True
        reason += f"BB상단근처 "
    
    # 4. 손절
    if profit_rate <= STOP_LOSS_RATE:
        sell_signal = True
        reason += f"손절({profit_rate*100:.2f}%) "
    
    return sell_signal, reason

# =====================================
# 메인 봇 로직
# =====================================

def log(message):
    """로그 출력"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def main():
    """메인 봇"""
    log("=" * 60)
    log("🤖 업비트 스캘핑 봇 시작!")
    log(f"💰 시드: {TOTAL_SEED:,}원")
    log(f"📊 분할: {SPLIT_COUNT}단계")
    log(f"🎯 코인: {TICKER}")
    log(f"📈 전략: 볼린저밴드 + RSI + 피보나치")
    log("=" * 60)
    
    # API 연결
    try:
        upbit = pyupbit.Upbit(ACCESS_KEY, SECRET_KEY)
        log("✅ 업비트 API 연결 성공")
    except Exception as e:
        log(f"❌ API 연결 실패: {e}")
        return
    
    # 매수 카운트 (5단계 중 몇 번째)
    buy_count = 0
    
    while True:
        try:
            # 1. 데이터 가져오기 (1분봉)
            df = pyupbit.get_ohlcv(TICKER, interval="minute1", count=100)
            
            if df is None or len(df) < BB_PERIOD:
                log("⚠️ 데이터 부족, 대기 중...")
                time.sleep(CHECK_INTERVAL)
                continue
            
            # 2. 지표 계산
            df['rsi'] = calculate_rsi(df, RSI_PERIOD)
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = calculate_bollinger_bands(df, BB_PERIOD, BB_STD)
            
            # 3. 현재 상태 조회
            current_price = get_current_price(TICKER)
            krw_balance = get_balance(upbit, "KRW")
            coin_balance = get_coin_balance(upbit, TICKER)
            avg_buy_price = get_avg_buy_price(upbit, TICKER)
            
            # 현재 수익률
            if avg_buy_price > 0 and coin_balance > 0:
                profit_rate = (current_price - avg_buy_price) / avg_buy_price * 100
            else:
                profit_rate = 0
            
            # 상태 로그
            rsi = df['rsi'].iloc[-1]
            bb_upper = df['bb_upper'].iloc[-1]
            bb_lower = df['bb_lower'].iloc[-1]
            
            log(f"💵 KRW: {krw_balance:,.0f}원 | 🪙 {TICKER.split('-')[1]}: {coin_balance:.8f} | 💹 수익률: {profit_rate:+.2f}%")
            log(f"📊 가격: {current_price:,.0f} | RSI: {rsi:.1f} | BB상: {bb_upper:,.0f} | BB하: {bb_lower:,.0f}")
            
            # 4. 매도 체크 (보유 중일 때)
            if coin_balance > 0:
                sell_signal, sell_reason = check_sell_signal(df, current_price, avg_buy_price)
                
                if sell_signal:
                    log(f"🔴 매도 신호! {sell_reason}")
                    
                    # 전량 매도
                    try:
                        result = upbit.sell_market_order(TICKER, coin_balance)
                        log(f"✅ 매도 완료: {coin_balance:.8f} @ {current_price:,.0f}원")
                        log(f"💰 수익: {profit_rate:+.2f}%")
                        buy_count = 0  # 매수 카운트 리셋
                    except Exception as e:
                        log(f"❌ 매도 실패: {e}")
            
            # 5. 매수 체크 (잔고가 있고 아직 5단계를 다 안 샀을 때)
            elif krw_balance >= 5000 and buy_count < SPLIT_COUNT:  # 최소 주문금액 5천원
                buy_signal, buy_reason = check_buy_signal(df, current_price)
                
                if buy_signal:
                    # 매수 금액 계산
                    available_amount = min(EACH_TRADE_AMOUNT, krw_balance)
                    
                    if available_amount >= 5000:
                        log(f"🟢 매수 신호! ({buy_count+1}/{SPLIT_COUNT}단계) {buy_reason}")
                        
                        try:
                            result = upbit.buy_market_order(TICKER, available_amount)
                            buy_count += 1
                            log(f"✅ 매수 완료: {available_amount:,.0f}원 @ {current_price:,.0f}원")
                        except Exception as e:
                            log(f"❌ 매수 실패: {e}")
            
            # 6. 대기
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            log("👋 봇 종료 (사용자 중단)")
            break
        except Exception as e:
            log(f"⚠️ 에러 발생: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # pyupbit 설치 확인
    try:
        import pyupbit
    except ImportError:
        print("pyupbit 설치 필요: pip install pyupbit")
        exit(1)
    
    main()
