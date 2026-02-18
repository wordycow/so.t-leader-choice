#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 Daily Trading Report Generator
Generates comprehensive daily trading statistics from imei_os/TRADING_LOG.csv
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import json

def load_trading_log(csv_path='imei_os/TRADING_LOG.csv'):
    """Load trading log from CSV"""
    trades = []
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        print(f"❌ Trading log not found: {csv_path}")
        return trades
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('timestamp') and not row['timestamp'].startswith('#'):
                trades.append(row)
    
    return trades

def parse_timestamp(ts_str):
    """Parse timestamp string to datetime"""
    try:
        return datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
    except:
        return None

def calculate_stats(trades, start_date=None, end_date=None):
    """Calculate trading statistics"""
    
    # Filter by date range if provided
    filtered_trades = []
    for trade in trades:
        ts = parse_timestamp(trade.get('timestamp', ''))
        if not ts:
            continue
        
        if start_date and ts < start_date:
            continue
        if end_date and ts > end_date:
            continue
        
        filtered_trades.append(trade)
    
    # Group by user
    user_trades = defaultdict(list)
    for trade in filtered_trades:
        user_id = trade.get('user_id', 'unknown')
        user_trades[user_id].append(trade)
    
    # Calculate stats per user
    results = {}
    
    for user_id, utrades in user_trades.items():
        # Separate BUY and SELL
        buys = [t for t in utrades if t.get('action') == 'BUY']
        sells = [t for t in utrades if t.get('action') == 'SELL']
        
        # Win/Loss calculation
        wins = []
        losses = []
        total_profit_pct = 0.0
        total_profit_krw = 0.0
        
        for sell in sells:
            try:
                profit_rate = float(sell.get('profit_rate', 0))
                entry_price = float(sell.get('entry_price', 0))
                exit_price = float(sell.get('exit_price', 0))
                amount = float(sell.get('amount', 0))
                
                if entry_price > 0:
                    profit_krw = (exit_price - entry_price) * amount
                    total_profit_krw += profit_krw
                    total_profit_pct += profit_rate
                    
                    if profit_rate > 0:
                        wins.append((sell, profit_rate, profit_krw))
                    else:
                        losses.append((sell, profit_rate, profit_krw))
            except:
                continue
        
        # Win rate
        total_closed = len(sells)
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_closed * 100) if total_closed > 0 else 0.0
        
        # Average profit/loss
        avg_profit_rate = total_profit_pct / total_closed if total_closed > 0 else 0.0
        
        # Risk:Reward calculation
        avg_win = sum(w[1] for w in wins) / len(wins) if wins else 0.0
        avg_loss = abs(sum(l[1] for l in losses) / len(losses)) if losses else 0.0
        risk_reward = avg_win / avg_loss if avg_loss > 0 else 0.0
        
        # Expected Value (EV)
        ev = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        # Max drawdown (simple estimate from consecutive losses)
        max_drawdown = 0.0
        current_drawdown = 0.0
        for sell in sells:
            try:
                profit_rate = float(sell.get('profit_rate', 0))
                if profit_rate < 0:
                    current_drawdown += abs(profit_rate)
                    max_drawdown = max(max_drawdown, current_drawdown)
                else:
                    current_drawdown = 0
            except:
                continue
        
        # Hold time analysis
        hold_times = []
        for sell in sells:
            try:
                hold_sec = int(sell.get('hold_time_seconds', 0))
                hold_times.append(hold_sec)
            except:
                continue
        
        avg_hold_time_sec = sum(hold_times) / len(hold_times) if hold_times else 0
        
        # Strategy breakdown
        strategy_stats = defaultdict(lambda: {'count': 0, 'wins': 0, 'profit': 0.0})
        for sell in sells:
            strategy = sell.get('strategy', 'unknown')
            profit_rate = float(sell.get('profit_rate', 0)) if sell.get('profit_rate') else 0.0
            
            strategy_stats[strategy]['count'] += 1
            if profit_rate > 0:
                strategy_stats[strategy]['wins'] += 1
            strategy_stats[strategy]['profit'] += profit_rate
        
        results[user_id] = {
            'total_trades': total_closed,
            'total_buys': len(buys),
            'total_sells': len(sells),
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': win_rate,
            'avg_profit_rate': avg_profit_rate,
            'total_profit_krw': total_profit_krw,
            'risk_reward': risk_reward,
            'expected_value': ev,
            'max_drawdown': max_drawdown,
            'avg_hold_time_sec': avg_hold_time_sec,
            'strategy_stats': dict(strategy_stats),
            'wins': wins,
            'losses': losses
        }
    
    return results

def print_report(stats, title="Trading Report"):
    """Print formatted report"""
    print("\n" + "="*80)
    print(f"📊 {title}")
    print("="*80)
    
    for user_id, data in stats.items():
        print(f"\n👤 User: {user_id}")
        print("-" * 80)
        print(f"  Total Trades (Closed): {data['total_trades']}")
        print(f"  Total Buys:            {data['total_buys']}")
        print(f"  Total Sells:           {data['total_sells']}")
        print(f"  Wins / Losses:         {data['win_count']} / {data['loss_count']}")
        print(f"  Win Rate:              {data['win_rate']:.2f}%")
        print(f"  Avg Profit Rate:       {data['avg_profit_rate']:+.2f}%")
        print(f"  Total Profit (KRW):    {data['total_profit_krw']:+,.0f} 원")
        print(f"  Risk:Reward Ratio:     {data['risk_reward']:.2f}")
        print(f"  Expected Value (EV):   {data['expected_value']:+.2f}%")
        print(f"  Max Drawdown:          {data['max_drawdown']:.2f}%")
        
        # Hold time
        avg_hold_min = data['avg_hold_time_sec'] / 60
        if avg_hold_min >= 60:
            print(f"  Avg Hold Time:         {avg_hold_min/60:.1f} hours")
        else:
            print(f"  Avg Hold Time:         {avg_hold_min:.1f} minutes")
        
        # Strategy breakdown
        print("\n  📈 Strategy Performance:")
        for strategy, st_data in data['strategy_stats'].items():
            st_win_rate = (st_data['wins'] / st_data['count'] * 100) if st_data['count'] > 0 else 0
            st_avg_profit = st_data['profit'] / st_data['count'] if st_data['count'] > 0 else 0
            print(f"    - {strategy:20s}: {st_data['count']:3d} trades | {st_win_rate:5.1f}% WR | {st_avg_profit:+6.2f}% avg")
    
    print("\n" + "="*80)

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate daily trading report')
    parser.add_argument('--csv', default='imei_os/TRADING_LOG.csv', help='Path to trading log CSV')
    parser.add_argument('--days', type=int, default=1, help='Number of days to analyze (default: 1 = today)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Load trades
    trades = load_trading_log(args.csv)
    
    if not trades:
        print("⚠️  No trades found in log")
        return
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    # Calculate stats
    stats = calculate_stats(trades, start_date, end_date)
    
    if not stats:
        print(f"⚠️  No trades in the last {args.days} day(s)")
        return
    
    # Output
    if args.json:
        # Convert to JSON-serializable format
        json_output = {}
        for user_id, data in stats.items():
            json_output[user_id] = {
                k: v for k, v in data.items() 
                if k not in ['wins', 'losses']  # Skip raw trade lists
            }
        print(json.dumps(json_output, indent=2, ensure_ascii=False))
    else:
        title = f"Trading Report - Last {args.days} Day(s)"
        print_report(stats, title)

if __name__ == '__main__':
    main()
