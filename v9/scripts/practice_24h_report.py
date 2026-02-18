#!/usr/bin/env python3
"""
Generate 24-hour practice run report
"""

import csv
import json
import os
from datetime import datetime
from collections import defaultdict

def generate_report():
    print("=" * 60)
    print("24-HOUR PRACTICE RUN REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Read trading log
    trades = []
    log_path = 'imei_os/TRADING_LOG.csv'
    
    if not os.path.exists(log_path):
        print("⚠️ Trading log not found!")
        return
    
    try:
        with open(log_path, 'r') as f:
            reader = csv.DictReader(f)
            trades = list(reader)
    except Exception as e:
        print(f"Error reading log: {e}")
        return
    
    if not trades:
        print("⚠️ No trades found!")
        return
    
    # Calculate metrics
    total_trades = len(trades)
    buys = [t for t in trades if t.get('type') == 'BUY']
    sells = [t for t in trades if t.get('type') == 'SELL']
    
    if not sells:
        print("⚠️ No completed trades (sells) yet!")
        print(f"  Entries: {len(buys)}")
        return
    
    wins = [t for t in sells if float(t.get('profit_pct', 0)) > 0]
    losses = [t for t in sells if float(t.get('profit_pct', 0)) <= 0]
    
    win_rate = (len(wins) / len(sells) * 100) if sells else 0
    
    avg_win = sum(float(t.get('profit_pct', 0)) for t in wins) / len(wins) if wins else 0
    avg_loss = sum(float(t.get('profit_pct', 0)) for t in losses) / len(losses) if losses else 0
    
    rr = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
    
    ev = (win_rate/100 * avg_win) + ((100-win_rate)/100 * avg_loss)
    
    # Total P&L
    total_pnl_krw = sum(float(t.get('profit_krw', 0)) for t in sells)
    
    # Max drawdown (simplified)
    equity = 1000000  # Starting equity
    peak = equity
    max_dd = 0
    
    for t in trades:
        if t.get('type') == 'SELL':
            profit = float(t.get('profit_krw', 0))
            equity += profit
            if equity > peak:
                peak = equity
            dd = ((peak - equity) / peak) * 100
            if dd > max_dd:
                max_dd = dd
    
    # Exit reasons
    exit_reasons = defaultdict(int)
    for t in sells:
        reason = t.get('exit_reason', 'UNKNOWN')
        exit_reasons[reason] += 1
    
    # Print report
    print("📊 SUMMARY")
    print(f"  Total Trades: {total_trades}")
    print(f"  Entries (BUY): {len(buys)}")
    print(f"  Exits (SELL): {len(sells)}")
    print(f"  Completed Cycles: {len(sells)}")
    print()
    
    print("🎯 PERFORMANCE")
    print(f"  Win Rate: {win_rate:.1f}% {'✅ PASS' if win_rate >= 55 else '❌ FAIL'} (target: ≥55%)")
    print(f"  Average R:R: {rr:.2f}:1 {'✅ PASS' if rr >= 1.5 else '❌ FAIL'} (target: ≥1.5:1)")
    print(f"  Expected Value: {ev:+.2f}% {'✅ PASS' if ev > 0 else '❌ FAIL'} (target: >0%)")
    print(f"  Max Drawdown: {max_dd:.2f}% {'✅ PASS' if max_dd <= 5 else '❌ FAIL'} (target: ≤5%)")
    print(f"  Total P&L: {total_pnl_krw:+,.0f} KRW")
    print(f"  Average Win: {avg_win:+.2f}%")
    print(f"  Average Loss: {avg_loss:.2f}%")
    print()
    
    print("📋 EXIT REASONS")
    for reason, count in sorted(exit_reasons.items(), key=lambda x: -x[1]):
        pct = (count / len(sells) * 100)
        print(f"  {reason}: {count} ({pct:.1f}%)")
    print()
    
    # Strategy breakdown
    strategy_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'total_profit': 0})
    for t in sells:
        strategy = t.get('strategy', 'UNKNOWN')
        profit_pct = float(t.get('profit_pct', 0))
        strategy_stats[strategy]['trades'] += 1
        if profit_pct > 0:
            strategy_stats[strategy]['wins'] += 1
        strategy_stats[strategy]['total_profit'] += profit_pct
    
    print("📈 STRATEGY BREAKDOWN")
    for strategy, stats in sorted(strategy_stats.items()):
        wr = (stats['wins'] / stats['trades'] * 100) if stats['trades'] else 0
        avg_profit = stats['total_profit'] / stats['trades'] if stats['trades'] else 0
        print(f"  {strategy}:")
        print(f"    Trades: {stats['trades']}")
        print(f"    Win Rate: {wr:.1f}%")
        print(f"    Avg Profit: {avg_profit:+.2f}%")
    print()
    
    # Time analysis
    if sells:
        hold_times = []
        for t in sells:
            try:
                time_held = float(t.get('time_held_min', 0))
                hold_times.append(time_held)
            except:
                pass
        
        if hold_times:
            avg_hold = sum(hold_times) / len(hold_times)
            print("⏱️ TIMING")
            print(f"  Average Hold Time: {avg_hold:.1f} minutes")
            print(f"  Min Hold Time: {min(hold_times):.1f} minutes")
            print(f"  Max Hold Time: {max(hold_times):.1f} minutes")
            print()
    
    # Pass/Fail
    print("=" * 60)
    print("✅ PASS/FAIL CRITERIA")
    print("=" * 60)
    
    checks = [
        ("Win Rate ≥55%", win_rate >= 55),
        ("R:R ≥1.5:1", rr >= 1.5),
        ("EV > 0", ev > 0),
        ("Max Drawdown ≤5%", max_dd <= 5),
        ("Sample Size ≥10 trades", total_trades >= 10),
    ]
    
    all_pass = all(check[1] for check in checks)
    
    for check, passed in checks:
        print(f"  {'✅' if passed else '❌'} {check}")
    
    print()
    print("=" * 60)
    if all_pass:
        print("✅ OVERALL: PASS - Ready for live trading")
    else:
        print("❌ OVERALL: FAIL - Review and adjust before live trading")
    print("=" * 60)
    
    # Recommendations
    if not all_pass:
        print()
        print("🔧 RECOMMENDATIONS:")
        if win_rate < 55:
            print("  • Review entry conditions (may be too aggressive)")
            print("  • Check exit timing (may be exiting winners too early)")
        if rr < 1.5:
            print("  • Review stop-loss levels (may be too tight)")
            print("  • Review take-profit targets (may be too conservative)")
        if ev <= 0:
            print("  • System has negative expectancy - must fix before live trading")
            print("  • Review entire strategy logic")
        if max_dd > 5:
            print("  • Reduce position sizing")
            print("  • Tighten risk management")
        if total_trades < 10:
            print("  • Extend practice run to get more data")

if __name__ == "__main__":
    generate_report()
