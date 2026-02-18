#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 봇 매매 로직 테스트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
실제로 신호가 감지되는지 테스트합니다.
"""

import pyupbit
import pandas as pd
from datetime import datetime, timedelta

# 설정값 (완화된 조건)
SURGE_THRESHOLD_1M = 0.8  # 1분에 0.8% 급등
MIN_VOLUME_KRW = 30000000  # 3천만원

def test_market_scan():
    """시장 스캔 테스트"""
    
    print("=" * 60)
    print("🔍 업비트 시장 스캔 테스트")
    print("=" * 60)
    
    # KRW 마켓 티커 가져오기
    tickers = pyupbit.get_tickers(fiat="KRW")
    print(f"\n총 {len(tickers)}개 코인 스캔 중...\n")
    
    signals = []
    
    for i, ticker in enumerate(tickers[:50], 1):  # 처음 50개만 테스트
        try:
            # 현재가 및 1분봉 데이터
            current_price = pyupbit.get_current_price(ticker)
            if not current_price:
                continue
            
            # 1분봉 데이터
            df = pyupbit.get_ohlcv(ticker, interval="minute1", count=2)
            if df is None or len(df) < 2:
                continue
            
            # 1분 변화율 계산
            price_1m_ago = df.iloc[-2]['close']
            change_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
            
            # 거래량 (KRW)
            volume_krw = df.iloc[-1]['value']
            
            # 신호 감지
            if change_1m >= SURGE_THRESHOLD_1M and volume_krw >= MIN_VOLUME_KRW:
                signals.append({
                    'ticker': ticker,
                    'price': current_price,
                    'change_1m': change_1m,
                    'volume_krw': volume_krw
                })
                print(f"🚀 [{i}/{50}] {ticker}: +{change_1m:.2f}% (거래량: {volume_krw/1000000:.1f}M)")
            
            if i % 10 == 0:
                print(f"   ... {i}/50 스캔 완료")
        
        except Exception as e:
            continue
    
    print(f"\n{'=' * 60}")
    print(f"📊 스캔 결과")
    print("=" * 60)
    print(f"총 스캔: 50개 코인")
    print(f"신호 감지: {len(signals)}개")
    
    if signals:
        print(f"\n🎯 매수 신호 목록:")
        for sig in signals:
            print(f"  {sig['ticker']}: {sig['price']:,}원 (+{sig['change_1m']:.2f}%) 거래량: {sig['volume_krw']/1000000:.1f}M")
    else:
        print(f"\n⚠️ 신호가 감지되지 않았습니다!")
        print(f"   조건:")
        print(f"   - 1분 변화율: >= {SURGE_THRESHOLD_1M}%")
        print(f"   - 거래량: >= {MIN_VOLUME_KRW/1000000:.0f}M원")
        print(f"\n💡 조건을 더 완화하거나, 더 많은 코인을 스캔해야 합니다.")

if __name__ == "__main__":
    test_market_scan()
