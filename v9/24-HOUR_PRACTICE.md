# 24-Hour Practice Run - Validation Checklist

## 🎯 Purpose

This document provides a comprehensive checklist and automation scripts for the **24-hour practice validation run** before enabling live trading.

**Duration**: 24 hours minimum  
**Mode**: Practice (ENABLE_REAL_TRADING=false)  
**Goal**: Validate system stability, strategy performance, and safety gates

---

## 📋 Pre-Start Checklist

Before starting the 24-hour run, verify:

- [ ] `ENABLE_REAL_TRADING=false` in `.env`
- [ ] `/enable_live.flag` does NOT exist
- [ ] All unit tests passed (see TESTING_GUIDE.md)
- [ ] WebSocket integration test passed
- [ ] Dashboard accessible at http://localhost:5000
- [ ] Sufficient mock capital (1,000,000 KRW recommended)
- [ ] Logs directory exists: `mkdir -p imei_os/practice_logs`

---

## 🚀 Start Practice Run

### Terminal 1: Signal Engine

```bash
cd /home/user/webapp/v9
python3 signal_engine/websocket_emitter.py 2>&1 | tee imei_os/practice_logs/signal_engine.log
```

### Terminal 2: Execution Engine

```bash
cd /home/user/webapp/v9
python3 execution_engine/websocket_receiver.py 2>&1 | tee imei_os/practice_logs/execution_engine.log
```

### Terminal 3: Dashboard

```bash
cd /home/user/webapp/v9
python3 dashboard/dashboard_app.py 2>&1 | tee imei_os/practice_logs/dashboard.log
```

### Terminal 4: Monitor (optional)

```bash
cd /home/user/webapp/v9
watch -n 10 'tail -20 imei_os/TRADING_LOG.csv'
```

**Start Time**: `________ (YYYY-MM-DD HH:MM)`

---

## ✅ Validation Checklist

### 1. System Stability (Critical)

Check every 4 hours:

| Hour | Status | Notes |
|------|--------|-------|
| 0h   | [ ]    | Start time |
| 4h   | [ ]    | |
| 8h   | [ ]    | |
| 12h  | [ ]    | |
| 16h  | [ ]    | |
| 20h  | [ ]    | |
| 24h  | [ ]    | End time |

**Requirements**:
- [ ] No process crashes
- [ ] No WebSocket disconnections > 30s
- [ ] CPU usage stable (< 80%)
- [ ] Memory usage stable (< 2GB)
- [ ] No Python exceptions in logs

---

### 2. Candidate Rotation (Every 5 min)

Sample checks:

| Time | TOP 20 Updated? | Candidates Changed? | Scores Valid? |
|------|-----------------|---------------------|---------------|
| 00:00 | [ ] | N/A | [ ] |
| 00:05 | [ ] | [ ] | [ ] |
| 00:10 | [ ] | [ ] | [ ] |
| 01:00 | [ ] | [ ] | [ ] |
| 06:00 | [ ] | [ ] | [ ] |
| 12:00 | [ ] | [ ] | [ ] |
| 18:00 | [ ] | [ ] | [ ] |
| 23:55 | [ ] | [ ] | [ ] |

**Requirements**:
- [ ] Snapshot fetched every 5 minutes
- [ ] TOP 20 list updates correctly
- [ ] Candidates reflect market movement
- [ ] Scores between 0.0 - 1.0

**Command**:
```bash
# Check snapshot updates
tail -100 imei_os/practice_logs/signal_engine.log | grep "TOP 20"
```

---

### 3. WebSocket Stability

**Metrics** (check at end of 24h):

- [ ] Total signals sent: `________`
- [ ] Total signals received: `________`
- [ ] Success rate: `________%` (should be >99.5%)
- [ ] Average latency: `________ms` (should be <100ms)
- [ ] Max latency: `________ms` (should be <500ms)
- [ ] Disconnections: `________` (should be 0)
- [ ] Reconnections: `________` (should be 0)

**Command**:
```bash
# Check WebSocket stats
grep "Signal sent" imei_os/practice_logs/signal_engine.log | wc -l
grep "Signal received" imei_os/practice_logs/execution_engine.log | wc -l
grep "WebSocket.*error" imei_os/practice_logs/*.log
```

---

### 4. Trade Execution

**Minimum Requirements**:

- [ ] At least 10 total trades
- [ ] At least 3 ULTRA_SCALP trades
- [ ] At least 2 DEEP_HUNTER trades
- [ ] At least 5 full entry→exit cycles completed
- [ ] All entries have `entry_reason`
- [ ] All exits have `exit_reason`

**Exit Reason Distribution**:

| Exit Reason | Count | Expected |
|-------------|-------|----------|
| PARTIAL_3   | _____ | ≥2 |
| PARTIAL_5   | _____ | ≥1 |
| TRAIL_7     | _____ | ≥0 |
| TIME_STOP   | _____ | ≥3 |
| RECOVERY_*  | _____ | 0 (unless -20% occurred) |
| EMERGENCY_EXIT | _____ | 0 |

**Command**:
```bash
# Count trades
wc -l imei_os/TRADING_LOG.csv

# Count exit reasons
tail -n +2 imei_os/TRADING_LOG.csv | cut -d',' -f10 | sort | uniq -c
```

---

### 5. Performance Metrics

**End-of-24h Report**:

```bash
# Generate report
python3 scripts/daily_report.py
```

**Required Metrics**:

| Metric | Value | Requirement | Pass/Fail |
|--------|-------|-------------|-----------|
| **Win Rate** | ____% | ≥55% | [ ] |
| **Average R:R** | ____:1 | ≥1.5:1 | [ ] |
| **Expected Value** | ____ | >0 | [ ] |
| **Max Drawdown** | ____% | ≤5% | [ ] |
| **Total P&L** | ____₩ | >0 preferred | [ ] |
| **Trade Count** | ____ | ≥10 | [ ] |
| **Avg Hold Time** | ____min | <30min (scalp) | [ ] |
| **Profit Factor** | ____ | ≥1.5 | [ ] |

**Definitions**:

- **Win Rate**: (Winning trades / Total trades) × 100%
- **R:R**: Average win size / Average loss size
- **Expected Value**: (Win rate × Avg win) - (Loss rate × Avg loss)
- **Max Drawdown**: (Peak equity - Trough equity) / Peak equity × 100%
- **Profit Factor**: Gross profit / Gross loss

---

### 6. Strategy Performance Breakdown

**ULTRA_SCALP**:

| Metric | Value | Target |
|--------|-------|--------|
| Trades | _____ | ≥3 |
| Win Rate | ____% | ≥60% |
| Avg Hold Time | ____min | 3-10min |
| Partial Exits Used | ____% | ≥50% |

**DEEP_HUNTER**:

| Metric | Value | Target |
|--------|-------|--------|
| Trades | _____ | ≥2 |
| Win Rate | ____% | ≥50% |
| Avg Hold Time | ____h | 2-24h |
| Stage 2/3 Entries | ____% | ≥30% |

**Command**:
```bash
# Strategy breakdown
tail -n +2 imei_os/TRADING_LOG.csv | awk -F',' '{print $4}' | sort | uniq -c
```

---

### 7. Safety Gates

**Exposure Limit**:

| Check Time | Total Invested | Limit | Pass/Fail |
|------------|----------------|-------|-----------|
| 0h         | ______₩        | 100k₩ | [ ] |
| 6h         | ______₩        | 100k₩ | [ ] |
| 12h        | ______₩        | 100k₩ | [ ] |
| 18h        | ______₩        | 100k₩ | [ ] |
| 24h        | ______₩        | 100k₩ | [ ] |

**Daily Drawdown**:

| Check Time | Daily DD% | Limit | Circuit Breaker | Pass/Fail |
|------------|-----------|-------|-----------------|-----------|
| 6h         | _____%    | -2%   | [ ] Active      | [ ] |
| 12h        | _____%    | -2%   | [ ] Active      | [ ] |
| 18h        | _____%    | -2%   | [ ] Active      | [ ] |
| 24h        | _____%    | -2%   | [ ] Active      | [ ] |

**Requirements**:
- [ ] No exposure limit breaches
- [ ] Circuit breaker NOT activated (unless legitimately triggered)
- [ ] All rejected trades logged with reason

**Command**:
```bash
# Check safety gate logs
grep "Safety Gate" imei_os/practice_logs/execution_engine.log | tail -50
```

---

### 8. BTC Stacking

**If any profit ≥10k KRW realized**:

- [ ] BTC purchase triggered
- [ ] BTC amount calculated correctly
- [ ] Log entry in `imei_os/BTC_STACKING_LOG.json`
- [ ] Total BTC accumulated updated

**Command**:
```bash
# Check BTC stacking
cat imei_os/BTC_STACKING_LOG.json | jq '.'
```

---

## 📊 Automated Monitoring Scripts

### Hourly Snapshot Script

Create `scripts/hourly_snapshot.sh`:

```bash
#!/bin/bash
# Hourly snapshot for 24h practice run

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOGFILE="imei_os/practice_logs/hourly_snapshots.log"

echo "=== $TIMESTAMP ===" | tee -a $LOGFILE

# KPIs
echo "📊 KPIs:" | tee -a $LOGFILE
curl -s http://localhost:5000/api/kpis | jq '{equity, daily_pnl, position_count, trades_today}' | tee -a $LOGFILE

# Holdings
echo "" | tee -a $LOGFILE
echo "💼 Holdings:" | tee -a $LOGFILE
curl -s http://localhost:5000/api/holdings | jq 'length' | xargs echo "Position count:" | tee -a $LOGFILE

# Safety
echo "" | tee -a $LOGFILE
echo "🔒 Safety:" | tee -a $LOGFILE
curl -s http://localhost:5000/api/safety | jq '{real_trading_enabled, circuit_breaker_active}' | tee -a $LOGFILE

echo "" | tee -a $LOGFILE
echo "---" | tee -a $LOGFILE
```

**Run every hour**:
```bash
chmod +x scripts/hourly_snapshot.sh
watch -n 3600 scripts/hourly_snapshot.sh
```

---

### End-of-24h Report Script

Create `scripts/practice_24h_report.py`:

```python
#!/usr/bin/env python3
"""
Generate 24-hour practice run report
"""

import csv
import json
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
    try:
        with open('imei_os/TRADING_LOG.csv', 'r') as f:
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
    buys = [t for t in trades if t['type'] == 'BUY']
    sells = [t for t in trades if t['type'] == 'SELL']
    
    wins = [t for t in sells if float(t.get('profit_pct', 0)) > 0]
    losses = [t for t in sells if float(t.get('profit_pct', 0)) <= 0]
    
    win_rate = (len(wins) / len(sells) * 100) if sells else 0
    
    avg_win = sum(float(t['profit_pct']) for t in wins) / len(wins) if wins else 0
    avg_loss = sum(float(t['profit_pct']) for t in losses) / len(losses) if losses else 0
    
    rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
    ev = (win_rate/100 * avg_win) + ((100-win_rate)/100 * avg_loss)
    
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
    print()
    
    print("🎯 PERFORMANCE")
    print(f"  Win Rate: {win_rate:.1f}% {'✅' if win_rate >= 55 else '❌'}")
    print(f"  Average R:R: {rr:.2f}:1 {'✅' if rr >= 1.5 else '❌'}")
    print(f"  Expected Value: {ev:.2f}% {'✅' if ev > 0 else '❌'}")
    print()
    
    print("📋 EXIT REASONS")
    for reason, count in sorted(exit_reasons.items()):
        print(f"  {reason}: {count}")
    print()
    
    # Strategy breakdown
    strategy_stats = defaultdict(lambda: {'trades': 0, 'wins': 0})
    for t in sells:
        strategy = t.get('strategy', 'UNKNOWN')
        strategy_stats[strategy]['trades'] += 1
        if float(t.get('profit_pct', 0)) > 0:
            strategy_stats[strategy]['wins'] += 1
    
    print("📈 STRATEGY BREAKDOWN")
    for strategy, stats in strategy_stats.items():
        wr = (stats['wins'] / stats['trades'] * 100) if stats['trades'] else 0
        print(f"  {strategy}:")
        print(f"    Trades: {stats['trades']}")
        print(f"    Win Rate: {wr:.1f}%")
    print()
    
    # Pass/Fail
    print("✅ PASS/FAIL CRITERIA")
    checks = [
        ("Win Rate ≥55%", win_rate >= 55),
        ("R:R ≥1.5:1", rr >= 1.5),
        ("EV > 0", ev > 0),
        ("Sample Size ≥10", total_trades >= 10),
    ]
    
    all_pass = all(check[1] for check in checks)
    
    for check, passed in checks:
        print(f"  {'✅' if passed else '❌'} {check}")
    
    print()
    print("=" * 60)
    print(f"OVERALL: {'✅ PASS' if all_pass else '❌ FAIL'}")
    print("=" * 60)

if __name__ == "__main__":
    generate_report()
```

**Run at end of 24h**:
```bash
chmod +x scripts/practice_24h_report.py
python3 scripts/practice_24h_report.py > imei_os/practice_logs/24h_report.txt
cat imei_os/practice_logs/24h_report.txt
```

---

## ✅ Final Pass/Fail Decision

### PASS Criteria (ALL must be true)

- [ ] Win rate ≥ 55%
- [ ] Average R:R ≥ 1.5:1
- [ ] Expected value > 0
- [ ] Max drawdown ≤ 5%
- [ ] No system crashes
- [ ] WebSocket success rate >99.5%
- [ ] All exits logged with reasons
- [ ] Circuit breaker NOT triggered (or triggered correctly)
- [ ] Sample size ≥ 10 trades
- [ ] Exposure limit never breached

### FAIL Conditions (ANY triggers fail)

- [ ] Win rate < 50%
- [ ] Max drawdown > 10%
- [ ] System crash/freeze
- [ ] Exit reasons missing/incorrect
- [ ] Circuit breaker triggered incorrectly
- [ ] Exposure limit breached

---

## 🔄 If FAIL: Adjust & Retry

**Review**:
1. Analyze losing trades
2. Check exit timing
3. Review entry conditions
4. Check safety gate logs

**Adjust**:
1. Fine-tune thresholds in `strategies.json`
2. Update entry/exit logic if needed
3. Review capital allocation
4. Check time-stop duration

**Retry**:
1. Reset logs: `rm imei_os/TRADING_LOG.csv; echo "timestamp,type,ticker,strategy,amount,entry_price,exit_price,profit_krw,profit_pct,exit_reason,time_held_min,fee_krw" > imei_os/TRADING_LOG.csv`
2. Restart 24-hour run
3. Monitor closely

---

## ✅ If PASS: Proceed to Live Trading

**Congratulations!** Your 24-hour practice run passed all criteria.

**Next Steps**:
1. Review final report thoroughly
2. Document any observations in `imei_os/practice_logs/notes.txt`
3. Proceed to **Step 8: Go Live** in ONBOARDING.md
4. Follow live trading enablement steps carefully

---

## 📝 Practice Run Notes

Use this space to document observations during the 24-hour run:

```
Date: __________
Start Time: __________
End Time: __________

Observations:
- 
- 
- 

Issues Encountered:
- 
- 

Adjustments Made:
- 
- 

Final Decision: [ ] PASS [ ] FAIL

Signed: __________
```

---

**Created**: 2026-02-18  
**Version**: 9.0  
**Purpose**: 24-hour practice validation before live trading
