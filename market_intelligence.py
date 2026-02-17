#!/usr/bin/env python3
"""
🧠 Market Intelligence System
- 시장 구분 (사람/고래/봇)
- 호가창 분석
- 패턴 학습
- 데이터 축적
"""

import sqlite3
import pyupbit
import json
from datetime import datetime
import time

# 데이터베이스 초기화
def init_market_db():
    """시장 분석 데이터베이스 생성"""
    conn = sqlite3.connect('market_intelligence.db')
    c = conn.cursor()
    
    # 1. 호가창 스냅샷
    c.execute('''
        CREATE TABLE IF NOT EXISTS orderbook_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            bid_total REAL,
            ask_total REAL,
            bid_depth TEXT,
            ask_depth TEXT,
            strength REAL,
            market_type TEXT
        )
    ''')
    
    # 2. 큰 주문 (고래)
    c.execute('''
        CREATE TABLE IF NOT EXISTS whale_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            order_type TEXT,
            price REAL,
            size REAL,
            size_krw REAL
        )
    ''')
    
    # 3. 거래 패턴
    c.execute('''
        CREATE TABLE IF NOT EXISTS trade_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pattern_type TEXT,
            score REAL,
            result TEXT,
            profit_rate REAL
        )
    ''')
    
    # 4. 시장 상태
    c.execute('''
        CREATE TABLE IF NOT EXISTS market_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            btc_price REAL,
            btc_change REAL,
            eth_change REAL,
            market_direction TEXT,
            active_coins INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Market Intelligence DB 초기화 완료")

def analyze_orderbook_depth(ticker):
    """호가창 분석 - 고래/봇/사람 구분"""
    try:
        orderbook = pyupbit.get_orderbook(ticker)
        if not orderbook:
            return None
        
        units = orderbook['orderbook_units']
        
        # 매수/매도 호가 분석
        bid_sizes = [u['bid_size'] for u in units]
        ask_sizes = [u['ask_size'] for u in units]
        bid_prices = [u['bid_price'] for u in units]
        ask_prices = [u['ask_price'] for u in units]
        
        total_bid = sum(bid_sizes)
        total_ask = sum(ask_sizes)
        
        # 1. 고래 감지 (큰 주문)
        max_bid = max(bid_sizes)
        max_ask = max(ask_sizes)
        avg_bid = total_bid / len(bid_sizes)
        avg_ask = total_ask / len(ask_sizes)
        
        whale_threshold = 10  # 평균의 10배
        
        has_whale = False
        whale_orders = []
        
        for i, (size, price) in enumerate(zip(bid_sizes, bid_prices)):
            if size > avg_bid * whale_threshold:
                has_whale = True
                whale_orders.append({
                    'type': 'BID',
                    'price': price,
                    'size': size,
                    'size_krw': price * size
                })
        
        for i, (size, price) in enumerate(zip(ask_sizes, ask_prices)):
            if size > avg_ask * whale_threshold:
                has_whale = True
                whale_orders.append({
                    'type': 'ASK',
                    'price': price,
                    'size': size,
                    'size_krw': price * size
                })
        
        # 2. 봇 감지 (규칙적 배치)
        # 가격 간격의 표준편차 계산
        bid_gaps = [bid_prices[i] - bid_prices[i+1] for i in range(len(bid_prices)-1)]
        ask_gaps = [ask_prices[i+1] - ask_prices[i] for i in range(len(ask_prices)-1)]
        
        # 간격이 일정하면 봇일 가능성
        import statistics
        try:
            bid_gap_std = statistics.stdev(bid_gaps) if len(bid_gaps) > 1 else 0
            ask_gap_std = statistics.stdev(ask_gaps) if len(ask_gaps) > 1 else 0
            bid_gap_mean = statistics.mean(bid_gaps) if len(bid_gaps) > 0 else 1
            ask_gap_mean = statistics.mean(ask_gaps) if len(ask_gaps) > 0 else 1
            
            bid_regularity = (bid_gap_std / bid_gap_mean) if bid_gap_mean != 0 else 1
            ask_regularity = (ask_gap_std / ask_gap_mean) if ask_gap_mean != 0 else 1
            
            is_bot_market = (bid_regularity < 0.1 and ask_regularity < 0.1)
        except:
            is_bot_market = False
        
        # 3. 시장 타입 판단
        if has_whale:
            market_type = 'WHALE'
        elif is_bot_market:
            market_type = 'BOT'
        else:
            market_type = 'RETAIL'
        
        return {
            'ticker': ticker,
            'bid_total': total_bid,
            'ask_total': total_ask,
            'strength': (total_bid / total_ask * 100) if total_ask > 0 else 100,
            'market_type': market_type,
            'whale_orders': whale_orders,
            'is_whale': has_whale,
            'is_bot': is_bot_market,
            'bid_regularity': bid_regularity if not is_bot_market else 0,
            'ask_regularity': ask_regularity if not is_bot_market else 0
        }
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

def save_orderbook_snapshot(data):
    """호가창 스냅샷 저장"""
    conn = sqlite3.connect('market_intelligence.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO orderbook_snapshots 
        (ticker, bid_total, ask_total, bid_depth, ask_depth, strength, market_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['ticker'],
        data['bid_total'],
        data['ask_total'],
        json.dumps([]),
        json.dumps([]),
        data['strength'],
        data['market_type']
    ))
    
    # 고래 주문 저장
    for order in data.get('whale_orders', []):
        c.execute('''
            INSERT INTO whale_orders 
            (ticker, order_type, price, size, size_krw)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['ticker'],
            order['type'],
            order['price'],
            order['size'],
            order['size_krw']
        ))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("🧠 Market Intelligence System 시작")
    init_market_db()
    
    # 테스트
    tickers = ['KRW-BTC', 'KRW-ETH', 'KRW-DOGE']
    
    for ticker in tickers:
        print(f"\n분석 중: {ticker}")
        data = analyze_orderbook_depth(ticker)
        if data:
            print(f"  시장 타입: {data['market_type']}")
            print(f"  채결 강도: {data['strength']:.1f}%")
            print(f"  고래: {'있음' if data['is_whale'] else '없음'}")
            print(f"  봇: {'예' if data['is_bot'] else '아니오'}")
            
            if data['whale_orders']:
                print(f"  🐋 고래 주문 {len(data['whale_orders'])}개:")
                for order in data['whale_orders'][:3]:
                    print(f"    {order['type']} {order['price']:,.0f}원 × {order['size']:.2f} = {order['size_krw']:,.0f}원")
            
            save_orderbook_snapshot(data)
        
        time.sleep(0.5)
    
    print("\n✅ 데이터 수집 완료!")
